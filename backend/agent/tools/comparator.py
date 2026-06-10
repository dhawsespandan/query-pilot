import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3]/".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

def compare_texts(text_a:str,text_b:str,label_a:str="Input A",label_b:str="Input B")->dict:
    try:
        raw=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"""Compare the following two pieces of content and answer:
1. Do they discuss the same topic? (Yes / No / Partially)
2. What are the common themes?
3. What are the key differences?

{label_a}:
{text_a[:1500]}

{label_b}:
{text_b[:1500]}

Respond in exactly this format:
SAME_TOPIC: <Yes / No / Partially>
COMMON_THEMES: <brief description>
DIFFERENCES: <brief description>
SUMMARY: <two sentence comparative analysis>"""}],
        ).choices[0].message.content
        same_topic=common_themes=differences=summary=""
        for line in raw.splitlines():
            if line.startswith("SAME_TOPIC:"):same_topic=line.replace("SAME_TOPIC:","").strip()
            elif line.startswith("COMMON_THEMES:"):common_themes=line.replace("COMMON_THEMES:","").strip()
            elif line.startswith("DIFFERENCES:"):differences=line.replace("DIFFERENCES:","").strip()
            elif line.startswith("SUMMARY:"):summary=line.replace("SUMMARY:","").strip()
        return {"same_topic":same_topic,"common_themes":common_themes,"differences":differences,"summary":summary}
    except Exception as e:
        return {"same_topic":"","common_themes":"","differences":"","summary":"","error":str(e)}