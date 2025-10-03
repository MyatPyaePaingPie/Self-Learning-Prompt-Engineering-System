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