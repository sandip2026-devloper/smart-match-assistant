from app import create_app
from app.services.docx_storage_service import (
    process_and_store_docx
)


app = create_app()

with app.app_context():

    result = process_and_store_docx(
        file_path=r"uploads\84b74b39d90e451ea5e18df7616e7e13.docx",
        document_id=8,
        user_id=1
    )

    print("DOCX Storage Result")
    print("===================")

    print("Success:")
    print(result["success"])

    if result["success"]:
        print("Document ID:", result["document_id"])
        print("Records processed:", result["record_count"])
        print("Records saved:", result["saved_count"])
        print("Paragraphs:", result["paragraph_count"])
        print("Tables:", result["table_count"])
    else:
        print("Stage:", result.get("stage"))
        print("Error:", result.get("error"))