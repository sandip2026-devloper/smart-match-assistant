from docx import Document
from docx.shared import Pt


def add_record_to_document(document, record):
    """
    Add a dictionary record to the DOCX document.
    """

    if not isinstance(record, dict):
        return

    for key, value in record.items():

        paragraph = document.add_paragraph()

        run = paragraph.add_run(
            f"{key}: "
        )

        run.bold = True

        paragraph.add_run(
            str(value)
        )


def export_match_result_to_docx(result, output_path):
    """
    Export matching results to DOCX.

    Creates sections for:
    - Summary
    - Matched records
    - Unmatched records
    - Duplicate / Ambiguous records
    """

    try:

        document = Document()

        # -----------------------------
        # Title
        # -----------------------------

        title = document.add_heading(
            "SMART MATCH ASSISTANT - MATCH RESULTS",
            level=0
        )

        title_run = title.runs[0]
        title_run.font.size = Pt(18)


        # -----------------------------
        # Summary
        # -----------------------------

        document.add_heading(
            "Summary",
            level=1
        )

        summary_table = document.add_table(
            rows=1,
            cols=2
        )

        summary_table.style = "Table Grid"

        header_cells = summary_table.rows[0].cells

        header_cells[0].text = "Category"
        header_cells[1].text = "Count"


        summary_rows = [
            (
                "Matched",
                result.get("matched_count", 0)
            ),
            (
                "Unmatched",
                result.get("unmatched_count", 0)
            ),
            (
                "Duplicate / Ambiguous",
                result.get("duplicate_count", 0)
            )
        ]


        for category, count in summary_rows:

            cells = summary_table.add_row().cells

            cells[0].text = str(category)
            cells[1].text = str(count)


        document.add_paragraph()


        # -----------------------------
        # Matched Records
        # -----------------------------

        document.add_heading(
            "Matched Records",
            level=1
        )

        matched_records = result.get(
            "matched",
            []
        )


        if matched_records:

            for index, item in enumerate(
                matched_records,
                start=1
            ):

                document.add_heading(
                    f"Matched Record {index}",
                    level=2
                )

                document.add_paragraph(
                    f"Status: {item.get('status', '')}"
                )

                document.add_paragraph(
                    f"Match Type: {item.get('match_type', '')}"
                )

                document.add_paragraph(
                    (
                        "Confidence: "
                        f"{item.get('confidence', 0) * 100:.2f}%"
                    )
                )


                matches = item.get(
                    "matches",
                    []
                )


                if matches:

                    main_record = matches[0]

                    raw_record = main_record.get(
                        "raw_record",
                        {}
                    )

                    document.add_paragraph(
                        "Main Record:"
                    )

                    add_record_to_document(
                        document,
                        raw_record
                    )

        else:

            document.add_paragraph(
                "No matched records."
            )


        # -----------------------------
        # Unmatched Records
        # -----------------------------

        document.add_heading(
            "Unmatched Records",
            level=1
        )

        unmatched_records = result.get(
            "unmatched",
            []
        )


        if unmatched_records:

            for index, item in enumerate(
                unmatched_records,
                start=1
            ):

                document.add_heading(
                    f"Unmatched Record {index}",
                    level=2
                )

                document.add_paragraph(
                    f"Status: {item.get('status', '')}"
                )


                secondary_record = item.get(
                    "secondary_record",
                    {}
                )


                raw_record = secondary_record.get(
                    "raw_record",
                    {}
                )


                add_record_to_document(
                    document,
                    raw_record
                )

        else:

            document.add_paragraph(
                "No unmatched records."
            )


        # -----------------------------
        # Duplicate / Ambiguous
        # -----------------------------

        document.add_heading(
            "Duplicate / Ambiguous Records",
            level=1
        )

        duplicate_records = result.get(
            "duplicate",
            []
        )


        if duplicate_records:

            for index, item in enumerate(
                duplicate_records,
                start=1
            ):

                document.add_heading(
                    f"Duplicate / Ambiguous Record {index}",
                    level=2
                )

                document.add_paragraph(
                    f"Status: {item.get('status', '')}"
                )

                document.add_paragraph(
                    f"Match Type: {item.get('match_type', '')}"
                )

                document.add_paragraph(
                    (
                        "Confidence: "
                        f"{item.get('confidence', 0) * 100:.2f}%"
                    )
                )


                matches = item.get(
                    "matches",
                    []
                )


                if matches:

                    document.add_paragraph(
                        "Possible Candidates:"
                    )


                    for candidate_index, candidate in enumerate(
                        matches,
                        start=1
                    ):

                        document.add_heading(
                            f"Candidate {candidate_index}",
                            level=3
                        )


                        raw_record = candidate.get(
                            "raw_record",
                            {}
                        )


                        add_record_to_document(
                            document,
                            raw_record
                        )

        else:

            document.add_paragraph(
                "No duplicate or ambiguous records."
            )


        # -----------------------------
        # Save
        # -----------------------------

        document.save(
            output_path
        )


        return {
            "success": True,
            "output_path": output_path
        }


    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }