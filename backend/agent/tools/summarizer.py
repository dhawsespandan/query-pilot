import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import re

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize(text: str) -> dict:
    try:
        prompt = f"""Summarize the following text in exactly this format:

ONE_LINER: <one sentence summary>

BULLETS:
- <point 1>
- <point 2>
- <point 3>

FIVE_SENTENCES: <five sentence summary>

Text:
{text}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            timeout=30,
        )

        raw = response.choices[0].message.content

        # Lenient parsers — handle extra whitespace, markdown bold, varied spacing
        one_liner_match = re.search(
            r"ONE_LINER\s*[:\-]\s*\*{0,2}(.+?)\*{0,2}\s*(?=\n|BULLETS|$)",
            raw, re.DOTALL | re.IGNORECASE
        )
        five_sentences_match = re.search(
            r"FIVE_SENTENCES\s*[:\-]\s*\*{0,2}(.+?)\*{0,2}\s*$",
            raw, re.DOTALL | re.IGNORECASE
        )
        bullets = re.findall(r"^\s*[-*•]\s+(.+)", raw, re.MULTILINE)

        one_liner = one_liner_match.group(1).strip() if one_liner_match else ""
        five_sentences = five_sentences_match.group(1).strip() if five_sentences_match else ""

        # Fallback: if still empty, split raw into sentences
        if not one_liner:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw.strip()) if s.strip()]
            one_liner = sentences[0] if sentences else ""
        if not five_sentences:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw.strip()) if s.strip()]
            five_sentences = " ".join(sentences[:5]) if sentences else ""

        return {
            "one_liner": one_liner,
            "bullets": bullets[:3],
            "five_sentences": five_sentences,
        }

    except Exception as e:
        return {"one_liner": "", "bullets": [], "five_sentences": "", "error": str(e)}

if __name__ == "__main__":
    sample = "Artificial intelligence is transforming industries worldwide. Companies are using AI to automate tasks, improve efficiency, and create new products. Machine learning models can now recognize images, translate languages, and generate text. However, concerns about job displacement and ethical issues remain. Governments are beginning to regulate AI development to ensure safety and fairness."
    result = summarize(sample)
    print(f"One liner: {result['one_liner']}")
    print(f"Bullets: {result['bullets']}")
    print(f"Five sentences: {result['five_sentences']}")
