from app import create_app

from app.services.document_processing_service import (
    process_and_store_document
)


app = create_app()

with app.app_context():

    result = process_and_store_document(
        document_id=24,
        user_id=1
    )

    print("Success:", result["success"])
    print("Document ID:", result.get("document_id"))
    print("Records processed:", result.get("record_count"))
    print("Records saved:", result.get("saved_count"))
    print("Status:", result.get("status"))

    if not result["success"]:
        print("Stage:", result.get("stage"))
        print("Error:", result.get("error"))