from app.services.pdf_processor import process_pdf


result = process_pdf(
    r"uploads\7c484c2817a44326a203b0bf48e6086e.pdf"
)

print("PDF Processing")
print("==============")

print("Success:")
print(result["success"])

if result["success"]:

    print("\nPages:", result["page_count"])
    print("Processed records:", result["record_count"])

    print("\nFirst 10 records")
    print("================")

    for record in result["records"][:10]:
        print(record)

else:
    print("Stage:", result.get("stage"))
    print("Error:", result.get("error"))