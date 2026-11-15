import os

from app import db
from app.models.document import Document

from app.services.unified_document_processor import (
    process_document
)
from app.services.record_storage import (
    save_processed_records
)


def process_and_store_document(
    document_id,
    user_id
):
    """
    Process an uploaded document and store
    its processed records in the database.
    """

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:
        return {
            "success": False,
            "stage": "validation",
            "error": "Document not found."
        }

    # Security: verify ownership
    if document.user_id != user_id:
        return {
            "success": False,
            "stage": "authorization",
            "error": "Access denied."
        }

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    upload_folder = os.path.join(
        project_root,
        "uploads"
    )

    file_path = os.path.join(
        upload_folder,
        document.stored_name
    )

    if not os.path.isfile(file_path):
        return {
            "success": False,
            "stage": "file",
            "error": "Uploaded file not found."
        }

    # Mark as processing
    document.status = "processing"
    db.session.commit()

    try:
        processing_result = process_document(
            file_path=file_path,
            document_type=document.original_type
        )

        if not processing_result.get("success"):
            document.status = "processing_failed"
            db.session.commit()

            return {
                "success": False,
                "stage": processing_result.get(
                    "stage",
                    "processing"
                ),
                "error": processing_result.get(
                    "error",
                    "Document processing failed."
                )
            }

        records = processing_result.get(
            "records",
            []
        )

        storage_result = save_processed_records(
            document_id=document.id,
            user_id=user_id,
            processed_records=records
        )

        if not storage_result.get("success"):
            document.status = "processing_failed"
            db.session.commit()

            return {
                "success": False,
                "stage": "storage",
                "error": storage_result.get(
                    "error",
                    "Failed to store processed records."
                )
            }

        document.status = "processed"
        db.session.commit()

        return {
            "success": True,
            "document_id": document.id,
            "record_count": processing_result.get(
                "record_count",
                0
            ),
            "saved_count": storage_result.get(
                "saved_count",
                0
            ),
            "status": document.status
        }

    except Exception as error:

        db.session.rollback()

        document = db.session.get(
            Document,
            document_id
        )

        if document is not None:
            document.status = "processing_failed"
            db.session.commit()

        return {
            "success": False,
            "stage": "processing",
            "error": str(error)
        }