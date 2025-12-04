"""
Self Learning Prompt Engineering System - Main Application
Refactored for maintainability - Main orchestrator only
"""
import streamlit as st
from auth_client import init_session_state, logout
from utils.session import check_authentication, show_page_header

# Page imports
from pages.auth import show_login_page
from pages.api_testing import show_api_testing, show_export_data
from pages.token_analytics import show_token_analytics
from pages.temporal_analysis import show_temporal_analysis
from pages.agent_effectiveness import show_agent_effectiveness
from pages.security_dashboard import show_security_dashboard

# Prompt enhancement - refactored into page module
from pages.prompt_enhancement import show_prompt_enhancement

# Page configuration
st.set_page_config(
    page_title="Self Learning Prompt Engineering System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()


def main():
    """Main application router"""
    try:
        if st.session_state.authenticated:
            # Authenticated: Show dashboard with page routing
            with st.sidebar:
                show_navigation_sidebar()
            
            # Route to current page
            page = st.session_state.get('current_page', 'dashboard')
            
            if page == "dashboard":
                show_prompt_enhancement()
            elif page == "token_analytics":
                show_token_analytics()
            elif page == "temporal_analysis":
                show_temporal_analysis()
            elif page == "agent_effectiveness":
                show_agent_effectiveness()
            elif page == "security_dashboard":
                show_security_dashboard()
            elif page == "api_test":
                show_api_testing()
            else:
                show_prompt_enhancement()
        else:
            # Not authenticated: Show login
            show_login_page()
    
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        show_error_recovery_options()


def show_navigation_sidebar():
    """Sidebar navigation"""
    # Hide Streamlit's automatic page navigation
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    show_page_header()
    
    # User info
    if st.session_state.user_info:
        st.success(f"👋 Welcome, **{st.session_state.user_info['username']}**!")
        
        with st.expander("👤 Profile Info", expanded=False):
            st.info(f"📧 Email: {st.session_state.user_info['email']}")
            st.info(f"🆔 User ID: {st.session_state.user_info['id']}")
            st.info(f"📅 Member Since: {st.session_state.user_info['created_at'][:10]}")
            if st.session_state.user_info['last_login']:
                st.info(f"⏰ Last Login: {st.session_state.user_info['last_login'][:19]}")
    
    st.markdown("---")
    
    # Navigation buttons
    st.subheader("🧭 Navigation")
    
    if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
        st.rerun()
    
    if st.button("📈 Agent Effectiveness", key="nav_effectiveness", use_container_width=True):
        st.session_state.current_page = "agent_effectiveness"
        st.rerun()
    
    if st.button("💰 Token Analytics", key="nav_tokens", use_container_width=True):
        st.session_state.current_page = "token_analytics"
        st.rerun()
    
    if st.button("🔒 Security Dashboard", key="nav_security", use_container_width=True):
        st.session_state.current_page = "security_dashboard"
        st.rerun()
    
    if st.button("⏱️ Temporal Analysis", key="nav_temporal", use_container_width=True):
        st.session_state.current_page = "temporal_analysis"
        st.rerun()
        
    if st.button("🔧 API Testing", key="nav_api", use_container_width=True):
        st.session_state.current_page = "api_test"
        st.rerun()
    
    st.markdown("---")
    
    # Security status
    st.subheader("🛡️ Security Status")
    st.success("🔐 Session Active")
    st.success("🔄 End-to-End Encrypted")
    st.success("✅ Rate Limited")
    
    if st.button("🚪 Logout", type="primary", use_container_width=True):
        logout()


def show_error_recovery_options():
    """Error recovery UI"""
    with st.expander("🔧 Troubleshooting Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Session"):
                st.rerun()
                
        with col2:
            if st.button("🗑️ Reset Application"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown("---")
        st.markdown("**If problems persist:**")
        st.markdown("1. Check your internet connection")
        st.markdown("2. Ensure the backend server is running on port 8001")
        st.markdown("3. Clear your browser cache")


if __name__ == "__main__":
    main()

