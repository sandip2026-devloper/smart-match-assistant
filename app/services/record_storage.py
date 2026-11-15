import math

from app import db
from app.models.document_record import DocumentRecord


def make_json_safe(value):

    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            make_json_safe(item)
            for item in value
        ]

    try:
        if hasattr(value, "item"):
            value = value.item()
    except Exception:
        pass

    return value


def save_processed_records(
    document_id,
    user_id,
    processed_records
):

    try:

        saved_count = 0

        for record in processed_records:

            raw_data = make_json_safe(
                record.get("raw_record", {})
            )

            normalized_data = make_json_safe(
                record.get(
                    "normalized_fields",
                    {}
                )
            )

            identifiers = make_json_safe(
                record.get(
                    "identifiers",
                    []
                )
            )

            document_record = DocumentRecord(
                document_id=document_id,
                user_id=user_id,
                sheet_name=record.get("sheet_name"),
                source_row=record.get("source_row"),
                header_type=record.get("header_type"),
                raw_data=raw_data,
                normalized_data=normalized_data,
                identifiers=identifiers
            )

            db.session.add(document_record)

            saved_count += 1

        db.session.commit()

        return {
            "success": True,
            "saved_count": saved_count
        }

    except Exception as error:

        db.session.rollback()

        return {
            "success": False,
            "saved_count": 0,
            "error": str(error)
        }