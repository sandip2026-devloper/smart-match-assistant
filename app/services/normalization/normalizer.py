import re
import math


# Common words used in real document headers
HEADER_KEYWORDS = {
    "sl",
    "sln",
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


def clean_text(value):
    """
    Clean text while keeping the original value unchanged.
    """

    if value is None:
        return ""

    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
    except Exception:
        pass

    text = str(value).strip()

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text


def normalize_text(value):
    """
    Create a matching-friendly version of a value.
    """

    text = clean_text(value)

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[\s\-_/.,]+", "", text)

    return text


def normalize_column_name(column_name):
    """
    Normalize a column name.
    """

    text = clean_text(column_name)

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[\s\-_/]+", "_", text)

    text = re.sub(r"[^a-z0-9_]", "", text)

    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def header_keyword_score(column_name):
    """
    Give a score showing how likely a column name is
    to be a real document header.
    """

    normalized = normalize_column_name(column_name)

    if not normalized:
        return 0

    # Remove underscores for comparison
    compact = normalized.replace("_", "")

    if compact in HEADER_KEYWORDS:
        return 3

    for keyword in HEADER_KEYWORDS:

        if keyword in compact:
            return 2

    return 0


def is_meaningful_header(column_name):
    """
    Check whether a column name looks like a real header.
    """

    text = clean_text(column_name)

    if not text:
        return False

    if text.lower().startswith("unnamed"):
        return False

    # A number is normally a data value, not a header
    if text.isdigit():
        return False

    # Student codes are normally data, not headers
    compact = re.sub(r"[\s\-_/]+", "", text).lower()

    if re.match(
        r"^[a-z]{2,10}\d{2,4}[a-z0-9]*$",
        compact
    ):
        return False

    # Names are normally data, not headers
    if len(text.split()) >= 2 and len(text) <= 60:
        if not any(
            keyword in compact
            for keyword in HEADER_KEYWORDS
        ):
            return False

    if header_keyword_score(text) > 0:
        return True

    return False


def detect_header_type(record):
    """
    Detect whether extracted column names appear to be
    real headers.
    """

    if not record:
        return "empty"

    total_columns = len(record)

    if total_columns == 0:
        return "empty"

    meaningful_headers = 0
    keyword_score = 0

    for column_name in record.keys():

        if is_meaningful_header(column_name):
            meaningful_headers += 1

        keyword_score += header_keyword_score(
            column_name
        )

    # Strong evidence of a real header
    if keyword_score >= 3:
        return "normal"

    # Most columns look like headers
    ratio = meaningful_headers / total_columns

    if ratio >= 0.5:
        return "normal"

    return "uncertain"


def normalize_record(
    record,
    sheet_name,
    source_row
):
    """
    Normalize one extracted row.

    raw_record:
        Original Excel values.

    normalized_fields:
        Clean values used later by the matching engine.
    """

    raw_record = {}

    normalized_fields = {}

    for column_name, value in record.items():

        original_column = str(column_name)

        raw_record[original_column] = value

        normalized_column = normalize_column_name(
            original_column
        )

        if not normalized_column:
            continue

        normalized_value = normalize_text(value)

        normalized_fields[
            normalized_column
        ] = normalized_value

    return {
        "sheet_name": sheet_name,
        "source_row": source_row,
        "raw_record": raw_record,
        "normalized_fields": normalized_fields
    }


def normalize_sheets(sheets):
    """
    Normalize all extracted sheets.
    """

    try:

        normalized_records = []

        sheet_summary = {}

        for sheet_name, records in sheets.items():

            if not isinstance(records, list):
                continue

            sheet_record_count = 0
            normal_count = 0
            uncertain_count = 0

            for index, record in enumerate(records):

                if not isinstance(record, dict):
                    continue

                # Excel data starts after the header row
                source_row = index + 2

                header_type = detect_header_type(
                    record
                )

                normalized_record = normalize_record(
                    record=record,
                    sheet_name=sheet_name,
                    source_row=source_row
                )

                normalized_record[
                    "header_type"
                ] = header_type

                normalized_records.append(
                    normalized_record
                )

                sheet_record_count += 1

                if header_type == "normal":
                    normal_count += 1

                elif header_type == "uncertain":
                    uncertain_count += 1

            sheet_summary[sheet_name] = {
                "records": sheet_record_count,
                "normal": normal_count,
                "uncertain": uncertain_count
            }

        return {
            "success": True,
            "records": normalized_records,
            "record_count": len(normalized_records),
            "sheet_summary": sheet_summary
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }