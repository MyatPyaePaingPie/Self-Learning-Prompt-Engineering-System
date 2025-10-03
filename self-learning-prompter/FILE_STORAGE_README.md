# File Storage System with CSV Learning - Sequential ID System

## Overview
This document describes the enhanced file storage implementation with CSV learning functionality using a sequential ID system. The system now uses numbered IDs (001, 002, etc.) with decimal versions for rewrites (001.1, 002.1, etc.).

## What Was Implemented

### 1. Core File Storage Features
- **Save prompts** with optional metadata to `prompts/` folder
- **Save results** with optional metadata to `results/` folder  
- **Load files** from either folder
- **List files** in each directory
- **Auto-generate IDs** with timestamps if not provided

### 2. NEW: CSV Learning System with Sequential IDs

**CSV Schema with Sequential ID System:**
```csv
prompt_id,llm_name,prompt,original_response,rewritten_prompt,rewritten_response,learning_memory,timestamp
```

**Sequential ID System:**
- **New prompts**: 001, 002, 003, 004, ...
- **Rewritten prompts**: 001.1, 002.1, 003.1, ...
- **Auto-generated** based on existing entries in CSV file
- **Tracks prompt evolution** clearly with decimal versions

**Example CSV Output:**
```csv
prompt_id,llm_name,prompt,original_response,rewritten_prompt,rewritten_response,learning_memory,timestamp
001,GPT-4,"Write a function to validate email addresses","Here is a basic regex validation function...",,,Basic validation works but lacks comprehensive error handling,2025-10-03T11:21:49.615551
001.1,GPT-4,"Write a comprehensive email validation function in Python with detailed error messages, support for international domains, and unit tests","Here is a robust email validator with comprehensive testing...",,,Adding specific requirements for error handling and testing greatly improves response quality,2025-10-03T11:21:49.615796
002,Claude-3,"Create a REST API for user management","Here is a basic Flask API...",,,Simple REST API request yielded basic implementation,2025-10-03T11:21:49.615937
```

### 3. Key CSV Features

- **Sequential numbering**: Auto-generates 001, 002, 003... for new prompts
- **Rewrite tracking**: Uses .1 suffix for rewritten versions (001.1, 002.1...)
- **LLM validation**: Validates against common LLMs (GPT-4, Claude-3, Gemini-Pro, etc.)
- **Interactive input**: Step-by-step data collection with user prompts
- **Auto-append**: Multiple entries automatically append to existing CSV files
- **Search functionality**: Find entries by any field or search across all fields
- **Special character handling**: Properly escapes commas, quotes, and multiline text
- **Timestamps**: Auto-generated for tracking when entries were created

### 4. Usage Examples

**Basic CSV Usage:**
```python
from file_storage import FileStorage

storage = FileStorage()

# Save new prompt (gets ID: 001)
prompt_data = {
    'llm_name': 'GPT-4',
    'prompt': 'Write a sorting algorithm',
    'original_response': 'Here is bubble sort...',
    'learning_memory': 'Basic request yielded simple solution'
}
storage.save_to_csv('my_learning_log', prompt_data)

# Save rewrite (gets ID: 001.1)
rewrite_data = {
    'llm_name': 'GPT-4', 
    'prompt': 'Write an efficient merge sort with time complexity analysis',
    'original_response': 'Here is optimized merge sort...',
    'learning_memory': 'Specific requirements improve response quality'
}
storage.save_to_csv('my_learning_log', rewrite_data, is_rewrite=True, base_prompt_id='001')

# Read and search
entries = storage.read_from_csv('my_learning_log')
matches = storage.search_csv_entries('my_learning_log', 'sorting')
```

**Interactive Data Collection:**
```python
# Guided data collection with user prompts
data = storage.collect_prompt_data_interactive()
storage.save_to_csv('my_prompts', data)  # Gets next sequential ID
```

## How to Run & Test

### 🚀 Quick Test Guide

**Step 1: Navigate to the project**
```bash
cd self-learning-prompter
```

**Step 2: Run the demo script**
```bash
python3 file_storage.py
```

You should see sequential ID system in action:
```
📊 CSV Functionality Demo (Sequential ID System)
--------------------------------------------------
✅ Saved first prompt (ID: 001)
✅ Saved rewritten prompt (ID: 001.1)  
✅ Saved second prompt (ID: 002)

📖 Reading CSV data with sequential IDs:
Entry 1: ID 001 - GPT-4
Entry 2: ID 001.1 - GPT-4  
Entry 3: ID 002 - Claude-3
```

**Step 3: Try the CSV usage example**
```bash
python3 csv_usage_example.py
```

**Step 4: View the generated CSV**
```bash
cat my_learning_log.csv
```

### 🧪 Run Tests
```bash
# Simple integration test
python3 tests/unit/test_file_storage.py

# Full test suite (requires pytest)
pytest tests/unit/test_file_storage.py -v
```

## Sequential ID System Benefits

1. **Clear Evolution Tracking**: Easy to see prompt improvements (001 → 001.1)
2. **Organized Numbering**: Sequential IDs are cleaner than timestamps  
3. **Logical Grouping**: Related prompts grouped by base number
4. **Scalable**: Supports unlimited prompts and rewrites
5. **Human Readable**: Easy to reference specific prompts in discussions

## CSV Methods Reference

- `save_to_csv(filename, data, is_rewrite=False, base_prompt_id=None)` - Save with sequential ID
- `read_from_csv(filename)` - Read all entries  
- `search_csv_entries(filename, search_term, field=None)` - Search entries
- `collect_prompt_data_interactive()` - Interactive data collection

## Integration Examples

### For Team Components
```python
# Streamlit integration with sequential IDs
learning_data = {
    'llm_name': selected_llm,
    'prompt': user_input,
    'original_response': llm_response,
    'learning_memory': user_feedback
}
storage.save_to_csv('streamlit_learning_log', learning_data)  # Gets next ID

# API integration with rewrite tracking  
@app.post("/learn")
def save_learning_entry(entry: LearningEntry):
    is_rewrite = entry.is_rewrite
    base_id = entry.base_prompt_id if is_rewrite else None
    storage.save_to_csv('api_learning_log', entry.dict(), is_rewrite, base_id)
    return {"status": "saved", "id": "auto-generated"}
```

## Files Created

- `file_storage.py` - Enhanced with sequential ID system (450+ lines)
- `csv_usage_example.py` - Demonstrates sequential ID functionality
- `tests/unit/test_file_storage.py` - Comprehensive test suite
- `FILE_STORAGE_README.md` - This documentation

**Generated CSV Files:**
- `prompt_learning_log.csv` - Demo data with sequential IDs
- `my_learning_log.csv` - Usage example with sequential IDs

---

**Sequential ID System**: ✅ Implemented  
**Status**: Complete and Ready for Use  
**Author**: Enhanced File Storage System