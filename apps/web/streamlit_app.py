import streamlit as st
import requests
import json

st.title("Self-Learning Prompt Engineering System")
st.header("Prompt Improvement Interface")

# Text input
user_prompt = st.text_area("Enter your prompt:", placeholder="e.g., Help me code a sorting algorithm", height=100)

# Improvement button
if st.button("Improve Prompt") and user_prompt:
    try:
        # Call the API endpoint
        response = requests.post(
            "http://localhost:8000/v1/prompts",
            json={"text": user_prompt}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Display original prompt
            st.subheader("Original Prompt:")
            st.text_area("Original Prompt", user_prompt, height=100, disabled=True, key="original", label_visibility="collapsed")

            
            # Display improved prompt
            st.subheader("Improved Prompt:")
            st.text_area("Improved Prompt", data["improved"], height=200, key="improved", label_visibility="collapsed")

            
            # Display explanation
            st.subheader("Improvement Explanation:")
            for bullet in data["explanation"]["bullets"]:
                st.write(f"• {bullet}")
            
            # Display judge scores
            st.subheader("Quality Scores:")
            judge_data = data["judge"]
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Clarity", f"{judge_data['clarity']:.1f}")
            with col2:
                st.metric("Specificity", f"{judge_data['specificity']:.1f}")
            with col3:
                st.metric("Actionability", f"{judge_data['actionability']:.1f}")
            with col4:
                st.metric("Structure", f"{judge_data['structure']:.1f}")
            with col5:
                st.metric("Context Use", f"{judge_data['context_use']:.1f}")
            
            st.metric("Total Score", f"{judge_data['total']:.1f}", help="Sum of all scores (max: 50)")
            
            # Display feedback
            st.subheader("Feedback:")
            feedback = judge_data["feedback"]
            if feedback.get("pros"):
                st.write("**Pros:**")
                for pro in feedback["pros"]:
                    st.write(f"✅ {pro}")
            
            if feedback.get("cons"):
                st.write("**Cons:**")
                for con in feedback["cons"]:
                    st.write(f"❌ {con}")
            
            if feedback.get("summary"):
                st.info(f"**Summary:** {feedback['summary']}")
            
            # Store prompt ID for future reference
            st.success(f"Prompt saved with ID: {data['promptId']}")
            
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add sidebar with information
st.sidebar.markdown("""
## How it works:
1. Enter your prompt in the text box
2. Click "Improve Prompt" to get an enhanced version
3. The system will:
   - Rewrite your prompt for clarity and specificity
   - Score the improvement on 5 criteria
   - Provide detailed feedback
   - Save the results for learning

## API Endpoints:
- `POST /v1/prompts` - Create and improve a prompt
- `GET /v1/prompts/{id}` - Get prompt details
- `POST /v1/prompts/{id}/improve` - Generate additional improvements

## Need help?
Make sure the backend API is running:
```
cd backend
python -m uvicorn api:app --reload
```
""")
