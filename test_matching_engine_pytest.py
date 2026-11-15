from app.services.matching.matching_engine import match_records


def test_duplicate_identifier_matching():
    main_records = [
        {
            "sheet_name": "MAIN",
            "source_row": 2,
            "raw_record": {
                "Student Code": "BWU/BSO/25/085",
                "Student Name": "Student One",
            },
            "normalized_fields": {
                "student_code": "bwubso25085",
                "student_name": "studentone",
            },
            "header_type": "normal",
            "identifiers": [
                {
                    "field": "student_code",
                    "value": "bwubso25085",
                    "score": 10,
                    "type": "student_code",
                }
            ],
        },
        {
            "sheet_name": "MAIN",
            "source_row": 3,
            "raw_record": {
                "Student Code": "BWU/BSO/25/085",
                "Student Name": "Student Two",
            },
            "normalized_fields": {
                "student_code": "bwubso25085",
                "student_name": "studenttwo",
            },
            "header_type": "normal",
            "identifiers": [
                {
                    "field": "student_code",
                    "value": "bwubso25085",
                    "score": 10,
                    "type": "student_code",
                }
            ],
        },
    ]

    secondary_records = [
        {
            "sheet_name": "SECONDARY",
            "source_row": 2,
            "raw_record": {
                "Student Code": "BWU/BSO/25/085",
            },
            "normalized_fields": {
                "student_code": "bwubso25085",
            },
            "header_type": "normal",
            "identifiers": [
                {
                    "field": "student_code",
                    "value": "bwubso25085",
                    "score": 10,
                    "type": "student_code",
                }
            ],
        }
    ]

    result = match_records(
        main_records=main_records,
        secondary_records=secondary_records,
    )

    assert result["success"] is True
    assert result["matched_count"] == 0
    assert result["unmatched_count"] == 0
    assert result["duplicate_count"] == 1
    assert len(result["duplicate"][0]["matches"]) == 2