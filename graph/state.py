"""
State definition for the Agentic Research & Article Generation System.
"""

from typing import TypedDict, List, Dict, Optional


class ResearchState(TypedDict, total=False):
    """
    Shared state object that flows through all nodes in the research graph.
    """
    
    # Input
    query: str                          # Original user query
    export_format: str                  # 'markdown' | 'docx' | 'notion'
    tone: str                           # 'professional' | 'casual' | 'technical'
    word_count: int                     # Target word count (500-2000)
    
    # Research phase
    sub_questions: List[str]            # Broken-down research topics
    search_results: List[Dict]          # Raw results from Tavily
    graded_results: List[Dict]          # Results with relevance scores (1-5)
    rejected_queries: List[str]         # Queries sent for rewriting
    sources: List[str]                  # All URLs used in research
    
    # Writing phase
    research_notes: str                 # Synthesized findings (structured)
    article_draft: str                  # Generated article text
    quality_score: float                # Checker's score (0-100)
    quality_feedback: str               # Checker's improvement notes
    
    # HITL phase
    human_feedback: str                 # Free-text feedback from human
    human_decision: str                 # 'approve' | 'edit' | 'reject'
    
    # Output
    final_article: str                  # Approved, publication-ready text
    export_path: str                    # Output file path
    
    # Control
    iteration_count: int                # Loop counter for search retries
    write_iteration_count: int          # Loop counter for article rewrites
