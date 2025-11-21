import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Security Dashboard", page_icon="🔒", layout="wide")

st.title("🔒 Security Dashboard")
st.markdown("Monitor and analyze security inputs, risk scores, and blocked attempts")

# API base URL
API_BASE = "http://localhost:8000"

# Sidebar filters
st.sidebar.header("🔍 Filters")

filter_label = st.sidebar.selectbox(
    "Filter by Label",
    ["All", "safe", "low-risk", "medium-risk", "high-risk", "blocked"],
    index=0
)

filter_blocked = st.sidebar.selectbox(
    "Filter by Blocked Status",
    ["All", "Blocked Only", "Not Blocked"],
    index=0
)

filter_high_risk = st.sidebar.checkbox("Show High-Risk Only (≥70)", value=False)

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
        response = requests.get(f"{API_BASE}/v1/security/inputs", params=params)
    
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
                st.metric("Blocked", blocked_count, delta=f"{(blocked_count/total_inputs*100):.1f}%" if total_inputs > 0 else "0%")
            
            with col3:
                st.metric("High-Risk (≥70)", high_risk_count, delta=f"{(high_risk_count/total_inputs*100):.1f}%" if total_inputs > 0 else "0%")
            
            with col4:
                st.metric("Avg Risk Score", f"{avg_risk_score:.1f}", delta=f"Max: {max((inp.get('riskScore', 0) for inp in inputs), default=0):.1f}")
            
            st.divider()
            
            # Risk indicators
            st.subheader("⚠️ Risk Indicators")
            
            indicator_col1, indicator_col2 = st.columns(2)
            
            with indicator_col1:
                if blocked_count > 0:
                    st.error(f"🚫 **{blocked_count} Blocked Attempt(s)**")
                    blocked_inputs = [inp for inp in inputs if inp.get("isBlocked", False)]
                    for inp in blocked_inputs[:5]:  # Show first 5
                        st.caption(f"• {inp.get('inputText', '')[:100]}... (Risk: {inp.get('riskScore', 0):.1f})")
                else:
                    st.success("✅ No blocked attempts")
            
            with indicator_col2:
                if high_risk_count > 0:
                    st.warning(f"⚠️ **{high_risk_count} High-Risk Attempt(s)**")
                    high_risk_inputs = [inp for inp in inputs if inp.get("riskScore", 0) >= 70]
                    for inp in high_risk_inputs[:5]:  # Show first 5
                        st.caption(f"• {inp.get('inputText', '')[:100]}... (Risk: {inp.get('riskScore', 0):.1f})")
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
                    risk_color = "🔴"
                elif risk_score >= 40:
                    risk_color = "🟡"
                else:
                    risk_color = "🟢"
                
                # Blocked indicator
                blocked_indicator = "🚫 BLOCKED" if inp.get("isBlocked", False) else "✅"
                
                table_data.append({
                    "Timestamp": formatted_time,
                    "Input Text": inp.get("inputText", "")[:150] + ("..." if len(inp.get("inputText", "")) > 150 else ""),
                    "Risk Score": f"{risk_color} {risk_score:.1f}",
                    "Label": inp.get("label", "unknown"),
                    "Status": blocked_indicator,
                    "User ID": inp.get("userId", "N/A")[:20] if inp.get("userId") else "N/A"
                })
            
            # Create DataFrame
            df = pd.DataFrame(table_data)
            
            # Display table with styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                    "Input Text": st.column_config.TextColumn("Input Text", width="large"),
                    "Risk Score": st.column_config.TextColumn("Risk Score", width="small"),
                    "Label": st.column_config.TextColumn("Label", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "User ID": st.column_config.TextColumn("User ID", width="small")
                }
            )
            
            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"security_inputs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
    elif response.status_code == 404:
        st.info("No security inputs found. Start logging security inputs to see data here.")
    else:
        st.error(f"❌ Error: {response.status_code} - {response.text}")

except requests.exceptions.ConnectionError:
    st.error("❌ Could not connect to the API. Make sure the backend is running on http://localhost:8000")
    st.info("""
    **To start the backend:**
    ```bash
    cd backend
    python -m uvicorn api:app --reload
    ```
    """)
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")

# Sidebar information
st.sidebar.divider()
st.sidebar.markdown("""
## 📖 About Security Dashboard

This dashboard displays:
- **Recent Inputs**: All security inputs with timestamps
- **Risk Scores**: 0-100 scale (higher = more risky)
- **Labels**: safe, low-risk, medium-risk, high-risk, blocked
- **Blocked Status**: Whether the input was blocked

## 🔍 Filter Options

- **Label Filter**: Filter by risk category
- **Blocked Filter**: Show only blocked/not blocked
- **High-Risk Filter**: Show only inputs with risk ≥70

## 🔌 API Endpoints

- `POST /v1/security/inputs` - Log a security input
- `GET /v1/security/inputs` - Get security inputs with filters
""")

st.sidebar.divider()
st.sidebar.caption("Built with ❤️ by the Prompt Engineering Team")


