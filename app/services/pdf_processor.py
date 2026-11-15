from app.services.extractors.pdf_extractor import extract_pdf
from app.services.normalization.normalizer import normalize_record
from app.services.matching.identifier_detector import analyze_record


def process_pdf(file_path):
    """
    Process a structured PDF containing student records.

    Expected record pattern:

    Serial Number
    Student Code
    Student Name
    Presentation Title
    Presentation Date
    """

    extraction_result = extract_pdf(file_path)

    if not extraction_result.get("success"):
        return {
            "success": False,
            "stage": "extraction",
            "error": extraction_result.get(
                "error",
                "PDF extraction failed."
            )
        }

    processed_records = []

    for page in extraction_result.get("pages", []):

        page_number = page.get("page_number")
        text = page.get("text", "")

        if not text:
            continue

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        index = 0

        while index < len(lines):

            current_line = lines[index]

            # Skip the table header
            if current_line in {
                "Sl.",
                "No.",
                "Student Code",
                "Name of the Student",
                "Title of Presentation",
                "Date of",
                "Presentation"
            }:
                index += 1
                continue

            # A student record starts with a serial number
            if current_line.isdigit():

                serial_no = current_line

                # We need at least:
                # serial
                # student code
                # name
                # title
                # date
                if index + 4 < len(lines):

                    student_code = lines[index + 1]
                    student_name = lines[index + 2]
                    title = lines[index + 3]
                    presentation_date = lines[index + 4]

                    raw_record = {
                        "serial_no": serial_no,
                        "student_code": student_code,
                        "name": student_name,
                        "title": title,
                        "date": presentation_date
                    }

                    normalized_record = normalize_record(
                        record=raw_record,
                        sheet_name=f"page_{page_number}",
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

                    index += 5
                    continue

            index += 1

    return {
        "success": True,
        "record_count": len(processed_records),
        "records": processed_records,
        "page_count": extraction_result.get(
            "page_count",
            0
        )
    }