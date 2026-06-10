import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

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
        )

        raw = response.choices[0].message.content
        label = confidence = justification = ""

        for line in raw.splitlines():
            if line.startswith("LABEL:"):
                label = line.replace("LABEL:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                confidence = float(line.replace("CONFIDENCE:", "").strip())
            elif line.startswith("JUSTIFICATION:"):
                justification = line.replace("JUSTIFICATION:", "").strip()

        return {
            "label": label,
            "confidence": confidence,
            "justification": justification,
        }

    except Exception as e:
        return {
            "label": "",
            "confidence": 0.0,
            "justification": "",
            "error": str(e),
        }

if __name__ == "__main__":
    sample = "I absolutely loved the product. It exceeded all my expectations and the customer service was outstanding."
    result = analyze_sentiment(sample)
    print(f"Label: {result['label']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Justification: {result['justification']}")