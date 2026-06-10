TOOL_MAP = {
    "summarize":     ["extract","summarizer"],
    "sentiment":     ["extract","sentiment"],
    "explain_code":  ["extract","code_explainer"],
    "youtube":       ["extract","youtube_tool","summarizer"],
    "audio_summary": ["audio_tool","summarizer"],
    "cross_input":   ["extract_all","comparator"],
    "general_qa":    ["conversational_llm"],
    "ocr_only":      ["extract"],
}

def get_tool_plan(intent:str)->list:
    return TOOL_MAP.get(intent.lower().strip(),["conversational_llm"])