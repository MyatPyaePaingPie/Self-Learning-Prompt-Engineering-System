#!/usr/bin/env python3
"""
Simple test script to verify that all imports in the engine.py work correctly.
"""

import sys
import traceback

def test_imports():
    """Test all the imports needed by the engine module."""
    print("Testing imports for Self-Learning Prompt Engineering System...")
    print("=" * 60)
    
    # Test standard library imports
    print("✓ Testing standard library imports...")
    try:
        import os
        import time
        import logging
        from datetime import datetime
        print("  ✓ Standard library imports successful")
    except ImportError as e:
        print(f"  ✗ Standard library import failed: {e}")
        return False
    
    # Test external package imports
    print("✓ Testing external package imports...")
    try:
        from pydantic import BaseModel
        print("  ✓ pydantic imported successfully")
    except ImportError as e:
        print(f"  ⚠ pydantic not available: {e}")
        print("    Install with: pip install pydantic")
    
    try:
        from groq import Groq
        print("  ✓ groq imported successfully")
    except ImportError as e:
        print(f"  ⚠ groq not available: {e}")
        print("    Install with: pip install groq")
    
    # Test our custom module imports
    print("✓ Testing custom module imports...")
    try:
        from packages.core.token_tracker import TokenTracker, TokenUsage
        print("  ✓ TokenTracker and TokenUsage imported successfully")
    except ImportError as e:
        print(f"  ✗ Custom module import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test that the engine module can be imported
    print("✓ Testing engine module import...")
    try:
        from packages.core.engine import improve_prompt, generate_llm_output, ImprovedOut
        print("  ✓ Engine module imported successfully")
    except ImportError as e:
        print(f"  ✗ Engine module import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test the TokenTracker functionality
    print("✓ Testing TokenTracker functionality...")
    try:
        tracker = TokenTracker()
        usage = tracker.track_llm_call("test prompt", "test response", "test-model")
        print(f"  ✓ TokenTracker test successful - tracked {usage.total_tokens} tokens")
    except Exception as e:
        print(f"  ✗ TokenTracker test failed: {e}")
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print("✓ All core imports and functionality tests passed!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)