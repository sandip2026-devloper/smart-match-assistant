from app.services.extractors.pdf_extractor import extract_pdf


result = extract_pdf(
    r"uploads\7c484c2817a44326a203b0bf48e6086e.pdf"
)

print("PDF Extraction")
print("==============")

print("Success:")
print(result["success"])

if result["success"]:
    print("Pages:", result["page_count"])

    print("\nFirst 3 pages")
    print("==============")

    for page in result["pages"][:3]:
        print("\nPage:", page["page_number"])
        print(page["text"][:500])

else:
    print("Error:", result["error"])