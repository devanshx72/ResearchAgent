"""
Article Writer Node - Generates full article from research notes.
"""

import os
from typing import Dict
from langchain_mistralai import ChatMistralAI
from graph.state import ResearchState
from prompts.templates import ARTICLE_WRITER_PROMPT


def writer_node(state: ResearchState) -> Dict:
    """
    Generate a full, structured article from research notes.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with article_draft
    """
    print("[Article Writer] Writing article from research notes...")
    
    research_notes = state.get("research_notes", "")
    tone = state.get("tone", "professional")
    word_count = state.get("word_count", 1000)
    export_format = state.get("export_format", "markdown")
    human_feedback = state.get("human_feedback", "")
    
    # Build human feedback section if present
    feedback_section = ""
    if human_feedback:
        feedback_section = f"""
IMPORTANT - HUMAN FEEDBACK TO INCORPORATE:
{human_feedback}

Please carefully incorporate this feedback into your article.
"""
    
    # Initialize Mistral for creative writing
    llm = ChatMistralAI(
        model="mistral-small-2503",
        temperature=0.7,
        api_key=os.getenv("MISTRAL_API_KEY")
    )
    
    # Generate article
    prompt = ARTICLE_WRITER_PROMPT.format(
        research_notes=research_notes,
        tone=tone,
        word_count=word_count,
        export_format=export_format,
        human_feedback_section=feedback_section
    )
    
    response = llm.invoke(prompt)
    article_draft = response.content
    
    # Estimate word count
    estimated_words = len(article_draft.split())
    print(f"[Article Writer] Article generated (~{estimated_words} words)")
    
    return {
        "article_draft": article_draft,
        "human_feedback": ""  # Clear feedback after incorporating
    }
