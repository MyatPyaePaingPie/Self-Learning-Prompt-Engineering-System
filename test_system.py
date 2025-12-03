#!/usr/bin/env python3
"""
Comprehensive test script for the Self-Learning Prompt Engineering System.
Tests core functionality without making actual API calls.
"""

import sys
from packages.core import (
    improve_prompt, 
    fallback_to_template, 
    ImprovedOut,
    TokenTracker,
    judge_prompt,
    Scorecard,
    should_keep_or_revert
)
from packages.core.engine import detect_domain, synth_explanation

def test_fallback_system():
    """Test the template-based fallback system."""
    print("\n" + "="*50)
    print("TESTING FALLBACK SYSTEM")
    print("="*50)
    
    # Test with code-related prompt
    original_code = "Write a function to sort a list"
    result = fallback_to_template(original_code)
    
    print(f"Original: {original_code}")
    print(f"Domain detected: {detect_domain(original_code)}")
    print(f"Improved: {result.text[:100]}...")
    print(f"Source: {result.source}")
    print(f"Explanation bullets: {len(result.explanation['bullets'])}")
    
    # Test with marketing prompt  
    original_marketing = "Create a marketing campaign for our product"
    result = fallback_to_template(original_marketing)
    
    print(f"\nOriginal: {original_marketing}")
    print(f"Domain detected: {detect_domain(original_marketing)}")
    print(f"Improved: {result.text[:100]}...")
    print(f"Source: {result.source}")
    
    return True

def test_token_tracker():
    """Test the TokenTracker functionality."""
    print("\n" + "="*50)
    print("TESTING TOKEN TRACKER")
    print("="*50)
    
    tracker = TokenTracker()
    
    # Test basic token counting
    test_prompt = "You are a helpful assistant. Please write a Python function."
    test_response = "Here's a Python function:\n\ndef hello():\n    print('Hello, World!')\n    return True"
    
    usage = tracker.track_llm_call(test_prompt, test_response)
    
    print(f"Test prompt tokens: {usage.prompt_tokens}")
    print(f"Test response tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")
    print(f"Cost: ${usage.cost_usd:.8f}")
    print(f"Model: {usage.model}")
    
    # Test comparison metrics
    original_prompt = "Write code"
    original_output = "def func(): pass"
    improved_prompt = "You are a Python expert. Write a well-documented function with error handling."
    improved_output = "def calculate_sum(numbers):\n    '''Calculate sum with error handling.'''\n    try:\n        return sum(numbers)\n    except TypeError:\n        return 0"
    
    comparison = tracker.compare_executions(
        original_prompt, original_output,
        improved_prompt, improved_output,
        improvement_tokens=50,
        improvement_cost=0.0001,
        judging_tokens=30,
        judging_cost=0.00005,
        quality_improvement=7.5
    )
    
    print(f"\nComparison Results:")
    print(f"Original tokens: {comparison.original_total_tokens}")
    print(f"Improved tokens: {comparison.improved_total_tokens}")
    print(f"Token efficiency: {comparison.token_efficiency_percent:.1f}%")
    print(f"Quality improvement: {comparison.output_quality_improvement}")
    print(f"Is worth it: {comparison.is_worth_it}")
    print(f"ROI score: {comparison.roi_score:.2f}")
    
    return True

def test_learning_system():
    """Test the learning and decision system."""
    print("\n" + "="*50)
    print("TESTING LEARNING SYSTEM")
    print("="*50)
    
    # Test decision making
    past_scores = [25.0, 27.5, 26.0, 28.0]
    new_score = 29.5
    
    decision = should_keep_or_revert(past_scores, new_score, threshold=0.5)
    avg_past = sum(past_scores) / len(past_scores)
    
    print(f"Past scores average: {avg_past:.1f}")
    print(f"New score: {new_score}")
    print(f"Decision: {decision}")
    
    # Test with lower score
    low_score = 24.0
    decision2 = should_keep_or_revert(past_scores, low_score, threshold=0.5)
    print(f"Low score: {low_score}")
    print(f"Decision for low score: {decision2}")
    
    return True

def test_complete_workflow():
    """Test a complete workflow using fallback mode."""
    print("\n" + "="*50)
    print("TESTING COMPLETE WORKFLOW")
    print("="*50)
    
    # Start with a basic prompt
    original = "Help me with Python"
    
    print(f"1. Original prompt: '{original}'")
    
    # Improve it using fallback
    improved_result = fallback_to_template(original)
    print(f"2. Improved prompt: '{improved_result.text[:80]}...'")
    
    # Create a mock scorecard for the original
    original_scorecard = Scorecard(
        clarity=4.0,
        specificity=3.0,
        actionability=2.0,
        structure=2.0,
        context_use=3.0,
        feedback={"pros": ["Brief"], "cons": ["Too vague"], "summary": "Needs improvement"},
        total=14.0
    )
    
    # Create a mock scorecard for improved
    improved_scorecard = Scorecard(
        clarity=8.0,
        specificity=7.5,
        actionability=8.0,
        structure=7.0,
        context_use=7.5,
        feedback={"pros": ["Clear role", "Good structure"], "cons": ["Could be more specific"], "summary": "Much better"},
        total=38.0
    )
    
    print(f"3. Original score: {original_scorecard.total}")
    print(f"4. Improved score: {improved_scorecard.total}")
    print(f"5. Improvement: +{improved_scorecard.total - original_scorecard.total} points")
    
    # Test decision making
    decision = should_keep_or_revert([14.0, 15.0, 16.0], improved_scorecard.total, threshold=1.0)
    print(f"6. Decision: {decision}")
    
    return True

def main():
    """Run all tests."""
    print("Self-Learning Prompt Engineering System - Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Fallback System", test_fallback_system),
        ("Token Tracker", test_token_tracker), 
        ("Learning System", test_learning_system),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS"))
            print(f"\n✅ {test_name}: PASSED")
        except Exception as e:
            results.append((test_name, f"❌ FAIL: {str(e)}"))
            print(f"\n❌ {test_name}: FAILED - {str(e)}")
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    
    all_passed = all("✅" in result for _, result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)