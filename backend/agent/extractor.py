from agent.tools.pdf_tool import extract_pdf
from agent.tools.ocr_tool import extract_image
from agent.tools.audio_tool import transcribe_audio

def extract_file(content: bytes, filename: str, ext: str) -> dict:
    if ext == "pdf":
        result = extract_pdf(content)
        return {
            "text": result.get("text", ""),
            "ocr_used": result.get("ocr_used", False),
            "page_count": result.get("page_count", 0),
            "confidence": None,
        }
    elif ext in ("jpg", "jpeg", "png"):
        result = extract_image(content)
        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "word_count": result.get("word_count", 0),
            "ocr_used": True,
        }
    elif ext in ("mp3", "wav", "m4a"):
        result = transcribe_audio(content, filename)
        return {
            "text": result.get("transcript", ""),
            "duration_seconds": result.get("duration_seconds", 0.0),
            "ocr_used": False,
            "confidence": None,
        }
    return {"text": "", "ocr_used": False, "confidence": None}
