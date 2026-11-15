from app.services.document_processor import process_excel
from app.services.docx_processor import process_docx
from app.services.pdf_processor import process_pdf
from app.services.txt_processor import process_txt
from app.services.ocr.image_processor import process_image


SUPPORTED_TYPES = {
    "xlsx": process_excel,
    "docx": process_docx,
    "pdf": process_pdf,
    "txt": process_txt,
    "png": process_image,
    "jpg": process_image,
    "jpeg": process_image,
}


def process_document(file_path, document_type):
    """
    Process a document using the correct processor
    based on its file type.
    """

    if not document_type:
        return {
            "success": False,
            "stage": "validation",
            "error": "Document type is required."
        }

    document_type = document_type.lower().strip()

    processor = SUPPORTED_TYPES.get(document_type)

    if processor is None:
        return {
            "success": False,
            "stage": "validation",
            "error": (
                f"Unsupported document type: "
                f"{document_type}"
            )
        }

    try:
        result = processor(file_path)

        return result

    except Exception as error:
        return {
            "success": False,
            "stage": "processing",
            "error": str(error)
        }