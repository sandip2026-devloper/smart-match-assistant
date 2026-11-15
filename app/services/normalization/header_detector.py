import re


HEADER_KEYWORDS = {
    "sl",
    "slno",
    "serial",
    "serialno",
    "student",
    "studentcode",
    "studentname",
    "name",
    "code",
    "roll",
    "rollno",
    "id",
    "studentid",
    "email",
    "phone",
    "mobile",
    "contact",
    "address",
    "course",
    "department",
    "branch",
    "age",
    "gender",
    "dob",
    "date",
    "attendance",
    "status",
    "semester",
    "year",
}


def clean_value(value):
    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    return re.sub(r"\s+", " ", text)


def normalize_header(value):
    text = clean_value(value).lower()

    text = re.sub(
        r"[\s\-_\/\.]+",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9]",
        "",
        text
    )

    return text


def header_score(value):
    """
    Give a score to a possible header.
    """

    normalized = normalize_header(value)

    if not normalized:
        return 0

    if normalized.startswith("unnamed"):
        return 0

    if normalized.isdigit():
        return 0

    if normalized in HEADER_KEYWORDS:
        return 3

    for keyword in HEADER_KEYWORDS:
        if keyword in normalized:
            return 2

    return 0


def looks_like_data(value):
    """
    Detect values that look more like actual data
    than column headers.
    """

    text = clean_value(value)

    if not text:
        return False

    # Student-code style value
    if re.match(
        r"^[A-Za-z]{2,10}[/\-_][A-Za-z0-9]{2,10}[/\-_]",
        text
    ):
        return True

    # Mostly numeric value
    if re.match(r"^\d+$", text):
        return True

    return False


def detect_header_row(rows, max_rows=10):
    """
    Inspect the first few rows of raw Excel data
    and find the most likely header row.

    Returns:
        {
            "header_row": integer or None,
            "confidence": float,
            "reason": str
        }
    """

    if not rows:
        return {
            "header_row": None,
            "confidence": 0.0,
            "reason": "No rows available."
        }

    best_row = None
    best_score = 0

    rows_to_check = rows[:max_rows]

    for row_index, row in enumerate(rows_to_check):

        if not isinstance(row, (list, tuple)):
            continue

        score = 0
        data_like_count = 0
        non_empty_count = 0

        for value in row:

            text = clean_value(value)

            if not text:
                continue

            non_empty_count += 1

            score += header_score(text)

            if looks_like_data(text):
                data_like_count += 1

        if non_empty_count == 0:
            continue

        # Penalize rows that look mostly like data.
        score -= data_like_count

        if score > best_score:
            best_score = score
            best_row = row_index

    if best_row is None:
        return {
            "header_row": None,
            "confidence": 0.0,
            "reason": "No meaningful header found."
        }

    confidence = min(
        best_score / 10,
        1.0
    )

    return {
        "header_row": best_row,
        "confidence": confidence,
        "reason": "Header keywords detected."
    }