"""
Verification script to test graph compilation without running LLM calls.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.graph_builder import build_graph


def test_graph_compilation():
    """Test that the graph compiles without errors."""
    print("="*80)
    print("GRAPH COMPILATION TEST")
    print("="*80)
    
    try:
        print("\nBuilding graph...")
        app = build_graph()
        print("[OK] Graph compiled successfully!")
        
        print("\nGraph Details:")
        print(f"   Nodes: {len(app.nodes)}")
        print(f"   Entry Point: query_analyzer")
        
        print("\n[OK] All compilation tests passed!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Graph compilation failed: {e}")
        import traceback
        traceback.print_exc()
        print("="*80)
        return False


if __name__ == "__main__":
    success = test_graph_compilation()
    sys.exit(0 if success else 1)
