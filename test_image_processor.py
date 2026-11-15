from app.services.ocr.image_processor import process_image


file_path = "uploads/test_ocr.png"

result = process_image(file_path)

print("Success:", result["success"])
print("Lines:", result["line_count"])
print("Processed records:", result["record_count"])

print("\nFirst records")
print("================")

for record in result["records"][:5]:
    print(record)
    