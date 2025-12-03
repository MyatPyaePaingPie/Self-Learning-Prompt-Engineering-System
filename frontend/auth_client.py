import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import os
import re
from dotenv import load_dotenv

load_dotenv()

class AuthClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8001")
        self.session = requests.Session()
        # Add security headers to all requests
        self.session.headers.update({
            'User-Agent': 'SecureAuthClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength on the frontend - simplified requirements."""
        errors = []
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        if not re.search(r"[A-Za-z]", password):
            errors.append("Password must contain at least one letter")
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength - simplified scoring."""
        score = 0
        if len(password) >= 6: score += 1
        if len(password) >= 10: score += 1
        if re.search(r"[A-Z]", password): score += 1
        if re.search(r"[a-z]", password): score += 1
        if re.search(r"\d", password): score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1
        
        if score < 2: return "Weak"
        elif score < 4: return "Medium"
        else: return "Strong"
        
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        try:
            response = self.session.post(
                f"{self.base_url}/register",
                json={"username": username, "email": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "Registration failed")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and get access token."""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                token_data = response.json()
                return {"success": True, "token": token_data["access_token"], "expires_in": token_data["expires_in"]}
            else:
                return {"success": False, "error": response.json().get("detail", "Login failed")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get current user information."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/me",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to get user info")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def access_protected_route(self, token: str) -> Dict[str, Any]:
        """Access a protected route as an example."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/protected",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "Access denied")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def enhance_prompt(self, text: str, enhancement_type: str, context: str = None, token: str = None) -> Dict[str, Any]:
        """Enhance a text prompt using AI optimization."""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            data = {
                "text": text,
                "enhancement_type": enhancement_type
            }
            if context:
                data["context"] = context
                
            response = self.session.post(
                f"{self.base_url}/prompts/enhance",
                json=data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()["data"]}
            else:
                return {"success": False, "error": response.json().get("detail", "Enhancement failed")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def save_prompt(self, text: str, category: str = None, tags: List[str] = None, token: str = None) -> Dict[str, Any]:
        """Save a prompt to the user's collection."""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            data = {
                "text": text,
                "category": category,
                "tags": tags or []
            }
                
            response = self.session.post(
                f"{self.base_url}/prompts/save",
                json=data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()["data"]}
            else:
                return {"success": False, "error": response.json().get("detail", "Save failed")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_my_prompts(self, token: str) -> Dict[str, Any]:
        """Get user's saved prompts."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/prompts/my-prompts",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()["data"]}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to fetch prompts")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'auth_client' not in st.session_state:
        st.session_state.auth_client = AuthClient()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = None

def logout():
    """Logout user and clear session state."""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.current_page = "dashboard"
    st.session_state.login_attempts = 0
    st.session_state.last_activity = None
    st.success("Logged out successfully!")
    st.rerun()

def check_authentication() -> bool:
    """Check if user is authenticated and token is valid."""
    if not st.session_state.authenticated or not st.session_state.access_token:
        return False
    
    # Check for session timeout (30 minutes of inactivity)
    import time
    current_time = time.time()
    if st.session_state.last_activity:
        if current_time - st.session_state.last_activity > 1800:  # 30 minutes
            st.warning("Session expired due to inactivity. Please log in again.")
            logout()
            return False
    
    # Update last activity
    st.session_state.last_activity = current_time
    
    # Verify token is still valid by checking user info
    result = st.session_state.auth_client.get_user_info(st.session_state.access_token)
    if result["success"]:
        st.session_state.user_info = result["data"]
        return True
    else:
        # Token expired or invalid, logout user
        st.error("Session expired. Please log in again.")
        logout()
        return False

def show_password_strength(password: str):
    """Display password strength indicator."""
    if not password:
        return
        
    validation = st.session_state.auth_client.validate_password_strength(password)
    
    # Color coding for strength
    colors = {"Weak": "🔴", "Medium": "🟡", "Strong": "🟢"}
    strength_color = colors.get(validation["strength"], "⚪")
    
    st.write(f"Password Strength: {strength_color} {validation['strength']}")
    
    if not validation["valid"]:
        with st.expander("Password Requirements"):
            for error in validation["errors"]:
                st.write(f"❌ {error}")
            st.write("✅ Requirements met: " + str(3 - len(validation["errors"])) + "/3")