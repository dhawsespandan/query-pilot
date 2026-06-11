import os
from fastapi import FastAPI,File,UploadFile,Form,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List,Optional
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1]/".env")

from agent.extractor import extract_file
from agent import orchestrator

app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

ALLOWED_EXT={"pdf","jpg","jpeg","png","mp3","wav","m4a"}
MAX_MB=25

@app.get("/")
def health():
    return {"status":"ok"}

@app.post("/chat")
async def chat(query:str=Form(...),files:Optional[List[UploadFile]]=File(default=None)):
    extracted_inputs={}
    if files:
        for file in files:
            ext=file.filename.rsplit(".",1)[-1].lower() if "." in file.filename else ""
            if ext not in ALLOWED_EXT:
                raise HTTPException(400,detail=f"Unsupported file type: {ext}")
            try:
                content=await file.read()
                if len(content)>MAX_MB*1024*1024:
                    raise HTTPException(400,detail=f"{file.filename} exceeds {MAX_MB}MB limit")
                extracted_inputs[file.filename]=extract_file(content,file.filename,ext)
            except HTTPException:raise
            except Exception as e:extracted_inputs[file.filename]=f"[Extraction failed: {e}]"
    try:
        return orchestrator.run(query,extracted_inputs)
    except Exception as e:
        raise HTTPException(500,detail=f"Agent error: {e}")