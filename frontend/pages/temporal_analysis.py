"""Temporal Analysis page - Timeline visualization and statistics"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from temporal_client import init_temporal_client
from utils.api_client import api_get


def show_temporal_analysis():
    """
    Temporal Analysis page with timeline visualization and statistics.
    Week 12: Temporal Prompt Learning & Causal Analysis
    """
    st.title("⏱️ Temporal Analysis")
    st.markdown("Analyze prompt evolution over time with trends, change-points, and causal hints")
    
    # Initialize temporal client with auth token
    temporal_client = init_temporal_client(token=st.session_state.access_token)
    
    # Get list of user's prompts from API (user-specific)
    try:
        response = api_get("/api/prompts", params={"limit": 50})
        
        if response.status_code != 200:
            st.error(f"Failed to load prompts: {response.status_code}")
            return
        
        prompts_data = response.json()
        if not prompts_data.get("success") or not prompts_data.get("data"):
                st.warning("⚠️ No prompts found. Create a prompt first using the Dashboard Prompt Enhancement.")
                if st.button("← Go to Dashboard"):
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                return
            
        prompts = prompts_data["data"]
        
        # Prompt selector
        prompt_options = {
            f"{p['original_text'][:60]}... ({p['created_at'][:10]})": p['id'] 
            for p in prompts
        }
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

