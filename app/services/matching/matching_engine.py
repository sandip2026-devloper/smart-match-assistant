from app.services.matching.exact_matcher import (
    build_identifier_index,
    exact_match_record
)

from app.services.matching.fuzzy_matcher import (
    fuzzy_match_record
)


def match_documents(
    main_records,
    secondary_records
):
    """
    Complete matching pipeline.

    Order:

    1. Exact identifier matching
    2. Fuzzy matching if exact match fails
    3. Unmatched if no suitable match exists
    4. Duplicate if multiple candidates are ambiguous
    """

    main_index = build_identifier_index(
        main_records
    )

    matched = []
    unmatched = []
    duplicate = []

    for secondary_record in secondary_records:

        # --------------------------------
        # STEP 1: EXACT MATCH
        # --------------------------------

        exact_result = exact_match_record(
            secondary_record,
            main_index
        )

        if exact_result["status"] == "matched":

            result_item = {
                "secondary_record": secondary_record,
                "status": "matched",
                "match_type": "exact_identifier",
                "confidence": 1.0,
                "matches": exact_result["matches"]
            }

            matched.append(result_item)

            continue

        # --------------------------------
        # STEP 2: EXACT DUPLICATE
        # --------------------------------

        if exact_result["status"] == "duplicate":

            result_item = {
                "secondary_record": secondary_record,
                "status": "duplicate",
                "match_type": "exact_identifier",
                "confidence": 1.0,
                "matches": exact_result["matches"]
            }

            duplicate.append(result_item)

            continue

        # --------------------------------
        # STEP 3: FUZZY MATCH
        # --------------------------------

        fuzzy_result = fuzzy_match_record(
            secondary_record,
            main_records
        )

        result_item = {
            "secondary_record": secondary_record,
            "status": fuzzy_result["status"],
            "match_type": fuzzy_result["match_type"],
            "confidence": fuzzy_result["confidence"],
            "matches": fuzzy_result["matches"]
        }

        # --------------------------------
        # STEP 4: SAVE RESULT
        # --------------------------------

        if fuzzy_result["status"] == "matched":

            matched.append(result_item)

        elif fuzzy_result["status"] == "duplicate":

            duplicate.append(result_item)

        else:

            unmatched.append(result_item)

    return {
        "success": True,

        "main_record_count": len(main_records),

        "secondary_record_count": len(
            secondary_records
        ),

        "matched": matched,

        "unmatched": unmatched,

        "duplicate": duplicate,

        "matched_count": len(matched),

        "unmatched_count": len(unmatched),

        "duplicate_count": len(duplicate)
    }