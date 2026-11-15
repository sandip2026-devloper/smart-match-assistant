from app.services.docx_processor import process_docx


result = process_docx(
    r"uploads\84b74b39d90e451ea5e18df7616e7e13.docx"
)

print("Processing:")
print(result["success"])

if result["success"]:

    print(
        "\nParagraphs:",
        result["paragraph_count"]
    )

    print(
        "Tables:",
        result["table_count"]
    )

    print(
        "Processed records:",
        result["record_count"]
    )

    print("\nFirst 5 records")
    print("================")

    for record in result["records"][:5]:

        print(record)

else:

    print(
        "Error:",
        result["error"]
    )