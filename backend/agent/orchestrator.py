import os,time
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from agent.tools.summarizer import summarize
from agent.tools.sentiment import analyze_sentiment
from agent.tools.code_explainer import explain_code
from agent.tools.youtube_tool import fetch_youtube_transcript
from agent.tools.comparator import compare_texts
from agent.planner import get_tool_plan

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2]/".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

INTENT_PROMPT="""You are an intent classifier for an AI agent.

Given a user query and content, return ONLY one of these labels:
summarize, sentiment, explain_code, youtube, audio_summary, cross_input, general_qa, ocr_only

Rules:
- If the query asks to compare two inputs → cross_input
- If the query mentions a YouTube URL or asks to summarize a video → youtube
- If the content is code and user asks to explain → explain_code
- If the intent is unclear → return: FOLLOW_UP: <one short clarifying question>

Query: {query}
Content preview: {content}

Return only the label or FOLLOW_UP line. Nothing else."""

def _groq_chat(messages:list,retries:int=2)->str:
    for attempt in range(retries+1):
        try:
            return client.chat.completions.create(
                model="llama-3.3-70b-versatile",messages=messages,timeout=30,
            ).choices[0].message.content.strip()
        except Exception as e:
            if attempt<retries:time.sleep(2)
            else:raise e

def run(query:str,extracted_inputs:dict)->dict:
    combined_text="\n\n".join(f"[{k}]: {v}" for k,v in extracted_inputs.items() if v)
    intent_raw=_groq_chat([{"role":"user","content":INTENT_PROMPT.format(query=query,content=combined_text[:2000])}])
    if intent_raw.startswith("FOLLOW_UP:"):
        return {"result":"","extracted_text":combined_text,"plan_trace":[],"follow_up":intent_raw.replace("FOLLOW_UP:","").strip()}
    intent=intent_raw.lower().strip()
    plan=get_tool_plan(intent)
    result={}
    if "comparator" in plan:
        inputs=list(extracted_inputs.values());keys=list(extracted_inputs.keys())
        if len(inputs)>=2:result=compare_texts(inputs[0],inputs[1],keys[0],keys[1])
        elif len(inputs)==1:result={"summary":inputs[0]}
        else:result={"summary":"No inputs provided to compare."}
    elif "youtube_tool" in plan:
        yt=fetch_youtube_transcript(combined_text)
        if yt["found"]:
            result=summarize(yt["transcript"]);result["video_id"]=yt["video_id"]
        elif combined_text.strip():
            result=summarize(combined_text)
        else:
            result={"answer":"No YouTube URL found in the provided content."}
    elif "summarizer" in plan:result=summarize(combined_text)
    elif "sentiment" in plan:result=analyze_sentiment(combined_text)
    elif "code_explainer" in plan:result=explain_code(combined_text)
    else:result={"answer":_groq_chat([
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":f"{query}\n\nContext:\n{combined_text}"},
    ])}
    return {"result":result,"extracted_text":combined_text,"plan_trace":plan,"follow_up":None}