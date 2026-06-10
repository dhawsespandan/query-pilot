import io
import pytesseract
from PIL import Image
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd=(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_image(file_bytes:bytes)->dict:
    try:
        image=Image.open(io.BytesIO(file_bytes))
        text=pytesseract.image_to_string(image)
        data=pytesseract.image_to_data(image,output_type=Output.DICT)
        confidences=[
            float(conf)
            for conf in data["conf"]
            if conf!="-1" and float(conf)>=0
        ]

        avg_confidence=(
            round(sum(confidences)/len(confidences),2)
            if confidences
            else 0.0
        )

        return {
            "text":text.strip(),
            "confidence":avg_confidence,
            "word_count":len(text.strip().split()) if text.strip() else 0,
        }

    except Exception as e:
        return{
            "text":"",
            "confidence":0.0,
            "word_count":0,
            "error":str(e),
        }


if __name__=="__main__":
    with open("test_image.jpg","rb") as f:
        result=extract_image(f.read())

    print(f"Confidence:{result['confidence']}")

    if "error" in result:
        print(f"Error: {result['error']}")

    print(f"\nExtracted Text:\n{result['text']}")