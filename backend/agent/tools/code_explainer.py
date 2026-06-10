import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def explain_code(code: str) -> dict:
    try:
        prompt = f"""You are a code reviewer. Analyze the following code.
Respond in exactly this format:

EXPLANATION: <what the code does>
BUGS: <list any bugs or issues, or write 'None found'>
TIME_COMPLEXITY: <Big O time complexity>

Code:
{code}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.choices[0].message.content
        explanation = bugs = time_complexity = ""

        for line in raw.splitlines():
            if line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("BUGS:"):
                bugs = line.replace("BUGS:", "").strip()
            elif line.startswith("TIME_COMPLEXITY:"):
                time_complexity = line.replace("TIME_COMPLEXITY:", "").strip()

        return {
            "explanation": explanation,
            "bugs": bugs,
            "time_complexity": time_complexity,
        }

    except Exception as e:
        return {
            "explanation": "",
            "bugs": "",
            "time_complexity": "",
            "error": str(e),
        }

if __name__ == "__main__":
    sample = """
def find_duplicate(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                return arr[i]
    return None
"""
    result = explain_code(sample)
    print(f"Explanation: {result['explanation']}")
    print(f"Bugs: {result['bugs']}")
    print(f"Time Complexity: {result['time_complexity']}")