"""
Resume script for HITL checkpoint - allows human to provide feedback and continue.
"""

import os
import argparse
from dotenv import load_dotenv
from graph.graph_builder import build_graph


def main():
    """Resume from HITL checkpoint with human feedback."""
    
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Resume from HITL checkpoint"
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        required=True,
        help="Thread ID of the paused execution"
    )
    parser.add_argument(
        "--decision",
        type=str,
        required=True,
        choices=["approve", "edit", "reject"],
        help="Your decision: approve, edit, or reject"
    )
    parser.add_argument(
        "--feedback",
        type=str,
        default="",
        help="Optional feedback for edit/reject decisions"
    )
    
    args = parser.parse_args()
    
    # Build graph (will restore state from checkpoint)
    print("Resuming from HITL checkpoint...")
    app = build_graph()
    
    # Configuration
    config = {"configurable": {"thread_id": args.thread_id}}
    
    # Human input to resume
    human_input = {
        "decision": args.decision,
        "feedback": args.feedback
    }
    
    print(f"\n{'='*80}")
    print(f"Decision: {args.decision}")
    if args.feedback:
        print(f"Feedback: {args.feedback}")
    print(f"{'='*80}\n")
    
    # Resume execution with human input
    try:
        for event in app.stream(human_input, config, stream_mode="updates"):
            for node_name, node_output in event.items():
                print(f"\n{'─'*80}")
                print(f"✓ Completed: {node_name}")
                print(f"{'─'*80}")
        
        print(f"\n{'='*80}")
        print("Pipeline complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        # Another HITL checkpoint might be reached
        if "interrupt" in str(e).lower() or hasattr(e, '__interrupt__'):
            print("\nAnother HITL Checkpoint Reached")
            print("="*80)
            print("Run this script again to provide additional feedback.")
            print("="*80)
        else:
            print(f"\nError during execution: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
