import streamlit as st
import pandas as pd

st.set_page_config(page_title="Token Analytics", page_icon="💰", layout="wide")

st.title("💰 Token Usage & Cost Analytics")

# Check for data
if 'latest_result' not in st.session_state:
    st.warning("⚠️ No data available. Please analyze a prompt first!")
    st.page_link("pages/1_🏠_Home.py", label="← Go to Home", icon="🏠")
    st.stop()

data = st.session_state['latest_result']
token_metrics = data.get('token_metrics', {})

# Add explanation section at the top
with st.expander("ℹ️ **How Token Tracking Works**", expanded=False):
    st.markdown("""
    ### 🔍 What We Track
    
    This system tracks **4 LLM API calls** made during the prompt improvement process:
    
    1. **🔧 Prompt Improvement** - Generating the improved version of your prompt
    2. **🔴 Original Execution** - Running your original prompt through the LLM
    3. **🟢 Improved Execution** - Running the improved prompt through the LLM
    4. **⚖️ Quality Judging** - Evaluating the improved prompt's quality
    
    ### 💵 Cost Calculation (Groq Pricing for llama-3.3-70b-versatile)
    
    - **Input tokens** (prompts sent TO the LLM): **$0.59 per 1M tokens** = $0.00000059 per token
    - **Output tokens** (responses FROM the LLM): **$0.79 per 1M tokens** = $0.00000079 per token
    
    **Formula:** `Cost = (Input Tokens × $0.00000059) + (Output Tokens × $0.00000079)`
    
    ### 📊 Token Counting
    
    - Uses **tiktoken** library with `cl100k_base` encoding (GPT-4 compatible)
    - Accuracy: ±2% of actual API usage
    - Tokens ≠ Words (e.g., "Hello world" = 2 tokens, not 2 words)
    
    ### 🎯 ROI Calculation
    
    **"Is it worth it?"** = Quality improves by >5 points AND cost increases by <100%
    
    **ROI Score** = Quality Improvement ÷ Additional Cost (higher is better)
    """)

st.divider()

# Section 1: Overview Cards with Cost Comparison
st.subheader("📊 Overview")

# Add cost comparison section
st.markdown("### 💰 Cost Comparison: Original vs Improved")
comp_col1, comp_col2, comp_col3 = st.columns(3)

with comp_col1:
    st.metric(
        "🔴 Original Only", 
        f"${token_metrics['original_cost_usd']:.6f}",
        help="Cost if you just used your original prompt (1 API call)"
    )
    st.caption(f"{token_metrics['original_total_tokens']:,} tokens")

with comp_col2:
    st.metric(
        "🟢 Improved Only", 
        f"${token_metrics['improved_cost_usd']:.6f}",
        delta=f"{((token_metrics['improved_cost_usd'] / token_metrics['original_cost_usd']) - 1) * 100:+.1f}%" if token_metrics['original_cost_usd'] > 0 else None,
        delta_color="inverse",
        help="Cost if you just used the improved prompt (1 API call)"
    )
    st.caption(f"{token_metrics['improved_total_tokens']:,} tokens")

with comp_col3:
    total_process_cost = token_metrics['improvement_process_cost_usd'] + token_metrics['judging_cost_usd']
    st.metric(
        "🔧 Improvement Overhead", 
        f"${total_process_cost:.6f}",
        help="Additional cost to generate and evaluate the improvement"
    )
    st.caption(f"{token_metrics['improvement_process_tokens'] + token_metrics['judging_tokens']:,} tokens")

st.divider()

# Total metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tokens Used", f"{token_metrics['total_tokens_used']:,}")

with col2:
    st.metric("Total Cost (All 4 Calls)", f"${token_metrics['total_cost_usd']:.6f}")

with col3:
    st.metric("Quality Improvement", f"+{token_metrics['output_quality_improvement']:.1f} pts")

with col4:
    roi_emoji = "✅" if token_metrics['is_worth_it'] else "⚠️"
    st.metric("Worth It?", f"{roi_emoji} {'Yes' if token_metrics['is_worth_it'] else 'Maybe'}")

st.divider()

# Section 2: Detailed Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Comparison", 
    "🔍 Detailed Breakdown",
    "⚙️ Process Overhead", 
    "📈 Efficiency", 
    "💡 Insights"
])

with tab1:
    st.markdown("### Token Usage Comparison")
    
    comparison_df = pd.DataFrame({
        "Metric": ["Prompt Tokens", "Output Tokens", "Total Tokens", "Cost (USD)"],
        "🔴 Original": [
            f"{token_metrics['original_prompt_tokens']:,}",
            f"{token_metrics['original_output_tokens']:,}",
            f"{token_metrics['original_total_tokens']:,}",
            f"${token_metrics['original_cost_usd']:.6f}"
        ],
        "🟢 Improved": [
            f"{token_metrics['improved_prompt_tokens']:,}",
            f"{token_metrics['improved_output_tokens']:,}",
            f"{token_metrics['improved_total_tokens']:,}",
            f"${token_metrics['improved_cost_usd']:.6f}"
        ],
        "Δ Difference": [
            f"{token_metrics['improved_prompt_tokens'] - token_metrics['original_prompt_tokens']:+,}",
            f"{token_metrics['token_difference']:+,}",
            f"{token_metrics['improved_total_tokens'] - token_metrics['original_total_tokens']:+,}",
            f"${token_metrics['improved_cost_usd'] - token_metrics['original_cost_usd']:+.6f}"
        ]
    })
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### 🔍 Complete Cost Breakdown")
    st.markdown("**Every LLM API call tracked with full transparency:**")
    
    st.markdown("---")
    st.markdown("#### 1️⃣ Original Prompt Execution")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Input Tokens", f"{token_metrics['original_prompt_tokens']:,}")
        st.caption("Your original prompt")
    with col2:
        st.metric("Output Tokens", f"{token_metrics['original_output_tokens']:,}")
        st.caption("LLM's response")
    with col3:
        st.metric("Cost", f"${token_metrics['original_cost_usd']:.6f}")
        st.caption(f"({token_metrics['original_prompt_tokens']:,} × $0.00000059) + ({token_metrics['original_output_tokens']:,} × $0.00000079)")
    
    st.markdown("---")
    st.markdown("#### 2️⃣ Improved Prompt Execution")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Input Tokens", f"{token_metrics['improved_prompt_tokens']:,}")
        st.caption("Improved prompt")
    with col2:
        st.metric("Output Tokens", f"{token_metrics['improved_output_tokens']:,}")
        st.caption("LLM's response")
    with col3:
        st.metric("Cost", f"${token_metrics['improved_cost_usd']:.6f}")
        st.caption(f"({token_metrics['improved_prompt_tokens']:,} × $0.00000059) + ({token_metrics['improved_output_tokens']:,} × $0.00000079)")
    
    st.markdown("---")
    st.markdown("#### 3️⃣ Prompt Improvement Process")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tokens", f"{token_metrics['improvement_process_tokens']:,}")
        st.caption("System prompt + original prompt → improved prompt")
    with col2:
        st.metric("Cost", f"${token_metrics['improvement_process_cost_usd']:.6f}")
        st.caption("Cost to generate the improvement")
    
    st.markdown("---")
    st.markdown("#### 4️⃣ Quality Judging Process")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tokens", f"{token_metrics['judging_tokens']:,}")
        st.caption("Evaluation system prompt + improved prompt → scores")
    with col2:
        st.metric("Cost", f"${token_metrics['judging_cost_usd']:.6f}")
        st.caption("Cost to score the quality" if token_metrics['judging_tokens'] > 0 else "Heuristic scoring (no API call)")
    
    st.markdown("---")
    st.markdown("#### 💰 **TOTAL COST BREAKDOWN**")
    
    breakdown_df = pd.DataFrame({
        "Component": [
            "Original Prompt Execution",
            "Improved Prompt Execution", 
            "Improvement Generation",
            "Quality Judging",
            "**GRAND TOTAL**"
        ],
        "Tokens": [
            f"{token_metrics['original_total_tokens']:,}",
            f"{token_metrics['improved_total_tokens']:,}",
            f"{token_metrics['improvement_process_tokens']:,}",
            f"{token_metrics['judging_tokens']:,}",
            f"**{token_metrics['total_tokens_used']:,}**"
        ],
        "Cost (USD)": [
            f"${token_metrics['original_cost_usd']:.6f}",
            f"${token_metrics['improved_cost_usd']:.6f}",
            f"${token_metrics['improvement_process_cost_usd']:.6f}",
            f"${token_metrics['judging_cost_usd']:.6f}",
            f"**${token_metrics['total_cost_usd']:.6f}**"
        ],
        "% of Total": [
            f"{(token_metrics['original_cost_usd'] / token_metrics['total_cost_usd'] * 100):.1f}%",
            f"{(token_metrics['improved_cost_usd'] / token_metrics['total_cost_usd'] * 100):.1f}%",
            f"{(token_metrics['improvement_process_cost_usd'] / token_metrics['total_cost_usd'] * 100):.1f}%",
            f"{(token_metrics['judging_cost_usd'] / token_metrics['total_cost_usd'] * 100 if token_metrics['total_cost_usd'] > 0 else 0):.1f}%",
            "**100.0%**"
        ]
    })
    
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### Process Overhead Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Improvement Process",
            f"{token_metrics['improvement_process_tokens']:,} tokens",
            f"${token_metrics['improvement_process_cost_usd']:.6f}"
        )
    
    with col2:
        st.metric(
            "Judging Process",
            f"{token_metrics['judging_tokens']:,} tokens",
            f"${token_metrics['judging_cost_usd']:.6f}"
        )
    
    st.markdown("### Cost Distribution")
    cost_data = pd.DataFrame({
        "Component": ["Original Exec", "Improved Exec", "Improvement", "Judging"],
        "Cost (USD)": [
            token_metrics['original_cost_usd'],
            token_metrics['improved_cost_usd'],
            token_metrics['improvement_process_cost_usd'],
            token_metrics['judging_cost_usd']
        ]
    })
    st.bar_chart(cost_data, x="Component", y="Cost (USD)")

with tab4:
    st.markdown("### Efficiency Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Output Verbosity Change",
            f"{token_metrics['token_efficiency_percent']:+.1f}%",
            help="How much more/less verbose is the improved output"
        )
        st.metric(
            "Cost per Quality Point",
            f"${token_metrics['cost_per_quality_point']:.8f}",
            help="Cost per point of quality improvement"
        )
    
    with col2:
        st.metric(
            "ROI Score",
            f"{token_metrics['roi_score']:.2f}",
            help="Return on investment (higher is better)"
        )

with tab5:
    st.markdown("### 💡 Key Insights")
    
    if token_metrics['is_worth_it']:
        st.success("✅ **Excellent Value!** The quality improvement justifies the additional cost.")
    else:
        st.warning("⚠️ **Consider Cost-Benefit:** The quality improvement may not justify the cost increase.")
    
    if token_metrics['token_efficiency_percent'] > 100:
        st.info(f"📝 The improved prompt generated {token_metrics['token_efficiency_percent']:.0f}% more detailed output.")
    elif token_metrics['token_efficiency_percent'] < -10:
        st.info(f"📝 The improved prompt generated {abs(token_metrics['token_efficiency_percent']):.0f}% more concise output.")
    
    if token_metrics['cost_per_quality_point'] < 0.0001:
        st.success("💰 Very cost-efficient improvement! Low cost per quality point.")

# Back button
st.divider()
st.page_link("pages/1_🏠_Home.py", label="← Back to Home", icon="🏠")
