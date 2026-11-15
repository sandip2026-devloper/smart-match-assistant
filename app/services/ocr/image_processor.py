from app.services.ocr.image_ocr import extract_image_ocr
from app.services.normalization.normalizer import normalize_record
from app.services.matching.identifier_detector import analyze_record


def parse_ocr_line(line):
    """
    Convert a simple OCR key:value line
    into a structured dictionary.
    """
    if ":" in line:
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key and value:
            return {
                key: value
            }

    return {}


def process_image(file_path):
    """
    Process an image using OCR.

    Groups OCR key:value lines into one structured record,
    then normalizes the data and detects identifiers.
    """

    extraction_result = extract_image_ocr(file_path)

    if not extraction_result.get("success"):
        return {
            "success": False,
            "stage": "ocr",
            "error": extraction_result.get(
                "error",
                "Image OCR failed."
            )
        }

    lines = extraction_result.get("lines", [])

    raw_record = {}

    for line in lines:
        if not line:
            continue

        parsed_data = parse_ocr_line(line)

        if parsed_data:
            raw_record.update(parsed_data)

    if not raw_record:
        return {
            "success": True,
            "record_count": 0,
            "records": [],
            "line_count": extraction_result.get(
                "line_count",
                0
            )
        }

    normalized_record = normalize_record(
        record=raw_record,
        sheet_name="ocr",
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
        "line_count": extraction_result.get(
            "line_count",
            0
        )
    }