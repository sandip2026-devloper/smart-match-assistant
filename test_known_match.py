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

        duplicate_records = [
            record
            for record in records
            if any(
                identifier.get("value")
                == "bwubnc26164"
                for identifier
                in record.get("identifiers", [])
            )
        ]

        print(
            "\nDuplicate records found:",
            len(duplicate_records)
        )

        for record in duplicate_records:

            print(
                record["sheet_name"],
                record["source_row"],
                record["raw_record"]
            )

        if len(duplicate_records) == 2:

            # Use the first record as the
            # secondary record.
            secondary_records = [
                duplicate_records[0]
            ]

            # Use both records as possible
            # Main-document candidates.
            main_records = duplicate_records

            match_result = match_documents(
                main_records,
                secondary_records
            )

            print("\nMatching Result")
            print("====================")
            print(
                "Matched:",
                match_result["matched_count"]
            )
            print(
                "Unmatched:",
                match_result["unmatched_count"]
            )
            print(
                "Duplicate:",
                match_result["duplicate_count"]
            )

            print("\nDuplicate Result:")

            if match_result["duplicate"]:

                print(
                    match_result["duplicate"][0]
                )

            else:

                print(
                    "ERROR: Expected duplicate result."
                )