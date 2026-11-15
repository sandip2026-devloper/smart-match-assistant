from app.services.extractors.txt_extractor import extract_txt


result = extract_txt(
    r"uploads\test_students.txt"
)

print("TXT Extraction")
print("==============")

print("Success:")
print(result["success"])

if result["success"]:
    print("Lines:", result["line_count"])

    print("\nExtracted Lines")
    print("================")

    for line in result["lines"]:
        print(line)

else:
    print("Error:", result["error"])