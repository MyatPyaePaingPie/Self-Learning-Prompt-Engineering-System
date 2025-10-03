def test_judge_scales_scores_0_10():
    from packages.core.judge import judge_prompt
    s = judge_prompt("You are a senior... Task: X\nDeliverables:\n- step-by-step\nConstraints:")
    for k in ["clarity","specificity","actionability","structure","context_use"]:
        assert 0 <= getattr(s, k) <= 10
    assert s.total <= 50

def test_judge_scorecard_structure():
    from packages.core.judge import judge_prompt
    s = judge_prompt("Simple prompt without structure")
    assert hasattr(s, 'clarity')
    assert hasattr(s, 'specificity')
    assert hasattr(s, 'actionability')
    assert hasattr(s, 'structure')
    assert hasattr(s, 'context_use')
    assert hasattr(s, 'feedback')
    assert isinstance(s.feedback, dict)
    assert 'summary' in s.feedback

def test_judge_recognizes_good_structure():
    from packages.core.judge import judge_prompt
    good_prompt = """You are a senior Python developer.
Task: Help me build a web scraper
Deliverables:
- step-by-step implementation plan
- working code with examples
Constraints: Use requests and BeautifulSoup only
If information is missing, ask clarifying questions first."""
    
    s = judge_prompt(good_prompt)
    # Should score well on most criteria
    assert s.clarity > 0
    assert s.specificity > 0
    assert s.actionability > 0
    assert s.structure > 0
    assert s.context_use > 0