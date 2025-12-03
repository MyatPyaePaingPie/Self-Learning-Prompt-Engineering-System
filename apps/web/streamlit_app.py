import streamlit as st

st.set_page_config(
    page_title="Prompt Engineering System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar branding
st.sidebar.title("🚀 Prompt Engineering System")
st.sidebar.markdown("---")

# Auto-navigate to home page
st.switch_page("pages/1_🏠_Home.py")
