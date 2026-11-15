import re


IDENTIFIER_KEYWORDS = {
    "student_code": 10,
    "student_id": 10,
    "roll_no": 10,
    "roll_number": 10,
    "registration_no": 10,
    "registration_number": 10,
    "reg_no": 10,
    "reg_number": 10,
    "id": 8,
    "email": 9,
    "phone": 8,
    "mobile": 8,
    "contact": 6,
}


def normalize_field_name(field_name):
    """
    Normalize a field/column name.

    Example:
        Student Code -> student_code
        Roll No -> roll_no
    """

    if not field_name:
        return ""

    field_name = str(field_name).lower()

    field_name = re.sub(
        r"[^a-z0-9]+",
        "_",
        field_name
    )

    field_name = re.sub(
        r"_+",
        "_",
        field_name
    )

    return field_name.strip("_")


def identifier_score(field_name):
    """
    Return the identifier importance score
    based on the field name.
    """

    normalized = normalize_field_name(
        field_name
    )

    if not normalized:
        return 0

    # Generic columns such as column_1,
    # column_2, etc. must be detected
    # from their values instead.
    if normalized.startswith("column_"):
        return 0

    if normalized in IDENTIFIER_KEYWORDS:
        return IDENTIFIER_KEYWORDS[
            normalized
        ]

    for keyword, score in IDENTIFIER_KEYWORDS.items():

        if keyword in normalized:
            return score - 1

    return 0


def is_email(value):
    """
    Check whether a value looks like an email.
    """

    if not value:
        return False

    return bool(
        re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            str(value)
        )
    )


def is_phone(value):
    """
    Check whether a value looks like a phone number.
    """

    if not value:
        return False

    digits = re.sub(
        r"\D",
        "",
        str(value)
    )

    return 10 <= len(digits) <= 15


def is_student_code(value):
    """
    Detect common student-code formats.

    Supports both the original value and
    normalized value.

    Examples:

        BWU/BPH/24/101
        BWU-BPH-24-101
        BWU_BPH_24_101

    Normalized:

        bwubph24101
        bwubso25085
    """

    if not value:
        return False

    value = str(value).strip()

    # --------------------------------
    # ORIGINAL / SEPARATED FORMAT
    # --------------------------------
    #
    # Example:
    # BWU/BPH/24/101
    #

    separated_pattern = (
        r"^[A-Za-z]{2,10}"
        r"[/_-]"
        r"[A-Za-z0-9]{2,10}"
        r"[/_-]"
        r"\d{2,4}"
        r"[/_-]"
        r"[A-Za-z0-9]{2,10}$"
    )

    if re.match(
        separated_pattern,
        value
    ):
        return True

    # --------------------------------
    # NORMALIZED / COMPACT FORMAT
    # --------------------------------
    #
    # Example:
    # BWUBPH24101
    #

    compact_pattern = (
        r"^[A-Za-z]{2,10}"
        r"[A-Za-z]{2,10}"
        r"\d{2,4}"
        r"[A-Za-z0-9]{2,10}$"
    )

    if re.match(
        compact_pattern,
        value
    ):
        return True

    return False


def detect_value_type(value):
    """
    Detect the type of an identifier value.
    """

    if not value:
        return "empty"

    if is_email(value):
        return "email"

    if is_phone(value):
        return "phone"

    if is_student_code(value):
        return "student_code"

    return "identifier"


def detect_identifiers(normalized_fields):
    """
    Detect identifiers using:

    1. Field/column names
    2. Value patterns

    Value-pattern detection is especially
    useful for headerless Excel sheets.
    """

    identifiers = []

    for field_name, value in normalized_fields.items():

        if not value:
            continue

        # --------------------------------
        # 1. HEADER-BASED IDENTIFIER
        # --------------------------------

        score = identifier_score(
            field_name
        )

        if score > 0:

            identifiers.append({
                "field": field_name,
                "value": value,
                "score": score,
                "type": detect_value_type(
                    value
                )
            })

            continue

        # --------------------------------
        # 2. VALUE-BASED STUDENT CODE
        # --------------------------------

        if is_student_code(value):

            identifiers.append({
                "field": field_name,
                "value": value,
                "score": 9,
                "type": "student_code"
            })

            continue

        # --------------------------------
        # 3. VALUE-BASED EMAIL
        # --------------------------------

        if is_email(value):

            identifiers.append({
                "field": field_name,
                "value": value,
                "score": 9,
                "type": "email"
            })

            continue

        # --------------------------------
        # 4. VALUE-BASED PHONE
        # --------------------------------

        if is_phone(value):

            identifiers.append({
                "field": field_name,
                "value": value,
                "score": 8,
                "type": "phone"
            })

    identifiers.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return identifiers


def analyze_record(normalized_record):
    """
    Analyze one normalized record and
    return its detected identifiers.
    """

    normalized_fields = normalized_record.get(
        "normalized_fields",
        {}
    )

    return detect_identifiers(
        normalized_fields
    )