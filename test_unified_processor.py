from app.services.unified_document_processor import (
    process_document
)


tests = [
    {
        "file": "uploads/2f8fbef6b7864a728751694e5f68bfbc.xlsx",
        "type": "xlsx"
    },
    {
        "file": "uploads/84b74b39d90e451ea5e18df7616e7e13.docx",
        "type": "docx"
    },
    {
        "file": "uploads/7c484c2817a44326a203b0bf48e6086e.pdf",
        "type": "pdf"
    },
    {
        "file": "uploads/63c6565dd6574c7d82326fb4abede090.txt",
        "type": "txt"
    },
    {
        "file": "uploads/681ac2e666dd44d0b33742373af2bd85.png",
        "type": "png"
    }
]


for test in tests:

    print("\n==============================")
    print("Testing:", test["type"])
    print("==============================")

    result = process_document(
        file_path=test["file"],
        document_type=test["type"]
    )

    print("Success:", result.get("success"))
    print("Records:", result.get("record_count"))

    if not result.get("success"):
        print("Stage:", result.get("stage"))
        print("Error:", result.get("error"))