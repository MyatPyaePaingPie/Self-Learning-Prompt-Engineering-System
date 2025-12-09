"""Authentication page - Login and Registration UI"""
import streamlit as st
import time
from auth_client import show_password_strength
from utils.session import show_page_header


def show_login_page():
    """Display enhanced login/register page."""
    show_page_header()
    
    # Add security notice
    st.info("🛡️ **Security Notice**: All communications are encrypted end-to-end using TLS/SSL and application-layer encryption.")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        
        # Rate limiting warning
        if st.session_state.login_attempts >= 3:
            st.error("⚠️ Too many failed login attempts. Please wait before trying again.")
            st.stop()
        
        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_login = st.form_submit_button("🚀 Login", type="primary")
            
            if submit_login and username and password:
                with st.spinner("Authenticating securely..."):
                    result = st.session_state.auth_client.login(username, password)
                    
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.access_token = result["token"]
                    st.session_state.login_attempts = 0  # Reset attempts
                    st.session_state.last_activity = time.time()
                    st.success("✅ Login successful! Redirecting to Prompt Enhancement...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 3 - st.session_state.login_attempts
                    st.error(f"❌ Login failed: {result['error']}")
                    if remaining > 0:
                        st.warning(f"⚠️ {remaining} attempts remaining")
    
    with tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                reg_username = st.text_input(
                    "Username",
                    key="reg_username",
                    help="3-50 characters: letters, numbers, hyphens, underscores only"
                )
                reg_email = st.text_input("Email Address", key="reg_email")
            
            with col2:
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            
            # Show real-time password strength
            if reg_password:
                show_password_strength(reg_password)
                
            submit_register = st.form_submit_button("🎯 Create Account", type="primary")
            
            if submit_register:
                if not all([reg_username, reg_email, reg_password, reg_password_confirm]):
                    st.error("❌ Please fill in all fields")
                elif reg_password != reg_password_confirm:
                    st.error("❌ Passwords don't match")
                else:
                    # Validate password strength
                    password_check = st.session_state.auth_client.validate_password_strength(reg_password)
                    if not password_check["valid"]:
                        st.error("❌ Password does not meet security requirements:")
                        for error in password_check["errors"]:
                            st.error(f"• {error}")
                    else:
                        with st.spinner("Creating secure account..."):
                            result = st.session_state.auth_client.register(reg_username, reg_email, reg_password)
                        
                        if result["success"]:
                            st.success("✅ Registration successful! Please login with your credentials.")
                            st.balloons()
                        else:
                            st.error(f"❌ Registration failed: {result['error']}")


