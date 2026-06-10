import io
import pymupdf
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd=(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_pdf(file_bytes: bytes)->dict:
    try:
        doc=pymupdf.open(stream=file_bytes, filetype="pdf")
        page_count=len(doc)
        extracted_pages=[]
        ocr_used=False

        for page in doc:
            text=page.get_text().strip()
            if not text:
                ocr_used=True
                pix=page.get_pixmap()
                image=Image.open(io.BytesIO(pix.tobytes("png")))
                text=pytesseract.image_to_string(image)
            extracted_pages.append(text)

        return {
            "text":"\n\n".join(extracted_pages),
            "ocr_used":ocr_used,
            "page_count":page_count,
        }

    except Exception as e:
        return {
            "text":"",
            "ocr_used":False,
            "page_count":0,
            "error":str(e),
        }

if __name__=="__main__":
    with open("test.pdf","rb") as f:
        result=extract_pdf(f.read())

    print(f"Pages:{result['page_count']}")
    print(f"OCR Used:{result['ocr_used']}")
    print("\nExtracted Text:\n")
    print(result["text"])