"""Agent Effectiveness page - Track agent performance statistics"""
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from temporal_client import init_temporal_client
from packages.db.session import get_session
from packages.db.models import Prompt, PromptVersion, JudgeScore
from utils.api_client import API_BASE


def show_agent_effectiveness():
    """Display agent effectiveness statistics (Database-First Pattern)"""
    st.title("📈 Agent Effectiveness Dashboard")
    st.markdown("Track which agents perform best over time")
    
    # Fetch effectiveness data from backend (queries database, not CSV)
    with st.spinner("Loading agent statistics from database..."):
        try:
            response = requests.get(
                f"{API_BASE}/api/agents/effectiveness",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                effectiveness = result.get("effectiveness", {})
            else:
                st.error(f"Failed to fetch data: {response.status_code}")
                effectiveness = {}
        except Exception as e:
            st.error(f"Failed to fetch effectiveness: {e}")
            effectiveness = {}
    
    if not effectiveness:
        st.info("No multi-agent requests yet. Try enhancing a prompt first!")
        return
    
    # Overall statistics
    st.subheader("Overall Performance")
    
    cols = st.columns(len(effectiveness))
    for col, (agent_name, stats) in zip(cols, effectiveness.items()):
        with col:
            st.metric(
                agent_name.title(),
                f"{stats['wins']} wins",
                f"{stats['win_rate']:.0%} win rate"
            )
            st.caption(f"Avg Score: {stats['avg_score']:.1f}/10")
    
    # Win rate comparison chart
    st.subheader("Win Rate Comparison")
    display_win_rate_chart(effectiveness)
    
    # Detailed statistics table
    st.subheader("Detailed Statistics")
    display_effectiveness_table(effectiveness)
    
    # Token usage by agent (if available)
    if 'latest_multi_agent_result' in st.session_state:
        st.divider()
        st.subheader("💰 Token Usage by Agent")
        st.markdown("Real-time cost and token tracking for each agent")
        
        data = st.session_state['latest_multi_agent_result']
        token_usage = data.get('token_usage', {})
        
        if token_usage:
            # Create DataFrame for agent token usage
            token_data = {
                "Agent": [],
                "Model": [],
                "Tokens Used": [],
                "Cost (USD)": [],
                "Efficiency": []
            }
            
            for agent_name, usage in token_usage.items():
                token_data["Agent"].append(agent_name.capitalize())
                token_data["Model"].append(usage.get('model', 'N/A'))
                token_data["Tokens Used"].append(usage.get('total_tokens', 0))
                token_data["Cost (USD)"].append(usage.get('cost_usd', 0))
                
                # Calculate efficiency (tokens per dollar)
                cost = usage.get('cost_usd', 0)
                tokens = usage.get('total_tokens', 0)
                efficiency = tokens / cost if cost > 0 else 0
                token_data["Efficiency"].append(f"{efficiency:,.0f} tokens/$")
            
            df_tokens = pd.DataFrame(token_data)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_tokens = sum(token_data["Tokens Used"])
                st.metric("Total Tokens", f"{total_tokens:,}")
            with col2:
                total_cost = sum(token_data["Cost (USD)"])
                st.metric("Total Cost", f"${total_cost:.6f}")
            with col3:
                avg_cost_per_1k = (total_cost / total_tokens * 1000) if total_tokens > 0 else 0
                st.metric("Avg Cost/1K Tokens", f"${avg_cost_per_1k:.4f}")
            
            # Display table
            st.dataframe(df_tokens, width='stretch', hide_index=True)
            
            # Token efficiency chart
            fig = go.Figure(data=[
                go.Bar(
                    x=token_data["Agent"],
                    y=token_data["Tokens Used"],
                    name="Tokens Used",
                    marker_color='#667eea',
                    hovertemplate='<b>%{x}</b><br>Tokens: %{y:,}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="Token Usage by Agent",
                xaxis_title="Agent",
                yaxis_title="Tokens Used",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, width='stretch')
            
            st.info("💡 Lower token usage = lower costs. Fast models (8B) use fewer tokens than powerful models (70B).")
        else:
            st.info("No token usage data available. Run a multi-agent enhancement to see token tracking.")
    
    # Darwinian Feedback Stats (Phase 1)
    st.divider()
    st.subheader("🧬 Darwinian Learning Progress")
    st.markdown("System learning from user feedback to improve agent selection")
    
    # Extract metadata from effectiveness
    metadata = effectiveness.get('_metadata', {})
    
    if metadata:
        feedback_rate = metadata.get('feedback_rate', 0.0)
        total_feedback = metadata.get('total_feedback', 0)
        total_requests = metadata.get('total_requests', 0)
        learning_status = metadata.get('learning_status', 'Cold Start')
        
        # Display learning progress metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Learning Status", learning_status)
        
        with col2:
            st.metric("Feedback Rate", f"{feedback_rate:.0%}", 
                     help="Percentage of requests with user feedback")
        
        with col3:
            st.metric("Total Feedback", total_feedback,
                     help="Number of requests with user feedback")
        
        with col4:
            st.metric("Total Requests", total_requests)
        
        # Display per-agent feedback stats
        if total_feedback > 0:
            st.markdown("**Agent Performance with User Feedback:**")
            
            feedback_data = {
                "Agent": [],
                "Judge Wins": [],
                "User Wins": [],
                "User Win Rate": [],
                "Judge Accuracy": []
            }
            
            for agent_name, stats in effectiveness.items():
                if agent_name != '_metadata':
                    feedback_data["Agent"].append(agent_name.title())
                    feedback_data["Judge Wins"].append(stats.get('wins', 0))
                    feedback_data["User Wins"].append(stats.get('user_wins', 0))
                    feedback_data["User Win Rate"].append(f"{stats.get('user_win_rate', 0):.0%}")
                    feedback_data["Judge Accuracy"].append(f"{stats.get('judge_accuracy', 0):.0%}")
            
            df_feedback = pd.DataFrame(feedback_data)
            st.dataframe(df_feedback, width='stretch', hide_index=True)
            
            st.caption("**Judge Wins:** How often the judge selected this agent")
            st.caption("**User Wins:** How often users validated this agent's superiority")
            st.caption("**User Win Rate:** Percentage of user feedback selecting this agent")
            st.caption("**Judge Accuracy:** How often the judge's selection matched user choice")
        
        # Learning status explanation
        if learning_status == "Cold Start":
            st.info("🧊 **Cold Start:** No feedback yet. System using equal weights for all agents.")
        elif learning_status == "Warming Up":
            st.warning(f"🔥 **Warming Up:** {total_feedback} feedback events collected. Need 10+ for learning.")
        else:
            st.success(f"✅ **Learned:** {total_feedback} feedback events. System adapting to your preferences!")
    else:
        st.info("No feedback data yet. Use 'Compare All' mode and vote to help the system learn!")
    
    # Temporal Analysis Widget (Week 12)
    st.markdown("---")
    st.subheader("⏱️ Agent Performance Over Time")
    st.markdown("Track how agent effectiveness evolves")
    
    with st.expander("📈 View Performance Trends", expanded=False):
        try:
            temporal_client = init_temporal_client(token=st.session_state.access_token)
            
            # Get user's prompts from API (for agent effectiveness)
            response = requests.get(
                f"{API_BASE}/api/prompts?limit=10",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            
            if response.status_code == 200:
                prompts_data = response.json()
                if prompts_data.get("success") and prompts_data.get("data"):
                    prompts_with_agents = prompts_data["data"]
                    st.info("💡 View temporal trends for each agent type to identify which strategies improve over time")
                    
                    # Get agent-specific trends
                    agent_trends = {}
                    session = get_session()
                    
                    for agent_name in ['syntax', 'structure', 'domain']:
                        # Get versions for this agent type
                        agent_versions = session.query(PromptVersion).filter(
                            PromptVersion.source == agent_name
                        ).order_by(PromptVersion.created_at).limit(30).all()
                        
                        if agent_versions:
                            # Calculate simple trend
                            scores = []
                            for v in agent_versions:
                                # Get judge score if available
                                judge = session.query(JudgeScore).filter(
                                    JudgeScore.prompt_version_id == v.id
                                ).first()
                                
                                if judge:
                                    avg_score = (judge.clarity + judge.specificity + judge.actionability + judge.structure + judge.context_use) / 5.0
                                    scores.append(avg_score)
                            
                            if scores:
                                agent_trends[agent_name] = {
                                    'count': len(scores),
                                    'avg_score': sum(scores) / len(scores),
                                    'trend': 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable'
                                }
                    
                    if agent_trends:
                        col1, col2, col3 = st.columns(3)
                        
                        for col, (agent, stats) in zip([col1, col2, col3], agent_trends.items()):
                            with col:
                                trend_icon = "📈" if stats['trend'] == 'improving' else "➡️"
                                st.metric(
                                    f"{agent.title()} Agent",
                                    f"{stats['avg_score']:.1f}",
                                    f"{trend_icon} {stats['trend'].title()}"
                                )
                                st.caption(f"{stats['count']} versions analyzed")
                        
                        st.success("💡 **Insight:** Use temporal data to identify which agent types consistently improve and allocate resources accordingly")
                    else:
                        st.info("💡 No score data available. Enhance prompts with multi-agent to track trends.")
                else:
                    st.info("💡 No agent data found. Use Multi-Agent Enhancement to create agent versions.")
        
        except Exception as e:
            st.warning(f"Performance trends unavailable: {str(e)}")
            st.info("💡 Use the Temporal Analysis page for detailed agent performance tracking")


def display_win_rate_chart(effectiveness):
    """Display win rate as progress bars"""
    # Alternative: Use columns for visual representation
    total_wins = sum(stats["wins"] for stats in effectiveness.values())
    
    if total_wins > 0:
        st.write("**Distribution of Winning Agents:**")
        for agent_name, stats in effectiveness.items():
            percentage = stats["wins"] / total_wins * 100
            st.progress(stats["wins"] / total_wins, text=f"{agent_name.title()}: {percentage:.1f}%")
    else:
        st.info("No wins recorded yet")


def display_effectiveness_table(effectiveness):
    """Display effectiveness as detailed table"""
    # Create DataFrame
    df = pd.DataFrame([
        {
            "Agent": name.title(),
            "Wins": stats["wins"],
            "Win Rate": f"{stats['win_rate']:.1%}",
            "Avg Score": f"{stats['avg_score']:.1f}/10"
        }
        for name, stats in effectiveness.items()
    ])
    
    # Sort by wins descending
    df = df.sort_values("Wins", ascending=False)
    
    st.dataframe(df, hide_index=True, width='stretch')

