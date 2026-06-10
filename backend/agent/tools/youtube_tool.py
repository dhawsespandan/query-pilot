import re
from youtube_transcript_api import YouTubeTranscriptApi


def fetch_youtube_transcript(text:str)->dict:
    try:
        pattern = (
            r"(?:youtube\.com/watch\?v=|youtu\.be/)"
            r"([a-zA-Z0-9_-]{11})"
        )

        matches = re.findall(pattern, text)

        if not matches:
            return{
                "transcript":"",
                "video_id":"",
                "found":False,
            }

        video_id=matches[0]

        ytt = YouTubeTranscriptApi()
        transcript_data = ytt.fetch(video_id)

        transcript=" ".join(
            entry.text
            for entry in transcript_data
        )

        return{
            "transcript":transcript,
            "video_id":video_id,
            "found":True,
        }

    except Exception as e:
        return {
            "transcript":"",
            "video_id":video_id if "video_id" in locals() else "",
            "found":False,
            "error":str(e),
        }


if __name__=="__main__":
    test_text=(
        "Check out this video: "
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

    result=fetch_youtube_transcript(test_text)

    print(f"Found: {result['found']}")
    print(f"Video ID: {result['video_id']}")

    if "error" in result:
        print(f"Error: {result['error']}")

    print(
        f"\nTranscript:\n"
        f"{result['transcript'][:300]}"
    )