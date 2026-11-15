import re

from rapidfuzz.fuzz import ratio


FUZZY_THRESHOLD = 0.85
STUDENT_CODE_THRESHOLD = 0.90


def fuzzy_similarity(value1, value2):
    """
    Calculate similarity between two values.

    Returns a value between 0.0 and 1.0.
    """

    if not value1 or not value2:
        return 0.0

    return ratio(
        str(value1),
        str(value2)
    ) / 100.0


def parse_student_code(value):
    """
    Parse a student code.

    Example:
        BWU/BNC/26/164

    Returns:
        university = bwu
        course = bnc
        year = 26
        number = 164
    """

    if not value:
        return None

    value = str(value).strip()

    pattern = (
        r"^([A-Za-z]{2,10})"
        r"[/_-]"
        r"([A-Za-z0-9]{2,10})"
        r"[/_-]"
        r"(\d{2,4})"
        r"[/_-]"
        r"([A-Za-z0-9]{2,10})$"
    )

    match = re.match(
        pattern,
        value
    )

    if not match:
        return None

    return {
        "university": match.group(1).lower(),
        "course": match.group(2).lower(),
        "year": match.group(3),
        "number": match.group(4).lower()
    }


def get_raw_identifier_value(
    record,
    identifier
):
    """
    Get the original identifier value
    from the raw record.
    """

    raw_record = record.get(
        "raw_record",
        {}
    )

    field = identifier.get(
        "field"
    )

    if field in raw_record:

        value = raw_record.get(
            field
        )

        if value is not None:
            return str(value).strip()

    return identifier.get(
        "value",
        ""
    )


def student_code_similarity(
    value1,
    value2
):
    """
    Compare two student codes.

    University, course and year must
    match exactly.

    A small typo in the final student
    number is allowed.
    """

    code1 = parse_student_code(
        value1
    )

    code2 = parse_student_code(
        value2
    )

    if code1 and code2:

        # University must match.
        if (
            code1["university"]
            != code2["university"]
        ):
            return 0.0

        # Course must match.
        if (
            code1["course"]
            != code2["course"]
        ):
            return 0.0

        # Year must match.
        if (
            code1["year"]
            != code2["year"]
        ):
            return 0.0

        # Exact student number.
        if (
            code1["number"]
            == code2["number"]
        ):
            return 1.0

        # Allow a small typo in the
        # final student number.
        number_similarity = fuzzy_similarity(
            code1["number"],
            code2["number"]
        )

        if number_similarity >= 0.60:
            return 0.92

        return 0.0

    return 0.0


def compare_identifier(
    secondary_record,
    secondary_identifier,
    main_record,
    main_identifier
):
    """
    Compare two identifiers.
    """

    secondary_type = (
        secondary_identifier.get(
            "type"
        )
    )

    main_type = (
        main_identifier.get(
            "type"
        )
    )

    # Identifier types must match.
    if secondary_type != main_type:
        return 0.0

    secondary_field = (
        secondary_identifier.get(
            "field"
        )
    )

    main_field = (
        main_identifier.get(
            "field"
        )
    )

    # For real headers, field names should
    # match. Headerless column_* fields are
    # allowed to match different column names.
    if (
        secondary_field != main_field
        and not str(
            secondary_field
        ).startswith("column_")
        and not str(
            main_field
        ).startswith("column_")
    ):
        return 0.0

    # Student-code matching uses the
    # original raw values.
    if secondary_type == "student_code":

        secondary_value = (
            get_raw_identifier_value(
                secondary_record,
                secondary_identifier
            )
        )

        main_value = (
            get_raw_identifier_value(
                main_record,
                main_identifier
            )
        )

        return student_code_similarity(
            secondary_value,
            main_value
        )

    # Other identifier types use their
    # normalized values.
    secondary_value = (
        secondary_identifier.get(
            "value"
        )
    )

    main_value = (
        main_identifier.get(
            "value"
        )
    )

    return fuzzy_similarity(
        secondary_value,
        main_value
    )


def fuzzy_match_record(
    secondary_record,
    main_records
):
    """
    Find the best fuzzy match for one
    secondary record.
    """

    secondary_identifiers = (
        secondary_record.get(
            "identifiers",
            []
        )
    )

    if not secondary_identifiers:

        return {
            "status": "unmatched",
            "match_type": None,
            "confidence": 0.0,
            "matches": []
        }

    candidates = []

    for main_record in main_records:

        main_identifiers = (
            main_record.get(
                "identifiers",
                []
            )
        )

        best_score = 0.0
        best_field = None

        for secondary_identifier in (
            secondary_identifiers
        ):

            for main_identifier in (
                main_identifiers
            ):

                score = compare_identifier(
                    secondary_record,
                    secondary_identifier,
                    main_record,
                    main_identifier
                )

                if score > best_score:

                    best_score = score

                    best_field = (
                        secondary_identifier.get(
                            "field"
                        )
                    )

        identifier_types = [
            identifier.get("type")
            for identifier
            in secondary_identifiers
        ]

        if "student_code" in identifier_types:

            threshold = (
                STUDENT_CODE_THRESHOLD
            )

        else:

            threshold = FUZZY_THRESHOLD

        if best_score >= threshold:

            candidates.append({
                "record": main_record,
                "confidence": best_score,
                "field": best_field
            })

    # No candidate passed the threshold.
    if not candidates:

        return {
            "status": "unmatched",
            "match_type": None,
            "confidence": 0.0,
            "matches": []
        }

    # Highest confidence first.
    candidates.sort(
        key=lambda item: item[
            "confidence"
        ],
        reverse=True
    )

    best = candidates[0]

    # If two candidates have almost the
    # same confidence, treat as duplicate.
    if len(candidates) > 1:

        second = candidates[1]

        confidence_gap = (
            best["confidence"]
            - second["confidence"]
        )

        if confidence_gap < 0.03:

            return {
                "status": "duplicate",
                "match_type": "fuzzy",
                "confidence": best[
                    "confidence"
                ],
                "matches": [
                    candidate["record"]
                    for candidate
                    in candidates
                ]
            }

    # One clear best candidate.
    return {
        "status": "matched",
        "match_type": "fuzzy",
        "confidence": best[
            "confidence"
        ],
        "matches": [
            best["record"]
        ]
    }