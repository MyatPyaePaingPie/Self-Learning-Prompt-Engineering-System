"""
File Storage System for Self-Learning Prompt Engineering System
Handles saving prompts, results, judge scores, and CSV learning data
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import uuid


class FileStorage:
    """Enhanced file storage with CSV learning system and sequential ID tracking"""
    
    def __init__(self, base_dir: str = "storage"):
        """Initialize file storage with base directory"""
        self.base_dir = Path(base_dir)
        self.prompts_dir = self.base_dir / "prompts"
        self.results_dir = self.base_dir / "results"
        
        # Create directories if they don't exist
        self.base_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def save_prompt(self, text: str, prompt_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """Save prompt to file with optional metadata"""
        if prompt_id is None:
            prompt_id = str(uuid.uuid4())
        
        filename = f"{prompt_id}.txt"
        file_path = self.prompts_dir / filename
        
        # Save main content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save metadata if provided
        if metadata:
            metadata_path = self.prompts_dir / f"{prompt_id}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        return filename
    
    def save_result(self, text: str, result_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """Save result to file with optional metadata"""
        if result_id is None:
            result_id = str(uuid.uuid4())
        
        filename = f"{result_id}.txt"
        file_path = self.results_dir / filename
        
        # Save main content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save metadata if provided
        if metadata:
            metadata_path = self.results_dir / f"{result_id}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        return filename
    
    def load_prompt(self, filename: str) -> str:
        """Load prompt from file"""
        file_path = self.prompts_dir / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_result(self, filename: str) -> str:
        """Load result from file"""
        file_path = self.results_dir / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_prompts(self) -> List[str]:
        """List all prompt files"""
        return [f.name for f in self.prompts_dir.glob("*.txt")]
    
    def list_results(self) -> List[str]:
        """List all result files"""
        return [f.name for f in self.results_dir.glob("*.txt")]
    
    def save_to_csv(self, filename: str, data: Dict[str, Any], is_rewrite: bool = False, base_prompt_id: Optional[str] = None) -> str:
        """Save data to CSV with sequential ID system"""
        csv_path = self.base_dir / f"{filename}.csv"
        
        # Generate sequential ID
        prompt_id = self._generate_sequential_id(csv_path, is_rewrite, base_prompt_id)
        
        # Add ID and timestamp to data
        data_with_id = {
            'prompt_id': prompt_id,
            'timestamp': datetime.now().isoformat(),
            **data
        }
        
        # Check if file exists to determine if we need headers
        file_exists = csv_path.exists()
        
        # Write to CSV
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            if data_with_id:
                writer = csv.DictWriter(f, fieldnames=data_with_id.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data_with_id)
        
        return prompt_id
    
    def save_version_to_csv(self, prompt_id: Union[str, 'UUID'], version) -> None:
        """Save prompt version to dedicated CSV file (for Week 6 compatibility)"""
        csv_path = self.base_dir / "prompt_versions.csv"
        
        # Extract version data
        version_data = {
            'prompt_id': str(prompt_id),
            'version_no': getattr(version, 'version_no', 0),
            'version_uuid': str(getattr(version, 'id', uuid.uuid4())),
            'text': getattr(version, 'text', ''),
            'source': getattr(version, 'source', 'unknown'),
            'explanation': json.dumps(getattr(version, 'explanation', {})),
            'timestamp': getattr(version, 'created_at', datetime.now()).isoformat() if hasattr(getattr(version, 'created_at', None), 'isoformat') else str(getattr(version, 'created_at', datetime.now().isoformat()))
        }
        
        # Check if file exists
        file_exists = csv_path.exists()
        
        # Write to CSV
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=version_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(version_data)
    
    def save_judge_scores_to_csv(self, prompt_id: Union[str, 'UUID'], version_id: Union[str, 'UUID'], judge_scores: Dict[str, Any]) -> None:
        """Save judge scores alongside prompts in CSV format"""
        csv_path = self.base_dir / "judge_scores.csv"
        
        # Prepare judge score data
        score_data = {
            'prompt_id': str(prompt_id),
            'version_id': str(version_id),
            'clarity': judge_scores.get('clarity', 0),
            'specificity': judge_scores.get('specificity', 0),
            'actionability': judge_scores.get('actionability', 0),
            'structure': judge_scores.get('structure', 0),
            'context_use': judge_scores.get('context_use', 0),
            'total': judge_scores.get('total', 0),
            'feedback': json.dumps(judge_scores.get('feedback', {})),
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if file exists
        file_exists = csv_path.exists()
        
        # Write to CSV
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=score_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(score_data)
    
    def read_from_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Read all entries from CSV file"""
        csv_path = self.base_dir / f"{filename}.csv"
        
        if not csv_path.exists():
            return []
        
        entries = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            entries = list(reader)
        
        return entries
    
    def search_csv_entries(self, filename: str, search_term: str, field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search CSV entries for specific term"""
        entries = self.read_from_csv(filename)
        
        if not entries:
            return []
        
        matches = []
        for entry in entries:
            if field:
                # Search in specific field
                if field in entry and search_term.lower() in str(entry[field]).lower():
                    matches.append(entry)
            else:
                # Search in all fields
                for value in entry.values():
                    if search_term.lower() in str(value).lower():
                        matches.append(entry)
                        break
        
        return matches
    
    def get_version_history(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Get all versions for a specific prompt from CSV"""
        return self.search_csv_entries('prompt_versions', prompt_id, 'prompt_id')
    
    def get_judge_scores_history(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Get all judge scores for a specific prompt"""
        return self.search_csv_entries('judge_scores', prompt_id, 'prompt_id')
    
    def _generate_sequential_id(self, csv_path: Path, is_rewrite: bool, base_prompt_id: Optional[str]) -> str:
        """Generate sequential ID (001, 002, 001.1, etc.)"""
        if is_rewrite and base_prompt_id:
            return f"{base_prompt_id}.1"
        
        if not csv_path.exists():
            return "001"
        
        # Read existing IDs
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_ids = [row.get('prompt_id', '') for row in reader]
        
        # Find next sequential number
        max_num = 0
        for existing_id in existing_ids:
            if '.' not in existing_id and existing_id.isdigit():
                max_num = max(max_num, int(existing_id))
        
        return f"{max_num + 1:03d}"
    
    def collect_prompt_data_interactive(self) -> Dict[str, str]:
        """Interactive data collection for prompts"""
        print("📝 Interactive Prompt Data Collection")
        print("-" * 40)
        
        data = {}
        data['llm_name'] = input("LLM Name (e.g., GPT-4, Claude-3): ") or "Unknown"
        data['prompt'] = input("Enter the prompt: ") or "No prompt provided"
        data['original_response'] = input("Enter the original response: ") or "No response provided"
        data['learning_memory'] = input("Learning memory/notes: ") or "No notes"
        
        return data


# Example usage and demo
if __name__ == "__main__":
    # Initialize storage
    storage = FileStorage("storage")
    
    print("🗂️  File Storage System Demo")
    print("=" * 50)
    
    # Basic file storage demo
    print("\n📁 Basic File Storage")
    print("-" * 30)
    
    # Save a prompt
    prompt_file = storage.save_prompt(
        text="Write a Python function to calculate factorial",
        prompt_id="factorial_prompt",
        metadata={"author": "System", "type": "coding"}
    )
    print(f"✅ Saved prompt: {prompt_file}")
    
    # Save a result
    result_file = storage.save_result(
        text="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
        result_id="factorial_solution"
    )
    print(f"✅ Saved result: {result_file}")
    
    # CSV functionality demo
    print("\n📊 CSV Functionality Demo (Sequential ID System)")
    print("-" * 50)
    
    # Save some sample learning data
    learning_data = [
        {
            'llm_name': 'GPT-4',
            'prompt': 'Write a sorting algorithm',
            'original_response': 'Here is bubble sort...',
            'learning_memory': 'Basic request yielded simple solution'
        },
        {
            'llm_name': 'Claude-3',
            'prompt': 'Explain quantum computing',
            'original_response': 'Quantum computing uses quantum mechanics...',
            'learning_memory': 'Good explanation but needs more examples'
        }
    ]
    
    # Save entries
    for i, data in enumerate(learning_data, 1):
        prompt_id = storage.save_to_csv('learning_log', data)
        print(f"Entry {i}: ID {prompt_id} - {data['llm_name']}")
    
    # Save a rewrite
    rewrite_data = {
        'llm_name': 'GPT-4',
        'prompt': 'Write efficient merge sort with complexity analysis',
        'original_response': 'Here is optimized merge sort...',
        'learning_memory': 'Specific requirements improve response quality'
    }
    rewrite_id = storage.save_to_csv('learning_log', rewrite_data, is_rewrite=True, base_prompt_id='001')
    print(f"Rewrite: ID {rewrite_id} - {rewrite_data['llm_name']}")
    
    # Demonstrate judge scores saving
    print("\n⚖️  Judge Scores Demo")
    print("-" * 25)
    
    sample_scores = {
        'clarity': 8.5,
        'specificity': 7.0,
        'actionability': 9.0,
        'structure': 8.0,
        'context_use': 6.5,
        'total': 39.0,
        'feedback': {
            'pros': ['Clear task definition', 'Good structure'],
            'cons': ['Could be more specific'],
            'summary': 'Well-structured prompt with room for improvement'
        }
    }
    
    storage.save_judge_scores_to_csv('factorial_prompt', 'version_001', sample_scores)
    print(f"✅ Saved judge scores for factorial_prompt")
    
    # Read and display data
    print("\n📖 Reading Saved Data")
    print("-" * 25)
    
    entries = storage.read_from_csv('learning_log')
    print(f"Total learning log entries: {len(entries)}")
    
    judge_entries = storage.read_from_csv('judge_scores')
    print(f"Total judge score entries: {len(judge_entries)}")
    
    # Search functionality
    print("\n🔍 Search Demo")
    print("-" * 15)
    matches = storage.search_csv_entries('learning_log', 'sorting')
    print(f"Found {len(matches)} entries containing 'sorting'")
    
    print("\n✅ Demo completed successfully!")