from app.services.txt_processor import process_txt


result = process_txt(
    r"uploads\test_students.txt"
)

print("TXT Processing")
print("==============")

print("Success:")
print(result["success"])

if result["success"]:

    print("\nLines:", result["line_count"])
    print("Processed records:", result["record_count"])

    print("\nRecords")
    print("=======")

    for record in result["records"]:
        print(record)

else:
    print("Stage:", result.get("stage"))
    print("Error:", result.get("error"))