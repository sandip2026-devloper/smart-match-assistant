import os

import pytesseract
from PIL import Image


def extract_image_ocr(file_path):
    """
    Extract text from an image using Tesseract OCR.
    """

    try:
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": "Image file not found."
            }

        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return {
            "success": True,
            "text": text,
            "lines": lines,
            "line_count": len(lines)
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }