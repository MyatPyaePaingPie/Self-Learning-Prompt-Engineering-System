"""Feedback component - Handle user feedback submission"""
import streamlit as st
from utils.api_client import api_post


def submit_feedback(request_id: str, user_choice: str, judge_winner: str, agent_winner: str) -> bool:
    """
    Submit user feedback to backend
    
    Args:
        request_id: Unique request identifier
        user_choice: User's choice (original/single/multi)
        judge_winner: Judge's selected agent
        agent_winner: Winning agent name
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = api_post(
            "/prompts/feedback",
            json_data={
                "request_id": request_id,
                "user_choice": user_choice,
                "judge_winner": judge_winner,
                "agent_winner": agent_winner
            }
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to submit feedback: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")
        return False


