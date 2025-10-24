"""
Streamlit Web Interface for Self-Learning Prompt Engineering System
Provides user interface for prompt improvement with version history and judge scoring
"""

import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from storage.file_storage import FileStorage
    from packages.core.engine import improve_prompt
    from packages.core.judge import judge_prompt
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Make sure you're running from the project root directory")
    st.stop()

# Initialize session state
if 'storage' not in st.session_state:
    st.session_state.storage = FileStorage("storage")
if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Self-Learning Prompt Engineering System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🤖 Self-Learning Prompt Engineering System")
    st.markdown("""
    **Automatically improve prompts through intelligent rewriting, scoring, and learning from feedback.**
    
    Enter your prompt below to get an improved version with detailed analysis and scoring.
    """)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Prompt Improvement", "Version History", "Judge Scores History", "System Analytics"]
    )
    
    if page == "Prompt Improvement":
        prompt_improvement_page()
    elif page == "Version History":
        version_history_page()
    elif page == "Judge Scores History":
        judge_scores_page()
    elif page == "System Analytics":
        analytics_page()

def prompt_improvement_page():
    """Main prompt improvement interface"""
    
    st.header("💡 Prompt Improvement")
    
    # Input form
    with st.form("prompt_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_prompt = st.text_area(
                "Enter your prompt:",
                height=120,
                placeholder="e.g., Help me write a Python function to calculate factorial"
            )
        
        with col2:
            strategy = st.selectbox(
                "Improvement Strategy:",
                ["v1", "v2", "template"],
                index=0,
                help="v1: Structured template, v2: Enhanced with examples, template: Basic improvement"
            )
        
        submitted = st.form_submit_button("🚀 Improve Prompt", use_container_width=True)
    
    # Process prompt improvement
    if submitted and user_prompt.strip():
        with st.spinner("Improving prompt and analyzing quality..."):
            process_prompt_improvement(user_prompt.strip(), strategy)
    
    elif submitted and not user_prompt.strip():
        st.error("Please enter a prompt to improve.")
    
    # Display recent improvements
    display_recent_improvements()

def process_prompt_improvement(prompt: str, strategy: str):
    """Process prompt improvement and scoring"""
    
    try:
        # Generate unique IDs
        prompt_id = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        version_id = f"version_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Improve the prompt
        improvement = improve_prompt(prompt, strategy)
        
        # Judge the improved prompt
        scores = judge_prompt(
            improvement['text'], 
            save_to_storage=st.session_state.storage,
            prompt_id=prompt_id,
            version_id=version_id
        )
        
        # Save to file storage (simulating database version)
        class MockVersion:
            def __init__(self, text, explanation, strategy):
                self.id = version_id
                self.version_no = 1
                self.text = text
                self.source = f'engine/{strategy}'
                self.explanation = explanation
                self.created_at = datetime.now()
        
        # Save original version (v0)
        original_version = MockVersion(prompt, {"bullets": ["Original prompt"]}, "original")
        original_version.version_no = 0
        original_version.source = "original"
        st.session_state.storage.save_version_to_csv(prompt_id, original_version)
        
        # Save improved version (v1)
        improved_version = MockVersion(improvement['text'], improvement['explanation'], strategy)
        st.session_state.storage.save_version_to_csv(prompt_id, improved_version)
        
        # Store in session for display
        result = {
            'prompt_id': prompt_id,
            'version_id': version_id,
            'original': prompt,
            'improved': improvement,
            'scores': scores,
            'timestamp': datetime.now()
        }
        
        st.session_state.prompt_history.insert(0, result)
        
        # Display results
        display_improvement_results(result)
        
    except Exception as e:
        st.error(f"Error processing prompt: {str(e)}")
        st.error("Please check that all system components are properly configured.")

def display_improvement_results(result: Dict[str, Any]):
    """Display prompt improvement results"""
    
    st.success("✅ Prompt improved successfully!")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Improved Prompt", "⚖️ Quality Scores", "🔍 Analysis"])
    
    with tab1:
        st.subheader("Original Prompt")
        st.text_area("Original:", value=result['original'], height=100, disabled=True)
        
        st.subheader("Improved Prompt")
        st.text_area("Improved:", value=result['improved']['text'], height=200, disabled=True)
        
        # Copy button simulation
        st.code(result['improved']['text'], language=None)
        
        # Metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Strategy", result['improved']['strategy'])
        with col2:
            st.metric("Domain", result['improved']['domain_detected'])
        with col3:
            st.metric("Prompt ID", result['prompt_id'][:8] + "...")
    
    with tab2:
        display_judge_scores(result['scores'])
    
    with tab3:
        display_improvement_analysis(result['improved'])

def display_judge_scores(scores: Dict[str, Any]):
    """Display judge scoring results"""
    
    st.subheader("📊 Quality Assessment")
    
    # Score metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Clarity", f"{scores['clarity']:.1f}/10", 
                 delta=f"{scores['clarity']-5:.1f}" if scores['clarity'] != 5 else None)
    with col2:
        st.metric("Specificity", f"{scores['specificity']:.1f}/10",
                 delta=f"{scores['specificity']-5:.1f}" if scores['specificity'] != 5 else None)
    with col3:
        st.metric("Actionability", f"{scores['actionability']:.1f}/10",
                 delta=f"{scores['actionability']-5:.1f}" if scores['actionability'] != 5 else None)
    with col4:
        st.metric("Structure", f"{scores['structure']:.1f}/10",
                 delta=f"{scores['structure']-5:.1f}" if scores['structure'] != 5 else None)
    with col5:
        st.metric("Context Use", f"{scores['context_use']:.1f}/10",
                 delta=f"{scores['context_use']-5:.1f}" if scores['context_use'] != 5 else None)
    
    # Total score with progress bar
    total_percentage = scores['feedback']['overall_score_percentage']
    st.metric("Overall Score", f"{scores['total']:.1f}/50.0 ({total_percentage:.1f}%)")
    st.progress(total_percentage / 100.0)
    
    # Feedback sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Strengths")
        for pro in scores['feedback']['pros']:
            st.success(f"• {pro}")
    
    with col2:
        st.subheader("⚠️ Areas for Improvement")
        for con in scores['feedback']['cons']:
            st.warning(f"• {con}")
    
    # Summary and recommendations
    st.subheader("📋 Summary")
    st.info(scores['feedback']['summary'])
    
    if scores['feedback']['recommendations']:
        st.subheader("💡 Recommendations")
        for rec in scores['feedback']['recommendations']:
            st.write(f"• {rec}")

def display_improvement_analysis(improvement: Dict[str, Any]):
    """Display detailed improvement analysis"""
    
    st.subheader("🔧 Improvement Analysis")
    
    # Explanation bullets
    st.write("**Changes Made:**")
    for bullet in improvement['explanation']['bullets']:
        st.write(f"• {bullet}")
    
    # Differences
    if improvement['explanation']['diffs']:
        st.subheader("📝 Text Differences")
        for i, diff in enumerate(improvement['explanation']['diffs'], 1):
            st.write(f"**Change {i}:**")
            col1, col2 = st.columns(2)
            with col1:
                st.text_area(f"From:", value=diff['from'], height=100, disabled=True, key=f"from_{i}")
            with col2:
                st.text_area(f"To:", value=diff['to'], height=100, disabled=True, key=f"to_{i}")

def display_recent_improvements():
    """Display recent prompt improvements"""
    
    if st.session_state.prompt_history:
        st.header("📚 Recent Improvements")
        
        # Show last 3 improvements
        for i, result in enumerate(st.session_state.prompt_history[:3]):
            with st.expander(f"🕐 {result['timestamp'].strftime('%H:%M:%S')} - {result['original'][:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original:**")
                    st.text(result['original'])
                    
                with col2:
                    st.write("**Improved:**")
                    st.text(result['improved']['text'][:200] + "..." if len(result['improved']['text']) > 200 else result['improved']['text'])
                
                # Quick scores
                scores = result['scores']
                st.write(f"**Score:** {scores['total']:.1f}/50 ({scores['feedback']['overall_score_percentage']:.1f}%)")

def version_history_page():
    """Display version history from CSV files"""
    
    st.header("📜 Version History")
    
    # Load version history from CSV
    version_entries = st.session_state.storage.read_from_csv('prompt_versions')
    
    if not version_entries:
        st.info("No version history available yet. Create some prompt improvements to see history here.")
        return
    
    # Group by prompt_id
    prompt_groups = {}
    for entry in version_entries:
        prompt_id = entry['prompt_id']
        if prompt_id not in prompt_groups:
            prompt_groups[prompt_id] = []
        prompt_groups[prompt_id].append(entry)
    
    # Display options
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_prompt = st.selectbox(
            "Select a prompt to view history:",
            options=list(prompt_groups.keys()),
            format_func=lambda x: f"{x} ({len(prompt_groups[x])} versions)"
        )
    
    with col2:
        show_all = st.checkbox("Show all versions at once")
    
    if selected_prompt:
        display_prompt_version_history(prompt_groups[selected_prompt], show_all)
    
    # Version statistics
    st.subheader("📊 Version Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Prompts", len(prompt_groups))
    with col2:
        total_versions = sum(len(versions) for versions in prompt_groups.values())
        st.metric("Total Versions", total_versions)
    with col3:
        avg_versions = total_versions / len(prompt_groups) if prompt_groups else 0
        st.metric("Avg Versions/Prompt", f"{avg_versions:.1f}")

def display_prompt_version_history(versions: List[Dict], show_all: bool = False):
    """Display version history for a specific prompt"""
    
    # Sort versions by version number
    sorted_versions = sorted(versions, key=lambda x: int(x.get('version_no', 0)))
    
    st.subheader(f"Versions for Prompt: {sorted_versions[0]['prompt_id']}")
    
    if show_all:
        # Show all versions in expandable sections
        for version in sorted_versions:
            version_no = version.get('version_no', '0')
            source = version.get('source', 'unknown')
            timestamp = version.get('timestamp', 'N/A')
            
            with st.expander(f"Version {version_no} ({source}) - {timestamp}"):
                st.text_area("Text:", value=version.get('text', ''), height=150, disabled=True)
                
                # Show explanation if available
                explanation = version.get('explanation', '{}')
                try:
                    exp_data = json.loads(explanation) if isinstance(explanation, str) else explanation
                    if exp_data and 'bullets' in exp_data:
                        st.write("**Improvements:**")
                        for bullet in exp_data['bullets']:
                            st.write(f"• {bullet}")
                except:
                    st.write(f"**Raw explanation:** {explanation}")
    else:
        # Show side-by-side comparison of versions
        if len(sorted_versions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original (v0)")
                original = next((v for v in sorted_versions if v.get('version_no') == '0'), sorted_versions[0])
                st.text_area("Original text:", value=original.get('text', ''), height=200, disabled=True)
                st.write(f"**Source:** {original.get('source', 'N/A')}")
                st.write(f"**Timestamp:** {original.get('timestamp', 'N/A')}")
            
            with col2:
                st.subheader("Latest Version")
                latest = sorted_versions[-1]
                st.text_area("Latest text:", value=latest.get('text', ''), height=200, disabled=True)
                st.write(f"**Version:** {latest.get('version_no', 'N/A')}")
                st.write(f"**Source:** {latest.get('source', 'N/A')}")
                st.write(f"**Timestamp:** {latest.get('timestamp', 'N/A')}")
        
        # Timeline view
        st.subheader("📅 Version Timeline")
        timeline_data = []
        for version in sorted_versions:
            timeline_data.append({
                'Version': f"v{version.get('version_no', '0')}",
                'Source': version.get('source', 'unknown'),
                'Timestamp': version.get('timestamp', 'N/A'),
                'Text Length': len(version.get('text', '')),
                'Has Explanation': 'Yes' if version.get('explanation') else 'No'
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True)

def judge_scores_page():
    """Display judge scores history"""
    
    st.header("⚖️ Judge Scores History")
    
    # Load judge scores from CSV
    score_entries = st.session_state.storage.read_from_csv('judge_scores')
    
    if not score_entries:
        st.info("No judge scores available yet. Improve some prompts to see scoring history here.")
        return
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(score_entries)
    
    # Ensure numeric columns
    score_columns = ['clarity', 'specificity', 'actionability', 'structure', 'context_use', 'total']
    for col in score_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Statistics overview
    st.subheader("📊 Scoring Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scores", len(df))
    with col2:
        avg_total = df['total'].mean() if 'total' in df.columns else 0
        st.metric("Average Total Score", f"{avg_total:.1f}/50")
    with col3:
        max_score = df['total'].max() if 'total' in df.columns else 0
        st.metric("Highest Score", f"{max_score:.1f}/50")
    with col4:
        min_score = df['total'].min() if 'total' in df.columns else 0
        st.metric("Lowest Score", f"{min_score:.1f}/50")
    
    # Score distribution
    if 'total' in df.columns and len(df) > 0:
        st.subheader("📈 Score Distribution")
        st.bar_chart(df[score_columns[:5]])  # Chart the 5 criteria scores
    
    # Recent scores table
    st.subheader("📋 Recent Scores")
    
    # Prepare display data
    display_columns = ['prompt_id', 'timestamp'] + score_columns
    display_df = df[display_columns].copy() if all(col in df.columns for col in display_columns) else df
    
    # Sort by timestamp (most recent first)
    if 'timestamp' in display_df.columns:
        display_df = display_df.sort_values('timestamp', ascending=False)
    
    st.dataframe(display_df.head(10), use_container_width=True)
    
    # Detailed score view
    if len(df) > 0:
        st.subheader("🔍 Detailed Score Analysis")
        
        selected_index = st.selectbox(
            "Select a score entry to view details:",
            options=range(len(df)),
            format_func=lambda x: f"{df.iloc[x]['prompt_id']} - {df.iloc[x]['timestamp']}"
        )
        
        if selected_index is not None:
            score_entry = df.iloc[selected_index]
            display_detailed_score(score_entry)

def display_detailed_score(score_entry: pd.Series):
    """Display detailed view of a single score entry"""
    
    # Score breakdown
    col1, col2, col3, col4, col5 = st.columns(5)
    score_columns = ['clarity', 'specificity', 'actionability', 'structure', 'context_use']
    
    for i, col_name in enumerate(score_columns):
        with [col1, col2, col3, col4, col5][i]:
            score = score_entry.get(col_name, 0)
            st.metric(col_name.title(), f"{score:.1f}/10")
    
    # Total score
    total = score_entry.get('total', 0)
    percentage = (total / 50) * 100
    st.metric("Total Score", f"{total:.1f}/50 ({percentage:.1f}%)")
    st.progress(percentage / 100)
    
    # Feedback details
    feedback_str = score_entry.get('feedback', '{}')
    try:
        feedback = json.loads(feedback_str) if isinstance(feedback_str, str) else feedback_str
        
        if feedback and isinstance(feedback, dict):
            col1, col2 = st.columns(2)
            
            with col1:
                if 'pros' in feedback:
                    st.subheader("✅ Strengths")
                    for pro in feedback['pros']:
                        st.success(f"• {pro}")
            
            with col2:
                if 'cons' in feedback:
                    st.subheader("⚠️ Weaknesses") 
                    for con in feedback['cons']:
                        st.warning(f"• {con}")
            
            if 'summary' in feedback:
                st.subheader("📋 Summary")
                st.info(feedback['summary'])
            
            if 'recommendations' in feedback:
                st.subheader("💡 Recommendations")
                for rec in feedback['recommendations']:
                    st.write(f"• {rec}")
    
    except Exception as e:
        st.write("**Raw Feedback Data:**")
        st.text(feedback_str)

def analytics_page():
    """Display system analytics and insights"""
    
    st.header("📊 System Analytics")
    
    # Load all data
    version_entries = st.session_state.storage.read_from_csv('prompt_versions')
    score_entries = st.session_state.storage.read_from_csv('judge_scores')
    
    if not version_entries and not score_entries:
        st.info("No data available for analytics. Use the system to generate some data first.")
        return
    
    # Overall statistics
    st.subheader("🎯 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_prompts = len(set(entry['prompt_id'] for entry in version_entries)) if version_entries else 0
        st.metric("Total Prompts", unique_prompts)
    
    with col2:
        total_versions = len(version_entries) if version_entries else 0
        st.metric("Total Versions", total_versions)
    
    with col3:
        total_scores = len(score_entries) if score_entries else 0
        st.metric("Total Scores", total_scores)
    
    with col4:
        avg_improvement = calculate_average_improvement(version_entries, score_entries)
        st.metric("Avg Improvement", f"{avg_improvement:.1f}%")
    
    # Performance trends
    if score_entries:
        st.subheader("📈 Performance Trends")
        score_df = pd.DataFrame(score_entries)
        
        # Convert numeric columns
        numeric_cols = ['clarity', 'specificity', 'actionability', 'structure', 'context_use', 'total']
        for col in numeric_cols:
            if col in score_df.columns:
                score_df[col] = pd.to_numeric(score_df[col], errors='coerce')
        
        # Time series if we have timestamps
        if 'timestamp' in score_df.columns and len(score_df) > 1:
            score_df['timestamp'] = pd.to_datetime(score_df['timestamp'])
            score_df = score_df.sort_values('timestamp')
            
            st.line_chart(score_df.set_index('timestamp')[numeric_cols[:5]])
    
    # Strategy analysis
    if version_entries:
        st.subheader("🔧 Strategy Analysis")
        strategy_counts = {}
        for entry in version_entries:
            source = entry.get('source', 'unknown')
            strategy_counts[source] = strategy_counts.get(source, 0) + 1
        
        if strategy_counts:
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(strategy_counts)
            with col2:
                st.write("**Strategy Usage:**")
                for strategy, count in strategy_counts.items():
                    st.write(f"• {strategy}: {count} times")

def calculate_average_improvement(version_entries: List[Dict], score_entries: List[Dict]) -> float:
    """Calculate average improvement percentage"""
    
    if not version_entries or not score_entries:
        return 0.0
    
    # Simple calculation based on score data
    score_df = pd.DataFrame(score_entries)
    if 'total' in score_df.columns:
        scores = pd.to_numeric(score_df['total'], errors='coerce')
        avg_score = scores.mean()
        return (avg_score / 50) * 100  # Convert to percentage
    
    return 0.0

# Run the application
if __name__ == "__main__":
    main()
