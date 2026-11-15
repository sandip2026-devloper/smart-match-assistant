def build_identifier_index(records):
    """
    Build an index of identifiers from Main-document records.

    The index uses:

        identifier_type:value

    instead of:

        field:value

    This allows headered and headerless records
    to match correctly.

    Example:

        student_code:bwubph24100
    """

    index = {}

    for record in records:

        identifiers = record.get(
            "identifiers",
            []
        )

        for identifier in identifiers:

            identifier_type = identifier.get(
                "type"
            )

            value = identifier.get(
                "value"
            )

            if not identifier_type or not value:
                continue

            key = (
                f"{identifier_type}:{value}"
            )

            if key not in index:

                index[key] = []

            index[key].append(
                record
            )

    return index


def exact_match_record(
    secondary_record,
    main_index
):
    """
    Find exact identifier matches for
    one secondary record.
    """

    identifiers = secondary_record.get(
        "identifiers",
        []
    )

    matches = []

    checked_keys = set()

    for identifier in identifiers:

        identifier_type = identifier.get(
            "type"
        )

        value = identifier.get(
            "value"
        )

        if not identifier_type or not value:
            continue

        key = (
            f"{identifier_type}:{value}"
        )

        if key in checked_keys:
            continue

        checked_keys.add(
            key
        )

        candidates = main_index.get(
            key,
            []
        )

        for candidate in candidates:

            if candidate not in matches:

                matches.append(
                    candidate
                )

    # --------------------------------
    # ONE MATCH
    # --------------------------------

    if len(matches) == 1:

        return {
            "status": "matched",
            "match_type": "exact_identifier",
            "confidence": 1.0,
            "matches": matches
        }

    # --------------------------------
    # MULTIPLE MATCHES
    # --------------------------------

    if len(matches) > 1:

        return {
            "status": "duplicate",
            "match_type": "exact_identifier",
            "confidence": 1.0,
            "matches": matches
        }

    # --------------------------------
    # NO MATCH
    # --------------------------------

    return {
        "status": "unmatched",
        "match_type": None,
        "confidence": 0.0,
        "matches": []
    }