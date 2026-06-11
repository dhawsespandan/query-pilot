import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tools.summarizer import summarize

def test_returns_dict():
    result = summarize("Python is a programming language used in data science and web development.")
    assert isinstance(result, dict)

def test_has_required_keys():
    result = summarize("AI is transforming industries worldwide.")
    assert "one_liner" in result
    assert "bullets" in result
    assert "five_sentences" in result

def test_bullets_is_list():
    result = summarize("Machine learning uses data to train models.")
    assert isinstance(result["bullets"], list)