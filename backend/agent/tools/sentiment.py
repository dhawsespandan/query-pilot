import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import re

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_sentiment(text: str) -> dict:
    try:
        prompt = f"""Analyze the sentiment of the following text.
Respond in exactly this format:

LABEL: <Positive, Negative, or Neutral>
CONFIDENCE: <number between 0 and 1>
JUSTIFICATION: <one sentence explanation>

Text:
{text}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            timeout=30,
        )

        raw = response.choices[0].message.content

        label = re.search(r"LABEL:\s*(.+?)(?=\nCONFIDENCE:|\Z)", raw, re.DOTALL)
        confidence_match = re.search(r"CONFIDENCE:\s*([0-9.]+)", raw)
        justification = re.search(r"JUSTIFICATION:\s*(.+?)$", raw, re.DOTALL)
        label = label.group(1).strip() if label else ""
        confidence = float(confidence_match.group(1)) if confidence_match else 0.0
        justification = justification.group(1).strip() if justification else ""

        return {"label": label, "confidence": confidence, "justification": justification}

    except Exception as e:
        return {"label": "", "confidence": 0.0, "justification": "", "error": str(e)}

if __name__ == "__main__":
    sample = "I absolutely loved the product. It exceeded all my expectations and the customer service was outstanding."
    result = analyze_sentiment(sample)
    print(f"Label: {result['label']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Justification: {result['justification']}")