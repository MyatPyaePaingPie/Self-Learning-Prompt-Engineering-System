def test_improve_adds_role_and_sections():
    from packages.core.engine import improve_prompt
    out = improve_prompt("help me code a parser in python")
    assert "You are a senior" in out.text
    assert "Deliverables:" in out.text
    assert out.explanation["bullets"]

def test_detect_domain():
    from packages.core.engine import detect_domain
    assert detect_domain("help me code something") == "Python developer"
    assert detect_domain("create a marketing campaign") == "marketing strategist"
    assert detect_domain("solve this math problem") == "subject-matter"

def test_improve_prompt_structure():
    from packages.core.engine import improve_prompt
    out = improve_prompt("solve this problem")
    assert "Task:" in out.text
    assert "Constraints:" in out.text
    assert out.source == "engine/v1"
    assert isinstance(out.explanation, dict)
    assert "bullets" in out.explanation
    assert "diffs" in out.explanation