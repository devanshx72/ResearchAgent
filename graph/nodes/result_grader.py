"""
Result Grader Node - Scores search results for relevance.
"""

import json
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import ResearchState
from prompts.templates import RESULT_GRADER_PROMPT


def result_grader_node(state: ResearchState) -> Dict:
    """
    Grade each search result on relevance and quality (1-5 scale).
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with graded_results and rejected_queries
    """
    print("[Result Grader] Grading search results for quality...")
    
    search_results = state.get("search_results", [])
    
    # Initialize Gemini Flash for consistent grading
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1
    )
    
    graded_results = []
    rejected_by_question = {}
    
    for result in search_results:
        # Grade this result
        prompt = RESULT_GRADER_PROMPT.format(
            query=result.get("sub_question", ""),
            title=result.get("title", ""),
            snippet=result.get("snippet", ""),
            url=result.get("url", "")
        )
        
        try:
            response = llm.invoke(prompt)
            grade_data = json.loads(response.content)
            score = grade_data.get("score", 3)
            reasoning = grade_data.get("reasoning", "")
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Grading error: {e}, defaulting to score 3")
            score = 3
            reasoning = "Default score due to grading error"
        
        # Add grade to result
        result["grade_score"] = score
        result["grade_reasoning"] = reasoning
        
        # Track accepted vs rejected
        if score >= 3:
            graded_results.append(result)
        else:
            question_idx = result.get("sub_question_index", 0)
            if question_idx not in rejected_by_question:
                rejected_by_question[question_idx] = []
            rejected_by_question[question_idx].append(result)
    
    print(f"[Result Grader] Accepted results: {len(graded_results)}")
    print(f"[Result Grader] Rejected results: {len(search_results) - len(graded_results)}")
    
    # Determine which sub-questions need rewriting (all results rejected)
    sub_questions = state.get("sub_questions", [])
    rejected_queries = []
    
    for idx, question in enumerate(sub_questions):
        question_results = [r for r in graded_results if r.get("sub_question_index") == idx]
        if not question_results:
            rejected_queries.append(question)
            print(f"Warning: No good results for: {question}")
    
    return {
        "graded_results": graded_results,
        "rejected_queries": rejected_queries
    }
