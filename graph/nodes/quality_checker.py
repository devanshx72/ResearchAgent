"""
Quality Checker Node - Evaluates article quality.
"""

import os
import json
from typing import Dict
from langchain_mistralai import ChatMistralAI
from graph.state import ResearchState
from prompts.templates import QUALITY_CHECKER_PROMPT
from graph.nodes.utils import extract_json


def quality_checker_node(state: ResearchState) -> Dict:
    """
    Evaluate article quality on multiple dimensions (0-100 scale).
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with quality_score and quality_feedback
    """
    print("[Quality Checker] Evaluating article quality...")
    
    article_draft = state.get("article_draft", "")
    research_notes = state.get("research_notes", "")
    sources = state.get("sources", [])
    write_iteration_count = state.get("write_iteration_count", 0)
    
    # Initialize Mistral for objective evaluation
    llm = ChatMistralAI(
        model="mistral-small-2503",
        temperature=0.1,
        api_key=os.getenv("MISTRAL_API_KEY")
    )
    
    # Evaluate article
    prompt = QUALITY_CHECKER_PROMPT.format(
        article_draft=article_draft,
        research_notes=research_notes,
        sources="\n".join(sources)
    )
    
    try:
        response = llm.invoke(prompt)
        evaluation = extract_json(response.content)
        
        quality_score = evaluation.get("total_score", 0)
        feedback = evaluation.get("feedback", "")
        
        print(f"[Quality Checker] Quality Scores:")
        print(f"   Coverage: {evaluation.get('coverage_score', 0)}/25")
        print(f"   Factual: {evaluation.get('factual_score', 0)}/25")
        print(f"   Structure: {evaluation.get('structure_score', 0)}/25")
        print(f"   Tone: {evaluation.get('tone_score', 0)}/25")
        print(f"   TOTAL: {quality_score}/100")
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Quality check error: {e}, defaulting to 75")
        quality_score = 75
        feedback = "Quality check error, proceeding to HITL"
    
    # Determine next step
    if quality_score >= 70:
        print("[Quality Checker] Quality threshold met (>=70), proceeding to HITL")
    else:
        print(f"Warning: Quality below threshold ({quality_score}/100)")
        if write_iteration_count < 2:
            print(f"   Sending back to writer (iteration {write_iteration_count + 1}/2)")
        else:
            print("   Max rewrites reached, escalating to HITL")
    
    return {
        "quality_score": quality_score,
        "quality_feedback": feedback,
        "write_iteration_count": write_iteration_count + 1
    }
