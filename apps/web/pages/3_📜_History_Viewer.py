import streamlit as st
import requests
import pandas as pd

st.title("📜 Prompt History Viewer")
st.write("Track all improved prompts, scores, and token usage.")

API_BASE = "http://localhost:8000"

# Fetch history
with st.spinner("Loading history..."):
    resp = requests.get(f"{API_BASE}/history")
    if resp.status_code != 200:
        st.error("Could not load history from backend.")
        st.stop()

data = resp.json()

if not data:
    st.info("No history available yet.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

st.subheader("📋 Full History")
st.dataframe(df, use_container_width=True)

# CSV export
st.download_button(
    label="📦 Download as CSV",
    data=df.to_csv(index=False),
    file_name="prompt_history.csv",
    mime="text/csv",
)

# Analytics
st.subheader("📊 Analytics")
with st.spinner("Loading analytics..."):
    analytics = requests.get(f"{API_BASE}/history/analytics").json()

st.json(analytics)
