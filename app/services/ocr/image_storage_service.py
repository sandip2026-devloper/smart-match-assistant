from app.services.ocr.image_processor import process_image
from app.services.record_storage import save_processed_records


def process_and_store_image(
    file_path,
    document_id,
    user_id
):
    """
    Process an image using OCR
    and store the processed records
    in the database.
    """

    processing_result = process_image(file_path)

    if not processing_result.get("success"):
        return {
            "success": False,
            "stage": processing_result.get(
                "stage",
                "processing"
            ),
            "error": processing_result.get(
                "error",
                "Image processing failed."
            )
        }

    storage_result = save_processed_records(
        document_id=document_id,
        user_id=user_id,
        processed_records=processing_result.get(
            "records",
            []
        )
    )

    if not storage_result.get("success"):
        return {
            "success": False,
            "stage": "storage",
            "error": storage_result.get(
                "error",
                "Failed to store image records."
            )
        }

    return {
        "success": True,
        "document_id": document_id,
        "user_id": user_id,
        "record_count": processing_result.get(
            "record_count",
            0
        ),
        "saved_count": storage_result.get(
            "saved_count",
            0
        ),
        "line_count": processing_result.get(
            "line_count",
            0
        )
    }