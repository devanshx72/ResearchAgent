"""
Research task executor - runs the LangGraph pipeline.
"""

import asyncio
from typing import Optional

from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from graph.graph_builder import build_graph
from api.task_manager import task_manager
from models.schemas import TaskStatus


async def execute_research_task(task_id: str, resume: bool = False):
    """
    Execute a research task through the agent pipeline.

    Args:
        task_id: Task identifier
        resume: Whether this is resuming from HITL checkpoint
    """
    try:
        # Get task
        task = await task_manager.get_task(task_id)
        if not task:
            return

        # Update status
        await task_manager.update_status(task_id, TaskStatus.processing)
        await task_manager.broadcast_update(task_id, {
            "task_id": task_id,
            "event_type": "status_update",
            "data": {"status": "processing", "message": "Starting research pipeline"}
        })

        # Build graph (singleton with persistent MemorySaver)
        app = build_graph()

        # Get request parameters
        request = task["request"]

        # Configuration — thread_id must be consistent for interrupt/resume
        config = {"configurable": {"thread_id": task_id}}

        # Determine what to stream
        if resume:
            # Resume from HITL: send the human decision via Command(resume=...)
            human_decision = task.get("human_decision", "approve")
            human_feedback = task.get("human_feedback", "")
            stream_input = Command(resume={
                "decision": human_decision,
                "feedback": human_feedback
            })
        else:
            # Fresh start
            stream_input = {
                "query": request["query"],
                "export_format": request["export_format"],
                "tone": request["tone"],
                "word_count": request["word_count"],
                "sub_questions": [],
                "search_results": [],
                "graded_results": [],
                "rejected_queries": [],
                "research_notes": "",
                "article_draft": "",
                "quality_score": 0.0,
                "quality_feedback": "",
                "sources": [],
                "human_feedback": "",
                "human_decision": "",
                "final_article": "",
                "export_path": "",
                "iteration_count": 0,
                "write_iteration_count": 0
            }

        # Keep a local copy of state for result extraction
        state = task.get("state", {}) if resume else {}

        # In LangGraph 0.6.x, app.stream() does NOT raise GraphInterrupt.
        # Instead it emits an "__interrupt__" key in the stream output and
        # then the iteration ends. We detect this with a flag.
        interrupted = False

        for output in app.stream(stream_input, config, stream_mode="updates"):
            node_name = list(output.keys())[0]

            # Skip the synthetic __interrupt__ event; set flag for post-loop check
            if node_name == "__interrupt__":
                interrupted = True
                continue

            await task_manager.update_task(task_id, {"current_node": node_name})

            node_output = output[node_name]
            state.update(node_output)
            await task_manager.update_state(task_id, state)

            # Broadcast progress
            await task_manager.broadcast_update(task_id, {
                "task_id": task_id,
                "event_type": "node_complete",
                "data": {
                    "node": node_name,
                    "state_keys": list(node_output.keys())
                }
            })

        if interrupted:
            # HITL checkpoint reached — pause and wait for human decision
            await task_manager.update_status(task_id, TaskStatus.hitl_review, "hitl")
            await task_manager.update_state(task_id, state)

            await task_manager.broadcast_update(task_id, {
                "task_id": task_id,
                "event_type": "hitl_checkpoint",
                "data": {
                    "status": "hitl_review",
                    "message": "Human review required",
                    "article_draft": state.get("article_draft", ""),
                    "quality_score": state.get("quality_score", 0.0),
                    "sources": state.get("sources", [])
                }
            })
        else:
            # Graph ran to completion
            await task_manager.set_result(task_id, {
                "final_article": state.get("final_article", ""),
                "export_path": state.get("export_path", ""),
                "sources": state.get("sources", []),
                "quality_score": state.get("quality_score", 0.0)
            })

            await task_manager.broadcast_update(task_id, {
                "task_id": task_id,
                "event_type": "status_update",
                "data": {
                    "status": "completed",
                    "message": "Research pipeline completed successfully"
                }
            })

    except Exception as e:
        error_msg = str(e)
        await task_manager.set_error(task_id, error_msg)

        await task_manager.broadcast_update(task_id, {
            "task_id": task_id,
            "event_type": "error",
            "data": {
                "status": "failed",
                "error": error_msg
            }
        })
