from app import create_app

from app.services.ocr.image_storage_service import (
    process_and_store_image
)


app = create_app()

file_path = (
    "uploads/"
    "681ac2e666dd44d0b33742373af2bd85.png"
)

with app.app_context():

    result = process_and_store_image(
        file_path=file_path,
        document_id=11,
        user_id=1
    )

    print("Success:", result["success"])
    print("Document ID:", result.get("document_id"))
    print("Records processed:", result.get("record_count"))
    print("Records saved:", result.get("saved_count"))
    print("Lines:", result.get("line_count"))

    if not result["success"]:
        print("Error:", result.get("error"))