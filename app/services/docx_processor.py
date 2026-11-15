from app.services.extractors.docx_extractor import extract_docx
from app.services.normalization.normalizer import normalize_record
from app.services.matching.identifier_detector import analyze_record


def process_docx(file_path):
    """
    Process a DOCX file.

    Extracts paragraphs and tables, converts them
    into structured records, normalizes the data,
    and detects identifiers.
    """

    extraction_result = extract_docx(file_path)

    if not extraction_result.get("success"):
        return {
            "success": False,
            "stage": "extraction",
            "error": extraction_result.get(
                "error",
                "DOCX extraction failed."
            )
        }

    processed_records = []

    # Process paragraphs
    for index, text in enumerate(
        extraction_result.get("paragraphs", [])
    ):

        if not text:
            continue

        raw_record = {
            "text": text
        }

        normalized_record = normalize_record(
            record=raw_record,
            sheet_name="paragraphs",
            source_row=index + 1
        )

        identifiers = analyze_record(
            normalized_record
        )

        processed_record = {
            **normalized_record,
            "identifiers": identifiers
        }

        processed_records.append(
            processed_record
        )

    # Process tables
    for table_index, table in enumerate(
        extraction_result.get("tables", [])
    ):

        if not table:
            continue

        for row_index, row in enumerate(table):

            raw_record = {}

            for column_index, value in enumerate(row):

                raw_record[
                    f"column_{column_index + 1}"
                ] = value

            normalized_record = normalize_record(
                record=raw_record,
                sheet_name=f"table_{table_index + 1}",
                source_row=row_index + 1
            )

            identifiers = analyze_record(
                normalized_record
            )

            processed_record = {
                **normalized_record,
                "identifiers": identifiers
            }

            processed_records.append(
                processed_record
            )

    return {
        "success": True,
        "record_count": len(processed_records),
        "records": processed_records,
        "paragraph_count": extraction_result.get(
            "paragraph_count",
            0
        ),
        "table_count": extraction_result.get(
            "table_count",
            0
        )
    }