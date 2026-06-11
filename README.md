# QueryPilot

QueryPilot is an agentic AI application in which we take input as text, image, pdf and audio files one at a time, or multiple files together, understand the user's intent, and perform the required task on its own by deciding which tool to use.

## Features

Operations can be performed on text queries, image ocr, parsing pdf with ocr in case of scanned image, transcribe audio. Can summarize, calculate sentiment, explain code, provide youtube transcripts, compare multiple inputs, and answer general questions. If the intent is unclear, it will ask a follow up question to user. All outputs are text-only.

## Tech Stack

Frontend: React + TypeScript + Vite. Backend: FastAPI + Python 3.11. LLM: Groq (llama-3.3-70b-versatile). Speech-to-Text: Groq Whisper. OCR: Tesseract + PyMuPDF. YouTube: youtube-transcript-api. Deployment: Render (backend) + Vercel (frontend).

## Setup

Clone the repo. Create a `.env` file in the root with `GROQ_API_KEY=your_key_here`. Install backend dependencies with `pip install -r backend/requirements.txt`. Run the backend with `uvicorn main:app --reload` from the `backend/` folder. For frontend, run `npm install` then `npm run dev` from the `frontend/` folder.

## Docker

Build and run the backend with `docker build -t querypilot ./backend` and `docker run -p 8000:8000 --env-file .env querypilot`.

## Live Demo

Backend: https://query-pilot.onrender.com

## Running Tests

Run `pytest` from the `backend/` folder.
