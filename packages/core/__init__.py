"""
Core packages for the Self-Learning Prompt Engineering System.

This package contains the core functionality for prompt improvement and token tracking.
"""

from .engine import improve_prompt, generate_llm_output, ImprovedOut, fallback_to_template
from .token_tracker import TokenTracker, TokenUsage, ComparisonMetrics
from .judge import judge_prompt, Scorecard
from .learning import LearningState, update_rules, should_keep_or_revert

__all__ = [
    "improve_prompt",
    "generate_llm_output",
    "ImprovedOut",
    "fallback_to_template",
    "TokenTracker",
    "TokenUsage",
    "ComparisonMetrics",
    "judge_prompt",
    "Scorecard",
    "LearningState",
    "update_rules",
    "should_keep_or_revert"
]