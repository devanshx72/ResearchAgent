"""
Research Synthesizer Node - Aggregates results into structured notes.
"""

from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import ResearchState
from prompts.templates import RESEARCH_SYNTHESIZER_PROMPT


def synthesizer_node(state: ResearchState) -> Dict:
    """
    Synthesize graded results into structured research notes.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with research_notes and sources
    """
    print("[Synthesizer] Synthesizing research findings into structured notes...")
    
    graded_results = state.get("graded_results", [])
    
    # Extract sources
    sources = list(set([r.get("url", "") for r in graded_results if r.get("url")]))
    
    # Format results for prompt
    formatted_results = []
    for result in graded_results:
        formatted_results.append(
            f"**Sub-Question:** {result.get('sub_question', 'N/A')}\n"
            f"**Source:** {result.get('title', 'N/A')} ({result.get('url', 'N/A')})\n"
            f"**Content:** {result.get('snippet', 'N/A')}\n"
            f"**Quality Score:** {result.get('grade_score', 'N/A')}/5\n"
        )
    
    results_text = "\n---\n".join(formatted_results)
    
    # Initialize Gemini Pro for synthesis
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2
    )
    
    # Generate research notes
    prompt = RESEARCH_SYNTHESIZER_PROMPT.format(graded_results=results_text)
    response = llm.invoke(prompt)
    research_notes = response.content
    
    print(f"[Synthesizer] Synthesized notes from {len(graded_results)} sources")
    print(f"[Synthesizer] Total unique sources: {len(sources)}")
    
    return {
        "research_notes": research_notes,
        "sources": sources
    }
