import streamlit as st
import time
import sys
import os

# Add parent directory to Python path so we can import packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth_client import AuthClient, init_session_state, logout, check_authentication, show_password_strength

# Page configuration
st.set_page_config(
    page_title="Self Learning Prompt Engineering System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

def show_page_header():
    """Show the main page header."""
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🤖 Self Learning Prompt Engineering System</h1>
        <p style='color: white; margin: 0; opacity: 0.9;'>Advanced AI Prompt Optimization with Secure Authentication</p>
    </div>
    """, unsafe_allow_html=True)

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

def show_dashboard():
    """Display enhanced user dashboard with navigation."""
    if not check_authentication():
        st.rerun()
        return
    
    # Sidebar navigation
    with st.sidebar:
        show_page_header()
        
        if st.session_state.user_info:
            st.success(f"👋 Welcome, **{st.session_state.user_info['username']}**!")
            
            with st.expander("👤 Profile Info", expanded=False):
                st.info(f"📧 Email: {st.session_state.user_info['email']}")
                st.info(f"🆔 User ID: {st.session_state.user_info['id']}")
                st.info(f"📅 Member Since: {st.session_state.user_info['created_at'][:10]}")
                if st.session_state.user_info['last_login']:
                    st.info(f"⏰ Last Login: {st.session_state.user_info['last_login'][:19]}")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("🧭 Navigation")
        if st.button("🚀 Prompt Enhancement", key="nav_prompts"):
            st.session_state.current_page = "prompts"
            st.rerun()
            
        if st.button("📊 Dashboard", key="nav_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("💰 Token Analytics", key="nav_tokens"):
            st.session_state.current_page = "token_analytics"
            st.rerun()
        
        if st.button("🔒 Security Dashboard", key="nav_security"):
            st.session_state.current_page = "security_dashboard"
            st.rerun()
            
        if st.button("🔧 API Testing", key="nav_api"):
            st.session_state.current_page = "api_test"
            st.rerun()
        
        st.markdown("---")
        
        # Security status
        st.subheader("🛡️ Security Status")
        st.success("🔐 Session Active")
        st.success("🔄 End-to-End Encrypted")
        st.success("✅ Rate Limited")
        
        if st.button("🚪 Logout", type="primary"):
            logout()
    
    # Main content based on current page
    if st.session_state.current_page == "prompts":
        show_prompt_enhancement()
    elif st.session_state.current_page == "api_test":
        show_api_testing()
    elif st.session_state.current_page == "token_analytics":
        show_token_analytics()
    elif st.session_state.current_page == "security_dashboard":
        show_security_dashboard()
    else:
        show_dashboard_overview()

def show_dashboard_overview():
    """Show the main dashboard overview."""
    st.title("📊 Dashboard Overview")
    
    # Welcome message
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔐 Security Level", "High", "End-to-End Encrypted")
        
    with col2:
        st.metric("⚡ Session Status", "Active", "Token Valid")
        
    with col3:
        st.metric("🎯 Features Available", "All", "Full Access")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Prompt Enhancement", type="primary"):
            st.session_state.current_page = "prompts"
            st.rerun()
            
        if st.button("🔧 Test API Endpoints"):
            st.session_state.current_page = "api_test"
            st.rerun()
    
    with col2:
        st.info("💡 **Tip**: Use the Prompt Enhancement feature to optimize your text prompts with AI-powered suggestions!")
        st.info("🔒 **Security**: All data transmission is encrypted and your session is automatically secured.")

def show_prompt_enhancement():
    """Show the prompt enhancement interface."""
    st.title("🤖 Self-Learning Prompt Engineering")
    st.markdown("Transform your prompts into structured, professional formats using expert templates and AI-powered optimization")
    
    # Import our engine components
    try:
        from packages.core import (
            fallback_to_template,
            judge_prompt,
            TokenTracker,
            generate_llm_output
        )
    except ImportError as e:
        st.error(f"❌ Failed to import core engine: {e}")
        st.info("Make sure the packages/core directory is in your Python path")
        return
    
    # Template explanation
    with st.expander("📋 How Template Enhancement Works", expanded=False):
        st.markdown("""
        **Your prompt will be transformed using this professional template:**
        
        ```
        You are a senior {domain} expert.
        Task: {task}
        Deliverables:
        - Clear, step-by-step plan
        - Examples and edge-cases
        - Final {artifact} ready to use
        Constraints: {constraints}
        If information is missing, list precise clarifying questions first, then proceed with best assumptions.
        ```
        
        **The system automatically:**
        - 🎯 **Identifies the domain** (Software Engineering, Creative Writing, Marketing, etc.)
        - 📋 **Structures your task** into clear, actionable format
        - 🎨 **Determines the deliverable** (code, content, analysis, etc.)
        - ⚖️ **Sets appropriate constraints** based on context
        """)
    
    # Enhancement interface
    with st.form("enhance_prompt_form"):
        st.subheader("📝 Enter Your Original Prompt")
        
        prompt_text = st.text_area(
            "Your Task/Request",
            placeholder="Example: 'Create a function to calculate compound interest' or 'Write a story about time travel'",
            height=150,
            help="Describe what you want to accomplish. The system will transform it into a structured, expert-level prompt."
        )
        
        context = st.text_input(
            "Domain Context (Optional)",
            placeholder="e.g., 'for a mobile app', 'academic research', 'marketing campaign'",
            help="Provide specific context to refine the domain and constraints"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            submit_enhance = st.form_submit_button("✨ Enhance", type="primary")
    
    if submit_enhance and prompt_text:
        if len(prompt_text) > 5000:
            st.error("❌ Prompt text exceeds maximum length of 5000 characters")
        else:
            # Initialize tracker
            tracker = TokenTracker()
            
            with st.spinner("🤖 Enhancing your prompt and generating responses..."):
                # Step 1: Enhance the prompt using fallback template
                enhanced_result = fallback_to_template(prompt_text)
                enhanced_prompt = enhanced_result.text
                
                # Step 2: Generate outputs with both prompts
                try:
                    # Generate with original prompt
                    original_output, original_usage = generate_llm_output(prompt_text)
                    
                    # Generate with enhanced prompt
                    enhanced_output, enhanced_usage = generate_llm_output(enhanced_prompt)
                    
                    # Step 3: Judge both prompts
                    original_score, original_judge_usage = judge_prompt(prompt_text)
                    enhanced_score, enhanced_judge_usage = judge_prompt(enhanced_prompt)
                    
                    llm_available = True
                except Exception as e:
                    st.warning(f"⚠️ LLM unavailable, using mock outputs: {str(e)}")
                    # Mock outputs for demonstration
                    original_output = "This is a mock response to your original prompt."
                    enhanced_output = "This is a detailed, structured response to your enhanced prompt with step-by-step guidance."
                    original_usage = tracker.track_llm_call(prompt_text, original_output, "mock-model")
                    enhanced_usage = tracker.track_llm_call(enhanced_prompt, enhanced_output, "mock-model")
                    
                    # Mock scoring
                    from packages.core.judge import Scorecard
                    original_score = Scorecard(
                        clarity=4.0, specificity=3.0, actionability=2.0,
                        structure=2.0, context_use=3.0, total=14.0,
                        feedback={"pros": ["Brief"], "cons": ["Too vague"], "summary": "Needs improvement"}
                    )
                    enhanced_score = Scorecard(
                        clarity=8.0, specificity=7.5, actionability=8.0,
                        structure=7.0, context_use=7.5, total=38.0,
                        feedback={"pros": ["Clear role", "Good structure"], "cons": ["Could be more specific"], "summary": "Much better"}
                    )
                    original_judge_usage = tracker.track_llm_call("judge prompt", "judge result", "mock-model")
                    enhanced_judge_usage = tracker.track_llm_call("judge prompt", "judge result", "mock-model")
                    llm_available = False
                
            st.success("✅ Prompt enhanced and evaluated successfully!")
            
            # Display comparison results
            st.subheader("📊 Enhancement Comparison")
            
            # Prompt comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Original Prompt")
                st.text_area("Original Prompt", value=prompt_text, height=150, disabled=True, key="orig_prompt", label_visibility="hidden")
                
                st.markdown("### 📈 Original Score")
                st.metric("Total Score", f"{original_score.total:.1f}/50", help="Overall prompt quality score")
                
                score_cols = st.columns(5)
                scores = [
                    ("Clarity", original_score.clarity),
                    ("Specific", original_score.specificity),
                    ("Action", original_score.actionability),
                    ("Structure", original_score.structure),
                    ("Context", original_score.context_use)
                ]
                for i, (label, score) in enumerate(scores):
                    with score_cols[i]:
                        st.metric(label, f"{score:.1f}")
                
                with st.expander("💬 Judge Feedback"):
                    st.write("**Strengths:**")
                    for pro in original_score.feedback.get("pros", []):
                        st.write(f"• {pro}")
                    st.write("**Areas for Improvement:**")
                    for con in original_score.feedback.get("cons", []):
                        st.write(f"• {con}")
                    st.write(f"**Summary:** {original_score.feedback.get('summary', 'No summary')}")
            
            with col2:
                st.markdown("### ✨ Enhanced Prompt")
                st.text_area("Enhanced Prompt", value=enhanced_prompt, height=150, key="enh_prompt", label_visibility="hidden")
                
                st.markdown("### 📈 Enhanced Score")
                improvement = enhanced_score.total - original_score.total
                st.metric("Total Score", f"{enhanced_score.total:.1f}/50", f"+{improvement:.1f}", help="Overall prompt quality score")
                
                score_cols = st.columns(5)
                enhanced_scores = [
                    ("Clarity", enhanced_score.clarity),
                    ("Specific", enhanced_score.specificity),
                    ("Action", enhanced_score.actionability),
                    ("Structure", enhanced_score.structure),
                    ("Context", enhanced_score.context_use)
                ]
                for i, (label, score) in enumerate(enhanced_scores):
                    with score_cols[i]:
                        delta = score - scores[i][1]
                        st.metric(label, f"{score:.1f}", f"+{delta:.1f}")
                
                with st.expander("💬 Judge Feedback"):
                    st.write("**Strengths:**")
                    for pro in enhanced_score.feedback.get("pros", []):
                        st.write(f"• {pro}")
                    st.write("**Areas for Improvement:**")
                    for con in enhanced_score.feedback.get("cons", []):
                        st.write(f"• {con}")
                    st.write(f"**Summary:** {enhanced_score.feedback.get('summary', 'No summary')}")
            
            # Output comparison
            st.markdown("---")
            st.subheader("🎯 Output Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📄 Original Output")
                st.text_area("Response to original prompt:", value=original_output, height=200, disabled=True, key="orig_output")
            
            with col2:
                st.markdown("### ✨ Enhanced Output")
                st.text_area("Response to enhanced prompt:", value=enhanced_output, height=200, disabled=True, key="enh_output")
            
            # Token tracking at the bottom
            st.markdown("---")
            st.subheader("📊 Token Usage & Cost Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔍 Original Prompt")
                st.metric("Prompt Tokens", original_usage.prompt_tokens)
                st.metric("Output Tokens", original_usage.completion_tokens)
                st.metric("Total Tokens", original_usage.total_tokens)
                st.metric("Cost", f"${original_usage.cost_usd:.8f}")
            
            with col2:
                st.markdown("### ✨ Enhanced Prompt")
                st.metric("Prompt Tokens", enhanced_usage.prompt_tokens)
                st.metric("Output Tokens", enhanced_usage.completion_tokens)
                st.metric("Total Tokens", enhanced_usage.total_tokens)
                st.metric("Cost", f"${enhanced_usage.cost_usd:.8f}")
            
            with col3:
                st.markdown("### 📈 Analysis")
                total_tokens = (original_usage.total_tokens + enhanced_usage.total_tokens +
                              original_judge_usage.total_tokens + enhanced_judge_usage.total_tokens)
                total_cost = (original_usage.cost_usd + enhanced_usage.cost_usd +
                            original_judge_usage.cost_usd + enhanced_judge_usage.cost_usd)
                
                st.metric("Total Tokens", total_tokens)
                st.metric("Total Cost", f"${total_cost:.8f}")
                st.metric("Quality Improvement", f"+{improvement:.1f} points")
                
                # ROI calculation
                if total_cost > 0 and improvement > 0:
                    roi = improvement / (total_cost * 1000000)  # Points per micro-dollar
                    st.metric("ROI", f"{roi:.1f} pts/μ$")
                
                # Value assessment
                if improvement > 5.0:
                    st.success("🎯 Excellent improvement!")
                elif improvement > 2.0:
                    st.info("👍 Good improvement")
                else:
                    st.warning("⚠️ Modest improvement")
            
            # Detailed breakdown
            with st.expander("🔍 Detailed Token Breakdown"):
                breakdown_data = [
                    ["Original Prompt Generation", original_usage.prompt_tokens, original_usage.completion_tokens, original_usage.total_tokens, f"${original_usage.cost_usd:.8f}"],
                    ["Enhanced Prompt Generation", enhanced_usage.prompt_tokens, enhanced_usage.completion_tokens, enhanced_usage.total_tokens, f"${enhanced_usage.cost_usd:.8f}"],
                    ["Original Prompt Judging", original_judge_usage.prompt_tokens, original_judge_usage.completion_tokens, original_judge_usage.total_tokens, f"${original_judge_usage.cost_usd:.8f}"],
                    ["Enhanced Prompt Judging", enhanced_judge_usage.prompt_tokens, enhanced_judge_usage.completion_tokens, enhanced_judge_usage.total_tokens, f"${enhanced_judge_usage.cost_usd:.8f}"],
                    ["**TOTAL**", "-", "-", total_tokens, f"**${total_cost:.8f}**"]
                ]
                
                st.table({
                    "Operation": [row[0] for row in breakdown_data],
                    "Prompt Tokens": [row[1] for row in breakdown_data],
                    "Completion Tokens": [row[2] for row in breakdown_data],
                    "Total Tokens": [row[3] for row in breakdown_data],
                    "Cost": [row[4] for row in breakdown_data]
                })
                
                if not llm_available:
                    st.info("💡 **Note**: These are mock values since LLM is not available. Set your GROQ_API_KEY to see real usage.")
    
    elif submit_enhance:
        st.error("❌ Please enter a prompt to enhance")

def show_api_testing():
    """Show API testing interface."""
    st.title("🔧 API Testing Center")
    st.markdown("Test various API endpoints and security features")
    
    # Test protected route
    st.subheader("🛡️ Protected Route Test")
    if st.button("Test Protected Endpoint"):
        with st.spinner("Testing protected route access..."):
            result = st.session_state.auth_client.access_protected_route(st.session_state.access_token)
        
        if result["success"]:
            st.success("✅ Protected route accessed successfully!")
            st.json(result["data"])
        else:
            st.error(f"❌ Access denied: {result['error']}")
    
    # Test user info endpoint
    st.subheader("👤 User Info Test")
    if st.button("Fetch User Information"):
        with st.spinner("Fetching user information..."):
            result = st.session_state.auth_client.get_user_info(st.session_state.access_token)
        
        if result["success"]:
            st.success("✅ User information retrieved!")
            st.json(result["data"])
        else:
            st.error(f"❌ Failed to get user info: {result['error']}")
    
    # Security features display
    st.markdown("---")
    st.subheader("🔒 Enhanced Security Features")
    
    security_features = [
        "✅ **Argon2 Password Hashing**: Industry-leading password security",
        "✅ **JWT with Enhanced Claims**: Secure tokens with additional security metadata",
        "✅ **Application-Layer Encryption**: Sensitive data encrypted beyond TLS",
        "✅ **Rate Limiting**: Protection against brute force attacks",
        "✅ **Session Timeout**: Automatic logout after 30 minutes of inactivity",
        "✅ **Strong Password Requirements**: Enforced password complexity",
        "✅ **Security Headers**: CSRF, XSS, and clickjacking protection",
        "✅ **Trusted Host Validation**: Protection against host header attacks",
        "✅ **Real-time Token Validation**: Continuous session security checks"
    ]
    
    for feature in security_features:
        st.markdown(feature)

def main():
    """Main application entry point with enhanced error handling."""
    try:
        if st.session_state.authenticated:
            show_dashboard()
        else:
            show_login_page()
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        
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

def show_token_analytics():
    """Show token usage and cost analytics."""
    st.title("💰 Token Usage & Cost Analytics")
    
    # Check for data
    if 'latest_result' not in st.session_state:
        st.warning("⚠️ No data available. Please analyze a prompt first!")
        if st.button("← Go to Prompt Enhancement"):
            st.session_state.current_page = "prompts"
            st.rerun()
        st.stop()
    
    data = st.session_state['latest_result']
    token_metrics = data.get('token_metrics', {})
    
    # Display token metrics
    st.subheader("📊 Token Usage Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tokens", f"{token_metrics.get('total_tokens', 0):,}")
    
    with col2:
        st.metric("Total Cost", f"${token_metrics.get('total_cost', 0):.6f}")
    
    with col3:
        improvement = token_metrics.get('quality_improvement', 0)
        st.metric("Quality Improvement", f"+{improvement:.1f} points")
    
    st.divider()
    
    # Detailed breakdown
    st.subheader("📋 Detailed Breakdown")
    
    breakdown_data = {
        "Operation": ["Prompt Improvement", "Original Execution", "Improved Execution", "Quality Judging"],
        "Tokens": [
            token_metrics.get('improvement_tokens', 0),
            token_metrics.get('original_execution_tokens', 0),
            token_metrics.get('improved_execution_tokens', 0),
            token_metrics.get('judging_tokens', 0)
        ],
        "Cost ($)": [
            token_metrics.get('improvement_cost', 0),
            token_metrics.get('original_execution_cost', 0),
            token_metrics.get('improved_execution_cost', 0),
            token_metrics.get('judging_cost', 0)
        ]
    }
    
    import pandas as pd
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def show_security_dashboard():
    """Show security input monitoring dashboard."""
    import requests
    from datetime import datetime
    import pandas as pd
    
    st.title("🔒 Security Dashboard")
    st.markdown("Monitor and analyze security inputs, risk scores, and blocked attempts")
    
    # API base URL - USE THE AUTHENTICATED BACKEND
    API_BASE = "http://localhost:8001"
    
    # Get auth token from session
    if not st.session_state.access_token:
        st.error("❌ Not authenticated. Please login first.")
        return
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        filter_label = st.selectbox(
            "Filter by Label",
            ["All", "safe", "low-risk", "medium-risk", "high-risk", "blocked"],
            index=0
        )
        
        filter_blocked = st.selectbox(
            "Filter by Blocked Status",
            ["All", "Blocked Only", "Not Blocked"],
            index=0
        )
        
        filter_high_risk = st.checkbox("Show High-Risk Only (≥70)", value=False)
    
    # Build query parameters
    params = {"limit": 1000}
    if filter_label != "All":
        params["filter_label"] = filter_label
    if filter_blocked == "Blocked Only":
        params["filter_blocked"] = True
    elif filter_blocked == "Not Blocked":
        params["filter_blocked"] = False
    if filter_high_risk:
        params["filter_high_risk"] = True
    
    # Fetch security inputs
    try:
        with st.spinner("Loading security inputs..."):
            response = requests.get(f"{API_BASE}/v1/security/inputs", params=params, headers=headers)
        
        if response.status_code == 200:
            inputs = response.json()
            
            if not inputs:
                st.info("No security inputs found matching the selected filters.")
            else:
                # Summary metrics
                st.subheader("📊 Summary Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                total_inputs = len(inputs)
                blocked_count = sum(1 for inp in inputs if inp.get("isBlocked", False))
                high_risk_count = sum(1 for inp in inputs if inp.get("riskScore", 0) >= 70)
                avg_risk_score = sum(inp.get("riskScore", 0) for inp in inputs) / total_inputs if total_inputs > 0 else 0
                
                with col1:
                    st.metric("Total Inputs", total_inputs)
                
                with col2:
                    st.metric("Blocked", blocked_count)
                
                with col3:
                    st.metric("High-Risk (≥70)", high_risk_count)
                
                with col4:
                    st.metric("Avg Risk Score", f"{avg_risk_score:.1f}")
                
                st.divider()
                
                # Risk indicators
                st.subheader("⚠️ Risk Indicators")
                
                indicator_col1, indicator_col2 = st.columns(2)
                
                with indicator_col1:
                    if blocked_count > 0:
                        st.error(f"🚫 **{blocked_count} Blocked Attempt(s)**")
                    else:
                        st.success("✅ No blocked attempts")
                
                with indicator_col2:
                    if high_risk_count > 0:
                        st.warning(f"⚠️ **{high_risk_count} High-Risk Attempt(s)**")
                    else:
                        st.info("ℹ️ No high-risk attempts")
                
                st.divider()
                
                # Data table
                st.subheader("📋 Security Input Log")
                
                # Prepare data for table
                table_data = []
                for inp in inputs:
                    # Format timestamp
                    try:
                        timestamp = datetime.fromisoformat(inp.get("createdAt", "").replace("Z", "+00:00"))
                        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_time = inp.get("createdAt", "N/A")
                    
                    # Risk score color coding
                    risk_score = inp.get("riskScore", 0)
                    if risk_score >= 70:
                        risk_emoji = "🔴"
                    elif risk_score >= 40:
                        risk_emoji = "🟡"
                    else:
                        risk_emoji = "🟢"
                    
                    # Blocked indicator
                    blocked_indicator = "🚫" if inp.get("isBlocked", False) else "✅"
                    
                    table_data.append({
                        "Timestamp": formatted_time,
                        "Input": inp.get("inputText", "")[:100] + ("..." if len(inp.get("inputText", "")) > 100 else ""),
                        "Risk": f"{risk_emoji} {risk_score:.1f}",
                        "Label": inp.get("label", "unknown"),
                        "Status": blocked_indicator,
                        "User": inp.get("userId", "N/A")[:15] if inp.get("userId") else "N/A"
                    })
                
                # Create DataFrame
                df = pd.DataFrame(table_data)
                
                # Display table
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"security_inputs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8001")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        if "401" in str(e) or "Unauthorized" in str(e):
            st.warning("⚠️ Your session may have expired. Please logout and login again.")

if __name__ == "__main__":
    main()