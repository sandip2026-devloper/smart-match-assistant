from app import create_app
from app.services.txt_storage_service import (
    process_and_store_txt
)


app = create_app()

with app.app_context():

    result = process_and_store_txt(
        file_path=r"uploads\63c6565dd6574c7d82326fb4abede090.txt",
        document_id=10,
        user_id=1
    )

    print("TXT Storage Result")
    print("==================")

    print("Success:")
    print(result["success"])

    if result["success"]:
        print("Document ID:", result["document_id"])
        print("Records processed:", result["record_count"])
        print("Records saved:", result["saved_count"])
        print("Lines:", result["line_count"])
    else:
        print("Stage:", result.get("stage"))
        print("Error:", result.get("error"))