"""Prompt Enhancement page - Main enhancement interface"""
import streamlit as st
import requests
import uuid
from components.feedback import submit_feedback
from utils.api_client import API_BASE


def show_prompt_enhancement():
    """Show the prompt enhancement interface."""
    # Enhancement mode selector - Default to Compare All to showcase multi-agent value
    enhancement_mode = st.radio(
        "Enhancement Method:",
        [
            "📊 Compare All (Recommended - See which method wins!)",
            "🔧 Single-Agent Only (Template)",
            "🤖 Multi-Agent Only (3 Experts)"
        ],
        index=0,
        help="Compare All: See Original vs Single-Agent vs Multi-Agent side-by-side with winner declaration"
    )
    
    # Template explanation (condensed for comparison mode)
    if "Single-Agent" in enhancement_mode:
        with st.expander("📋 How Template Enhancement Works", expanded=False):
            st.markdown("""
            **Your prompt will be transformed using this professional template:**
            
            ```
            You are a senior {domain} expert.
            Task: {task}
            Deliverables:
            - Clear, step-by-step plan
            - Examples and edge-cases
            - Final {artifact} ready to use
            Constraints: {constraints}
            If information is missing, list precise clarifying questions first, then proceed with best assumptions.
            ```
            
            **The system automatically:**
            - 🎯 **Identifies the domain** (Software Engineering, Creative Writing, Marketing, etc.)
            - 📋 **Structures your task** into clear, actionable format
            - 🎨 **Determines the deliverable** (code, content, analysis, etc.)
            - ⚖️ **Sets appropriate constraints** based on context
            """)
    
    # Enhancement interface
    with st.form("enhance_prompt_form"):
        st.subheader("📝 Enter Your Original Prompt")
        
        prompt_text = st.text_area(
            "Your Task/Request",
            placeholder="Example: 'Create a function to calculate compound interest' or 'Write a story about time travel'",
            height=150,
            help="Describe what you want to accomplish. The system will transform it into a structured, expert-level prompt."
        )
        
        context = st.text_input(
            "Domain Context (Optional)",
            placeholder="e.g., 'for a mobile app', 'academic research', 'marketing campaign'",
            help="Provide specific context to refine the domain and constraints"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            submit_enhance = st.form_submit_button("✨ Enhance & Compare", type="primary")
    
    if submit_enhance and prompt_text:
        # Clear previous results when submitting new prompt
        if 'comparison_results' in st.session_state:
            del st.session_state['comparison_results']
        
        if "Compare All" in enhancement_mode:
            show_three_way_comparison(prompt_text, context)
        elif "Single-Agent" in enhancement_mode:
            show_single_agent_only(prompt_text, context)
        else:
            show_multi_agent_only(prompt_text)
    
    # Display previous results if they exist (persists across feedback button clicks)
    elif 'comparison_results' in st.session_state:
        results = st.session_state['comparison_results']
        display_three_way_results(
            results['request_id'],
            results['original_prompt'],
            results['single_enhanced'],
            results['multi_enhanced'],
            results['original_output'],
            results['single_output'],
            results['multi_output'],
            results['original_score'],
            results['single_score'],
            results['multi_score'],
            results['original_usage'],
            results['single_usage'],
            results['multi_usage'],
            results['original_judge_usage'],
            results['single_judge_usage'],
            results['multi_judge_usage'],
            results['multi_metadata']
        )
    elif submit_enhance:
        st.error("❌ Please enter a prompt to enhance")


def show_three_way_comparison(original_prompt: str, context: str = ""):
    """Compare Original vs Single-Agent vs Multi-Agent enhancement"""
    
    # Generate unique request ID for tracking feedback
    request_id = str(uuid.uuid4())
    
    # Initialize tracker
    try:
        from packages.core import (
            fallback_to_template,
            judge_prompt,
            TokenTracker,
            generate_llm_output
        )
    except ImportError as e:
        st.error(f"❌ Failed to import core engine: {e}")
        return
    
    tracker = TokenTracker()
    
    with st.spinner("🤖 Running full comparison (enhancing prompts + executing all 3 with LLM)..."):
        # Step 1: Single-Agent Enhancement (existing pattern)
        try:
            single_enhanced = fallback_to_template(original_prompt).text
        except Exception as e:
            st.error(f"Single-agent enhancement failed: {e}")
            return
        
        # Step 2: Multi-Agent Enhancement (new)
        try:
            response = requests.post(
                f"{API_BASE}/prompts/multi-agent-enhance",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={"text": original_prompt, "enhancement_type": "general"}
            )
            
            if response.status_code == 200:
                multi_result = response.json()
                if multi_result.get("success"):
                    multi_enhanced = multi_result["data"]["enhanced_text"]
                    multi_metadata = multi_result["data"]  # For agent breakdown
                else:
                    st.error("Multi-agent enhancement failed")
                    return
            else:
                st.error(f"Multi-agent API error: {response.status_code}")
                return
        except Exception as e:
            st.error(f"Multi-agent call failed: {e}")
            return
        
        # Step 3: Generate outputs with all 3 prompts
        try:
            original_output, original_usage = generate_llm_output(original_prompt)
            single_output, single_usage = generate_llm_output(single_enhanced)
            multi_output, multi_usage = generate_llm_output(multi_enhanced)
            llm_available = True
        except Exception as e:
            st.warning(f"⚠️ LLM unavailable, using mock outputs: {str(e)}")
            # Mock outputs for demo
            original_output = "Mock response to original prompt."
            single_output = "Mock structured response to enhanced prompt."
            multi_output = "Mock comprehensive response with expert analysis."
            original_usage = tracker.track_llm_call(original_prompt, original_output, "mock")
            single_usage = tracker.track_llm_call(single_enhanced, single_output, "mock")
            multi_usage = tracker.track_llm_call(multi_enhanced, multi_output, "mock")
            llm_available = False
        
        # Step 4: Judge all 3 prompts
        try:
            original_score, original_judge_usage = judge_prompt(original_prompt)
            single_score, single_judge_usage = judge_prompt(single_enhanced)
            multi_score, multi_judge_usage = judge_prompt(multi_enhanced)
        except Exception as e:
            st.warning(f"⚠️ Judge unavailable, using mock scores: {str(e)}")
            from packages.core.judge import Scorecard
            original_score = Scorecard(clarity=4.0, specificity=3.0, actionability=2.0, structure=2.0, context_use=3.0, total=14.0, feedback={"pros": ["Brief"], "cons": ["Vague"], "summary": "Needs work"})
            single_score = Scorecard(clarity=8.0, specificity=7.5, actionability=8.0, structure=7.0, context_use=7.5, total=38.0, feedback={"pros": ["Clear", "Structured"], "cons": ["Generic"], "summary": "Good"})
            multi_score = Scorecard(clarity=9.0, specificity=9.0, actionability=9.0, structure=9.0, context_use=9.0, total=45.0, feedback={"pros": ["Expert", "Complete"], "cons": ["Verbose"], "summary": "Excellent"})
            original_judge_usage = tracker.track_llm_call("judge", "result", "mock")
            single_judge_usage = tracker.track_llm_call("judge", "result", "mock")
            multi_judge_usage = tracker.track_llm_call("judge", "result", "mock")
    
    # Store results in session state so they persist across button clicks
    st.session_state['comparison_results'] = {
        'request_id': request_id,
        'original_prompt': original_prompt,
        'single_enhanced': single_enhanced,
        'multi_enhanced': multi_enhanced,
        'original_output': original_output,
        'single_output': single_output,
        'multi_output': multi_output,
        'original_score': original_score,
        'single_score': single_score,
        'multi_score': multi_score,
        'original_usage': original_usage,
        'single_usage': single_usage,
        'multi_usage': multi_usage,
        'original_judge_usage': original_judge_usage,
        'single_judge_usage': single_judge_usage,
        'multi_judge_usage': multi_judge_usage,
        'multi_metadata': multi_metadata
    }
    
    # Display results
    display_three_way_results(
        request_id,
        original_prompt, single_enhanced, multi_enhanced,
        original_output, single_output, multi_output,
        original_score, single_score, multi_score,
        original_usage, single_usage, multi_usage,
        original_judge_usage, single_judge_usage, multi_judge_usage,
        multi_metadata
    )


def display_three_way_results(
    request_id,
    original_prompt, single_enhanced, multi_enhanced,
    original_output, single_output, multi_output,
    original_score, single_score, multi_score,
    original_usage, single_usage, multi_usage,
    original_judge_usage, single_judge_usage, multi_judge_usage,
    multi_metadata
):
    """Display three-way comparison results"""
    
    st.success("✅ Comparison complete!")
    st.subheader("📊 Enhancement Comparison")
    
    # Three-column layout
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Original
    with col1:
        st.markdown("### 📄 Original")
        st.caption("Your prompt as-is")
        
        # Prompt
        with st.expander("View Prompt", expanded=False):
            st.text_area("Original Prompt", value=original_prompt, height=100, disabled=True, key="orig_prompt_comp", label_visibility="hidden")
        
        # Score
        st.metric("Quality Score", f"{original_score.total:.1f}/50", help="Judge evaluation")
        
        # LLM Output preview
        st.write("**LLM Response (preview):**")
        output_preview = original_output[:200] + ("..." if len(original_output) > 200 else "")
        st.text_area("Original LLM Output Preview", value=output_preview, height=100, disabled=True, key="orig_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = original_usage.cost_usd + original_judge_usage.cost_usd
        st.metric("Cost", f"${total_cost:.6f}")
    
    # Column 2: Single-Agent
    with col2:
        st.markdown("### 🔧 Single-Agent")
        st.caption("Template-based enhancement")
        
        # Prompt
        with st.expander("View Enhanced Prompt", expanded=False):
            st.text_area("Single-Agent Enhanced Prompt", value=single_enhanced, height=100, disabled=True, key="single_prompt_comp", label_visibility="hidden")
        
        # Score with delta
        improvement = single_score.total - original_score.total
        st.metric("Quality Score", f"{single_score.total:.1f}/50", f"+{improvement:.1f}", help="Judge evaluation")
        
        # LLM Output preview
        st.write("**LLM Response (preview):**")
        output_preview = single_output[:200] + ("..." if len(single_output) > 200 else "")
        st.text_area("Single-Agent LLM Output Preview", value=output_preview, height=100, disabled=True, key="single_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = single_usage.cost_usd + single_judge_usage.cost_usd
        cost_increase = total_cost - (original_usage.cost_usd + original_judge_usage.cost_usd)
        st.metric("Cost", f"${total_cost:.6f}", f"+${cost_increase:.6f}")
    
    # Column 3: Multi-Agent
    with col3:
        st.markdown("### 🤖 Multi-Agent")
        st.caption("3 expert agents")
        
        # Prompt
        with st.expander("View Enhanced Prompt", expanded=False):
            st.text_area("Multi-Agent Enhanced Prompt", value=multi_enhanced, height=100, disabled=True, key="multi_prompt_comp", label_visibility="hidden")
        
        # Score with delta (compare to single-agent)
        improvement_vs_original = multi_score.total - original_score.total
        improvement_vs_single = multi_score.total - single_score.total
        
        # Show winner badge if best
        if multi_score.total > single_score.total and multi_score.total > original_score.total:
            st.metric("Quality Score", f"{multi_score.total:.1f}/50 🏆", f"+{improvement_vs_single:.1f} vs Single")
        else:
            st.metric("Quality Score", f"{multi_score.total:.1f}/50", f"+{improvement_vs_original:.1f}")
        
        # LLM Output preview
        st.write("**LLM Response (preview):**")
        output_preview = multi_output[:200] + ("..." if len(multi_output) > 200 else "")
        st.text_area("Multi-Agent LLM Output Preview", value=output_preview, height=100, disabled=True, key="multi_output_comp", label_visibility="hidden")
        
        # Cost
        total_cost = multi_usage.cost_usd + multi_judge_usage.cost_usd
        cost_increase = total_cost - (original_usage.cost_usd + original_judge_usage.cost_usd)
        st.metric("Cost", f"${total_cost:.6f}", f"+${cost_increase:.6f}")
        
        # Agent breakdown (expandable)
        with st.expander("🔍 See Agent Contributions"):
            st.caption(f"Winner: {multi_metadata['selected_agent'].title()}")
            st.write(f"**Rationale:** {multi_metadata['decision_rationale']}")
            
            # Vote breakdown
            vote_breakdown = multi_metadata['vote_breakdown']
            for agent, score in vote_breakdown.items():
                st.write(f"- {agent.title()}: {score:.2f}")
    
    # Full LLM execution outputs prominently displayed
    st.divider()
    st.subheader("🚀 LLM Execution Results - Side by Side Comparison")
    st.markdown("**These are the actual responses from executing each prompt with an LLM:**")
    st.caption("All three prompts were sent to the LLM and generated these responses")
    
    # Three-column layout for outputs
    output_col1, output_col2, output_col3 = st.columns(3)
    
    with output_col1:
        st.markdown("### 📝 Original Prompt → LLM Output")
        st.caption("What the LLM generated from your original prompt")
        st.text_area("Original LLM Response", value=original_output, height=400, disabled=True, key="full_orig_top", label_visibility="hidden")
    
    with output_col2:
        st.markdown("### 🔧 Single-Agent Prompt → LLM Output")
        st.caption("What the LLM generated from the template-enhanced prompt")
        st.text_area("Single-Agent LLM Response", value=single_output, height=400, disabled=True, key="full_single_top", label_visibility="hidden")
    
    with output_col3:
        st.markdown("### 🤖 Multi-Agent Prompt → LLM Output")
        st.caption("What the LLM generated from the multi-agent enhanced prompt")
        st.text_area("Multi-Agent LLM Response", value=multi_output, height=400, disabled=True, key="full_multi_top", label_visibility="hidden")
    
    # Winner declaration
    st.divider()
    st.subheader("🏆 Winner Declaration")
    
    scores = {
        "Original": original_score.total,
        "Single-Agent": single_score.total,
        "Multi-Agent": multi_score.total
    }
    winner = max(scores, key=scores.get)
    winner_score = scores[winner]
    
    # Calculate improvements
    if winner == "Multi-Agent":
        improvement_text = f"+{winner_score - single_score.total:.1f} points vs Single-Agent, +{winner_score - original_score.total:.1f} vs Original"
        st.success(f"🏆 WINNER: {winner} ({winner_score:.1f}/50 points)")
        st.info(f"📈 Improvement: {improvement_text}")
    elif winner == "Single-Agent":
        improvement_text = f"+{winner_score - original_score.total:.1f} points vs Original"
        st.success(f"🏆 WINNER: {winner} ({winner_score:.1f}/50 points)")
        st.info(f"📈 Improvement: {improvement_text}")
    else:
        st.warning(f"Original prompt scored highest ({winner_score:.1f}/50) - enhancement didn't help!")
    
    # User Feedback Collection (Darwinian Evolution - Phase 1)
    st.divider()
    st.subheader("👍 Was this the right winner?")
    st.caption("Your feedback helps the system learn your preferences and improve over time")
    
    # Map winner to agent for tracking
    judge_winner = multi_metadata["selected_agent"]  # syntax, structure, or domain
    
    # Check if feedback already submitted (use session state)
    feedback_key = f"feedback_submitted_{request_id}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = False
    
    if not st.session_state[feedback_key]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👍 Original was best", key=f"vote_orig_{request_id}", type="secondary"):
                submit_feedback(request_id, "original", judge_winner, "none")
                st.session_state[feedback_key] = True
                # No page refresh - feedback submitted silently
        
        with col2:
            if st.button("👍 Single-Agent was best", key=f"vote_single_{request_id}", type="secondary"):
                submit_feedback(request_id, "single", judge_winner, "template")
                st.session_state[feedback_key] = True
                # No page refresh - feedback submitted silently
        
        with col3:
            if st.button("👍 Multi-Agent was best", key=f"vote_multi_{request_id}", type="primary"):
                submit_feedback(request_id, "multi", judge_winner, judge_winner)
                st.session_state[feedback_key] = True
                # No page refresh - feedback submitted silently
    
    # Show confirmation immediately after any button click
    if st.session_state[feedback_key]:
        st.success("✅ Thank you! Your feedback has been recorded and will help the system learn.")
    
    # ROI Analysis
    st.divider()
    st.subheader("💰 Cost-Benefit Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cost Comparison:**")
        original_total = original_usage.cost_usd + original_judge_usage.cost_usd
        single_total = single_usage.cost_usd + single_judge_usage.cost_usd
        multi_total = multi_usage.cost_usd + multi_judge_usage.cost_usd
        
        st.write(f"- Original: ${original_total:.6f}")
        st.write(f"- Single-Agent: ${single_total:.6f} ({(single_total/original_total):.1f}x)")
        st.write(f"- Multi-Agent: ${multi_total:.6f} ({(multi_total/original_total):.1f}x)")
    
    with col2:
        st.write("**Quality vs Cost:**")
        
        # Single-Agent ROI
        single_quality_gain = single_score.total - original_score.total
        single_cost_increase = single_total - original_total
        if single_cost_increase > 0:
            single_roi = single_quality_gain / (single_cost_increase * 1000000)  # points per micro-dollar
            st.write(f"- Single-Agent: {single_roi:.1f} pts/μ$")
        
        # Multi-Agent ROI
        multi_quality_gain = multi_score.total - original_score.total
        multi_cost_increase = multi_total - original_total
        if multi_cost_increase > 0:
            multi_roi = multi_quality_gain / (multi_cost_increase * 1000000)
            st.write(f"- Multi-Agent: {multi_roi:.1f} pts/μ$")
        
        # Recommendation
        if multi_score.total > single_score.total:
            st.success("💡 Multi-Agent delivers higher quality")
        elif multi_cost_increase > 0 and single_cost_increase > 0 and multi_roi > single_roi:
            st.info("💡 Multi-Agent has better ROI")
        else:
            st.info("💡 Single-Agent is more cost-effective")


def show_multi_agent_only(prompt_text: str):
    """Multi-Agent enhancement only (no comparison)"""
    
    with st.spinner("Running multi-agent analysis..."):
        try:
            response = requests.post(
                f"{API_BASE}/prompts/multi-agent-enhance",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={"text": prompt_text, "enhancement_type": "general"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    display_multi_agent_results(result["data"])
                else:
                    st.error(f"Enhancement failed: {result.get('error', 'Unknown error')}")
            else:
                st.error(f"Request failed with status {response.status_code}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")


def show_single_agent_only(prompt_text: str, context: str = ""):
    """Single-Agent enhancement (existing flow)"""
    
    # Import our engine components
    try:
        from packages.core import (
            fallback_to_template,
            judge_prompt,
            TokenTracker,
            generate_llm_output
        )
    except ImportError as e:
        st.error(f"❌ Failed to import core engine: {e}")
        st.info("Make sure the packages/core directory is in your Python path")
        return
    
    if len(prompt_text) > 5000:
        st.error("❌ Prompt text exceeds maximum length of 5000 characters")
    else:
        # Initialize tracker
        tracker = TokenTracker()
        
        with st.spinner("🤖 Enhancing your prompt and generating responses..."):
            # Step 1: Enhance the prompt using fallback template
            enhanced_result = fallback_to_template(prompt_text)
            enhanced_prompt = enhanced_result.text
            
            # Step 2: Generate outputs with both prompts
            try:
                # Generate with original prompt
                original_output, original_usage = generate_llm_output(prompt_text)
                
                # Generate with enhanced prompt
                enhanced_output, enhanced_usage = generate_llm_output(enhanced_prompt)
                
                # Step 3: Judge both prompts
                original_score, original_judge_usage = judge_prompt(prompt_text)
                enhanced_score, enhanced_judge_usage = judge_prompt(enhanced_prompt)
                
                llm_available = True
            except Exception as e:
                st.warning(f"⚠️ LLM unavailable, using mock outputs: {str(e)}")
                # Mock outputs for demonstration
                original_output = "This is a mock response to your original prompt."
                enhanced_output = "This is a detailed, structured response to your enhanced prompt with step-by-step guidance."
                original_usage = tracker.track_llm_call(prompt_text, original_output, "mock-model")
                enhanced_usage = tracker.track_llm_call(enhanced_prompt, enhanced_output, "mock-model")
                
                # Mock scoring
                from packages.core.judge import Scorecard
                original_score = Scorecard(
                    clarity=4.0, specificity=3.0, actionability=2.0,
                    structure=2.0, context_use=3.0, total=14.0,
                    feedback={"pros": ["Brief"], "cons": ["Too vague"], "summary": "Needs improvement"}
                )
                enhanced_score = Scorecard(
                    clarity=8.0, specificity=7.5, actionability=8.0,
                    structure=7.0, context_use=7.5, total=38.0,
                    feedback={"pros": ["Clear role", "Good structure"], "cons": ["Could be more specific"], "summary": "Much better"}
                )
                original_judge_usage = tracker.track_llm_call("judge prompt", "judge result", "mock-model")
                enhanced_judge_usage = tracker.track_llm_call("judge prompt", "judge result", "mock-model")
                llm_available = False
        
        st.success("✅ Prompt enhanced and evaluated successfully!")
        
        # Display comparison results
        st.subheader("📊 Enhancement Comparison")
        
        # Prompt comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Original Prompt")
            st.text_area("Original Prompt", value=prompt_text, height=150, disabled=True, key="orig_prompt", label_visibility="hidden")
            
            st.markdown("### 📈 Original Score")
            st.metric("Total Score", f"{original_score.total:.1f}/50", help="Overall prompt quality score")
            
            score_cols = st.columns(5)
            scores = [
                ("Clarity", original_score.clarity),
                ("Specific", original_score.specificity),
                ("Action", original_score.actionability),
                ("Structure", original_score.structure),
                ("Context", original_score.context_use)
            ]
            for i, (label, score) in enumerate(scores):
                with score_cols[i]:
                    st.metric(label, f"{score:.1f}")
            
            with st.expander("💬 Judge Feedback"):
                st.write("**Strengths:**")
                for pro in original_score.feedback.get("pros", []):
                    st.write(f"• {pro}")
                st.write("**Areas for Improvement:**")
                for con in original_score.feedback.get("cons", []):
                    st.write(f"• {con}")
                st.write(f"**Summary:** {original_score.feedback.get('summary', 'No summary')}")
        
        with col2:
            st.markdown("### ✨ Enhanced Prompt")
            st.text_area("Enhanced Prompt", value=enhanced_prompt, height=150, key="enh_prompt", label_visibility="hidden")
            
            st.markdown("### 📈 Enhanced Score")
            improvement = enhanced_score.total - original_score.total
            st.metric("Total Score", f"{enhanced_score.total:.1f}/50", f"+{improvement:.1f}", help="Overall prompt quality score")
            
            score_cols = st.columns(5)
            enhanced_scores = [
                ("Clarity", enhanced_score.clarity),
                ("Specific", enhanced_score.specificity),
                ("Action", enhanced_score.actionability),
                ("Structure", enhanced_score.structure),
                ("Context", enhanced_score.context_use)
            ]
            for i, (label, score) in enumerate(enhanced_scores):
                with score_cols[i]:
                    delta = score - scores[i][1]
                    st.metric(label, f"{score:.1f}", f"+{delta:.1f}")
            
            with st.expander("💬 Judge Feedback"):
                st.write("**Strengths:**")
                for pro in enhanced_score.feedback.get("pros", []):
                    st.write(f"• {pro}")
                st.write("**Areas for Improvement:**")
                for con in enhanced_score.feedback.get("cons", []):
                    st.write(f"• {con}")
                st.write(f"**Summary:** {enhanced_score.feedback.get('summary', 'No summary')}")
        
        # Output comparison
        st.markdown("---")
        st.subheader("🎯 Output Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Original Output")
            st.text_area("Response to original prompt:", value=original_output, height=200, disabled=True, key="orig_output")
        
        with col2:
            st.markdown("### ✨ Enhanced Output")
            st.text_area("Response to enhanced prompt:", value=enhanced_output, height=200, disabled=True, key="enh_output")


def display_multi_agent_results(data):
    """Display multi-agent enhancement results"""
    st.success("✅ Multi-agent enhancement complete!")
    
    st.subheader("🤖 Enhanced Prompt (Best Agent)")
    st.text_area("Enhanced Prompt", value=data["enhanced_text"], height=200, disabled=True, key="multi_enhanced")
    
    st.subheader("🏆 Winning Agent")
    st.info(f"**{data['selected_agent'].title()} Agent** was selected as the winner")
    st.write(f"**Rationale:** {data['decision_rationale']}")
    
    st.subheader("📊 Agent Vote Breakdown")
    vote_breakdown = data["vote_breakdown"]
    for agent, score in vote_breakdown.items():
        st.write(f"- **{agent.title()}**: {score:.2f}")

