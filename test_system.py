#!/usr/bin/env python3
"""
Test script for Self-Learning Prompt Engineering System
Tests file storage, judge scores, and version history functionality
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from storage.file_storage import FileStorage
from packages.core.engine import improve_prompt
from packages.core.judge import judge_prompt
from datetime import datetime

def test_file_storage():
    """Test basic file storage functionality"""
    print("🗂️  Testing File Storage...")
    
    storage = FileStorage("storage")
    
    # Test basic file operations
    prompt_file = storage.save_prompt(
        text="Write a Python function to calculate factorial",
        prompt_id="test_factorial",
        metadata={"test": True, "author": "test_system"}
    )
    
    result_file = storage.save_result(
        text="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
        result_id="test_factorial_solution"
    )
    
    print(f"✅ Saved prompt: {prompt_file}")
    print(f"✅ Saved result: {result_file}")
    
    # Test CSV functionality
    test_data = {
        'llm_name': 'Test-Engine',
        'prompt': 'Test prompt for CSV functionality',
        'original_response': 'Test response',
        'learning_memory': 'Testing CSV storage'
    }
    
    csv_id = storage.save_to_csv('test_learning_log', test_data)
    print(f"✅ Saved to CSV with ID: {csv_id}")
    
    # Read back CSV data
    entries = storage.read_from_csv('test_learning_log')
    print(f"✅ Read {len(entries)} entries from CSV")
    
    return storage

def test_prompt_engine():
    """Test prompt improvement engine"""
    print("\n🚀 Testing Prompt Engine...")
    
    test_prompts = [
        "Help me code",
        "Write a sorting algorithm",
        "Create a marketing plan"
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: '{prompt}'")
        
        # Test improvement
        improvement = improve_prompt(prompt, strategy='v1')
        
        print(f"✅ Domain detected: {improvement['domain_detected']}")
        print(f"✅ Strategy used: {improvement['strategy']}")
        print(f"✅ Improved text length: {len(improvement['text'])} characters")
        print(f"✅ Improvements made: {improvement['explanation']['improvements_made']}")
    
    return improvement

def test_judge_system():
    """Test judge scoring system"""
    print("\n⚖️  Testing Judge System...")
    
    test_prompts = [
        "Help me code",  # Poor quality
        """You are a senior Python developer.
Task: Write a function to calculate factorial with error handling
Requirements:
- Handle negative numbers appropriately
- Include docstring and type hints
- Provide both recursive and iterative solutions
Constraints: Python 3.8+, no external libraries
Format: Return clean, commented code with examples"""  # Good quality
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nJudging prompt {i}...")
        
        scores = judge_prompt(prompt)
        
        print(f"✅ Clarity: {scores['clarity']:.1f}/10")
        print(f"✅ Specificity: {scores['specificity']:.1f}/10")
        print(f"✅ Actionability: {scores['actionability']:.1f}/10")
        print(f"✅ Structure: {scores['structure']:.1f}/10")
        print(f"✅ Context Use: {scores['context_use']:.1f}/10")
        print(f"✅ Total: {scores['total']:.1f}/50 ({scores['feedback']['overall_score_percentage']:.1f}%)")
        print(f"✅ Summary: {scores['feedback']['summary']}")
    
    return scores

def test_integrated_workflow():
    """Test complete workflow with file storage integration"""
    print("\n🔄 Testing Integrated Workflow...")
    
    # Initialize storage
    storage = FileStorage("storage")
    
    # Test prompt
    original_prompt = "Write a web scraper for news articles"
    prompt_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    version_id = f"version_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Testing with prompt: '{original_prompt}'")
    
    # Step 1: Improve prompt
    print("Step 1: Improving prompt...")
    improvement = improve_prompt(original_prompt, strategy='v1')
    print(f"✅ Prompt improved (length: {len(improvement['text'])})")
    
    # Step 2: Judge the improved prompt
    print("Step 2: Judging improved prompt...")
    scores = judge_prompt(
        improvement['text'],
        save_to_storage=storage,
        prompt_id=prompt_id,
        version_id=version_id
    )
    print(f"✅ Prompt judged (score: {scores['total']:.1f}/50)")
    
    # Step 3: Save version history (simulating database objects)
    print("Step 3: Saving version history...")
    
    class MockVersion:
        def __init__(self, text, explanation, strategy, version_no=1):
            self.id = version_id
            self.version_no = version_no
            self.text = text
            self.source = f'engine/{strategy}' if strategy != 'original' else 'original'
            self.explanation = explanation
            self.created_at = datetime.now()
    
    # Save original version (v0)
    original_version = MockVersion(
        original_prompt, 
        {"bullets": ["Original prompt"]}, 
        "original", 
        0
    )
    storage.save_version_to_csv(prompt_id, original_version)
    
    # Save improved version (v1)
    improved_version = MockVersion(
        improvement['text'],
        improvement['explanation'],
        improvement['strategy']
    )
    storage.save_version_to_csv(prompt_id, improved_version)
    
    print(f"✅ Saved version history for {prompt_id}")
    
    # Step 4: Verify data persistence
    print("Step 4: Verifying data persistence...")
    
    # Check version history
    version_history = storage.get_version_history(prompt_id)
    print(f"✅ Found {len(version_history)} versions in history")
    
    # Check judge scores
    score_history = storage.get_judge_scores_history(prompt_id)
    print(f"✅ Found {len(score_history)} score entries")
    
    return {
        'prompt_id': prompt_id,
        'version_id': version_id,
        'improvement': improvement,
        'scores': scores,
        'version_history': version_history,
        'score_history': score_history
    }

def test_version_history_display():
    """Test version history functionality"""
    print("\n📜 Testing Version History Display...")
    
    storage = FileStorage("storage")
    
    # Read all version data
    all_versions = storage.read_from_csv('prompt_versions')
    print(f"✅ Found {len(all_versions)} total versions")
    
    # Group by prompt_id
    prompt_groups = {}
    for entry in all_versions:
        prompt_id = entry['prompt_id']
        if prompt_id not in prompt_groups:
            prompt_groups[prompt_id] = []
        prompt_groups[prompt_id].append(entry)
    
    print(f"✅ Found {len(prompt_groups)} unique prompts")
    
    # Display sample version history
    for prompt_id, versions in list(prompt_groups.items())[:2]:  # Show first 2
        print(f"\n📝 Prompt {prompt_id}:")
        for version in sorted(versions, key=lambda x: int(x.get('version_no', 0))):
            version_no = version.get('version_no', '0')
            source = version.get('source', 'unknown')
            text_preview = version.get('text', '')[:50] + '...'
            print(f"   v{version_no} ({source}): {text_preview}")
    
    return prompt_groups

def run_complete_test():
    """Run complete system test"""
    print("🧪 Starting Complete System Test")
    print("=" * 60)
    
    try:
        # Test 1: File Storage
        storage = test_file_storage()
        
        # Test 2: Prompt Engine
        improvement = test_prompt_engine()
        
        # Test 3: Judge System
        scores = test_judge_system()
        
        # Test 4: Integrated Workflow
        workflow_result = test_integrated_workflow()
        
        # Test 5: Version History
        version_groups = test_version_history_display()
        
        # Summary
        print("\n🎉 Test Summary")
        print("=" * 40)
        print("✅ File Storage: Working")
        print("✅ Prompt Engine: Working") 
        print("✅ Judge System: Working")
        print("✅ Integrated Workflow: Working")
        print("✅ Version History: Working")
        
        print(f"\n📊 Data Created:")
        print(f"   • Prompts with versions: {len(version_groups)}")
        print(f"   • Latest workflow prompt: {workflow_result['prompt_id']}")
        print(f"   • Latest score: {workflow_result['scores']['total']:.1f}/50")
        
        print("\n🚀 System is ready! You can now run:")
        print("   python -m streamlit run apps/web/streamlit_app.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)