from app import create_app
from app.services.document_processor import process_excel
from app.services.matching.fuzzy_matcher import (
    fuzzy_match_record,
    student_code_similarity
)


app = create_app()

with app.app_context():

    result = process_excel(
        r"uploads\2f8fbef6b7864a728751694e5f68bfbc.xlsx"
    )

    print("Processing:", result["success"])
    print("Total records:", result["record_count"])

    if result["success"]:

        records = result["records"]

        main_records = [
            record
            for record in records
            if any(
                identifier.get("value")
                == "bwubnc26164"
                for identifier in record.get(
                    "identifiers",
                    []
                )
            )
        ]

        print("\nMain candidates:", len(main_records))

        for record in main_records:
            print(
                "RAW:",
                record["raw_record"]
            )
            print(
                "IDENTIFIERS:",
                record["identifiers"]
            )

        print("\nDirect Similarity Test")
        print("======================")

        similarity = student_code_similarity(
            "BWU/BNC/26/16A",
            "BWU/BNC/26/164"
        )

        print(
            "Similarity:",
            similarity
        )

        test_record = {
            "raw_record": {
                "column_3": "BWU/BNC/26/16A"
            },
            "normalized_fields": {
                "column_3": "bwubnc2616a"
            },
            "identifiers": [
                {
                    "field": "column_3",
                    "value": "bwubnc2616a",
                    "score": 9,
                    "type": "student_code"
                }
            ]
        }

        print("\nFuzzy Matcher Test")
        print("==================")

        fuzzy_result = fuzzy_match_record(
            test_record,
            main_records
        )

        print(
            "Status:",
            fuzzy_result["status"]
        )

        print(
            "Match Type:",
            fuzzy_result["match_type"]
        )

        print(
            "Confidence:",
            fuzzy_result["confidence"]
        )

        print(
            "Matches:",
            fuzzy_result["matches"]
        )