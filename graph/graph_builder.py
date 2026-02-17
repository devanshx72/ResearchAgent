"""
LangGraph StateGraph builder with conditional routing.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import ResearchState
from graph.nodes.query_analyzer import query_analyzer_node
from graph.nodes.web_search import web_search_node
from graph.nodes.result_grader import result_grader_node
from graph.nodes.query_rewriter import query_rewriter_node
from graph.nodes.synthesizer import synthesizer_node
from graph.nodes.writer import writer_node
from graph.nodes.quality_checker import quality_checker_node
from graph.nodes.hitl import hitl_checkpoint_node
from graph.nodes.publisher import publisher_node


def route_after_grader(state: ResearchState) -> str:
    """
    Route after result grader based on whether we have accepted results.
    
    Returns:
        - 'synthesizer' if we have accepted results
        - 'query_rewriter' if all results were rejected
    """
    graded_results = state.get("graded_results", [])
    rejected_queries = state.get("rejected_queries", [])
    iteration_count = state.get("iteration_count", 0)
    
    # If max iterations reached, proceed to synthesizer with what we have
    if iteration_count >= 3:
        print("[Router] Max iterations reached, proceeding to synthesis")
        return "synthesizer"
    
    # If we have accepted results, proceed to synthesizer
    if len(graded_results) > 0:
        print("[Router] Routing to synthesizer (have accepted results)")
        return "synthesizer"
    
    # If all results rejected and we have rejected queries, rewrite them
    if len(rejected_queries) > 0:
        print("[Router] Routing to query_rewriter (no accepted results)")
        return "query_rewriter"
    
    # Default: proceed to synthesizer
    print("[Router] Routing to synthesizer (default)")
    return "synthesizer"


def route_after_quality_checker(state: ResearchState) -> str:
    """
    Route after quality checker based on score and iteration count.
    
    Returns:
        - 'hitl' if score >= 70 OR max rewrites reached
        - 'writer' if score < 70 AND more rewrites available
    """
    quality_score = state.get("quality_score", 0)
    write_iteration_count = state.get("write_iteration_count", 0)
    
    # If quality is good, go to HITL
    if quality_score >= 70:
        print("[Router] Routing to HITL (quality passed)")
        return "hitl"
    
    # If max rewrites reached, escalate to HITL anyway
    if write_iteration_count >= 2:
        print("[Router] Routing to HITL (max rewrites reached)")
        return "hitl"
    
    # Otherwise, send back to writer for revision
    print("[Router] Routing back to writer (quality below threshold)")
    return "writer"


def route_after_hitl(state: ResearchState) -> str:
    """
    Route after HITL based on human decision.
    
    Returns:
        - 'publisher' if approved
        - 'writer' if edit
        - 'query_analyzer' if reject
    """
    decision = state.get("human_decision", "approve")
    
    if decision == "approve":
        print("[Router] Routing to publisher (human approved)")
        return "publisher"
    elif decision == "edit":
        print("[Router] Routing to writer (human requested edits)")
        return "writer"
    elif decision == "reject":
        print("[Router] Routing to query_analyzer (human rejected, restarting)")
        return "query_analyzer"
    else:
        # Default to approve
        print("[Router] Routing to publisher (default approve)")
        return "publisher"


def build_graph() -> StateGraph:
    """
    Build the complete research agent StateGraph.
    
    Returns:
        Compiled StateGraph with checkpointing
    """
    # Create graph with state schema
    workflow = StateGraph(ResearchState)
    
    # Add all nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("result_grader", result_grader_node)
    workflow.add_node("query_rewriter", query_rewriter_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("quality_checker", quality_checker_node)
    workflow.add_node("hitl", hitl_checkpoint_node)
    workflow.add_node("publisher", publisher_node)
    
    # Set entry point
    workflow.set_entry_point("query_analyzer")
    
    # Add edges
    # query_analyzer -> web_search
    workflow.add_edge("query_analyzer", "web_search")
    
    # web_search -> result_grader
    workflow.add_edge("web_search", "result_grader")
    
    # result_grader -> [synthesizer OR query_rewriter]
    workflow.add_conditional_edges(
        "result_grader",
        route_after_grader,
        {
            "synthesizer": "synthesizer",
            "query_rewriter": "query_rewriter"
        }
    )
    
    # query_rewriter -> web_search (loop back)
    workflow.add_edge("query_rewriter", "web_search")
    
    # synthesizer -> writer
    workflow.add_edge("synthesizer", "writer")
    
    # writer -> quality_checker
    workflow.add_edge("writer", "quality_checker")
    
    # quality_checker -> [hitl OR writer]
    workflow.add_conditional_edges(
        "quality_checker",
        route_after_quality_checker,
        {
            "hitl": "hitl",
            "writer": "writer"
        }
    )
    
    # hitl -> [publisher OR writer OR query_analyzer]
    workflow.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {
            "publisher": "publisher",
            "writer": "writer",
            "query_analyzer": "query_analyzer"
        }
    )
    
    # publisher -> END
    workflow.add_edge("publisher", END)
    
    # Compile with checkpointing for HITL
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
