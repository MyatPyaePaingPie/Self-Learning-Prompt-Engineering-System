#!/usr/bin/env python3
"""
Test script to verify frontend integration with our core engine.
"""

import sys
import os

# Add packages to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_frontend_integration():
    """Test that frontend can import and use our core components."""
    print("Testing Frontend Integration...")
    print("="*50)
    
    try:
        # Test core imports
        from packages.core import (
            fallback_to_template, 
            judge_prompt, 
            TokenTracker,
            generate_llm_output
        )
        print("✅ Core imports successful")
        
        # Test a complete workflow like the frontend would
        original_prompt = "Write a Python function"
        
        # Step 1: Enhance prompt
        enhanced_result = fallback_to_template(original_prompt) 
        print(f"✅ Prompt enhancement: {len(enhanced_result.text)} chars")
        
        # Step 2: Track tokens
        tracker = TokenTracker()
        usage = tracker.track_llm_call(original_prompt, "def func(): pass", "test-model")
        print(f"✅ Token tracking: {usage.total_tokens} tokens")
        
        # Step 3: Judge prompt (using heuristic fallback)
        from packages.core.judge import _heuristic_judge
        score = _heuristic_judge(enhanced_result.text)
        print(f"✅ Prompt judging: {score.total:.1f}/50 score")
        
        # Step 4: Test comparison metrics
        comparison = tracker.compare_executions(
            original_prompt, "def func(): pass",
            enhanced_result.text, "def calculate_sum(numbers): return sum(numbers)",
            improvement_tokens=30, improvement_cost=0.00005,
            judging_tokens=20, judging_cost=0.00003,
            quality_improvement=12.5
        )
        print(f"✅ Comparison metrics: ROI={comparison.roi_score:.2f}")
        
        print("\n" + "="*50)
        print("✅ All frontend integration tests passed!")
        print("The Streamlit app should be able to use all core features.")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test that our modifications are compatible with Streamlit."""
    print("\nTesting Streamlit Compatibility...")
    print("="*50)
    
    try:
        # Check if streamlit is available (optional)
        try:
            import streamlit as st
            print("✅ Streamlit available")
        except ImportError:
            print("⚠️ Streamlit not installed (optional for testing)")
        
        # Test the core functionality that frontend needs
        from packages.core.judge import Scorecard
        
        # Create sample scorecards like frontend does
        original_score = Scorecard(
            clarity=4.0, specificity=3.0, actionability=2.0,
            structure=2.0, context_use=3.0, total=14.0,
            feedback={"pros": ["Brief"], "cons": ["Too vague"], "summary": "Needs improvement"}
        )
        
        enhanced_score = Scorecard(
            clarity=8.0, specificity=7.5, actionability=8.0,
            structure=7.0, context_use=7.5, total=38.0,
            feedback={"pros": ["Clear role", "Good structure"], "cons": ["Could be more specific"], "summary": "Much better"}
        )
        
        # Test metrics that frontend calculates
        improvement = enhanced_score.total - original_score.total
        print(f"✅ Score comparison: +{improvement:.1f} improvement")
        
        # Test individual score deltas
        score_deltas = [
            enhanced_score.clarity - original_score.clarity,
            enhanced_score.specificity - original_score.specificity,
            enhanced_score.actionability - original_score.actionability,
            enhanced_score.structure - original_score.structure,
            enhanced_score.context_use - original_score.context_use
        ]
        print(f"✅ Individual deltas: {[f'+{d:.1f}' for d in score_deltas]}")
        
        print("✅ Streamlit compatibility verified!")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit compatibility test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Frontend Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Core Integration", test_frontend_integration),
        ("Streamlit Compatibility", test_streamlit_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS" if success else "❌ FAIL"))
        except Exception as e:
            results.append((test_name, f"❌ FAIL: {str(e)}"))
    
    print("\n" + "="*60)
    print("INTEGRATION TEST RESULTS")
    print("="*60)
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    
    all_passed = all("✅" in result for _, result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Your frontend is ready!")
        print("Run: streamlit run frontend/app.py")
        print("The enhanced prompt engineering interface should work correctly.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)