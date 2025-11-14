import streamlit as st
import requests
import json

st.set_page_config(page_title="Prompt Engineering System", layout="wide")

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def login_user(username, password):
    """Login user and store session data"""
    try:
        response = requests.post(
            "http://localhost:8000/v1/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.token = data["token"]
            st.session_state.username = data["username"]
            st.session_state.user_id = data["user_id"]
            return True, "Login successful!"
        else:
            return False, f"Login failed: {response.json().get('detail', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the API. Make sure the backend is running."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def register_user(username, password):
    """Register new user"""
    try:
        response = requests.post(
            "http://localhost:8000/v1/register",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.token = data["token"]
            st.session_state.username = data["username"]
            st.session_state.user_id = data["user_id"]
            return True, "Registration successful!"
        else:
            return False, f"Registration failed: {response.json().get('detail', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the API. Make sure the backend is running."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def logout_user():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.user_id = None

def get_auth_headers():
    """Get authorization headers for API calls"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# Main App Logic
st.title("Self-Learning Prompt Engineering System")

# Authentication Section
if not st.session_state.authenticated:
    st.header("🔐 Authentication Required")
    
    # Tabs for Login/Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login", type="primary")
            
            if login_button:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register", type="primary")
            
            if register_button:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        success, message = register_user(new_username, new_password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")

else:
    # User is authenticated - show main interface
    
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"Welcome back, {st.session_state.username}! 👋")
    with col2:
        if st.button("Logout", type="secondary"):
            logout_user()
            st.rerun()
    
    # Main navigation tabs
    tab1, tab2 = st.tabs(["🆕 Improve New Prompt", "📚 Prompt History"])
    
    with tab1:
        st.header("Prompt Improvement Interface")
        
        # Text input
        user_prompt = st.text_area("Enter your prompt:", placeholder="e.g., Help me code a sorting algorithm", height=100)
        
        # Improvement button
        if st.button("Improve Prompt", type="primary") and user_prompt:
            try:
                # Call the API endpoint with authentication
                with st.spinner("Improving your prompt..."):
                    response = requests.post(
                        "http://localhost:8000/v1/prompts",
                        json={"text": user_prompt},
                        headers=get_auth_headers()
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display original and improved side-by-side
                    st.subheader("📊 Comparison: Original vs Improved")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🔴 Original")
                        st.markdown("**Prompt:**")
                        st.text_area(
                            "Original Prompt",
                            data["original"],
                            height=200,
                            disabled=True,
                            key="original_prompt",
                            label_visibility="collapsed"
                        )
                        st.caption(f"📏 {len(data['original'])} characters | {len(data['original'].split())} words")
                        
                        st.markdown("**LLM Output:**")
                        st.text_area(
                            "Original Output",
                            data["original_output"],
                            height=300,
                            disabled=True,
                            key="original_output",
                            label_visibility="collapsed"
                        )
                        st.caption(f"📝 {len(data['original_output'])} characters | {len(data['original_output'].split())} words")
                    
                    with col2:
                        st.markdown("### 🟢 Improved")
                        st.markdown("**Prompt:**")
                        st.text_area(
                            "Improved Prompt",
                            data["improved"],
                            height=200,
                            key="improved_prompt",
                            label_visibility="collapsed"
                        )
                        prompt_char_diff = len(data["improved"]) - len(data["original"])
                        prompt_word_diff = len(data["improved"].split()) - len(data["original"].split())
                        st.caption(f"📏 {len(data['improved'])} characters ({prompt_char_diff:+d}) | {len(data['improved'].split())} words ({prompt_word_diff:+d})")
                        
                        st.markdown("**LLM Output:**")
                        st.text_area(
                            "Improved Output",
                            data["improved_output"],
                            height=300,
                            key="improved_output",
                            label_visibility="collapsed"
                        )
                        output_char_diff = len(data["improved_output"]) - len(data["original_output"])
                        output_word_diff = len(data["improved_output"].split()) - len(data["original_output"].split())
                        st.caption(f"📝 {len(data['improved_output'])} characters ({output_char_diff:+d}) | {len(data['improved_output'].split())} words ({output_word_diff:+d})")
                    
                    st.divider()
                    
                    # Display output quality comparison
                    st.subheader("📈 Output Quality Comparison")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        st.metric(
                            "Prompt Improvement",
                            f"{prompt_char_diff:+d} chars",
                            help="Change in prompt length"
                        )
                    
                    with metric_col2:
                        st.metric(
                            "Output Length Change",
                            f"{output_char_diff:+d} chars",
                            help="Change in LLM response length"
                        )
                    
                    with metric_col3:
                        output_quality_change = ((len(data["improved_output"]) / len(data["original_output"])) - 1) * 100 if len(data["original_output"]) > 0 else 0
                        st.metric(
                            "Output Size Change",
                            f"{output_quality_change:+.1f}%",
                            help="Percentage change in response length"
                        )
                    
                    st.divider()
                    
                    # Display improvement explanation
                    st.subheader("🔍 What Changed in the Prompt?")
                    
                    with st.expander("📝 Improvement Summary", expanded=True):
                        for bullet in data["explanation"]["bullets"]:
                            st.write(f"✨ {bullet}")
                    
                    st.divider()
                    
                    # Display quality scores
                    st.subheader("📈 Quality Assessment")
                    
                    judge_data = data["judge"]
                    metric_cols = st.columns(6)
                    
                    metrics = [
                        ("Clarity", judge_data['clarity'], "Clear and understandable"),
                        ("Specificity", judge_data['specificity'], "Precise and detailed"),
                        ("Actionability", judge_data['actionability'], "Easy to act upon"),
                        ("Structure", judge_data['structure'], "Well organized"),
                        ("Context", judge_data['context_use'], "Uses context effectively"),
                        ("Total", judge_data['total'], "Overall score (max: 50)")
                    ]
                    
                    for col, (label, value, help_text) in zip(metric_cols, metrics):
                        with col:
                            if label == "Total":
                                st.metric(label, f"{value:.1f}/50", help=help_text)
                            else:
                                st.metric(label, f"{value:.1f}/10", help=help_text)
                    
                    st.divider()
                    
                    # Display feedback
                    st.subheader("💭 Detailed Feedback")
                    feedback = judge_data["feedback"]
                    
                    col_pros, col_cons = st.columns(2)
                    
                    with col_pros:
                        if feedback.get("pros"):
                            st.markdown("**✅ Strengths:**")
                            for pro in feedback["pros"]:
                                st.write(f"• {pro}")
                    
                    with col_cons:
                        if feedback.get("cons"):
                            st.markdown("**⚠️ Areas for Improvement:**")
                            for con in feedback["cons"]:
                                st.write(f"• {con}")
                    
                    if feedback.get("summary"):
                        st.info(f"**📋 Summary:** {feedback['summary']}")
                    
                    # Store prompt ID for future reference
                    st.success(f"✅ Prompt saved to your account with ID: {data['promptId']}")
                
                elif response.status_code == 401:
                    st.error("❌ Session expired. Please log in again.")
                    logout_user()
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8000")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    
    with tab2:
        st.header("📚 Your Prompt History")
        st.write("Browse all your saved prompts and their improved versions:")
        
        # Fetch user's prompt history
        try:
            with st.spinner("Loading your prompt history..."):
                response = requests.get(
                    "http://localhost:8000/v1/prompts",
                    headers=get_auth_headers()
                )
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", [])
                
                if not prompts:
                    st.info("📝 No prompts found. Create your first prompt in the 'Improve New Prompt' tab!")
                else:
                    st.success(f"Found {len(prompts)} saved prompts")
                    
                    # Display prompts in reverse chronological order (newest first)
                    for i, prompt in enumerate(prompts):
                        with st.expander(f"📌 {prompt['originalText'][:100]}{'...' if len(prompt['originalText']) > 100 else ''}", expanded=(i < 2)):
                            
                            # Show basic prompt info
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.markdown(f"**Original Prompt:**")
                                st.text_area(
                                    "Original Text",
                                    prompt['originalText'],
                                    height=80,
                                    disabled=True,
                                    key=f"orig_{prompt['promptId']}",
                                    label_visibility="collapsed"
                                )
                            with col2:
                                st.metric("Created", prompt['createdAt'][:10])
                            with col3:
                                if st.button("🔍 View Details", key=f"details_{prompt['promptId']}"):
                                    st.session_state[f"show_details_{prompt['promptId']}"] = not st.session_state.get(f"show_details_{prompt['promptId']}", False)
                            
                            # Show detailed history if requested
                            if st.session_state.get(f"show_details_{prompt['promptId']}", False):
                                try:
                                    # Fetch detailed prompt history
                                    detail_response = requests.get(
                                        f"http://localhost:8000/v1/prompts/{prompt['promptId']}",
                                        headers=get_auth_headers()
                                    )
                                    
                                    if detail_response.status_code == 200:
                                        details = detail_response.json()
                                        
                                        # Show best version
                                        if details.get("best"):
                                            st.markdown("### 🏆 Best Version")
                                            best = details["best"]
                                            
                                            col1, col2 = st.columns([2, 1])
                                            with col1:
                                                st.text_area(
                                                    "Best Prompt",
                                                    best['text'],
                                                    height=100,
                                                    disabled=True,
                                                    key=f"best_{prompt['promptId']}",
                                                    label_visibility="collapsed"
                                                )
                                            with col2:
                                                st.metric("Score", f"{best['score']:.1f}/50")
                                                st.metric("Version", f"v{best['versionNo']}")
                                        
                                        # Show version history
                                        if details.get("history"):
                                            st.markdown("### 📊 Version History")
                                            
                                            for version in details["history"]:
                                                version_col1, version_col2, version_col3 = st.columns([3, 1, 1])
                                                
                                                with version_col1:
                                                    st.markdown(f"**Version {version['versionNo']}** - {version['source']}")
                                                    with st.expander(f"View v{version['versionNo']} text", expanded=False):
                                                        st.text(version['text'])
                                                
                                                with version_col2:
                                                    if version.get('scores'):
                                                        latest_score = version['scores'][-1]
                                                        st.metric("Score", f"{latest_score['total']:.1f}/50")
                                                
                                                with version_col3:
                                                    st.caption(version['created_at'][:10])
                                    
                                    else:
                                        st.error("❌ Failed to load prompt details")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error loading details: {str(e)}")
                            
                            st.divider()
            
            elif response.status_code == 401:
                st.error("❌ Session expired. Please log in again.")
                logout_user()
                st.rerun()
            else:
                st.error(f"❌ Error loading prompts: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8000")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Sidebar for authenticated users
if st.session_state.authenticated:
    st.sidebar.markdown(f"## 👤 User: {st.session_state.username}")
    st.sidebar.markdown("---")

# Add sidebar with information
st.sidebar.markdown("""
## 🎯 How it works:
1. **Login or Register** to create your account
2. **Improve New Prompt** tab:
   - Enter your prompt in the text box
   - Click "Improve Prompt" to get an enhanced version
   - View side-by-side comparison with quality scores
3. **Prompt History** tab:
   - Browse all your previously improved prompts
   - View version history and best versions
   - See quality scores for each version

## ✨ New Features:
- **📚 Prompt History**: Access all your saved prompts and improvements
- **🏆 Best Version Tracking**: See which version performed best
- **📊 Version Timeline**: View the evolution of each prompt
- **🔍 Detailed Analysis**: Expandable view for complete prompt details

## 🔐 Authentication Features:
- **Secure User Accounts**: Your prompts are saved to your personal account
- **JWT Token Authentication**: Industry-standard security
- **Session Management**: Stay logged in during your session

## 🔌 API Endpoints:
- `POST /v1/register` - Create new account
- `POST /v1/login` - Login to account
- `POST /v1/prompts` - Create and improve prompts (requires auth)
- `GET /v1/prompts` - List all user prompts (requires auth)
- `GET /v1/prompts/{id}` - Get prompt details (requires auth)

## 🚀 Need help?
Make sure the backend API is running:
```
cd backend
python -m uvicorn api:app --reload
```
""")

# Add footer
st.sidebar.divider()
st.sidebar.caption("Built with ❤️ by the Prompt Engineering Team")
st.sidebar.caption("🔒 Now with secure authentication!")
