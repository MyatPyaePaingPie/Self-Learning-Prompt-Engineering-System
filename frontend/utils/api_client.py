"""Centralized API client for backend communication"""
import requests
import streamlit as st
from typing import Dict, Any, Optional

# Single source of truth for API base URL
API_BASE = "http://localhost:8001"


def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers with current session token"""
    if 'access_token' not in st.session_state:
        return {}
    return {"Authorization": f"Bearer {st.session_state.access_token}"}


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    """
    Make authenticated GET request to backend API
    
    Args:
        endpoint: API endpoint path (e.g., "/api/tokens")
        params: Optional query parameters
    
    Returns:
        requests.Response object
    """
    url = f"{API_BASE}{endpoint}"
    return requests.get(url, headers=get_auth_headers(), params=params or {})


def api_post(endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
    """
    Make authenticated POST request to backend API
    
    Args:
        endpoint: API endpoint path (e.g., "/prompts/multi-agent-enhance")
        json_data: Optional JSON payload
    
    Returns:
        requests.Response object
    """
    url = f"{API_BASE}{endpoint}"
    return requests.post(url, headers=get_auth_headers(), json=json_data or {})

