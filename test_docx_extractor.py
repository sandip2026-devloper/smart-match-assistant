from app.services.extractors.docx_extractor import extract_docx


result = extract_docx(
    r"uploads\84b74b39d90e451ea5e18df7616e7e13.docx"
)

print("Success:")
print(result["success"])

if result["success"]:

    print("\nParagraphs:")
    print(result["paragraphs"])

    print("\nTables:")
    print(result["tables"])

    print(
        "\nParagraph count:",
        result["paragraph_count"]
    )

    print(
        "Table count:",
        result["table_count"]
    )

else:

    print(
        "Error:",
        result["error"]
    )