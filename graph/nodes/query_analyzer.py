"""
Query Analyzer Node - Breaks user query into sub-questions.
"""

import os
import json
from typing import Dict
from langchain_mistralai import ChatMistralAI
from graph.state import ResearchState
from prompts.templates import QUERY_ANALYZER_PROMPT
from graph.nodes.utils import extract_json


def query_analyzer_node(state: ResearchState) -> Dict:
    """
    Analyze user query and break it into 3-5 focused sub-questions.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with sub_questions populated
    """
    print("[Query Analyzer] Analyzing query and generating sub-questions...")
    
    query = state.get("query", "")
    
    # Initialize Mistral for structured decomposition
    llm = ChatMistralAI(
        model="mistral-small-2503",
        temperature=0.2,
        api_key=os.getenv("MISTRAL_API_KEY")
    )
    
    # Generate sub-questions
    prompt = QUERY_ANALYZER_PROMPT.format(query=query)
    response = llm.invoke(prompt)
    
    # Parse JSON response
    try:
        result = extract_json(response.content)
        sub_questions = result.get("sub_questions", [])
    except (ValueError, Exception):
        # Fallback: extract questions from text
        print("Warning: JSON parsing failed, using fallback extraction")
        sub_questions = [q.strip() for q in response.content.split("\n") if q.strip() and "?" in q][:5]
    
    print(f"[Query Analyzer] Generated {len(sub_questions)} sub-questions:")
    for i, q in enumerate(sub_questions, 1):
        print(f"   {i}. {q}")
    
    return {
        "sub_questions": sub_questions,
        "iteration_count": 0,
        "write_iteration_count": 0
    }
