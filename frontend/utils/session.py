"""Session state management utilities"""
import streamlit as st
import time


def check_authentication() -> bool:
    """
    Check if user is authenticated and session is valid
    
    Returns:
        True if authenticated, False otherwise (triggers logout)
    """
    if not st.session_state.get('authenticated', False):
        return False
    
    # Check session timeout (30 minutes)
    if 'last_activity' in st.session_state:
        elapsed = time.time() - st.session_state.last_activity
        if elapsed > 1800:  # 30 minutes in seconds
            st.warning("⚠️ Session expired. Please login again.")
            st.session_state.authenticated = False
            return False
    
    # Update last activity
    st.session_state.last_activity = time.time()
    return True


def show_page_header():
    """Show the main page header (reusable across pages)"""
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🤖 Self Learning Prompt Engineering System</h1>
        <p style='color: white; margin: 0; opacity: 0.9;'>Advanced AI Prompt Optimization with Secure Authentication</p>
    </div>
    """, unsafe_allow_html=True)


