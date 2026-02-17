"""
Web Search Node - Executes searches for sub-questions.
"""

from typing import Dict
from graph.state import ResearchState
from tools.tavily_search import TavilySearch


def web_search_node(state: ResearchState) -> Dict:
    """
    Search the web for each sub-question using Tavily API.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with search_results populated
    """
    print("[Web Search] Searching the web for research material...")
    
    sub_questions = state.get("sub_questions", [])
    iteration_count = state.get("iteration_count", 0)
    
    # Initialize Tavily
    tavily = TavilySearch()
    
    # Search all sub-questions
    all_results = []
    for i, question in enumerate(sub_questions, 1):
        print(f"   Searching: {question}")
        results = tavily.search_query(question, max_results=5)
        
        # Add metadata to each result
        for result in results:
            result["sub_question"] = question
            result["sub_question_index"] = i - 1
        
        all_results.extend(results)
        print(f"   Found {len(results)} results")
    
    print(f"[Web Search] Total results found: {len(all_results)}")
    
    return {
        "search_results": all_results
    }
