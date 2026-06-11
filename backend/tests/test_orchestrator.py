import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent import orchestrator

def test_returns_required_keys():
    result = orchestrator.run("What is Python?", {})
    assert "result" in result
    assert "extracted_text" in result
    assert "plan_trace" in result
    assert "follow_up" in result

def test_plan_trace_is_list():
    result = orchestrator.run("What is Python?", {})
    assert isinstance(result["plan_trace"], list)

def test_cross_input_two_texts():
    result = orchestrator.run("Do these discuss the same topic?", {
        "a.txt": "Machine learning uses statistical models.",
        "b.txt": "Deep learning is a subset of machine learning.",
    })
    assert isinstance(result, dict)
    assert "result" in result