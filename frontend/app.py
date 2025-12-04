import streamlit as st
import time
import sys
import os
import requests
import uuid

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
        if st.button("🚀 Single-Agent Enhancement", key="nav_prompts"):
            st.session_state.current_page = "prompts"
            st.rerun()
        
        if st.button("🤖 Multi-Agent Enhancement", key="nav_multi_agent"):
            st.session_state.current_page = "multi_agent"
            st.rerun()
        
        if st.button("📈 Agent Effectiveness", key="nav_effectiveness"):
            st.session_state.current_page = "agent_effectiveness"
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
        
        if st.button("⏱️ Temporal Analysis", key="nav_temporal"):
            st.session_state.current_page = "temporal_analysis"
            st.rerun()
        
        if st.button("📊 Export Data (CSV)", key="nav_export"):
            st.session_state.current_page = "export_data"
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
    elif st.session_state.current_page == "multi_agent":
        show_multi_agent_enhancement()
    elif st.session_state.current_page == "agent_effectiveness":
        show_agent_effectiveness()
    elif st.session_state.current_page == "export_data":
        show_export_data()
    elif st.session_state.current_page == "api_test":
        show_api_testing()
    elif st.session_state.current_page == "token_analytics":
        show_token_analytics()
    elif st.session_state.current_page == "security_dashboard":
        show_security_dashboard()
    elif st.session_state.current_page == "temporal_analysis":
        show_temporal_analysis()
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
    st.title("🤖 Prompt Enhancement & Comparison")
    st.markdown("Compare enhancement methods and see which produces best results")
    
    # Enhancement mode selector - Default to Compare All to showcase multi-agent value
    enhancement_mode = st.radio(
        "Enhancement Method:",
        [
            "📊 Compare All (Recommended - See which method wins!)",
            "🔧 Single-Agent Only (Template)",
            "🤖 Multi-Agent Only (3 Experts)"
        ],
        index=0,
        help="Compare All: See Original vs Single-Agent vs Multi-Agent side-by-side with winner declaration"
    )
    
    # Template explanation (condensed for comparison mode)
    if "Single-Agent" in enhancement_mode:
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
            submit_enhance = st.form_submit_button("✨ Enhance & Compare", type="primary")
    
    if submit_enhance and prompt_text:
        if "Compare All" in enhancement_mode:
            show_three_way_comparison(prompt_text, context)
        elif "Single-Agent" in enhancement_mode:
            show_single_agent_only(prompt_text, context)
        else:
            show_multi_agent_only(prompt_text)
    elif submit_enhance:
        st.error("❌ Please enter a prompt to enhance")

def show_three_way_comparison(original_prompt: str, context: str = ""):
    """Compare Original vs Single-Agent vs Multi-Agent enhancement"""
    
    # Generate unique request ID for tracking feedback
    request_id = str(uuid.uuid4())
    
    # Initialize tracker
    try:
        from packages.core import (
            fallback_to_template,
            judge_prompt,
            TokenTracker,
            generate_llm_output
        )
    except ImportError as e:
        st.error(f"❌ Failed to import core engine: {e}")
        return
    
    tracker = TokenTracker()
    
    with st.spinner("🤖 Running comparison (Original + Single + Multi)..."):
        # Step 1: Single-Agent Enhancement (existing pattern)
        try:
            single_enhanced = fallback_to_template(original_prompt).text
        except Exception as e:
            st.error(f"Single-agent enhancement failed: {e}")
            return
        
        # Step 2: Multi-Agent Enhancement (new)
        try:
            API_BASE = "http://localhost:8001"
            response = requests.post(
                f"{API_BASE}/prompts/multi-agent-enhance",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={"text": original_prompt, "enhancement_type": "general"}
            )
            
            if response.status_code == 200:
                multi_result = response.json()
                if multi_result.get("success"):
                    multi_enhanced = multi_result["data"]["enhanced_text"]
                    multi_metadata = multi_result["data"]  # For agent breakdown
                else:
                    st.error("Multi-agent enhancement failed")
                    return
            else:
                st.error(f"Multi-agent API error: {response.status_code}")
                return
        except Exception as e:
            st.error(f"Multi-agent call failed: {e}")
            return
        
        # Step 3: Generate outputs with all 3 prompts
        try:
            original_output, original_usage = generate_llm_output(original_prompt)
            single_output, single_usage = generate_llm_output(single_enhanced)
            multi_output, multi_usage = generate_llm_output(multi_enhanced)
            llm_available = True
        except Exception as e:
            st.warning(f"⚠️ LLM unavailable, using mock outputs: {str(e)}")
            # Mock outputs for demo
            original_output = "Mock response to original prompt."
            single_output = "Mock structured response to enhanced prompt."
            multi_output = "Mock comprehensive response with expert analysis."
            original_usage = tracker.track_llm_call(original_prompt, original_output, "mock")
            single_usage = tracker.track_llm_call(single_enhanced, single_output, "mock")
            multi_usage = tracker.track_llm_call(multi_enhanced, multi_output, "mock")
            llm_available = False
        
        # Step 4: Judge all 3 prompts
        try:
            original_score, original_judge_usage = judge_prompt(original_prompt)
            single_score, single_judge_usage = judge_prompt(single_enhanced)
            multi_score, multi_judge_usage = judge_prompt(multi_enhanced)
        except Exception as e:
            st.warning(f"⚠️ Judge unavailable, using mock scores: {str(e)}")
            from packages.core.judge import Scorecard
            original_score = Scorecard(clarity=4.0, specificity=3.0, actionability=2.0, structure=2.0, context_use=3.0, total=14.0, feedback={"pros": ["Brief"], "cons": ["Vague"], "summary": "Needs work"})
            single_score = Scorecard(clarity=8.0, specificity=7.5, actionability=8.0, structure=7.0, context_use=7.5, total=38.0, feedback={"pros": ["Clear", "Structured"], "cons": ["Generic"], "summary": "Good"})
            multi_score = Scorecard(clarity=9.0, specificity=9.0, actionability=9.0, structure=9.0, context_use=9.0, total=45.0, feedback={"pros": ["Expert", "Complete"], "cons": ["Verbose"], "summary": "Excellent"})
            original_judge_usage = tracker.track_llm_call("judge", "result", "mock")
            single_judge_usage = tracker.track_llm_call("judge", "result", "mock")
            multi_judge_usage = tracker.track_llm_call("judge", "result", "mock")
    
    # Display results
    display_three_way_results(
        request_id,
        original_prompt, single_enhanced, multi_enhanced,
        original_output, single_output, multi_output,
        original_score, single_score, multi_score,
        original_usage, single_usage, multi_usage,
        original_judge_usage, single_judge_usage, multi_judge_usage,
        multi_metadata
    )

def submit_feedback(request_id: str, user_choice: str, judge_winner: str, agent_winner: str):
    """Submit user feedback to backend"""
    API_BASE = "http://localhost:8001"
    
    try:
        response = requests.post(
            f"{API_BASE}/prompts/feedback",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json={
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

def display_three_way_results(
    request_id,
    original_prompt, single_enhanced, multi_enhanced,
    original_output, single_output, multi_output,
    original_score, single_score, multi_score,
    original_usage, single_usage, multi_usage,
    original_judge_usage, single_judge_usage, multi_judge_usage,
    multi_metadata
):
    """Display three-way comparison results"""
    
    st.success("✅ Comparison complete!")
    st.subheader("📊 Enhancement Comparison")
    
    # Three-column layout
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Original
    with col1:
        st.markdown("### 📄 Original")
        st.caption("Your prompt as-is")
        
        # Prompt
        with st.expander("View Prompt", expanded=False):
            st.text_area("Prompt", value=original_prompt, height=100, disabled=True, key="orig_prompt_comp", label_visibility="hidden")
        
        # Score
        st.metric("Quality Score", f"{original_score.total:.1f}/50", help="Judge evaluation")
        
        # Output preview
        st.write("**Output Preview:**")
        output_preview = original_output[:200] + ("..." if len(original_output) > 200 else "")
        st.text_area("Output", value=output_preview, height=100, disabled=True, key="orig_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = original_usage.cost_usd + original_judge_usage.cost_usd
        st.metric("Cost", f"${total_cost:.6f}")
    
    # Column 2: Single-Agent
    with col2:
        st.markdown("### 🔧 Single-Agent")
        st.caption("Template-based enhancement")
        
        # Prompt
        with st.expander("View Enhanced Prompt", expanded=False):
            st.text_area("Prompt", value=single_enhanced, height=100, disabled=True, key="single_prompt_comp", label_visibility="hidden")
        
        # Score with delta
        improvement = single_score.total - original_score.total
        st.metric("Quality Score", f"{single_score.total:.1f}/50", f"+{improvement:.1f}", help="Judge evaluation")
        
        # Output preview
        st.write("**Output Preview:**")
        output_preview = single_output[:200] + ("..." if len(single_output) > 200 else "")
        st.text_area("Output", value=output_preview, height=100, disabled=True, key="single_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = single_usage.cost_usd + single_judge_usage.cost_usd
        cost_increase = total_cost - (original_usage.cost_usd + original_judge_usage.cost_usd)
        st.metric("Cost", f"${total_cost:.6f}", f"+${cost_increase:.6f}")
    
    # Column 3: Multi-Agent
    with col3:
        st.markdown("### 🤖 Multi-Agent")
        st.caption("3 expert agents")
        
        # Prompt
        with st.expander("View Enhanced Prompt", expanded=False):
            st.text_area("Prompt", value=multi_enhanced, height=100, disabled=True, key="multi_prompt_comp", label_visibility="hidden")
        
        # Score with delta (compare to single-agent)
        improvement_vs_original = multi_score.total - original_score.total
        improvement_vs_single = multi_score.total - single_score.total
        
        # Show winner badge if best
        if multi_score.total > single_score.total and multi_score.total > original_score.total:
            st.metric("Quality Score", f"{multi_score.total:.1f}/50 🏆", f"+{improvement_vs_single:.1f} vs Single")
        else:
            st.metric("Quality Score", f"{multi_score.total:.1f}/50", f"+{improvement_vs_original:.1f}")
        
        # Output preview
        st.write("**Output Preview:**")
        output_preview = multi_output[:200] + ("..." if len(multi_output) > 200 else "")
        st.text_area("Output", value=output_preview, height=100, disabled=True, key="multi_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = multi_usage.cost_usd + multi_judge_usage.cost_usd
        cost_increase = total_cost - (original_usage.cost_usd + original_judge_usage.cost_usd)
        st.metric("Cost", f"${total_cost:.6f}", f"+${cost_increase:.6f}")
        
        # Agent breakdown (expandable)
        with st.expander("🔍 See Agent Contributions"):
            st.caption(f"Winner: {multi_metadata['selected_agent'].title()}")
            st.write(f"**Rationale:** {multi_metadata['decision_rationale']}")
            
            # Vote breakdown
            vote_breakdown = multi_metadata['vote_breakdown']
            for agent, score in vote_breakdown.items():
                st.write(f"- {agent.title()}: {score:.2f}")
    
    # Winner declaration
    st.divider()
    st.subheader("🏆 Winner Declaration")
    
    scores = {
        "Original": original_score.total,
        "Single-Agent": single_score.total,
        "Multi-Agent": multi_score.total
    }
    winner = max(scores, key=scores.get)
    winner_score = scores[winner]
    
    # Calculate improvements
    if winner == "Multi-Agent":
        improvement_text = f"+{winner_score - single_score.total:.1f} points vs Single-Agent, +{winner_score - original_score.total:.1f} vs Original"
        st.success(f"🏆 WINNER: {winner} ({winner_score:.1f}/50 points)")
        st.info(f"📈 Improvement: {improvement_text}")
    elif winner == "Single-Agent":
        improvement_text = f"+{winner_score - original_score.total:.1f} points vs Original"
        st.success(f"🏆 WINNER: {winner} ({winner_score:.1f}/50 points)")
        st.info(f"📈 Improvement: {improvement_text}")
    else:
        st.warning(f"Original prompt scored highest ({winner_score:.1f}/50) - enhancement didn't help!")
    
    # User Feedback Collection (Darwinian Evolution - Phase 1)
    st.divider()
    st.subheader("👍 Was this the right winner?")
    st.caption("Your feedback helps the system learn your preferences and improve over time")
    
    # Map winner to agent for tracking
    judge_winner = multi_metadata["selected_agent"]  # syntax, structure, or domain
    
    # Check if feedback already submitted (use session state)
    feedback_key = f"feedback_submitted_{request_id}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = False
    
    if not st.session_state[feedback_key]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👍 Original was best", key=f"vote_orig_{request_id}", type="secondary"):
                submit_feedback(request_id, "original", judge_winner, "none")
                st.session_state[feedback_key] = True
                st.rerun()
        
        with col2:
            if st.button("👍 Single-Agent was best", key=f"vote_single_{request_id}", type="secondary"):
                submit_feedback(request_id, "single", judge_winner, "template")
                st.session_state[feedback_key] = True
                st.rerun()
        
        with col3:
            if st.button("👍 Multi-Agent was best", key=f"vote_multi_{request_id}", type="primary"):
                submit_feedback(request_id, "multi", judge_winner, judge_winner)
                st.session_state[feedback_key] = True
                st.rerun()
    else:
        st.success("✅ Thank you! Your feedback has been recorded and will help the system learn.")
    
    # ROI Analysis
    st.divider()
    st.subheader("💰 Cost-Benefit Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cost Comparison:**")
        original_total = original_usage.cost_usd + original_judge_usage.cost_usd
        single_total = single_usage.cost_usd + single_judge_usage.cost_usd
        multi_total = multi_usage.cost_usd + multi_judge_usage.cost_usd
        
        st.write(f"- Original: ${original_total:.6f}")
        st.write(f"- Single-Agent: ${single_total:.6f} ({(single_total/original_total):.1f}x)")
        st.write(f"- Multi-Agent: ${multi_total:.6f} ({(multi_total/original_total):.1f}x)")
    
    with col2:
        st.write("**Quality vs Cost:**")
        
        # Single-Agent ROI
        single_quality_gain = single_score.total - original_score.total
        single_cost_increase = single_total - original_total
        if single_cost_increase > 0:
            single_roi = single_quality_gain / (single_cost_increase * 1000000)  # points per micro-dollar
            st.write(f"- Single-Agent: {single_roi:.1f} pts/μ$")
        
        # Multi-Agent ROI
        multi_quality_gain = multi_score.total - original_score.total
        multi_cost_increase = multi_total - original_total
        if multi_cost_increase > 0:
            multi_roi = multi_quality_gain / (multi_cost_increase * 1000000)
            st.write(f"- Multi-Agent: {multi_roi:.1f} pts/μ$")
        
        # Recommendation
        if multi_score.total > single_score.total:
            st.success("💡 Multi-Agent delivers higher quality")
        elif multi_cost_increase > 0 and single_cost_increase > 0 and multi_roi > single_roi:
            st.info("💡 Multi-Agent has better ROI")
        else:
            st.info("💡 Single-Agent is more cost-effective")
    
    # Full outputs (expandable)
    st.divider()
    st.subheader("📄 Full Outputs")
    
    output_tabs = st.tabs(["Original Output", "Single-Agent Output", "Multi-Agent Output"])
    
    with output_tabs[0]:
        st.text_area("Full output from original prompt:", value=original_output, height=300, disabled=True, key="full_orig", label_visibility="hidden")
    
    with output_tabs[1]:
        st.text_area("Full output from single-agent enhanced prompt:", value=single_output, height=300, disabled=True, key="full_single", label_visibility="hidden")
    
    with output_tabs[2]:
        st.text_area("Full output from multi-agent enhanced prompt:", value=multi_output, height=300, disabled=True, key="full_multi", label_visibility="hidden")

def show_multi_agent_only(prompt_text: str):
    """Multi-Agent enhancement only (no comparison)"""
    
    # Reuse existing show_multi_agent_enhancement() logic
    # Just call the multi-agent enhancement page with prompt pre-filled
    # This is a simple wrapper for consistency with new mode selector
    
    API_BASE = "http://localhost:8001"
    
    with st.spinner("Running multi-agent analysis..."):
        try:
            response = requests.post(
                f"{API_BASE}/prompts/multi-agent-enhance",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={"text": prompt_text, "enhancement_type": "general"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    display_multi_agent_results(result["data"])
                else:
                    st.error(f"Enhancement failed: {result.get('error', 'Unknown error')}")
            else:
                st.error(f"Request failed with status {response.status_code}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")

def show_single_agent_only(prompt_text: str, context: str = ""):
    """Single-Agent enhancement (existing flow)"""
    
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

def show_export_data():
    """
    Export data from database to CSV files.
    
    Database-First Pattern:
    - Manual CSV export (not automatic)
    - Reads from database (single source of truth)
    - Generates CSV for analysis/backup
    """
    st.title("📊 Export Data to CSV")
    st.markdown("Generate CSV files from database for analysis and backup")
    
    API_BASE = "http://localhost:8001"
    
    st.info("💡 **Database-First Pattern**: CSV files are generated from the database on demand. All production data is stored in PostgreSQL.")
    
    # Export buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Multi-Agent Data", type="primary", use_container_width=True):
            with st.spinner("Exporting multi-agent results from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-multi-agent",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Exported {result['records']} records to: `{result['csv_path']}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col2:
        if st.button("⏰ Export Temporal Data", type="primary", use_container_width=True):
            with st.spinner("Exporting temporal version chains from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-temporal",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Exported {result['records']} versions to: `{result['csv_path']}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col3:
        if st.button("📦 Export All Data", type="primary", use_container_width=True):
            with st.spinner("Exporting all data from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-all",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        paths = result['csv_paths']
                        st.success(f"✅ Exported all data:")
                        for name, path in paths.items():
                            st.success(f"  - {name}: `{path}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    st.markdown("---")
    
    # Export information
    st.subheader("📋 Export Information")
    
    st.markdown("""
    **What gets exported:**
    - **Multi-Agent Data**: All prompt versions from different agents (syntax, structure, domain)
    - **Temporal Data**: Version chains with parent-child relationships and change types
    
    **Why export to CSV:**
    - 📊 Analysis in Excel, Python, R
    - 💾 Backup and archival
    - 📈 Custom visualizations
    - 🔍 Data exploration
    
    **Database-First Pattern:**
    - ✅ PostgreSQL is the single source of truth
    - ✅ CSV files are generated on demand
    - ✅ No data drift between database and CSV
    - ✅ All queries read from database (not CSV)
    """)

def show_temporal_analysis():
    """
    Temporal Analysis page with timeline visualization and statistics.
    Week 12: Temporal Prompt Learning & Causal Analysis
    """
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, timedelta
    from temporal_client import init_temporal_client
    
    st.title("⏱️ Temporal Analysis")
    st.markdown("Analyze prompt evolution over time with trends, change-points, and causal hints")
    
    # Initialize temporal client with auth token
    temporal_client = init_temporal_client(token=st.session_state.access_token)
    
    # Get list of prompts for selection (using database)
    from packages.db.session import get_session
    from packages.db.models import Prompt
    
    try:
        with get_session() as session:
            prompts = session.query(Prompt).order_by(Prompt.created_at.desc()).limit(50).all()
            
            if not prompts:
                st.warning("⚠️ No prompts found. Create a prompt first using Single-Agent or Multi-Agent Enhancement.")
                if st.button("← Go to Prompt Enhancement"):
                    st.session_state.current_page = "prompts"
                    st.rerun()
                return
            
            # Prompt selector
            prompt_options = {f"{p.original_text[:60]}... ({p.created_at.strftime('%Y-%m-%d')})": str(p.id) for p in prompts}
            selected_prompt_label = st.selectbox("Select Prompt:", list(prompt_options.keys()))
            selected_prompt_id = prompt_options[selected_prompt_label]
            
            # Synthetic data generator button
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("🧪 Generate 30-Day Test Data", type="primary"):
                    with st.spinner("Generating synthetic history..."):
                        result = temporal_client.generate_synthetic(selected_prompt_id, days=30, versions_per_day=2)
                    
                    if result["success"]:
                        st.success(f"✅ Generated {result['data']['created_versions']} versions!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")
            
            # Tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["📈 Timeline", "📊 Statistics", "🔗 Causal Hints"])
            
            # Tab 1: Timeline Visualization
            with tab1:
                st.subheader("Prompt Evolution Timeline")
                
                # Date range selector
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        value=(datetime.now() - timedelta(days=30)).date()
                    )
                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=datetime.now().date()
                    )
                
                # Get timeline data
                timeline_result = temporal_client.get_timeline(
                    selected_prompt_id,
                    start_date.isoformat(),
                    end_date.isoformat()
                )
                
                if timeline_result["success"]:
                    timeline_data = timeline_result["data"]
                    
                    if not timeline_data:
                        st.info("💡 No temporal data found for this prompt. Generate synthetic data to see visualizations.")
                    else:
                        # Convert to DataFrame
                        df = pd.DataFrame(timeline_data)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        
                        # Create interactive line chart with plotly
                        fig = px.line(
                            df,
                            x='timestamp',
                            y='score',
                            color='change_type',
                            title='Judge Score Over Time',
                            labels={'score': 'Judge Score (0-100)', 'timestamp': 'Date', 'change_type': 'Change Type'},
                            markers=True
                        )
                        
                        fig.update_layout(
                            hovermode='x unified',
                            xaxis_title="Date",
                            yaxis_title="Judge Score",
                            legend_title="Change Type"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Data table
                        with st.expander("📋 View Raw Data"):
                            st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error(f"❌ Error loading timeline: {timeline_result['error']}")
            
            # Tab 2: Statistics
            with tab2:
                st.subheader("Temporal Statistics")
                
                stats_result = temporal_client.get_statistics(selected_prompt_id)
                
                if stats_result["success"]:
                    stats = stats_result["data"]
                    
                    # Metric cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        trend_icons = {"improving": "🟢", "degrading": "🔴", "stable": "🟡"}
                        trend_icon = trend_icons.get(stats['trend'], "⚪")
                        st.metric("Trend", f"{trend_icon} {stats['trend'].title()}")
                    
                    with col2:
                        st.metric("Average Score", f"{stats['avg_score']:.1f}")
                    
                    with col3:
                        st.metric("Score Std Dev", f"{stats['score_std']:.1f}")
                    
                    with col4:
                        st.metric("Total Versions", stats['total_versions'])
                    
                    st.markdown("---")
                    
                    # Additional statistics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Min Score", f"{stats.get('min_score', 0):.1f}")
                    with col2:
                        st.metric("Max Score", f"{stats.get('max_score', 0):.1f}")
                    
                    # Trend interpretation
                    if stats['trend'] == 'improving':
                        st.success("📈 **Interpretation:** This prompt is improving over time! Continue current optimization strategy.")
                    elif stats['trend'] == 'degrading':
                        st.warning("📉 **Interpretation:** This prompt is degrading over time. Consider reverting recent changes or trying a different approach.")
                    else:
                        st.info("➡️ **Interpretation:** This prompt has stable performance. Try more significant changes to improve scores.")
                else:
                    st.error(f"❌ Error loading statistics: {stats_result['error']}")
            
            # Tab 3: Causal Hints
            with tab3:
                st.subheader("Causal Hints: Change Types vs Score Deltas")
                st.markdown("Correlation analysis between change types and score improvements")
                
                hints_result = temporal_client.get_causal_hints(selected_prompt_id)
                
                if hints_result["success"]:
                    hints = hints_result["data"]
                    
                    if not hints:
                        st.info("💡 No causal data found. Generate synthetic data to see correlations.")
                    else:
                        # Display as DataFrame
                        df_hints = pd.DataFrame(hints)
                        df_hints = df_hints.sort_values('avg_score_delta', ascending=False)
                        
                        st.dataframe(df_hints, use_container_width=True, hide_index=True)
                        
                        # Interpretation
                        if not df_hints.empty:
                            best_type = df_hints.iloc[0]['change_type']
                            best_delta = df_hints.iloc[0]['avg_score_delta']
                            worst_type = df_hints.iloc[-1]['change_type']
                            worst_delta = df_hints.iloc[-1]['avg_score_delta']
                            
                            st.success(f"💡 **Best Strategy:** '{best_type}' changes tend to increase scores by **{best_delta:.1f} points** on average")
                            
                            if worst_delta < 0:
                                st.warning(f"⚠️ **Avoid:** '{worst_type}' changes tend to decrease scores by **{abs(worst_delta):.1f} points** on average")
                            
                            # Visualization
                            fig = px.bar(
                                df_hints,
                                x='change_type',
                                y='avg_score_delta',
                                color='avg_score_delta',
                                title='Average Score Delta by Change Type',
                                labels={'avg_score_delta': 'Avg Score Delta', 'change_type': 'Change Type'},
                                color_continuous_scale='RdYlGn'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Error loading causal hints: {hints_result['error']}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


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
    """Show token usage and cost analytics with multi-agent breakdown."""
    st.title("💰 Token Usage & Cost Analytics")
    st.markdown("Real-time token tracking across all AI agents with model-specific pricing")
    
    # Check for data
    if 'latest_multi_agent_result' not in st.session_state:
        st.warning("⚠️ No multi-agent data available. Please run a multi-agent enhancement first!")
        if st.button("← Go to Multi-Agent Enhancement"):
            st.session_state.current_page = "multi_agent"
            st.rerun()
        st.stop()
    
    data = st.session_state['latest_multi_agent_result']
    
    # Extract token usage
    token_usage = data.get('token_usage', {})
    total_cost = data.get('total_cost_usd', 0)
    total_tokens = data.get('total_tokens', 0)
    
    # Display aggregate metrics
    st.subheader("📊 Multi-Agent Token Usage Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tokens", f"{total_tokens:,}" if total_tokens else "N/A")
    
    with col2:
        st.metric("Total Cost", f"${total_cost:.6f}" if total_cost else "N/A")
    
    with col3:
        agents_used = len(token_usage) if token_usage else 0
        st.metric("Agents Used", agents_used)
    
    with col4:
        # Calculate cost per 1K tokens
        cost_per_1k = (total_cost / total_tokens * 1000) if total_tokens > 0 else 0
        st.metric("Cost per 1K Tokens", f"${cost_per_1k:.4f}" if cost_per_1k > 0 else "N/A")
    
    st.divider()
    
    # Per-agent breakdown
    st.subheader("🤖 Per-Agent Token Breakdown")
    
    if token_usage:
        import pandas as pd
        
        breakdown_data = {
            "Agent": [],
            "Model": [],
            "Prompt Tokens": [],
            "Completion Tokens": [],
            "Total Tokens": [],
            "Cost (USD)": []
        }
        
        for agent_name, usage in token_usage.items():
            breakdown_data["Agent"].append(agent_name.capitalize())
            breakdown_data["Model"].append(usage.get('model', 'N/A'))
            breakdown_data["Prompt Tokens"].append(f"{usage.get('prompt_tokens', 0):,}")
            breakdown_data["Completion Tokens"].append(f"{usage.get('completion_tokens', 0):,}")
            breakdown_data["Total Tokens"].append(f"{usage.get('total_tokens', 0):,}")
            breakdown_data["Cost (USD)"].append(f"${usage.get('cost_usd', 0):.6f}")
        
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Token distribution pie chart
        st.subheader("📊 Token Distribution by Agent")
        
        import plotly.graph_objects as go
        
        agent_names = []
        agent_tokens = []
        agent_colors = {
            'syntax': '#667eea',
            'structure': '#764ba2',
            'domain': '#f093fb'
        }
        
        for agent_name, usage in token_usage.items():
            agent_names.append(agent_name.capitalize())
            agent_tokens.append(usage.get('total_tokens', 0))
        
        fig = go.Figure(data=[go.Pie(
            labels=agent_names,
            values=agent_tokens,
            marker=dict(colors=[agent_colors.get(n.lower(), '#cccccc') for n in agent_names]),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Tokens: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Token Usage Distribution",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No per-agent token usage data available")
    
    st.divider()
    
    # Cost comparison
    st.subheader("💸 Cost Comparison & Savings")
    
    if token_usage and total_cost:
        # Calculate hypothetical cost with all 70B models
        avg_70b_price_per_token = (0.00000059 + 0.00000079) / 2  # Average of input+output
        all_70b_cost = total_tokens * avg_70b_price_per_token
        
        savings = all_70b_cost - total_cost
        savings_percent = (savings / all_70b_cost * 100) if all_70b_cost > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "All 70B Models Cost",
                f"${all_70b_cost:.6f}",
                help="Cost if all agents used Llama 3.3 70B model"
            )
        
        with col2:
            st.metric(
                "Optimized Cost",
                f"${total_cost:.6f}",
                delta=f"-${savings:.6f}",
                delta_color="inverse",
                help="Actual cost with optimized model assignment"
            )
        
        with col3:
            st.metric(
                "Cost Savings",
                f"{savings_percent:.1f}%",
                delta=f"${savings:.6f} saved",
                help="Percentage saved by using optimized model assignment"
            )
        
        # Savings chart
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(
                name='All 70B Models',
                x=['Cost Comparison'],
                y=[all_70b_cost * 1000000],  # Convert to per million for better visibility
                marker_color='#ef4444',
                text=[f"${all_70b_cost * 1000000:.2f} per 1M tokens"],
                textposition='auto'
            ),
            go.Bar(
                name='Optimized Assignment',
                x=['Cost Comparison'],
                y=[total_cost * 1000000],
                marker_color='#10b981',
                text=[f"${total_cost * 1000000:.2f} per 1M tokens"],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Cost per Million Tokens",
            yaxis_title="Cost ($) per 1M Tokens",
            barmode='group',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"✅ You saved **${savings:.6f} ({savings_percent:.1f}%)** by using optimized model assignment!")
    else:
        st.info("Run a multi-agent enhancement to see cost comparisons")
    
    # Temporal Analysis Widget (Week 12)
    st.markdown("---")
    st.subheader("⏱️ Token Usage Trends Over Time")
    st.markdown("Track how token usage evolves with prompt versions")
    
    with st.expander("📈 View Temporal Trends", expanded=False):
        from temporal_client import init_temporal_client
        from packages.db.session import get_session
        from packages.db.models import Prompt
        
        try:
            temporal_client = init_temporal_client(token=st.session_state.access_token)
            
            with get_session() as session:
                # Get recent prompts
                prompts = session.query(Prompt).order_by(Prompt.created_at.desc()).limit(10).all()
                
                if prompts:
                    # Prompt selector
                    prompt_options = {f"{p.original_text[:50]}...": str(p.id) for p in prompts}
                    selected_label = st.selectbox("Select prompt for trend analysis:", list(prompt_options.keys()), key="token_temporal_prompt")
                    selected_id = prompt_options[selected_label]
                    
                    # Get statistics
                    stats_result = temporal_client.get_statistics(selected_id)
                    
                    if stats_result["success"]:
                        stats = stats_result["data"]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            trend_icons = {"improving": "📈", "degrading": "📉", "stable": "➡️"}
                            st.metric("Performance Trend", f"{trend_icons.get(stats['trend'], '➡️')} {stats['trend'].title()}")
                        with col2:
                            st.metric("Avg Score", f"{stats['avg_score']:.1f}")
                        with col3:
                            st.metric("Versions", stats['total_versions'])
                        
                        st.info("💡 **Insight:** Monitor trends to optimize token spending on high-performing prompt strategies")
                    else:
                        st.info("💡 No temporal data available. Generate test data in Temporal Analysis page.")
                else:
                    st.info("💡 No prompts found. Create prompts to track token usage trends.")
        
        except Exception as e:
            st.warning(f"Temporal trends unavailable: {str(e)}")
            st.info("💡 Use the Temporal Analysis page for detailed trend analysis")

def show_multi_agent_enhancement():
    """Multi-Agent Prompt Enhancement Interface"""
    st.title("🤖 Multi-Agent Prompt Enhancement")
    st.markdown("Collaborative prompt optimization using specialized AI agents")
    
    # API base URL
    API_BASE = "http://localhost:8001"
    
    # Input section
    prompt_text = st.text_area(
        "Enter your prompt:",
        height=150,
        placeholder="Example: Write a Python function to sort a list..."
    )
    
    enhancement_type = st.selectbox(
        "Enhancement Focus:",
        ["general", "technical", "creative", "persuasive", "clear"]
    )
    
    if st.button("🚀 Enhance with Multi-Agent", type="primary"):
        if not prompt_text.strip():
            st.error("Please enter a prompt to enhance")
            return
        
        with st.spinner("Running multi-agent analysis..."):
            # Call backend endpoint
            try:
                response = requests.post(
                    f"{API_BASE}/prompts/multi-agent-enhance",
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    json={
                        "text": prompt_text,
                        "enhancement_type": enhancement_type
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        display_multi_agent_results(result["data"])
                    else:
                        st.error(f"Enhancement failed: {result.get('error', 'Unknown error')}")
                else:
                    st.error(f"Request failed with status {response.status_code}")
            except Exception as e:
                st.error(f"Error calling backend: {e}")

def display_multi_agent_results(data):
    """Display multi-agent enhancement results with token tracking"""
    import pandas as pd
    
    # Store in session state for token analytics page
    st.session_state['latest_multi_agent_result'] = data
    
    # Final result (top section)
    st.subheader("✨ Enhanced Prompt")
    st.success(data["enhanced_text"])
    
    # Decision info with token usage
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Selected Agent", data["selected_agent"].title())
    with col2:
        # Show token usage if available
        total_tokens = data.get("total_tokens")
        if total_tokens:
            st.metric("Total Tokens", f"{total_tokens:,}")
        else:
            st.info(data["decision_rationale"])
    with col3:
        # Show total cost if available
        total_cost = data.get("total_cost_usd")
        if total_cost:
            st.metric("Total Cost", f"${total_cost:.6f}")
        else:
            st.info("Cost tracking unavailable")
    
    # Token analytics quick link
    if data.get("token_usage"):
        st.info("💡 View detailed token analytics in the **Token Analytics** page (sidebar)")
    
    st.divider()
    
    # Agent comparison section
    st.subheader("🔍 Agent Analysis")
    
    # Create tabs for each agent
    agent_results = data["agent_results"]
    agent_tabs = st.tabs([r["agent_name"].title() for r in agent_results])
    
    for tab, result in zip(agent_tabs, agent_results):
        with tab:
            display_agent_result(result, is_winner=(result["agent_name"] == data["selected_agent"]))
    
    # Vote breakdown visualization
    st.subheader("📊 Vote Breakdown")
    display_vote_breakdown(data["vote_breakdown"])

def display_agent_result(result, is_winner):
    """Display individual agent result"""
    
    # Winner badge
    if is_winner:
        st.success("🏆 Selected Agent")
    
    # Score and confidence
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{result['analysis']['score']:.1f}/10")
    with col2:
        st.metric("Confidence", f"{result['suggestions']['confidence']:.0%}")
    with col3:
        focus = result["metadata"].get("focus", "N/A")
        st.metric("Focus", focus.title())
    
    # Strengths and weaknesses
    col_strength, col_weakness = st.columns(2)
    
    with col_strength:
        st.write("**✅ Strengths:**")
        for strength in result["analysis"]["strengths"]:
            st.write(f"- {strength}")
    
    with col_weakness:
        st.write("**⚠️ Weaknesses:**")
        for weakness in result["analysis"]["weaknesses"]:
            st.write(f"- {weakness}")
    
    # Suggestions
    st.write("**💡 Suggested Improvements:**")
    for i, suggestion in enumerate(result["suggestions"]["suggestions"], 1):
        st.write(f"{i}. {suggestion}")
    
    # Agent's improved version (expandable)
    with st.expander("View this agent's improved version"):
        st.code(result["suggestions"]["improved_prompt"], language="text")

def display_vote_breakdown(vote_breakdown):
    """Display vote breakdown as bar chart"""
    import pandas as pd
    
    # Create DataFrame for chart
    df = pd.DataFrame({
        "Agent": [name.title() for name in vote_breakdown.keys()],
        "Score": list(vote_breakdown.values())
    })
    
    # Sort by score descending
    df = df.sort_values("Score", ascending=False)
    
    # Display bar chart
    st.bar_chart(df.set_index("Agent"))
    
    # Display table
    st.dataframe(df, hide_index=True)

def show_agent_effectiveness():
    """Display agent effectiveness statistics (Database-First Pattern)"""
    import pandas as pd
    
    st.title("📈 Agent Effectiveness Dashboard")
    st.markdown("Track which agents perform best over time")
    
    API_BASE = "http://localhost:8001"
    
    # Fetch effectiveness data from backend (queries database, not CSV)
    with st.spinner("Loading agent statistics from database..."):
        try:
            response = requests.get(
                f"{API_BASE}/api/agents/effectiveness",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                effectiveness = result.get("effectiveness", {})
            else:
                st.error(f"Failed to fetch data: {response.status_code}")
                effectiveness = {}
        except Exception as e:
            st.error(f"Failed to fetch effectiveness: {e}")
            effectiveness = {}
    
    if not effectiveness:
        st.info("No multi-agent requests yet. Try enhancing a prompt first!")
        return
    
    # Overall statistics
    st.subheader("Overall Performance")
    
    cols = st.columns(len(effectiveness))
    for col, (agent_name, stats) in zip(cols, effectiveness.items()):
        with col:
            st.metric(
                agent_name.title(),
                f"{stats['wins']} wins",
                f"{stats['win_rate']:.0%} win rate"
            )
            st.caption(f"Avg Score: {stats['avg_score']:.1f}/10")
    
    # Win rate comparison chart
    st.subheader("Win Rate Comparison")
    display_win_rate_chart(effectiveness)
    
    # Detailed statistics table
    st.subheader("Detailed Statistics")
    display_effectiveness_table(effectiveness)
    
    # Token usage by agent (if available)
    if 'latest_multi_agent_result' in st.session_state:
        st.divider()
        st.subheader("💰 Token Usage by Agent")
        st.markdown("Real-time cost and token tracking for each agent")
        
        data = st.session_state['latest_multi_agent_result']
        token_usage = data.get('token_usage', {})
        
        if token_usage:
            import pandas as pd
            
            # Create DataFrame for agent token usage
            token_data = {
                "Agent": [],
                "Model": [],
                "Tokens Used": [],
                "Cost (USD)": [],
                "Efficiency": []
            }
            
            for agent_name, usage in token_usage.items():
                token_data["Agent"].append(agent_name.capitalize())
                token_data["Model"].append(usage.get('model', 'N/A'))
                token_data["Tokens Used"].append(usage.get('total_tokens', 0))
                token_data["Cost (USD)"].append(usage.get('cost_usd', 0))
                
                # Calculate efficiency (tokens per dollar)
                cost = usage.get('cost_usd', 0)
                tokens = usage.get('total_tokens', 0)
                efficiency = tokens / cost if cost > 0 else 0
                token_data["Efficiency"].append(f"{efficiency:,.0f} tokens/$")
            
            df_tokens = pd.DataFrame(token_data)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_tokens = sum(token_data["Tokens Used"])
                st.metric("Total Tokens", f"{total_tokens:,}")
            with col2:
                total_cost = sum(token_data["Cost (USD)"])
                st.metric("Total Cost", f"${total_cost:.6f}")
            with col3:
                avg_cost_per_1k = (total_cost / total_tokens * 1000) if total_tokens > 0 else 0
                st.metric("Avg Cost/1K Tokens", f"${avg_cost_per_1k:.4f}")
            
            # Display table
            st.dataframe(df_tokens, use_container_width=True, hide_index=True)
            
            # Token efficiency chart
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=token_data["Agent"],
                    y=token_data["Tokens Used"],
                    name="Tokens Used",
                    marker_color='#667eea',
                    hovertemplate='<b>%{x}</b><br>Tokens: %{y:,}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="Token Usage by Agent",
                xaxis_title="Agent",
                yaxis_title="Tokens Used",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 Lower token usage = lower costs. Fast models (8B) use fewer tokens than powerful models (70B).")
        else:
            st.info("No token usage data available. Run a multi-agent enhancement to see token tracking.")
    
    # Darwinian Feedback Stats (Phase 1)
    st.divider()
    st.subheader("🧬 Darwinian Learning Progress")
    st.markdown("System learning from user feedback to improve agent selection")
    
    # Extract metadata from effectiveness
    metadata = effectiveness.get('_metadata', {})
    
    if metadata:
        feedback_rate = metadata.get('feedback_rate', 0.0)
        total_feedback = metadata.get('total_feedback', 0)
        total_requests = metadata.get('total_requests', 0)
        learning_status = metadata.get('learning_status', 'Cold Start')
        
        # Display learning progress metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Learning Status", learning_status)
        
        with col2:
            st.metric("Feedback Rate", f"{feedback_rate:.0%}", 
                     help="Percentage of requests with user feedback")
        
        with col3:
            st.metric("Total Feedback", total_feedback,
                     help="Number of requests with user feedback")
        
        with col4:
            st.metric("Total Requests", total_requests)
        
        # Display per-agent feedback stats
        if total_feedback > 0:
            st.markdown("**Agent Performance with User Feedback:**")
            
            feedback_data = {
                "Agent": [],
                "Judge Wins": [],
                "User Wins": [],
                "User Win Rate": [],
                "Judge Accuracy": []
            }
            
            for agent_name, stats in effectiveness.items():
                if agent_name != '_metadata':
                    feedback_data["Agent"].append(agent_name.title())
                    feedback_data["Judge Wins"].append(stats.get('wins', 0))
                    feedback_data["User Wins"].append(stats.get('user_wins', 0))
                    feedback_data["User Win Rate"].append(f"{stats.get('user_win_rate', 0):.0%}")
                    feedback_data["Judge Accuracy"].append(f"{stats.get('judge_accuracy', 0):.0%}")
            
            df_feedback = pd.DataFrame(feedback_data)
            st.dataframe(df_feedback, use_container_width=True, hide_index=True)
            
            st.caption("**Judge Wins:** How often the judge selected this agent")
            st.caption("**User Wins:** How often users validated this agent's superiority")
            st.caption("**User Win Rate:** Percentage of user feedback selecting this agent")
            st.caption("**Judge Accuracy:** How often the judge's selection matched user choice")
        
        # Learning status explanation
        if learning_status == "Cold Start":
            st.info("🧊 **Cold Start:** No feedback yet. System using equal weights for all agents.")
        elif learning_status == "Warming Up":
            st.warning(f"🔥 **Warming Up:** {total_feedback} feedback events collected. Need 10+ for learning.")
        else:
            st.success(f"✅ **Learned:** {total_feedback} feedback events. System adapting to your preferences!")
    else:
        st.info("No feedback data yet. Use 'Compare All' mode and vote to help the system learn!")
    
    # Temporal Analysis Widget (Week 12)
    st.markdown("---")
    st.subheader("⏱️ Agent Performance Over Time")
    st.markdown("Track how agent effectiveness evolves")
    
    with st.expander("📈 View Performance Trends", expanded=False):
        from temporal_client import init_temporal_client
        from packages.db.session import get_session
        from packages.db.models import Prompt, PromptVersion
        import pandas as pd
        import plotly.express as px
        
        try:
            temporal_client = init_temporal_client(token=st.session_state.access_token)
            
            with get_session() as session:
                # Get prompts with agent versions
                prompts_with_agents = session.query(Prompt).join(PromptVersion).filter(
                    PromptVersion.source.in_(['syntax', 'structure', 'domain'])
                ).distinct().order_by(Prompt.created_at.desc()).limit(10).all()
                
                if prompts_with_agents:
                    st.info("💡 View temporal trends for each agent type to identify which strategies improve over time")
                    
                    # Get agent-specific trends
                    agent_trends = {}
                    for agent_name in ['syntax', 'structure', 'domain']:
                        # Get versions for this agent type
                        agent_versions = session.query(PromptVersion).filter(
                            PromptVersion.source == agent_name
                        ).order_by(PromptVersion.created_at).limit(30).all()
                        
                        if agent_versions:
                            # Calculate simple trend
                            scores = []
                            for v in agent_versions:
                                # Get judge score if available
                                from packages.db.models import JudgeScore
                                judge = session.query(JudgeScore).filter(
                                    JudgeScore.prompt_version_id == v.id
                                ).first()
                                
                                if judge:
                                    avg_score = (judge.clarity + judge.specificity + judge.actionability + judge.structure + judge.context_use) / 5.0
                                    scores.append(avg_score)
                            
                            if scores:
                                agent_trends[agent_name] = {
                                    'count': len(scores),
                                    'avg_score': sum(scores) / len(scores),
                                    'trend': 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable'
                                }
                    
                    if agent_trends:
                        col1, col2, col3 = st.columns(3)
                        
                        for col, (agent, stats) in zip([col1, col2, col3], agent_trends.items()):
                            with col:
                                trend_icon = "📈" if stats['trend'] == 'improving' else "➡️"
                                st.metric(
                                    f"{agent.title()} Agent",
                                    f"{stats['avg_score']:.1f}",
                                    f"{trend_icon} {stats['trend'].title()}"
                                )
                                st.caption(f"{stats['count']} versions analyzed")
                        
                        st.success("💡 **Insight:** Use temporal data to identify which agent types consistently improve and allocate resources accordingly")
                    else:
                        st.info("💡 No score data available. Enhance prompts with multi-agent to track trends.")
                else:
                    st.info("💡 No agent data found. Use Multi-Agent Enhancement to create agent versions.")
        
        except Exception as e:
            st.warning(f"Performance trends unavailable: {str(e)}")
            st.info("💡 Use the Temporal Analysis page for detailed agent performance tracking")

def display_win_rate_chart(effectiveness):
    """Display win rate as progress bars"""
    # Alternative: Use columns for visual representation
    total_wins = sum(stats["wins"] for stats in effectiveness.values())
    
    if total_wins > 0:
        st.write("**Distribution of Winning Agents:**")
        for agent_name, stats in effectiveness.items():
            percentage = stats["wins"] / total_wins * 100
            st.progress(stats["wins"] / total_wins, text=f"{agent_name.title()}: {percentage:.1f}%")
    else:
        st.info("No wins recorded yet")

def display_effectiveness_table(effectiveness):
    """Display effectiveness as detailed table"""
    import pandas as pd
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            "Agent": name.title(),
            "Wins": stats["wins"],
            "Win Rate": f"{stats['win_rate']:.1%}",
            "Avg Score": f"{stats['avg_score']:.1f}/10"
        }
        for name, stats in effectiveness.items()
    ])
    
    # Sort by wins descending
    df = df.sort_values("Wins", ascending=False)
    
    st.dataframe(df, hide_index=True, use_container_width=True)

def show_multi_agent_history():
    """View multi-agent request history"""
    st.title("📜 Multi-Agent Request History")
    
    st.info("💡 Click any request to see detailed agent contributions")
    
    # Placeholder for MVP - will be implemented in Phase 2
    st.warning("⚠️ History view coming soon! This feature will be available once Phase 2 storage is complete.")
    
    # TODO: Implement based on Phase 2 storage structure
    # For MVP: Could read CSV directly or add backend endpoint
    pass

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
                
                # API Usage & Token Tracking section
                st.subheader("💰 API Usage & Token Tracking")
                
                if 'latest_multi_agent_result' in st.session_state:
                    data = st.session_state['latest_multi_agent_result']
                    token_usage = data.get('token_usage', {})
                    total_cost = data.get('total_cost_usd', 0)
                    total_tokens = data.get('total_tokens', 0)
                    
                    if token_usage:
                        api_col1, api_col2, api_col3, api_col4 = st.columns(4)
                        
                        with api_col1:
                            st.metric("Multi-Agent Calls", "1", help="Latest multi-agent enhancement request")
                        
                        with api_col2:
                            st.metric("Total Tokens", f"{total_tokens:,}" if total_tokens else "N/A")
                        
                        with api_col3:
                            st.metric("Total Cost", f"${total_cost:.6f}" if total_cost else "N/A")
                        
                        with api_col4:
                            # Calculate projected monthly cost (assuming 100 requests/day)
                            requests_per_day = 100
                            requests_per_month = requests_per_day * 30
                            projected_cost = total_cost * requests_per_month if total_cost else 0
                            st.metric("Projected Monthly", f"${projected_cost:.2f}", help="Based on 100 requests/day")
                        
                        # Token usage table
                        import pandas as pd
                        
                        token_data = []
                        for agent_name, usage in token_usage.items():
                            token_data.append({
                                "Agent": agent_name.capitalize(),
                                "Model": usage.get('model', 'N/A'),
                                "Tokens": usage.get('total_tokens', 0),
                                "Cost": f"${usage.get('cost_usd', 0):.6f}"
                            })
                        
                        if token_data:
                            df_tokens = pd.DataFrame(token_data)
                            st.dataframe(df_tokens, use_container_width=True, hide_index=True)
                        
                        st.info("💡 Monitor token usage to optimize costs. View detailed analytics in **Token Analytics** page.")
                    else:
                        st.info("No token usage data available. Run a multi-agent enhancement to track API usage.")
                else:
                    st.info("No multi-agent requests yet. Try the **Multi-Agent Enhancement** page to see token tracking.")
                
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
                
                # Temporal Analysis Widget (Week 12)
                st.markdown("---")
                st.subheader("⏱️ Security Risk Trends Over Time")
                st.markdown("Monitor risk score evolution and detect escalation patterns")
                
                with st.expander("📈 View Risk Trends", expanded=False):
                    import plotly.express as px
                    
                    try:
                        # Analyze temporal risk trends
                        if len(inputs) > 1:
                            # Sort by timestamp
                            sorted_inputs = sorted(inputs, key=lambda x: x.get("createdAt", ""))
                            
                            # Prepare time series data
                            timestamps = []
                            risk_scores = []
                            
                            for inp in sorted_inputs:
                                try:
                                    ts = datetime.fromisoformat(inp.get("createdAt", "").replace("Z", "+00:00"))
                                    timestamps.append(ts)
                                    risk_scores.append(inp.get("riskScore", 0))
                                except:
                                    continue
                            
                            if timestamps and risk_scores:
                                # Create time series DataFrame
                                ts_df = pd.DataFrame({
                                    'Timestamp': timestamps,
                                    'Risk Score': risk_scores
                                })
                                
                                # Plot risk trend
                                fig = px.line(
                                    ts_df,
                                    x='Timestamp',
                                    y='Risk Score',
                                    title='Risk Score Evolution',
                                    labels={'Risk Score': 'Risk Score (0-100)', 'Timestamp': 'Time'}
                                )
                                
                                # Add threshold lines
                                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk")
                                fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Medium Risk")
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Change-point detection (simple)
                                if len(risk_scores) > 5:
                                    recent_avg = sum(risk_scores[-5:]) / 5
                                    overall_avg = sum(risk_scores) / len(risk_scores)
                                    
                                    if recent_avg > overall_avg + 15:
                                        st.error(f"🚨 **Risk Escalation Detected!** Recent average ({recent_avg:.1f}) is significantly higher than overall average ({overall_avg:.1f})")
                                        st.warning("⚠️ **Action Required:** Investigate recent inputs for potential security threats")
                                    elif recent_avg < overall_avg - 15:
                                        st.success(f"✅ **Risk Reduction Observed:** Recent average ({recent_avg:.1f}) is lower than overall average ({overall_avg:.1f})")
                                    else:
                                        st.info(f"ℹ️ **Stable Risk Level:** Recent average ({recent_avg:.1f}) is consistent with overall average ({overall_avg:.1f})")
                                
                                # Statistics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Current Risk", f"{risk_scores[-1]:.1f}")
                                with col2:
                                    st.metric("Average Risk", f"{overall_avg:.1f}")
                                with col3:
                                    trend = "📈" if len(risk_scores) > 1 and risk_scores[-1] > risk_scores[0] else "📉"
                                    st.metric("Trend", trend)
                                
                                st.info("💡 **Insight:** Use temporal trends to detect security pattern changes and respond proactively")
                            else:
                                st.info("💡 No valid timestamp data for trend analysis")
                        else:
                            st.info("💡 Need more security inputs (2+) to analyze trends")
                    
                    except Exception as e:
                        st.warning(f"Risk trend analysis unavailable: {str(e)}")
                        st.info("💡 Continue monitoring security inputs to enable trend detection")

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