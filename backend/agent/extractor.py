from agent.tools.pdf_tool import extract_pdf
from agent.tools.ocr_tool import extract_image
from agent.tools.audio_tool import transcribe_audio

def extract_file(content: bytes, filename: str, ext: str) -> str:
    if ext == "pdf":
        return extract_pdf(content).get("text", "")
    elif ext in ("jpg", "jpeg", "png"):
        return extract_image(content).get("text", "")
    elif ext in ("mp3", "wav", "m4a"):
        audio_result = transcribe_audio(content, filename)
        transcript = audio_result.get("transcript", "")
        duration = audio_result.get("duration_seconds", 0)
        return f"{transcript}\n[Duration: {duration}s]" if duration else transcript
    return ""