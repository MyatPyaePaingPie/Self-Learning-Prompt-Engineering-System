import streamlit as st
import requests
import json

st.set_page_config(page_title="Prompt Improvement", page_icon="🏠", layout="wide")

st.title("Self-Learning Prompt Engineering System")
st.header("Prompt Improvement Interface")

# Text input
user_prompt = st.text_area("Enter your prompt:", placeholder="e.g., Help me code a sorting algorithm", height=100)

# Improvement button
if st.button("Improve Prompt", type="primary") and user_prompt:
    try:
        # Call the API endpoint
        with st.spinner("Improving your prompt..."):
            response = requests.post(
                "http://localhost:8000/v1/prompts",
                json={"text": user_prompt}
            )
        
        if response.status_code == 200:
            data = response.json()
            
            # Store in session state for analytics page
            st.session_state['latest_result'] = data
            
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
            st.success(f"✅ Prompt saved with ID: {data['promptId']}")
            
            # Navigation to analytics
            st.divider()
            st.page_link("pages/2_💰_Token_Analytics.py", label="📊 View Token Analytics →", icon="💰")
            
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

# Add sidebar with information
st.sidebar.markdown("""
## 🎯 How it works:
1. Enter your prompt in the text box
2. Click "Improve Prompt" to get an enhanced version
3. The system will:
   - Rewrite your prompt for clarity and specificity
   - Generate LLM outputs for BOTH prompts
   - Show before/after comparison side-by-side
   - Compare output quality differences
   - Score the improvement on 5 criteria
   - Provide detailed feedback
   - Save the results for learning

## 🔌 API Endpoints:
- `POST /v1/prompts` - Create and improve a prompt
- `GET /v1/prompts/{id}` - Get prompt details
- `POST /v1/prompts/{id}/improve` - Generate additional improvements

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

