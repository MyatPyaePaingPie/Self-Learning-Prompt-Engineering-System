import streamlit as st
import requests
import os

# adding page configuration at the very top
st.set_page_config(page_title="Self-Learning Prompt Improver", layout="wide")

# sidebar version history
st.sidebar.header("📜 Version History")
history_dir = "storage/prompts"
if os.path.exists(history_dir):
    files = sorted(os.listdir(history_dir), reverse=True)
    for f in files:
        if f.endswith(".txt"):
            st.sidebar.write(f"- {f}")
else:
    st.sidebar.info("No saved prompts yet.")

# main title & caption
st.title("🧠 Self-Learning Prompt Engineering System")
st.caption("Automatically improves your prompts, scores them, and learns over time.")
st.header("Prompt Improvement Interface")

# text input 
user_prompt = st.text_area(
    "Enter your prompt:",
    placeholder="e.g., Help me code a sorting algorithm",
    height=100
)

# improved button + spinner + timeout handling
if st.button("✨ Improve Prompt") and user_prompt:
    with st.spinner("Improving your prompt..."):
        try:
            response = requests.post(
                "http://localhost:8000/v1/prompts",
                json={"text": user_prompt},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                # improved layout: show original + improved side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📝 Original Prompt")
                    st.text_area(
                        "Original Prompt (read-only)",
                        user_prompt,
                        height=120,
                        disabled=True,
                        label_visibility="collapsed"
                    )

                with col2:
                    st.markdown("### 🚀 Improved Prompt")
                    st.text_area(
                        "Improved Prompt (read-only)",
                        data["improved"],
                        height=120,
                        disabled=True,
                        label_visibility="collapsed"
                    )


                # explanation section
                st.markdown("### 💡 Improvement Explanation")
                for bullet in data["explanation"]["bullets"]:
                    st.write(f"• {bullet}")

                # updated quality scores (use columns for all six metrics)
                st.markdown("### 🧮 Quality Scores")
                judge_data = data["judge"]
                cols = st.columns(6)
                metrics = [
                    ("Clarity", judge_data["clarity"]),
                    ("Specificity", judge_data["specificity"]),
                    ("Actionability", judge_data["actionability"]),
                    ("Structure", judge_data["structure"]),
                    ("Context Use", judge_data["context_use"]),
                    ("Total", judge_data["total"]),
                ]
                for (label, value), col in zip(metrics, cols):
                    col.metric(label, f"{value:.1f}")

                # ✅ feedback section
                st.markdown("### 🗣️ Feedback")
                feedback = judge_data["feedback"]

                if feedback.get("pros"):
                    st.write("**✅ Pros:**")
                    for pro in feedback["pros"]:
                        st.write(f"- {pro}")

                if feedback.get("cons"):
                    st.write("**❌ Cons:**")
                    for con in feedback["cons"]:
                        st.write(f"- {con}")

                if feedback.get("summary"):
                    st.info(f"**Summary:** {feedback['summary']}")

                st.success(f"Prompt saved with ID: {data['promptId']}")

            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("🚫 Could not connect to the API. Make sure FastAPI is running on port 8000.")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try again.")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")

# improved sidebar footer help text
st.sidebar.markdown("""
---
### 🧭 How It Works
1. Enter a prompt.
2. Click “Improve Prompt”.
3. The system:
   - Rewrites your prompt for clarity and specificity  
   - Scores the improvement on 5 criteria  
   - Provides detailed feedback  
   - Saves the result for learning

### ⚙️ Backend Info
- `POST /v1/prompts` → Create & improve prompt  
- `GET /v1/prompts/{id}` → Retrieve details  
- `POST /v1/prompts/{id}/improve` → Generate variants
""")
