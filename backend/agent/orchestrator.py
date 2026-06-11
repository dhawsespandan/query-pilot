import os, time
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from agent.tools.summarizer import summarize
from agent.tools.sentiment import analyze_sentiment
from agent.tools.code_explainer import explain_code
from agent.tools.youtube_tool import fetch_youtube_transcript
from agent.tools.comparator import compare_texts
from agent.planner import get_tool_plan

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

INTENT_PROMPT = """You are an intent classifier for an AI agent.

Given a user query and content, return ONLY one of these labels:
summarize, sentiment, explain_code, youtube, audio_summary, cross_input, general_qa, ocr_only

Rules:
- If the query asks to compare two inputs → cross_input
- If the query mentions a YouTube URL or asks to summarize a video → youtube
- If the content is code and user asks to explain → explain_code
- If an audio file is present and user wants a summary or transcript → audio_summary
- If the intent is unclear → return: FOLLOW_UP: <one short clarifying question>

Query: {query}
Content preview: {content}

Return only the label or FOLLOW_UP line. Nothing else."""


def _groq_chat(messages: list, retries: int = 2) -> str:
    for attempt in range(retries + 1):
        try:
            return client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                timeout=30,
            ).choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                raise e


def _make_trace_step(name: str, status: str, duration_ms: int, note: str = "") -> dict:
    return {"tool": name, "status": status, "duration_ms": duration_ms, "note": note}


def run(query: str, extracted_inputs: dict) -> dict:
    # Build combined text from full extracted text (not truncated) for tool execution
    combined_text = "\n\n".join(
        f"[{k}]: {v['text']}" for k, v in extracted_inputs.items() if v.get("text")
    )

    # Collect OCR metadata
    ocr_meta = {}
    audio_meta = {}
    for k, v in extracted_inputs.items():
        if v.get("ocr_used") and v.get("confidence") is not None:
            ocr_meta[k] = v["confidence"]
        if v.get("duration_seconds"):
            audio_meta[k] = v["duration_seconds"]

    # Intent classification uses a 3000-char preview but YouTube URL scan uses full text
    t0 = time.time()
    intent_raw = _groq_chat([{
        "role": "user",
        "content": INTENT_PROMPT.format(query=query, content=combined_text[:3000])
    }])
    intent_ms = int((time.time() - t0) * 1000)

    if intent_raw.startswith("FOLLOW_UP:"):
        return {
            "result": "",
            "extracted_text": combined_text,
            "ocr_meta": ocr_meta,
            "plan_trace": [_make_trace_step("intent_classifier", "follow_up", intent_ms)],
            "follow_up": intent_raw.replace("FOLLOW_UP:", "").strip(),
        }

    intent = intent_raw.lower().strip()
    plan = get_tool_plan(intent)
    plan_trace = [_make_trace_step("intent_classifier", "ok", intent_ms, intent)]

    result = {}

    if "comparator" in plan:
        inputs = list(extracted_inputs.values())
        keys = list(extracted_inputs.keys())
        t0 = time.time()
        if len(inputs) >= 2:
            result = compare_texts(inputs[0]["text"], inputs[1]["text"], keys[0], keys[1])
        elif len(inputs) == 1:
            result = {"summary": inputs[0]["text"]}
        else:
            result = {"summary": "No inputs provided to compare."}
        plan_trace.append(_make_trace_step("comparator", "ok", int((time.time() - t0) * 1000)))

    elif "youtube_tool" in plan:
        # Scan FULL combined_text for YouTube URL — not truncated
        t0 = time.time()
        yt = fetch_youtube_transcript(combined_text)
        plan_trace.append(_make_trace_step(
            "youtube_tool",
            "ok" if yt["found"] else "not_found",
            int((time.time() - t0) * 1000),
            yt.get("video_id", "")
        ))
        if yt["found"]:
            t0 = time.time()
            result = summarize(yt["transcript"])
            result["video_id"] = yt["video_id"]
            plan_trace.append(_make_trace_step("summarizer", "ok", int((time.time() - t0) * 1000)))
        elif combined_text.strip():
            t0 = time.time()
            result = summarize(combined_text)
            plan_trace.append(_make_trace_step("summarizer", "ok", int((time.time() - t0) * 1000)))
        else:
            result = {"answer": "No YouTube URL found in the provided content."}

    elif "audio_tool" in plan:
        audio_keys = [k for k, v in extracted_inputs.items()
                      if k.rsplit(".", 1)[-1].lower() in ("mp3", "wav", "m4a")]
        t0 = time.time()
        result = summarize(combined_text)
        plan_trace.append(_make_trace_step("audio_tool+summarizer", "ok", int((time.time() - t0) * 1000)))
        # Attach duration from metadata
        for k in audio_keys:
            dur = extracted_inputs[k].get("duration_seconds", 0)
            if dur:
                result["duration_seconds"] = dur
                break

    elif "summarizer" in plan:
        t0 = time.time()
        result = summarize(combined_text)
        plan_trace.append(_make_trace_step("summarizer", "ok", int((time.time() - t0) * 1000)))

    elif "sentiment" in plan:
        t0 = time.time()
        result = analyze_sentiment(combined_text)
        plan_trace.append(_make_trace_step("sentiment", "ok", int((time.time() - t0) * 1000)))

    elif "code_explainer" in plan:
        t0 = time.time()
        result = explain_code(combined_text)
        plan_trace.append(_make_trace_step("code_explainer", "ok", int((time.time() - t0) * 1000)))

    else:
        t0 = time.time()
        answer = _groq_chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{query}\n\nContext:\n{combined_text}"},
        ])
        result = {"answer": answer}
        plan_trace.append(_make_trace_step("conversational_llm", "ok", int((time.time() - t0) * 1000)))

    # Attach OCR confidence to result if present
    if ocr_meta:
        result["ocr_confidence"] = ocr_meta

    return {
        "result": result,
        "extracted_text": combined_text,
        "ocr_meta": ocr_meta,
        "plan_trace": plan_trace,
        "follow_up": None,
    }
