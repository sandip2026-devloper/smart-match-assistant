from app import create_app
from app.services.document_processor import process_excel
from app.services.matching.matching_engine import match_documents

app = create_app()

with app.app_context():

    result = process_excel(
        r"uploads\2f8fbef6b7864a728751694e5f68bfbc.xlsx"
    )

    print("Processing:", result["success"])
    print("Total records:", result["record_count"])

    if result["success"]:

        records = result["records"]

        # Temporary test:
        # First 100 records = Main Document
        # Next 20 records = Secondary Document
        main_records = records[:100]
        secondary_records = records[100:120]

        match_result = match_documents(
            main_records,
            secondary_records
        )

        print("\nMatching Result")
        print("====================")
        print("Main records:", match_result["main_record_count"])
        print("Secondary records:", match_result["secondary_record_count"])
        print("Matched:", match_result["matched_count"])
        print("Unmatched:", match_result["unmatched_count"])
        print("Duplicate:", match_result["duplicate_count"])

        print("\nFirst Result:")
        if match_result["matched"]:
            print(match_result["matched"][0])
        elif match_result["unmatched"]:
            print(match_result["unmatched"][0])
        elif match_result["duplicate"]:
            print(match_result["duplicate"][0])