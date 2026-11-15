from app import create_app

from app.services.matching.matching_engine import (
    match_records
)


app = create_app()


with app.app_context():

    # Main Document
    main_record_1 = {
        "sheet_name": "MAIN",
        "source_row": 2,
        "raw_record": {
            "Student Code": "BWU/BSO/25/085",
            "Student Name": "Student One"
        },
        "normalized_fields": {
            "student_code": "bwubso25085",
            "student_name": "studentone"
        },
        "header_type": "normal",
        "identifiers": [
            {
                "field": "student_code",
                "value": "bwubso25085",
                "score": 10,
                "type": "student_code"
            }
        ]
    }

    main_record_2 = {
        "sheet_name": "MAIN",
        "source_row": 3,
        "raw_record": {
            "Student Code": "BWU/BSO/25/085",
            "Student Name": "Student Two"
        },
        "normalized_fields": {
            "student_code": "bwubso25085",
            "student_name": "studenttwo"
        },
        "header_type": "normal",
        "identifiers": [
            {
                "field": "student_code",
                "value": "bwubso25085",
                "score": 10,
                "type": "student_code"
            }
        ]
    }

    # Secondary Document
    secondary_record = {
        "sheet_name": "SECONDARY",
        "source_row": 2,
        "raw_record": {
            "Student Code": "BWU/BSO/25/085"
        },
        "normalized_fields": {
            "student_code": "bwubso25085"
        },
        "header_type": "normal",
        "identifiers": [
            {
                "field": "student_code",
                "value": "bwubso25085",
                "score": 10,
                "type": "student_code"
            }
        ]
    }

    result = match_records(
        main_records=[
            main_record_1,
            main_record_2
        ],
        secondary_records=[
            secondary_record
        ]
    )

    print("\nDuplicate Test Result")
    print("======================")

    print(
        "Matched:",
        result["matched_count"]
    )

    print(
        "Unmatched:",
        result["unmatched_count"]
    )

    print(
        "Duplicate:",
        result["duplicate_count"]
    )

    print("\nDuplicate Results:")

    for item in result["duplicate"]:
        print(item)