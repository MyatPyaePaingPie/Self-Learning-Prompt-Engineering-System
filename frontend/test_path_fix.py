#!/usr/bin/env python3
"""
Test script to verify path fix works from frontend directory.
"""

import sys
import os

# Add parent directory to Python path so we can import packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Parent directory added to path: {parent_dir}")
print(f"Python path: {sys.path[:3]}...")

try:
    from packages.core import (
        fallback_to_template, 
        judge_prompt, 
        TokenTracker,
        generate_llm_output
    )
    print("✅ SUCCESS: All packages.core imports work!")
    
    # Test basic functionality
    result = fallback_to_template("Test prompt")
    print(f"✅ Template fallback works: {len(result.text)} chars")
    
    tracker = TokenTracker()
    usage = tracker.track_llm_call("test", "response", "model")
    print(f"✅ Token tracking works: {usage.total_tokens} tokens")
    
    print("\n🎉 Path fix is working correctly!")
    print("The Streamlit app should now be able to import packages.core")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()