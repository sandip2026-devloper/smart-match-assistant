from app.services.ocr.image_ocr import extract_image_ocr


file_path = "uploads/test_ocr.png"

result = extract_image_ocr(file_path)

print("Success:", result["success"])
print("Lines:", result.get("line_count"))

print("\nOCR Text")
print("========")
print(result.get("text", ""))

print("\nOCR Lines")
print("=========")

for line in result.get("lines", []):
    print(line)