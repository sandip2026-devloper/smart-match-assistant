from app.services.extractors.excel_extractor import extract_excel
from app.services.normalization.normalizer import normalize_sheets
from app.services.matching.identifier_detector import analyze_record


def process_excel(file_path):
    """
    Complete processing pipeline for an Excel document.

    Excel
      ↓
    Extraction
      ↓
    Normalization
      ↓
    Identifier Detection
    """

    # Step 1: Extract Excel data
    extraction_result = extract_excel(file_path)

    if not extraction_result.get("success"):
        return {
            "success": False,
            "stage": "extraction",
            "error": extraction_result.get(
                "error",
                "Excel extraction failed."
            )
        }

    # Step 2: Normalize extracted data
    normalization_result = normalize_sheets(
        extraction_result["sheets"]
    )

    if not normalization_result.get("success"):
        return {
            "success": False,
            "stage": "normalization",
            "error": normalization_result.get(
                "error",
                "Normalization failed."
            )
        }

    # Step 3: Detect identifiers
    processed_records = []

    for record in normalization_result["records"]:

        identifiers = analyze_record(
            record
        )

        processed_record = {
            **record,
            "identifiers": identifiers
        }

        processed_records.append(
            processed_record
        )

    return {
        "success": True,
        "record_count": len(processed_records),
        "records": processed_records,
        "sheet_summary": normalization_result.get(
            "sheet_summary",
            {}
        )
    }