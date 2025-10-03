#!/usr/bin/env python3
"""
File Storage Script for Self-Learning Prompt Engineering System
Author: Atang's Assignment

This script provides functionality to save text content to organized folders:
- prompts/ - for storing original and improved prompts
- results/ - for storing processing results and outputs
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Common LLM names for validation
COMMON_LLMS = [
    "GPT-4", "GPT-3.5", "Claude-3", "Claude-3.5", "Gemini-Pro",
    "Llama-2", "Mistral-7B", "PaLM-2", "Other"
]

class FileStorage:
    """Simple file storage system for prompts and results with CSV support."""
    
    def __init__(self, base_dir: str = "."):
        """Initialize file storage with base directory."""
        self.base_dir = Path(base_dir)
        self.prompts_dir = self.base_dir / "prompts"
        self.results_dir = self.base_dir / "results"
        
        # Ensure directories exist
        self.prompts_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def save_prompt(self, text: str, prompt_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save a prompt to the prompts/ folder.
        
        Args:
            text: The prompt text to save
            prompt_id: Optional custom ID, otherwise generates timestamp-based ID
            metadata: Optional metadata dictionary
            
        Returns:
            str: The filename where the prompt was saved
        """
        if prompt_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_id = f"prompt_{timestamp}"
        
        filename = f"{prompt_id}.txt"
        filepath = self.prompts_dir / filename
        
        # Prepare content with metadata header if provided
        content = text
        if metadata:
            header = f"# Metadata: {json.dumps(metadata, indent=2)}\n# Content:\n"
            content = header + text
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Prompt saved to: {filepath}")
            return filename
        except Exception as e:
            print(f"❌ Error saving prompt: {e}")
            raise
    
    def save_result(self, text: str, result_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save a result to the results/ folder.
        
        Args:
            text: The result text to save
            result_id: Optional custom ID, otherwise generates timestamp-based ID
            metadata: Optional metadata dictionary
            
        Returns:
            str: The filename where the result was saved
        """
        if result_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_id = f"result_{timestamp}"
        
        filename = f"{result_id}.txt"
        filepath = self.results_dir / filename
        
        # Prepare content with metadata header if provided
        content = text
        if metadata:
            header = f"# Metadata: {json.dumps(metadata, indent=2)}\n# Content:\n"
            content = header + text
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Result saved to: {filepath}")
            return filename
        except Exception as e:
            print(f"❌ Error saving result: {e}")
            raise
    
    def load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts/ folder."""
        filepath = self.prompts_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error loading prompt {filename}: {e}")
            raise
    
    def load_result(self, filename: str) -> str:
        """Load a result from the results/ folder."""
        filepath = self.results_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error loading result {filename}: {e}")
            raise
    
    def list_prompts(self) -> list[str]:
        """List all prompt files."""
        return [f.name for f in self.prompts_dir.glob("*.txt")]
    
    def list_results(self) -> list[str]:
        """List all result files."""
        return [f.name for f in self.results_dir.glob("*.txt")]
    
    def _get_next_prompt_id(self, csv_filename: str, is_rewrite: bool = False, base_id: str = None) -> str:
        """
        Generate the next sequential prompt ID using number system.
        
        Args:
            csv_filename: Name of the CSV file to check existing IDs
            is_rewrite: Whether this is a rewritten prompt (adds .1)
            base_id: Base ID for rewrite (e.g., "001" becomes "001.1")
            
        Returns:
            str: Next sequential ID (e.g., "001", "002", "001.1", "002.1")
        """
        # Ensure .csv extension
        if not csv_filename.endswith('.csv'):
            csv_filename += '.csv'
            
        csv_path = self.base_dir / csv_filename
        
        if is_rewrite and base_id:
            # For rewrites, use base_id + .1
            return f"{base_id}.1"
        
        # Get existing entries to find the highest number
        existing_ids = []
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if 'prompt_id' in row:
                            existing_ids.append(row['prompt_id'])
            except Exception:
                pass  # If file can't be read, start from 001
        
        # Find the highest base number (ignoring .1 versions)
        max_num = 0
        for id_str in existing_ids:
            try:
                # Extract the base number (before any decimal)
                base_part = id_str.split('.')[0]
                # Try to convert to int
                num = int(base_part)
                max_num = max(max_num, num)
            except ValueError:
                continue  # Skip non-numeric IDs
        
        # Return next sequential number
        next_num = max_num + 1
        return f"{next_num:03d}"  # Format as 001, 002, 003, etc.
    
    def save_to_csv(self, csv_filename: str, prompt_data: Dict[str, str], is_rewrite: bool = False, base_prompt_id: str = None) -> str:
        """
        Save prompt data to a CSV file with structured columns.
        
        Args:
            csv_filename: Name of the CSV file (will add .csv if not present)
            prompt_data: Dictionary containing prompt information
            is_rewrite: Whether this is a rewritten version of an existing prompt
            base_prompt_id: Base prompt ID for rewrites (e.g., "001" becomes "001.1")
            
        Expected keys in prompt_data:
            - prompt_id: Unique identifier (auto-generated if not provided using number system)
            - llm_name: Name of the LLM used
            - prompt: Original prompt text
            - original_response: Response from the original prompt
            - rewritten_prompt: Improved version of the prompt
            - rewritten_response: Response from the improved prompt
            - learning_memory: Notes about what was learned
            
        Returns:
            str: Path to the CSV file
        """
        # Ensure .csv extension
        if not csv_filename.endswith('.csv'):
            csv_filename += '.csv'
            
        csv_path = self.base_dir / csv_filename
        
        # Generate prompt_id if not provided using sequential numbering
        if 'prompt_id' not in prompt_data or not prompt_data['prompt_id']:
            prompt_data['prompt_id'] = self._get_next_prompt_id(csv_filename, is_rewrite, base_prompt_id)
        
        # Validate LLM name
        if 'llm_name' in prompt_data and prompt_data['llm_name'] not in COMMON_LLMS:
            print(f"⚠️  Warning: '{prompt_data['llm_name']}' is not in common LLMs list")
        
        # CSV headers
        headers = [
            'prompt_id', 'llm_name', 'prompt', 'original_response',
            'rewritten_prompt', 'rewritten_response', 'learning_memory', 'timestamp'
        ]
        
        # Add timestamp
        prompt_data['timestamp'] = datetime.now().isoformat()
        
        # Check if file exists to determine if we need headers
        file_exists = csv_path.exists()
        
        try:
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write the data row
                writer.writerow({key: prompt_data.get(key, '') for key in headers})
                
            print(f"✅ Data saved to CSV: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
            raise
    
    def read_from_csv(self, csv_filename: str) -> List[Dict[str, str]]:
        """
        Read all entries from a CSV file.
        
        Args:
            csv_filename: Name of the CSV file
            
        Returns:
            List of dictionaries containing prompt data
        """
        if not csv_filename.endswith('.csv'):
            csv_filename += '.csv'
            
        csv_path = self.base_dir / csv_filename
        
        if not csv_path.exists():
            print(f"❌ CSV file not found: {csv_path}")
            return []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
                print(f"✅ Loaded {len(data)} entries from CSV: {csv_path}")
                return data
                
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            raise
    
    def collect_prompt_data_interactive(self) -> Dict[str, str]:
        """
        Interactive method to collect prompt data from user input.
        
        Returns:
            Dictionary with collected prompt data
        """
        print("\n📝 Interactive Prompt Data Collection")
        print("=" * 50)
        
        data = {}
        
        # Prompt ID (optional)
        prompt_id = input("Prompt ID (press Enter to auto-generate): ").strip()
        if prompt_id:
            data['prompt_id'] = prompt_id
        
        # LLM Name with suggestions
        print(f"\nAvailable LLMs: {', '.join(COMMON_LLMS)}")
        while True:
            llm_name = input("LLM Name: ").strip()
            if llm_name:
                data['llm_name'] = llm_name
                break
            print("LLM Name is required!")
        
        # Original Prompt
        print("\nEnter the original prompt (press Enter twice to finish):")
        prompt_lines = []
        while True:
            line = input()
            if line == "" and len(prompt_lines) > 0:
                break
            prompt_lines.append(line)
        data['prompt'] = '\n'.join(prompt_lines)
        
        # Original Response
        print("\nEnter the original response (press Enter twice to finish):")
        response_lines = []
        while True:
            line = input()
            if line == "" and len(response_lines) > 0:
                break
            response_lines.append(line)
        data['original_response'] = '\n'.join(response_lines)
        
        # Rewritten Prompt (optional)
        print("\nEnter the rewritten prompt (optional, press Enter twice to finish):")
        rewritten_prompt_lines = []
        while True:
            line = input()
            if line == "":
                break
            rewritten_prompt_lines.append(line)
        data['rewritten_prompt'] = '\n'.join(rewritten_prompt_lines) if rewritten_prompt_lines else ''
        
        # Rewritten Response (optional)
        if data['rewritten_prompt']:
            print("\nEnter the rewritten response (press Enter twice to finish):")
            rewritten_response_lines = []
            while True:
                line = input()
                if line == "":
                    break
                rewritten_response_lines.append(line)
            data['rewritten_response'] = '\n'.join(rewritten_response_lines) if rewritten_response_lines else ''
        else:
            data['rewritten_response'] = ''
        
        # Learning and Memory
        learning = input("\nWhat did you learn from this interaction? ").strip()
        data['learning_memory'] = learning
        
        return data
    
    def search_csv_entries(self, csv_filename: str, search_term: str, search_field: str = None) -> List[Dict[str, str]]:
        """
        Search for entries in CSV file.
        
        Args:
            csv_filename: Name of the CSV file
            search_term: Term to search for
            search_field: Specific field to search in (optional, searches all fields if None)
            
        Returns:
            List of matching entries
        """
        data = self.read_from_csv(csv_filename)
        
        if not data:
            return []
        
        matches = []
        search_term_lower = search_term.lower()
        
        for entry in data:
            if search_field:
                # Search in specific field
                if search_field in entry and search_term_lower in entry[search_field].lower():
                    matches.append(entry)
            else:
                # Search in all fields
                found = any(search_term_lower in str(value).lower() for value in entry.values())
                if found:
                    matches.append(entry)
        
        print(f"🔍 Found {len(matches)} matches for '{search_term}'")
        return matches


def main():
    """Example usage of the file storage system with CSV functionality."""
    storage = FileStorage()
    
    print("🗃️  File Storage System Demo (with CSV Support)")
    print("=" * 50)
    
    # Example 1: Save a simple prompt (original functionality)
    sample_prompt = "Help me write a Python function to calculate fibonacci numbers"
    prompt_file = storage.save_prompt(
        text=sample_prompt,
        prompt_id="example_prompt",
        metadata={"author": "Atang", "type": "coding", "difficulty": "beginner"}
    )
    
    # Example 2: Save a result (original functionality)
    sample_result = """
Here's a Python function to calculate Fibonacci numbers:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage:
print(fibonacci(10))  # Output: 55
"""
    result_file = storage.save_result(
        text=sample_result,
        result_id="fibonacci_solution",
        metadata={"prompt_id": "example_prompt", "language": "python", "status": "completed"}
    )
    
    # Example 3: List files (original functionality)
    print(f"\n📁 Prompts: {storage.list_prompts()}")
    print(f"📁 Results: {storage.list_results()}")
    
    # NEW: Example 4: CSV functionality with sequential numbering
    print(f"\n📊 CSV Functionality Demo (Sequential ID System)")
    print("-" * 50)
    
    # Create sample CSV data (ID will be auto-generated as 001)
    sample_csv_data1 = {
        'llm_name': 'GPT-4',
        'prompt': 'Write a Python function to calculate fibonacci numbers',
        'original_response': 'Here is a basic recursive implementation...',
        'learning_memory': 'Basic prompt yielded simple recursive solution'
    }
    
    # Save to CSV (will get ID: 001)
    csv_file = storage.save_to_csv('prompt_learning_log', sample_csv_data1)
    
    # Create a rewritten version of the first prompt (ID will be 001.1)
    sample_csv_rewrite = {
        'llm_name': 'GPT-4',
        'prompt': 'Write an efficient Python function to calculate fibonacci numbers using dynamic programming, include error handling and docstring',
        'original_response': 'Here is an optimized implementation with memoization...',
        'learning_memory': 'Adding specific requirements about efficiency and documentation improves response quality significantly'
    }
    
    # Save as rewrite of first prompt (will get ID: 001.1)
    storage.save_to_csv('prompt_learning_log', sample_csv_rewrite, is_rewrite=True, base_prompt_id='001')
    
    # Add another new entry (will get ID: 002)
    sample_csv_data2 = {
        'llm_name': 'Claude-3',
        'prompt': 'Implement a sorting algorithm',
        'original_response': 'Here is bubble sort...',
        'rewritten_prompt': 'Implement merge sort algorithm in Python with time complexity analysis and unit tests',
        'rewritten_response': 'Here is an efficient merge sort implementation...',
        'learning_memory': 'Specific algorithm requests with analysis requirements yield better educational content'
    }
    
    # Save new prompt (will get ID: 002)
    storage.save_to_csv('prompt_learning_log', sample_csv_data2)
    
    # Read from CSV
    print(f"\n📖 Reading CSV data with sequential IDs:")
    csv_data = storage.read_from_csv('prompt_learning_log')
    for i, entry in enumerate(csv_data, 1):
        print(f"Entry {i}: ID {entry['prompt_id']} - {entry['llm_name']}")
    
    # Search functionality
    print(f"\n🔍 Searching for 'fibonacci' in CSV:")
    matches = storage.search_csv_entries('prompt_learning_log', 'fibonacci')
    for match in matches:
        print(f"Found: ID {match['prompt_id']} - {match['learning_memory'][:50]}...")
    
    # Interactive mode prompt
    print(f"\n💡 Sequential ID System:")
    print("• New prompts get sequential IDs: 001, 002, 003...")
    print("• Rewrites get decimal versions: 001.1, 002.1...")
    print("• To try interactive data collection:")
    print("  data = storage.collect_prompt_data_interactive()")
    print("  storage.save_to_csv('my_prompts', data)  # Gets next sequential ID")
    print("  storage.save_to_csv('my_prompts', rewrite_data, is_rewrite=True, base_prompt_id='001')  # Gets 001.1")


if __name__ == "__main__":
    main()