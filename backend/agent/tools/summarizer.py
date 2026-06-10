import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

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
        )

        raw = response.choices[0].message.content

        one_liner = ""
        bullets = []
        five_sentences = ""

        for line in raw.splitlines():
            if line.startswith("ONE_LINER:"):
                one_liner = line.replace("ONE_LINER:", "").strip()
            elif line.startswith("- "):
                bullets.append(line.strip())
            elif line.startswith("FIVE_SENTENCES:"):
                five_sentences = line.replace("FIVE_SENTENCES:", "").strip()

        return {
            "one_liner": one_liner,
            "bullets": bullets[:3],
            "five_sentences": five_sentences,
        }

    except Exception as e:
        return {
            "one_liner": "",
            "bullets": [],
            "five_sentences": "",
            "error": str(e),
        }

if __name__ == "__main__":
    sample = "Artificial intelligence is transforming industries worldwide. Companies are using AI to automate tasks, improve efficiency, and create new products. Machine learning models can now recognize images, translate languages, and generate text. However, concerns about job displacement and ethical issues remain. Governments are beginning to regulate AI development to ensure safety and fairness."
    result = summarize(sample)
    print(f"One liner: {result['one_liner']}")
    print(f"Bullets: {result['bullets']}")
    print(f"Five sentences: {result['five_sentences']}")