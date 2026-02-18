"""
Research API endpoints.
"""

import asyncio
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse

from models.schemas import (
    ResearchRequest,
    ResearchResponse,
    TaskStatusResponse,
    TaskResultResponse,
    TaskStatus,
    HITLResumeRequest
)
from api.task_manager import task_manager
from api.research_executor import execute_research_task


router = APIRouter(prefix="/api/research", tags=["Research"])


@router.post("", response_model=ResearchResponse)
async def create_research_task(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new research task.
    
    This endpoint creates a new research task and begins processing in the background.
    The task will proceed through the agent pipeline until it reaches a HITL checkpoint
    or completes.
    """
    # Create task
    task_id = await task_manager.create_task(request)
    
    # Start processing in background
    background_tasks.add_task(execute_research_task, task_id)
    
    return ResearchResponse(
        task_id=task_id,
        status=TaskStatus.pending,
        message=f"Research task created successfully. Task ID: {task_id}"
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the current status of a research task.
    
    Returns task status, current progress, and draft article if at HITL checkpoint.
    """
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    state = task.get("state", {})
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        current_node=task.get("current_node"),
        progress={
            "sub_questions": state.get("sub_questions", []),
            "search_results_count": len(state.get("search_results", [])),
            "graded_results_count": len(state.get("graded_results", [])),
            "iteration_count": state.get("iteration_count", 0),
            "write_iteration_count": state.get("write_iteration_count", 0),
        },
        article_draft=state.get("article_draft") if task["status"] == TaskStatus.hitl_review else None,
        quality_score=state.get("quality_score"),
        sources=state.get("sources"),
        error=task.get("error")
    )
    
    return response


@router.post("/{task_id}/resume", response_model=ResearchResponse)
async def resume_task(
    task_id: str,
    resume_request: HITLResumeRequest,
    background_tasks: BackgroundTasks
):
    """
    Resume a task from HITL checkpoint with human decision.
    
    Provide a decision (approve/edit/reject) and optional feedback to continue
    the research pipeline from where it paused.
    """
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task["status"] != TaskStatus.hitl_review:
        raise HTTPException(
            status_code=400,
            detail=f"Task is not at HITL checkpoint. Current status: {task['status']}"
        )
    
    # Store human decision in task
    await task_manager.update_task(task_id, {
        "human_decision": resume_request.decision.value,
        "human_feedback": resume_request.feedback or ""
    })
    
    # Resume processing
    background_tasks.add_task(execute_research_task, task_id, resume=True)
    
    return ResearchResponse(
        task_id=task_id,
        status=TaskStatus.processing,
        message=f"Task resumed with decision: {resume_request.decision.value}"
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    """
    Get the final result of a completed research task.
    
    Returns the final article, export path, sources, and quality metrics.
    """
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task["status"] != TaskStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Task not completed. Current status: {task['status']}"
        )
    
    result = task.get("result", {})
    export_path = result.get("export_path", "")

    return TaskResultResponse(
        task_id=task_id,
        status=task["status"],
        final_article=result.get("final_article", ""),
        export_path=export_path,
        download_url=f"/api/research/{task_id}/download" if export_path else None,
        sources=result.get("sources", []),
        quality_score=result.get("quality_score", 0.0)
    )


@router.get("/{task_id}/download")
async def download_task_result(task_id: str):
    """
    Download the final research article as a file.

    Returns the generated file (markdown or docx) as a direct download.
    Only available for completed tasks.
    """
    task = await task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if task["status"] != TaskStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Task not completed. Current status: {task['status']}"
        )

    result = task.get("result", {})
    export_path = result.get("export_path", "")

    if not export_path or not os.path.exists(export_path):
        raise HTTPException(
            status_code=404,
            detail="Output file not found. The article may not have been exported yet."
        )

    filename = os.path.basename(export_path)
    # Determine media type from extension
    ext = os.path.splitext(filename)[1].lower()
    media_type_map = {
        ".md": "text/markdown",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }
    media_type = media_type_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=export_path,
        filename=filename,
        media_type=media_type
    )


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its associated data."""
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Remove from manager
    async with task_manager._lock:
        del task_manager.tasks[task_id]
    
    return JSONResponse(
        content={"message": f"Task {task_id} deleted successfully"}
    )
