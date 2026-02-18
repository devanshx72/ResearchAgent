"""
Query Rewriter Node - Reformulates rejected queries.
"""

import os
import json
from typing import Dict
from langchain_mistralai import ChatMistralAI
from graph.state import ResearchState
from prompts.templates import QUERY_REWRITER_PROMPT
from graph.nodes.utils import extract_json


def query_rewriter_node(state: ResearchState) -> Dict:
    """
    Rewrite rejected queries with different keywords and phrasing.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with rewritten sub_questions and incremented iteration_count
    """
    print("[Query Rewriter] Rewriting queries that didn't yield good results...")
    
    rejected_queries = state.get("rejected_queries", [])
    sub_questions = state.get("sub_questions", [])
    iteration_count = state.get("iteration_count", 0)
    
    # Check max iterations
    if iteration_count >= 3:
        print("Warning: Max iterations reached (3), proceeding with available results")
        return {
            "iteration_count": iteration_count
        }
    
    # Initialize Mistral for creative rephrasing
    llm = ChatMistralAI(
        model="mistral-small-2503",
        temperature=0.5,
        api_key=os.getenv("MISTRAL_API_KEY")
    )
    
    # Rewrite each rejected query
    rewritten_questions = sub_questions.copy()
    
    for rejected_query in rejected_queries:
        # Find index in original sub_questions
        try:
            idx = sub_questions.index(rejected_query)
        except ValueError:
            continue
        
        prompt = QUERY_REWRITER_PROMPT.format(
            original_query=state.get("query", ""),
            rejected_query=rejected_query
        )
        
        try:
            response = llm.invoke(prompt)
            result = extract_json(response.content)
            rewritten = result.get("rewritten_query", rejected_query)
        except (ValueError, Exception) as e:
            print(f"Warning: Rewrite error: {e}, using original")
            rewritten = rejected_query
        
        rewritten_questions[idx] = rewritten
        print(f"   Original: {rejected_query}")
        print(f"   Rewritten: {rewritten}")
    
    print(f"[Query Rewriter] Rewrote {len(rejected_queries)} queries (iteration {iteration_count + 1}/3)")
    
    return {
        "sub_questions": rewritten_questions,
        "iteration_count": iteration_count + 1,
        "rejected_queries": []  # Clear for next round
    }
