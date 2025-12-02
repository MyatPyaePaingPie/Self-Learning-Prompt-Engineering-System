from dataclasses import dataclass

@dataclass
class LearningState:
    require_role: bool = True
    require_deliverables: bool = True
    require_constraints: bool = True
    require_questions_first: bool = True

STATE = LearningState()

def update_rules(history: list[dict]) -> LearningState:
    """
    history: [{text, scorecard:{...}}]
    Simple signal: if versions with 'Constraints:' consistently score higher,
    lock this element in; else consider relaxing.
    """
    # placeholder: compute deltas, toggle flags. For now, keep defaults.
    return STATE


def should_keep_or_revert(scores: list[float], new_score: float, threshold: float = 0.5):
    """
    Decide whether to keep or revert based on average past scores.

    Args:
        scores: List of previous total scores.
        new_score: The most recent version's total score.
        threshold: How much higher the new score must be to be considered better.

    Returns:
        "keep" if new_score is >= average + threshold
        "revert" otherwise.
    """
    if not scores:
        return "keep"
    avg_score = sum(scores) / len(scores)
    return "keep" if new_score >= avg_score + threshold else "revert"