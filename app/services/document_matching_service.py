from app import db

from app.models.document import Document
from app.models.document_record import DocumentRecord

from app.services.matching.matching_engine import match_documents


def get_document_records(document_id, user_id):
    """
    Get all processed records belonging to
    a specific user's document.
    """

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:
        return {
            "success": False,
            "error": "Document not found."
        }

    # Security check:
    # A user can only access their own document.
    if document.user_id != user_id:
        return {
            "success": False,
            "error": "Access denied."
        }

    records = DocumentRecord.query.filter_by(
        document_id=document_id,
        user_id=user_id
    ).order_by(
        DocumentRecord.id.asc()
    ).all()

    processed_records = []

    for record in records:

        processed_records.append({
            "sheet_name": record.sheet_name,
            "source_row": record.source_row,
            "header_type": record.header_type,
            "raw_record": record.raw_data,
            "normalized_fields": record.normalized_data,
            "identifiers": record.identifiers or []
        })

    return {
        "success": True,
        "document": document,
        "records": processed_records,
        "record_count": len(processed_records)
    }


def match_document_pair(
    main_document_id,
    secondary_document_id,
    user_id
):
    """
    Match one Main Document against one
    Secondary Document.

    Both documents must belong to the
    current user.
    """

    # Prevent accidentally matching a document
    # against itself.
    if main_document_id == secondary_document_id:
        return {
            "success": False,
            "error": "Main and Secondary documents must be different."
        }

    main_result = get_document_records(
        main_document_id,
        user_id
    )

    if not main_result["success"]:
        return main_result

    secondary_result = get_document_records(
        secondary_document_id,
        user_id
    )

    if not secondary_result["success"]:
        return secondary_result

    match_result = match_documents(
        main_records=main_result["records"],
        secondary_records=secondary_result["records"]
    )

    return {
        "success": True,

        "main_document": main_result["document"],
        "secondary_document": secondary_result["document"],

        "main_record_count": main_result[
            "record_count"
        ],

        "secondary_record_count": secondary_result[
            "record_count"
        ],

        "matched": match_result["matched"],
        "unmatched": match_result["unmatched"],
        "duplicate": match_result["duplicate"],

        "matched_count": match_result[
            "matched_count"
        ],

        "unmatched_count": match_result[
            "unmatched_count"
        ],

        "duplicate_count": match_result[
            "duplicate_count"
        ]
    }
