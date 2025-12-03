#!/usr/bin/env python3
"""
Example usage of the CSV functionality with Sequential ID System
"""

from file_storage import FileStorage

def main():
    """Demo of CSV functionality with sequential numbering for prompt engineering learning."""
    storage = FileStorage()
    
    print("📊 CSV Sequential ID System Demo")
    print("=" * 40)
    
    # Example 1: Manual data entry (ID will be auto-generated as 001)
    prompt_data = {
        'llm_name': 'GPT-4',
        'prompt': 'Write a function to validate email addresses',
        'original_response': 'Here is a basic regex validation function...',
        'learning_memory': 'Basic validation works but lacks comprehensive error handling'
    }
    
    # Save to CSV (gets ID: 001)
    storage.save_to_csv('my_learning_log', prompt_data)
    print(f"✅ Saved first prompt (ID: 001)")
    
    # Example 1b: Rewritten version of the first prompt
    rewrite_data = {
        'llm_name': 'GPT-4',
        'prompt': 'Write a comprehensive email validation function in Python with detailed error messages, support for international domains, and unit tests',
        'original_response': 'Here is a robust email validator with comprehensive testing...',
        'learning_memory': 'Adding specific requirements for error handling and testing greatly improves response quality'
    }
    
    # Save as rewrite of first prompt (gets ID: 001.1)
    storage.save_to_csv('my_learning_log', rewrite_data, is_rewrite=True, base_prompt_id='001')
    print(f"✅ Saved rewritten prompt (ID: 001.1)")
    
    # Example 1c: Another new prompt
    new_prompt_data = {
        'llm_name': 'Claude-3',
        'prompt': 'Create a REST API for user management',
        'original_response': 'Here is a basic Flask API...',
        'learning_memory': 'Simple REST API request yielded basic implementation'
    }
    
    # Save new prompt (gets ID: 002)
    storage.save_to_csv('my_learning_log', new_prompt_data)
    print(f"✅ Saved second prompt (ID: 002)")
    
    # Example 2: Read and display data with sequential IDs
    print("\n📖 Reading CSV data (Sequential ID System):")
    data = storage.read_from_csv('my_learning_log')
    for entry in data:
        prompt_type = "REWRITE" if "." in entry['prompt_id'] else "NEW"
        print(f"ID: {entry['prompt_id']} ({prompt_type})")
        print(f"LLM: {entry['llm_name']}")
        print(f"Learning: {entry['learning_memory'][:60]}...")
        print("-" * 30)
    
    # Example 3: Search functionality
    print("\n🔍 Searching for 'email':")
    matches = storage.search_csv_entries('my_learning_log', 'email')
    for match in matches:
        print(f"Found: ID {match['prompt_id']} - {match['learning_memory']}")
    
    print(f"\n💡 Sequential ID System Features:")
    print(f"• New prompts: 001, 002, 003, ...")
    print(f"• Rewrites: 001.1, 002.1, 003.1, ...")
    print(f"• Auto-generation based on existing entries")
    print(f"\nFor interactive data collection:")
    print(f"data = storage.collect_prompt_data_interactive()")
    print(f"storage.save_to_csv('my_prompts', data)  # Gets next sequential ID")
    print(f"storage.save_to_csv('my_prompts', rewrite, is_rewrite=True, base_prompt_id='001')")

if __name__ == "__main__":
    main()