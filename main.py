"""
Main entry point for the Agentic Research & Article Generation System.
"""

import os
import argparse
from dotenv import load_dotenv
from graph.graph_builder import build_graph
from graph.state import ResearchState


def main():
    """Run the research agent pipeline."""
    
    # Load environment variables
    load_dotenv()
    
    # Verify API keys
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment")
        print("   Please create a .env file with your API key")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("Error: TAVILY_API_KEY not found in environment")
        print("   Please create a .env file with your API key")
        return
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Agentic Research & Article Generation System"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Research topic or question"
    )
    parser.add_argument(
        "--export-format",
        type=str,
        default="markdown",
        choices=["markdown", "md", "docx", "notion"],
        help="Export format (default: markdown)"
    )
    parser.add_argument(
        "--tone",
        type=str,
        default="professional",
        choices=["professional", "casual", "technical"],
        help="Article tone (default: professional)"
    )
    parser.add_argument(
        "--word-count",
        type=int,
        default=1000,
        help="Target word count (default: 1000)"
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        default="default",
        help="Thread ID for state persistence (default: 'default')"
    )
    
    args = parser.parse_args()
    
    # Build the graph
    print("Building research agent graph...")
    app = build_graph()
    
    # Initialize state
    initial_state: ResearchState = {
        "query": args.query,
        "export_format": args.export_format,
        "tone": args.tone,
        "word_count": args.word_count,
        "sub_questions": [],
        "search_results": [],
        "graded_results": [],
        "rejected_queries": [],
        "sources": [],
        "research_notes": "",
        "article_draft": "",
        "quality_score": 0.0,
        "quality_feedback": "",
        "human_feedback": "",
        "human_decision": "",
        "final_article": "",
        "export_path": "",
        "iteration_count": 0,
        "write_iteration_count": 0
    }
    
    # Configuration for thread
    config = {"configurable": {"thread_id": args.thread_id}}
    
    print(f"\n{'='*80}")
    print(f"Research Topic: {args.query}")
    print(f"Target: {args.word_count} words, {args.tone} tone")
    print(f"Export Format: {args.export_format}")
    print(f"{'='*80}\n")
    
    # Run the graph
    try:
        # Stream events to show progress
        for event in app.stream(initial_state, config, stream_mode="updates"):
            # Event contains the node name and updated state
            for node_name, node_output in event.items():
                print(f"\n{'─'*80}")
                print(f"✓ Completed: {node_name}")
                print(f"{'─'*80}")
        
        print(f"\n{'='*80}")
        print("Research and article generation complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        # Check if it's a HITL interrupt
        if "interrupt" in str(e).lower() or hasattr(e, '__interrupt__'):
            print("\nHITL Checkpoint Reached")
            print("="*80)
            print("The graph has been paused for human review.")
            print("\nTo resume, run the following:")
            print(f"  python resume_hitl.py --thread-id {args.thread_id}")
            print("="*80)
        else:
            print(f"\nError during execution: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
