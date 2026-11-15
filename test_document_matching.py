from app import create_app

from app.services.document_matching_service import (
    match_document_pair
)


app = create_app()

with app.app_context():

    result = match_document_pair(
        main_document_id=7,
        secondary_document_id=8,
        user_id=1
    )

    print("Success:")
    print(result["success"])

    if result["success"]:

        print("\nDocument Matching Result")
        print("=========================")

        print(
            "Main document:",
            result["main_document"].original_name
        )

        print(
            "Secondary document:",
            result["secondary_document"].original_name
        )

        print(
            "Main records:",
            result["main_record_count"]
        )

        print(
            "Secondary records:",
            result["secondary_record_count"]
        )

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

    else:

        print(
            "Error:",
            result["error"]
        )
        