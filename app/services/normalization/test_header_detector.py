from app import create_app
from app.services.extractors.excel_extractor import extract_excel
from app.services.normalization.header_detector import detect_header_row

app = create_app()

with app.app_context():

    result = extract_excel(
        r"uploads\2f8fbef6b7864a728751694e5f68bfbc.xlsx"
    )

    print("Extraction:", result["success"])

    if result["success"]:

        for sheet_name, records in result["sheets"].items():

            print("\n==============================")
            print("Sheet:", sheet_name)
            print("Records:", len(records))

            if not records:
                continue

            # Convert dictionary records into rows
            rows = []

            for record in records[:10]:
                rows.append(
                    list(record.values())
                )

            header_result = detect_header_row(rows)

            print(
                "Detected header row:",
                header_result["header_row"]
            )

            print(
                "Confidence:",
                header_result["confidence"]
            )

            print(
                "Reason:",
                header_result["reason"]
            )

            print(
                "First row:",
                rows[0]
            )