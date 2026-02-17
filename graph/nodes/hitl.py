"""
HITL (Human-in-the-Loop) Checkpoint Node.
"""

from typing import Dict
from graph.state import ResearchState
from prompts.templates import HITL_DISPLAY_TEMPLATE
from langgraph.types import interrupt


def hitl_checkpoint_node(state: ResearchState) -> Dict:
    """
    Pause for human review and decision (approve/edit/reject).
    
    This node uses LangGraph's interrupt() to pause execution and
    wait for human input.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with human_decision and optionally human_feedback
    """
    print("[HITL Checkpoint] Pausing for human review...")
    
    article_draft = state.get("article_draft", "")
    quality_score = state.get("quality_score", 0)
    sources = state.get("sources", [])
    
    # Format sources for display
    sources_list = "\n".join([f"{i+1}. {url}" for i, url in enumerate(sources)])
    
    # Display article for review
    display = HITL_DISPLAY_TEMPLATE.format(
        quality_score=quality_score,
        article_draft=article_draft,
        sources_list=sources_list
    )
    
    print(display)
    
    # Interrupt the graph and wait for human input
    # The value passed to interrupt() is presented to the human
    human_input = interrupt({
        "message": "Article ready for review",
        "article": article_draft,
        "quality_score": quality_score,
        "sources": sources,
        "instructions": (
            "Please review the article and provide:\n"
            "1. Decision: 'approve', 'edit', or 'reject'\n"
            "2. Feedback: (optional for approve, required for edit/reject)\n\n"
            "Return as dict: {'decision': 'approve/edit/reject', 'feedback': 'your feedback'}"
        )
    })
    
    # Extract decision and feedback from human input
    decision = human_input.get("decision", "approve").lower()
    feedback = human_input.get("feedback", "")
    
    print(f"[HITL Checkpoint] Human decision: {decision}")
    if feedback:
        print(f"[HITL Checkpoint] Feedback: {feedback}")
    
    # Set final article if approved
    final_article = ""
    if decision == "approve":
        final_article = article_draft
        print("[HITL Checkpoint] Article approved for publication!")
    
    return {
        "human_decision": decision,
        "human_feedback": feedback,
        "final_article": final_article
    }
