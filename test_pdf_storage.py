from app import create_app
from app.services.pdf_storage_service import (
    process_and_store_pdf
)


app = create_app()

with app.app_context():

    result = process_and_store_pdf(
        file_path=r"uploads\7c484c2817a44326a203b0bf48e6086e.pdf",
        document_id=9,
        user_id=1
    )

    print("PDF Storage Result")
    print("==================")

    print("Success:")
    print(result["success"])

    if result["success"]:
        print("Document ID:", result["document_id"])
        print("Records processed:", result["record_count"])
        print("Records saved:", result["saved_count"])
        print("Pages:", result["page_count"])
    else:
        print("Stage:", result.get("stage"))
        print("Error:", result.get("error"))