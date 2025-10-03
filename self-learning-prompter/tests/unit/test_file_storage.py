#!/usr/bin/env python3
"""
Tests for File Storage System
Author: Atang's Assignment

This test module verifies the file storage functionality works correctly.
"""

import os
import tempfile
import sys
from pathlib import Path

# Add the parent directory to the path to import file_storage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from file_storage import FileStorage

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest.raises for basic functionality
    class MockPytest:
        @staticmethod
        def raises(exception):
            class RaisesContext:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is None:
                        raise AssertionError(f"Expected {exception.__name__} to be raised")
                    return exc_type is exception
            return RaisesContext()
    pytest = MockPytest()

class TestFileStorage:
    """Test cases for FileStorage class."""
    
    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileStorage(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary files after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_directories_created(self):
        """Test that prompts/ and results/ directories are created."""
        assert self.storage.prompts_dir.exists()
        assert self.storage.results_dir.exists()
        assert self.storage.prompts_dir.is_dir()
        assert self.storage.results_dir.is_dir()
    
    def test_save_prompt_basic(self):
        """Test basic prompt saving functionality."""
        test_text = "Help me write a Python function"
        filename = self.storage.save_prompt(test_text, prompt_id="test_prompt")
        
        assert filename == "test_prompt.txt"
        assert (self.storage.prompts_dir / filename).exists()
        
        # Verify content
        saved_content = self.storage.load_prompt(filename)
        assert test_text in saved_content
    
    def test_save_prompt_with_metadata(self):
        """Test saving prompt with metadata."""
        test_text = "Create a web scraper"
        metadata = {"author": "Atang", "type": "coding"}
        
        filename = self.storage.save_prompt(test_text, prompt_id="meta_test", metadata=metadata)
        saved_content = self.storage.load_prompt(filename)
        
        assert test_text in saved_content
        assert "Metadata" in saved_content
        assert "author" in saved_content
        assert "Atang" in saved_content
    
    def test_save_result_basic(self):
        """Test basic result saving functionality."""
        test_result = "Here's your Python function:\n\ndef hello():\n    print('Hello!')"
        filename = self.storage.save_result(test_result, result_id="test_result")
        
        assert filename == "test_result.txt"
        assert (self.storage.results_dir / filename).exists()
        
        # Verify content
        saved_content = self.storage.load_result(filename)
        assert test_result in saved_content
    
    def test_save_result_with_metadata(self):
        """Test saving result with metadata."""
        test_result = "Solution: Use requests library"
        metadata = {"prompt_id": "test_prompt", "status": "completed"}
        
        filename = self.storage.save_result(test_result, result_id="meta_result", metadata=metadata)
        saved_content = self.storage.load_result(filename)
        
        assert test_result in saved_content
        assert "Metadata" in saved_content
        assert "completed" in saved_content
    
    def test_auto_generated_ids(self):
        """Test that IDs are auto-generated when not provided."""
        filename1 = self.storage.save_prompt("Test prompt 1")
        filename2 = self.storage.save_prompt("Test prompt 2")
        
        # Should have different filenames
        assert filename1 != filename2
        assert filename1.startswith("prompt_")
        assert filename2.startswith("prompt_")
        assert filename1.endswith(".txt")
        assert filename2.endswith(".txt")
    
    def test_list_prompts(self):
        """Test listing prompt files."""
        # Initially empty
        assert len(self.storage.list_prompts()) == 0
        
        # Add some prompts
        self.storage.save_prompt("Prompt 1", "p1")
        self.storage.save_prompt("Prompt 2", "p2")
        
        prompts = self.storage.list_prompts()
        assert len(prompts) == 2
        assert "p1.txt" in prompts
        assert "p2.txt" in prompts
    
    def test_list_results(self):
        """Test listing result files."""
        # Initially empty
        assert len(self.storage.list_results()) == 0
        
        # Add some results
        self.storage.save_result("Result 1", "r1")
        self.storage.save_result("Result 2", "r2")
        
        results = self.storage.list_results()
        assert len(results) == 2
        assert "r1.txt" in results
        assert "r2.txt" in results
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.storage.load_prompt("nonexistent.txt")
        
        with pytest.raises(FileNotFoundError):
            self.storage.load_result("nonexistent.txt")
    
    def test_round_trip(self):
        """Test saving and loading preserves content."""
        original_text = """
        Multi-line prompt:
        1. First instruction
        2. Second instruction
        3. Final instruction
        """
        
        filename = self.storage.save_prompt(original_text.strip(), "round_trip")
        loaded_text = self.storage.load_prompt(filename)
        
        # Content should be preserved
        assert original_text.strip() in loaded_text


def test_file_storage_integration():
    """Integration test: does the file storage work end-to-end?"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = FileStorage(temp_dir)
        
        # Save a prompt
        prompt_text = "Write a function to reverse a string"
        prompt_file = storage.save_prompt(prompt_text, "integration_prompt")
        
        # Save a result
        result_text = "def reverse_string(s): return s[::-1]"
        result_file = storage.save_result(result_text, "integration_result")
        
        # Verify both exist and can be loaded
        assert prompt_file in storage.list_prompts()
        assert result_file in storage.list_results()
        
        loaded_prompt = storage.load_prompt(prompt_file)
        loaded_result = storage.load_result(result_file)
        
        assert prompt_text in loaded_prompt
        assert result_text in loaded_result
        
        print("✅ Integration test passed!")


    def test_save_to_csv_basic(self):
        """Test basic CSV saving functionality."""
        prompt_data = {
            'prompt_id': 'test_csv_001',
            'llm_name': 'GPT-4',
            'prompt': 'Write a hello world program',
            'original_response': 'print("Hello, World!")',
            'rewritten_prompt': 'Write a hello world program with error handling',
            'rewritten_response': 'try:\n    print("Hello, World!")\nexcept Exception as e:\n    print(f"Error: {e}")',
            'learning_memory': 'Adding error handling improves robustness'
        }
        
        csv_file = self.storage.save_to_csv('test_log', prompt_data)
        
        # Check file was created
        expected_path = self.storage.base_dir / 'test_log.csv'
        assert expected_path.exists()
        
        # Verify content can be read back
        data = self.storage.read_from_csv('test_log')
        assert len(data) == 1
        assert data[0]['prompt_id'] == 'test_csv_001'
        assert data[0]['llm_name'] == 'GPT-4'
    
    def test_save_to_csv_auto_id(self):
        """Test CSV saving with auto-generated prompt ID."""
        prompt_data = {
            'llm_name': 'Claude-3',
            'prompt': 'Explain recursion',
            'original_response': 'Recursion is when a function calls itself...',
            'learning_memory': 'Simple explanations work well'
        }
        
        self.storage.save_to_csv('auto_id_test', prompt_data)
        data = self.storage.read_from_csv('auto_id_test')
        
        assert len(data) == 1
        assert data[0]['prompt_id'].startswith('prompt_')
        assert data[0]['llm_name'] == 'Claude-3'
    
    def test_save_to_csv_append(self):
        """Test that multiple entries are appended to the same CSV file."""
        # First entry
        data1 = {
            'prompt_id': 'append_test_001',
            'llm_name': 'GPT-4',
            'prompt': 'First prompt',
            'learning_memory': 'First learning'
        }
        
        # Second entry
        data2 = {
            'prompt_id': 'append_test_002',
            'llm_name': 'Claude-3',
            'prompt': 'Second prompt',
            'learning_memory': 'Second learning'
        }
        
        self.storage.save_to_csv('append_test', data1)
        self.storage.save_to_csv('append_test', data2)
        
        # Check both entries are present
        csv_data = self.storage.read_from_csv('append_test')
        assert len(csv_data) == 2
        assert csv_data[0]['prompt_id'] == 'append_test_001'
        assert csv_data[1]['prompt_id'] == 'append_test_002'
    
    def test_read_from_csv_nonexistent(self):
        """Test reading from a non-existent CSV file."""
        data = self.storage.read_from_csv('nonexistent_file')
        assert data == []
    
    def test_search_csv_entries_all_fields(self):
        """Test searching across all fields in CSV."""
        # Add test data
        test_data = [
            {
                'prompt_id': 'search_test_001',
                'llm_name': 'GPT-4',
                'prompt': 'Calculate fibonacci numbers',
                'learning_memory': 'Fibonacci is a classic algorithm problem'
            },
            {
                'prompt_id': 'search_test_002',
                'llm_name': 'Claude-3',
                'prompt': 'Implement sorting algorithm',
                'learning_memory': 'Sorting algorithms are fundamental to CS'
            }
        ]
        
        for data in test_data:
            self.storage.save_to_csv('search_test', data)
        
        # Search for 'fibonacci'
        matches = self.storage.search_csv_entries('search_test', 'fibonacci')
        assert len(matches) == 1
        assert matches[0]['prompt_id'] == 'search_test_001'
        
        # Search for 'algorithm' (should match both)
        matches = self.storage.search_csv_entries('search_test', 'algorithm')
        assert len(matches) == 2
    
    def test_search_csv_entries_specific_field(self):
        """Test searching in a specific field."""
        test_data = {
            'prompt_id': 'field_search_001',
            'llm_name': 'GPT-4',
            'prompt': 'Write Python code',
            'learning_memory': 'Python is versatile for many tasks'
        }
        
        self.storage.save_to_csv('field_search_test', test_data)
        
        # Search for 'Python' in prompt field (should find)
        matches = self.storage.search_csv_entries('field_search_test', 'Python', 'prompt')
        assert len(matches) == 1
        
        # Search for 'Python' in llm_name field (should not find)
        matches = self.storage.search_csv_entries('field_search_test', 'Python', 'llm_name')
        assert len(matches) == 0
        
        # Search for 'GPT' in llm_name field (should find)
        matches = self.storage.search_csv_entries('field_search_test', 'GPT', 'llm_name')
        assert len(matches) == 1
    
    def test_csv_file_extension_handling(self):
        """Test that .csv extension is handled correctly."""
        prompt_data = {
            'prompt_id': 'extension_test',
            'llm_name': 'GPT-4',
            'prompt': 'Test extension handling'
        }
        
        # Save without .csv extension
        self.storage.save_to_csv('no_extension', prompt_data)
        
        # Save with .csv extension
        self.storage.save_to_csv('with_extension.csv', prompt_data)
        
        # Both should create .csv files
        assert (self.storage.base_dir / 'no_extension.csv').exists()
        assert (self.storage.base_dir / 'with_extension.csv').exists()
        
        # Both should be readable
        data1 = self.storage.read_from_csv('no_extension')
        data2 = self.storage.read_from_csv('with_extension.csv')
        
        assert len(data1) == 1
        assert len(data2) == 1
    
    def test_csv_with_special_characters(self):
        """Test CSV handling with special characters and multiline text."""
        prompt_data = {
            'prompt_id': 'special_chars_001',
            'llm_name': 'GPT-4',
            'prompt': 'Write a function that handles:\n1. Commas, quotes\n2. "Special characters"\n3. Line breaks',
            'original_response': 'Here\'s a function:\ndef handle_special(text):\n    return text.replace(",", "comma")',
            'learning_memory': 'CSV properly escapes special characters like commas, quotes, and newlines'
        }
        
        self.storage.save_to_csv('special_chars_test', prompt_data)
        data = self.storage.read_from_csv('special_chars_test')
        
        assert len(data) == 1
        assert 'commas, quotes' in data[0]['prompt']
        assert '"Special characters"' in data[0]['prompt']
        assert '\n' in data[0]['prompt']  # Newlines preserved
        assert 'def handle_special' in data[0]['original_response']


def test_csv_integration():
    """Integration test for CSV functionality."""
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = FileStorage(temp_dir)
        
        # Create a complete prompt learning entry
        prompt_data = {
            'prompt_id': 'integration_csv_001',
            'llm_name': 'Claude-3.5',
            'prompt': 'Create a simple web scraper for news headlines',
            'original_response': 'Here\'s a basic web scraper using requests and BeautifulSoup...',
            'rewritten_prompt': 'Create a robust web scraper for news headlines with error handling, rate limiting, and respect for robots.txt',
            'rewritten_response': 'Here\'s an improved web scraper with proper error handling...',
            'learning_memory': 'Adding specific requirements about error handling and ethics significantly improves the quality of code responses'
        }
        
        # Save to CSV
        csv_file = storage.save_to_csv('integration_test', prompt_data)
        assert csv_file
        
        # Read back and verify
        data = storage.read_from_csv('integration_test')
        assert len(data) == 1
        entry = data[0]
        
        # Verify all fields are present and correct
        assert entry['prompt_id'] == 'integration_csv_001'
        assert entry['llm_name'] == 'Claude-3.5'
        assert 'web scraper' in entry['prompt']
        assert 'robots.txt' in entry['rewritten_prompt']
        assert 'error handling' in entry['learning_memory']
        assert 'timestamp' in entry  # Auto-generated field
        
        # Test search functionality
        matches = storage.search_csv_entries('integration_test', 'scraper')
        assert len(matches) == 1
        
        matches = storage.search_csv_entries('integration_test', 'nonexistent')
        assert len(matches) == 0
        
        print("✅ CSV Integration test passed!")


if __name__ == "__main__":
    # Run a simple integration test
    test_file_storage_integration()
    test_csv_integration()
    print("✅ All basic tests passed! Run 'pytest tests/unit/test_file_storage.py -v' for detailed testing.")