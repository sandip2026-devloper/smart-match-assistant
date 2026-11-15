import fitz


def extract_pdf(file_path):
    """
    Extract text from a PDF file page by page.
    """

    try:
        document = fitz.open(file_path)

        pages = []

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "text": text
                })

        document.close()

        return {
            "success": True,
            "pages": pages,
            "page_count": len(pages)
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }