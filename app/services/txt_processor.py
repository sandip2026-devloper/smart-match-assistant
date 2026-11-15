from app.services.extractors.txt_extractor import extract_txt
from app.services.normalization.normalizer import normalize_record
from app.services.matching.identifier_detector import analyze_record


def parse_key_value_lines(lines):
    """
    Convert key:value TXT lines into one structured record.
    """

    raw_record = {}

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        if key and value:
            raw_record[key] = value

    return raw_record


def process_txt(file_path):
    """
    Process TXT files.

    Supports:
    1. Key:value format
    2. Simple comma-separated data with headers
    """

    extraction_result = extract_txt(file_path)

    if not extraction_result.get("success"):
        return {
            "success": False,
            "stage": "extraction",
            "error": extraction_result.get(
                "error",
                "TXT extraction failed."
            )
        }

    lines = extraction_result.get("lines", [])

    if not lines:
        return {
            "success": True,
            "record_count": 0,
            "records": [],
            "line_count": 0
        }

    try:
        key_value_record = parse_key_value_lines(lines)

        if key_value_record:
            normalized_record = normalize_record(
                record=key_value_record,
                sheet_name="txt",
                source_row=1
            )

            identifiers = analyze_record(
                normalized_record
            )

            processed_record = {
                **normalized_record,
                "identifiers": identifiers
            }

            return {
                "success": True,
                "record_count": 1,
                "records": [
                    processed_record
                ],
                "line_count": len(lines)
            }

        return {
            "success": True,
            "record_count": 0,
            "records": [],
            "line_count": len(lines)
        }

    except Exception as error:
        return {
            "success": False,
            "stage": "processing",
            "error": str(error)
        }