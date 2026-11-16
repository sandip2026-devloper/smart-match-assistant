import re

from rapidfuzz.fuzz import ratio


FUZZY_THRESHOLD = 0.85
STUDENT_CODE_THRESHOLD = 0.90


def fuzzy_similarity(value1, value2):
    if not value1 or not value2:
        return 0.0

    return ratio(str(value1), str(value2)) / 100.0


def parse_student_code(value):
    if not value:
        return None

    value = str(value).strip()

    compact_pattern = r"^([A-Za-z]{4,10})(\d{2})(\d{2,10})$"

    compact_match = re.match(
        compact_pattern,
        value
    )

    if compact_match:
        return {
            "university": compact_match.group(1).lower(),
            "course": "",
            "year": compact_match.group(2),
            "number": compact_match.group(3).lower()
        }

    separated_pattern = (
        r"^([A-Za-z]{2,10})"
        r"[/_-]"
        r"([A-Za-z0-9]{2,10})"
        r"[/_-]"
        r"(\d{2,4})"
        r"[/_-]"
        r"([A-Za-z0-9]{2,10})$"
    )

    separated_match = re.match(
        separated_pattern,
        value
    )

    if separated_match:
        return {
            "university": separated_match.group(1).lower(),
            "course": separated_match.group(2).lower(),
            "year": separated_match.group(3),
            "number": separated_match.group(4).lower()
        }

    return None
    return {
        "university": match.group(1).lower(),
        "course": match.group(2).lower(),
        "year": match.group(3),
        "number": match.group(4).lower()
    }


def get_raw_identifier_value(record, identifier):
    raw_record = record.get("raw_record", {})

    field = identifier.get("field")

    if field in raw_record:
        value = raw_record.get(field)

        if value is not None:
            return str(value).strip()

    return identifier.get("value", "")


def student_code_similarity(value1, value2):
    code1 = parse_student_code(value1)
    code2 = parse_student_code(value2)

    if not code1 or not code2:
        return 0.0

    if code1["university"] != code2["university"]:
        return 0.0

    if code1["course"] != code2["course"]:
        return 0.0

    if code1["year"] != code2["year"]:
        return 0.0

    if code1["number"] == code2["number"]:
        return 1.0

    number_similarity = fuzzy_similarity(
        code1["number"],
        code2["number"]
    )

    if number_similarity >= 0.60:
        return 0.92

    return 0.0


def compare_identifier(
    secondary_record,
    secondary_identifier,
    main_record,
    main_identifier
):
    secondary_type = secondary_identifier.get("type")
    main_type = main_identifier.get("type")

    if secondary_type != main_type:
        return 0.0

    secondary_field = secondary_identifier.get("field")
    main_field = main_identifier.get("field")

    if (
        secondary_field != main_field
        and not str(secondary_field).startswith("column_")
        and not str(main_field).startswith("column_")
    ):
        return 0.0

    if secondary_type == "student_code":

        secondary_value = get_raw_identifier_value(
            secondary_record,
            secondary_identifier
        )

        main_value = get_raw_identifier_value(
            main_record,
            main_identifier
        )

        return student_code_similarity(
            secondary_value,
            main_value
        )

    secondary_value = secondary_identifier.get("value")
    main_value = main_identifier.get("value")

    return fuzzy_similarity(
        secondary_value,
        main_value
    )


def fuzzy_match_record(secondary_record, main_records):

    secondary_identifiers = secondary_record.get(
        "identifiers",
        []
    )

    if not secondary_identifiers:
        return {
            "status": "unmatched",
            "match_type": None,
            "confidence": 0.0,
            "matches": []
        }

    candidates = []

    student_code_identifiers = [
        identifier
        for identifier in secondary_identifiers
        if identifier.get("type") == "student_code"
    ]

    for main_record in main_records:

        main_identifiers = main_record.get(
            "identifiers",
            []
        )

        # Optimization:
        # For student codes, only compare records that have
        # the same university/course/year structure.
        if student_code_identifiers:

            compatible_main_identifiers = []

            for main_identifier in main_identifiers:

                if main_identifier.get("type") != "student_code":
                    continue

                secondary_value = get_raw_identifier_value(
                    secondary_record,
                    student_code_identifiers[0]
                )

                main_value = get_raw_identifier_value(
                    main_record,
                    main_identifier
                )

                secondary_code = parse_student_code(
                    secondary_value
                )

                main_code = parse_student_code(
                    main_value
                )

                if not secondary_code or not main_code:
                    continue

                if (
                    secondary_code["university"]
                    == main_code["university"]
                    and
                    secondary_code["course"]
                    == main_code["course"]
                    and
                    secondary_code["year"]
                    == main_code["year"]
                ):
                    compatible_main_identifiers.append(
                        main_identifier
                    )

            if not compatible_main_identifiers:
                continue

            main_identifiers = compatible_main_identifiers

        best_score = 0.0
        best_field = None

        for secondary_identifier in secondary_identifiers:

            for main_identifier in main_identifiers:

                score = compare_identifier(
                    secondary_record,
                    secondary_identifier,
                    main_record,
                    main_identifier
                )

                if score > best_score:
                    best_score = score
                    best_field = secondary_identifier.get(
                        "field"
                    )

        identifier_types = [
            identifier.get("type")
            for identifier in secondary_identifiers
        ]

        if "student_code" in identifier_types:
            threshold = STUDENT_CODE_THRESHOLD
        else:
            threshold = FUZZY_THRESHOLD

        if best_score >= threshold:

            candidates.append({
                "record": main_record,
                "confidence": best_score,
                "field": best_field
            })

    if not candidates:

        return {
            "status": "unmatched",
            "match_type": None,
            "confidence": 0.0,
            "matches": []
        }

    candidates.sort(
        key=lambda item: item["confidence"],
        reverse=True
    )

    best = candidates[0]

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
                "confidence": best["confidence"],
                "matches": [
                    candidate["record"]
                    for candidate in candidates
                ]
            }

    return {
        "status": "matched",
        "match_type": "fuzzy",
        "confidence": best["confidence"],
        "matches": [
            best["record"]
        ]
    }