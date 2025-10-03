import streamlit as st

st.title("Self-Learning Prompt Engineering System")
st.header("Simple Form")

# Text input
user_prompt = st.text_input("Enter your prompt:")

# Output box
if user_prompt:
    st.text_area("Output:", f"Processed: {user_prompt}", height=200)
