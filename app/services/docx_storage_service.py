from app.services.docx_processor import process_docx
from app.services.record_storage import save_processed_records


def process_and_store_docx(
    file_path,
    document_id,
    user_id
):
    """
    Process a DOCX file and store its
    processed records in the database.
    """

    processing_result = process_docx(file_path)

    if not processing_result.get("success"):
        return {
            "success": False,
            "stage": processing_result.get(
                "stage",
                "processing"
            ),
            "error": processing_result.get(
                "error",
                "DOCX processing failed."
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
                "Failed to store DOCX records."
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
        "paragraph_count": processing_result.get(
            "paragraph_count",
            0
        ),
        "table_count": processing_result.get(
            "table_count",
            0
        )
    }
