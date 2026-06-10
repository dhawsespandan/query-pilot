import io
import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_bytes:bytes,filename:str)->dict:

    try:
        audio_file=io.BytesIO(file_bytes)
        audio_file.name=filename

        response=client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="verbose_json",
        )

        return{
            "transcript":response.text,
            "duration_seconds":response.duration,
        }

    except Exception as e:
        return{
            "transcript":"",
            "duration_seconds":0.0,
            "error":str(e),
        }


if __name__=="__main__":
    with open("test_audio.mp3","rb") as f:
        result=transcribe_audio(
            f.read(),
            "test_audio.mp3"
        )

    print(f"Duration:{result['duration_seconds']}s")

    if "error" in result:
        print(f"Error:{result['error']}")

    print(f"\nTranscript:\n{result['transcript']}")