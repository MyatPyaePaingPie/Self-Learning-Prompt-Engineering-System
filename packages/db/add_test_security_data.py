#!/usr/bin/env python3
"""
Add test security input data for dashboard testing
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from packages.db.session import get_session
from packages.db.crud import create_security_input_row
from datetime import datetime

def add_test_data():
    """Add sample security inputs for testing"""
    test_inputs = [
        {
            "user_id": "test_user_1",
            "input_text": "This is a safe prompt about Python programming",
            "risk_score": 15.0,
            "label": "safe",
            "is_blocked": False,
            "analysis_metadata": {"reason": "Normal prompt", "category": "programming"}
        },
        {
            "user_id": "test_user_2",
            "input_text": "How to hack into a system?",
            "risk_score": 85.0,
            "label": "high-risk",
            "is_blocked": True,
            "analysis_metadata": {"reason": "Suspicious hacking attempt", "category": "security"}
        },
        {
            "user_id": "test_user_3",
            "input_text": "Generate code to delete all files",
            "risk_score": 75.0,
            "label": "high-risk",
            "is_blocked": True,
            "analysis_metadata": {"reason": "Destructive operation", "category": "dangerous"}
        },
        {
            "user_id": "test_user_1",
            "input_text": "Explain machine learning concepts",
            "risk_score": 25.0,
            "label": "low-risk",
            "is_blocked": False,
            "analysis_metadata": {"reason": "Educational content", "category": "learning"}
        },
        {
            "user_id": "test_user_4",
            "input_text": "Create a script to access private data",
            "risk_score": 65.0,
            "label": "medium-risk",
            "is_blocked": False,
            "analysis_metadata": {"reason": "Privacy concern", "category": "privacy"}
        },
        {
            "user_id": "test_user_2",
            "input_text": "Help me write a sorting algorithm",
            "risk_score": 10.0,
            "label": "safe",
            "is_blocked": False,
            "analysis_metadata": {"reason": "Normal coding request", "category": "programming"}
        },
    ]
    
    with get_session() as s:
        count = 0
        for test_input in test_inputs:
            try:
                create_security_input_row(
                    s,
                    test_input["user_id"],
                    test_input["input_text"],
                    test_input["risk_score"],
                    test_input["label"],
                    test_input["is_blocked"],
                    test_input["analysis_metadata"]
                )
                count += 1
            except Exception as e:
                print(f"Error adding test input: {e}")
        
        s.commit()
        print(f"✅ Added {count} test security inputs")
        return count

if __name__ == "__main__":
    add_test_data()

