"""Security Dashboard page - Monitor security inputs and risk scores"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.api_client import API_BASE


def show_security_dashboard():
    """Show security input monitoring dashboard."""
    st.title("🔒 Security Dashboard")
    st.markdown("Monitor and analyze security inputs, risk scores, and blocked attempts")
    
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

