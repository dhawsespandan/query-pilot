import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tools.pdf_tool import extract_pdf

def test_returns_dict():
    result = extract_pdf(b"")
    assert isinstance(result, dict)

def test_bad_input_no_crash():
    result = extract_pdf(b"not a pdf")
    assert "error" in result or result["text"] == ""

def test_has_required_keys():
    result = extract_pdf(b"")
    assert "text" in result or "error" in result