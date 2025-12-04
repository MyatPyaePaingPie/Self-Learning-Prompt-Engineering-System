"""Token Analytics page - Display token usage and cost tracking"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.api_client import api_get


def show_token_analytics():
    """Show token usage and cost analytics from database (Database-First Pattern 2025-12-04)."""
    st.title("💰 Token Usage & Cost Analytics")
    st.markdown("Real-time token tracking across all AI agents with model-specific pricing")
    
    # Query token history from database (not session state)
    try:
        response = api_get("/api/tokens", params={"limit": 100})
        
        if response.status_code != 200:
            st.error(f"❌ Failed to load token history: {response.status_code}")
            if st.button("← Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
            return
        
        result = response.json()
        
        if not result.get("success"):
            st.error("❌ Failed to load token history")
            return
        
        token_records = result["data"]
        total_tokens_all = result.get("total_tokens", 0)
        total_cost_all = result.get("total_cost", 0)
        
        if not token_records:
            st.info("📊 No token history yet. Enhance a prompt to start tracking!")
            if st.button("← Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
            return
        
        # Display aggregate metrics
        st.subheader("📊 Token Usage Summary (All Time)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tokens", f"{total_tokens_all:,}")
        
        with col2:
            st.metric("Total Cost", f"${total_cost_all:.6f}")
        
        with col3:
            st.metric("Total Requests", len(token_records))
        
        with col4:
            # Calculate average cost per request
            avg_cost = total_cost_all / len(token_records) if token_records else 0
            st.metric("Avg Cost/Request", f"${avg_cost:.6f}")
        
        st.divider()
        
        # Token history table
        st.subheader("📊 Token Usage History")
        
        # Prepare data for table
        table_data = {
            "Date": [],
            "Model": [],
            "Prompt Tokens": [],
            "Completion Tokens": [],
            "Total Tokens": [],
            "Cost (USD)": []
        }
        
        for record in token_records:
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(record["created_at"])
                formatted_date = timestamp.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = record["created_at"][:16]
            
            table_data["Date"].append(formatted_date)
            table_data["Model"].append(record["model"])
            table_data["Prompt Tokens"].append(record["prompt_tokens"])
            table_data["Completion Tokens"].append(record["completion_tokens"])
            table_data["Total Tokens"].append(record["total_tokens"])
            table_data["Cost (USD)"].append(f"${record['cost_usd']:.6f}")
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Token usage over time chart
        st.subheader("📈 Token Usage Over Time")
        
        # Convert for plotly
        chart_df = pd.DataFrame(token_records)
        chart_df['created_at'] = pd.to_datetime(chart_df['created_at'])
        chart_df = chart_df.sort_values('created_at')
        
        fig = px.line(
            chart_df,
            x='created_at',
            y='total_tokens',
            title='Token Usage Timeline',
            labels={'total_tokens': 'Total Tokens', 'created_at': 'Date'},
            markers=True
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Date",
            yaxis_title="Total Tokens"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model breakdown
        st.subheader("🤖 Usage by Model")
        
        model_stats = {}
        for record in token_records:
            model = record["model"]
            if model not in model_stats:
                model_stats[model] = {"count": 0, "tokens": 0, "cost": 0.0}
            model_stats[model]["count"] += 1
            model_stats[model]["tokens"] += record["total_tokens"]
            model_stats[model]["cost"] += record["cost_usd"]
        
        model_df = pd.DataFrame([
            {
                "Model": model,
                "Requests": stats["count"],
                "Total Tokens": f"{stats['tokens']:,}",
                "Total Cost": f"${stats['cost']:.6f}",
                "Avg Tokens/Request": f"{stats['tokens'] // stats['count']:,}"
            }
            for model, stats in model_stats.items()
        ])
        
        st.dataframe(model_df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Error loading token history: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

