import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

from agent.extractor import extract_file
from agent import orchestrator

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

ALLOWED_EXT = {"pdf", "jpg", "jpeg", "png", "mp3", "wav", "m4a"}
MAX_MB = 25


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(
    query: str = Form(...),
    files: Optional[List[UploadFile]] = File(default=None),
):
    extracted_inputs = {}
    if files:
        for file in files:
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
            if ext not in ALLOWED_EXT:
                raise HTTPException(400, detail=f"Unsupported file type: {ext}")
            try:
                content = await file.read()
                if len(content) > MAX_MB * 1024 * 1024:
                    raise HTTPException(400, detail=f"{file.filename} exceeds {MAX_MB}MB limit")
                extracted_inputs[file.filename] = extract_file(content, file.filename, ext)
            except HTTPException:
                raise
            except Exception as e:
                extracted_inputs[file.filename] = {
                    "text": f"[Extraction failed: {e}]",
                    "ocr_used": False,
                    "confidence": None,
                }

    try:
        return orchestrator.run(query, extracted_inputs)
    except Exception as e:
        raise HTTPException(500, detail=f"Agent error: {e}")


@app.post("/chat/stream")
async def chat_stream(
    query: str = Form(...),
    files: Optional[List[UploadFile]] = File(default=None),
):
    extracted_inputs = {}
    if files:
        for file in files:
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
            if ext not in ALLOWED_EXT:
                raise HTTPException(400, detail=f"Unsupported file type: {ext}")
            try:
                content = await file.read()
                if len(content) > MAX_MB * 1024 * 1024:
                    raise HTTPException(400, detail=f"{file.filename} exceeds {MAX_MB}MB limit")
                extracted_inputs[file.filename] = extract_file(content, file.filename, ext)
            except HTTPException:
                raise
            except Exception as e:
                extracted_inputs[file.filename] = {
                    "text": f"[Extraction failed: {e}]",
                    "ocr_used": False,
                    "confidence": None,
                }

    def generate():
        try:
            result = orchestrator.run(query, extracted_inputs)
            # Stream plan trace steps first
            for step in result.get("plan_trace", []):
                yield f"data: {json.dumps({'type': 'trace', 'step': step})}\n\n"
            # Stream extracted text
            if result.get("extracted_text"):
                yield f"data: {json.dumps({'type': 'extracted', 'text': result['extracted_text'][:2000]})}\n\n"
            # Stream final result
            yield f"data: {json.dumps({'type': 'result', 'data': result['result'], 'follow_up': result.get('follow_up'), 'ocr_meta': result.get('ocr_meta', {})})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
