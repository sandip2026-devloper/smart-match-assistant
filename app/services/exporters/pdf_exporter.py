from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def export_match_result_to_pdf(
    result,
    output_path
):
    """
    Export matching results to PDF.

    Creates sections for:
    - Summary
    - Matched records
    - Unmatched records
    - Duplicate / Ambiguous records
    """

    try:

        document = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        story = []

        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["BodyText"]

        story.append(
            Paragraph(
                "SMART MATCH ASSISTANT - MATCH RESULTS",
                title_style
            )
        )

        story.append(
            Spacer(
                1,
                15
            )
        )


        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Summary",
                heading_style
            )
        )

        summary_data = [
            ["Category", "Count"],
            [
                "Matched",
                str(
                    result.get(
                        "matched_count",
                        0
                    )
                )
            ],
            [
                "Unmatched",
                str(
                    result.get(
                        "unmatched_count",
                        0
                    )
                )
            ],
            [
                "Duplicate / Ambiguous",
                str(
                    result.get(
                        "duplicate_count",
                        0
                    )
                )
            ]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                220,
                100
            ]
        )

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
            ])
        )

        story.append(summary_table)

        story.append(
            Spacer(
                1,
                20
            )
        )


        # -------------------------------------------------
        # MATCHED RECORDS
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Matched Records",
                heading_style
            )
        )

        matched_records = result.get(
            "matched",
            []
        )

        if matched_records:

            matched_data = [
                [
                    "Status",
                    "Match Type",
                    "Confidence",
                    "Main Record"
                ]
            ]

            for item in matched_records:

                matches = item.get(
                    "matches",
                    []
                )

                if not matches:
                    continue

                raw_record = matches[0].get(
                    "raw_record",
                    {}
                )

                if not isinstance(
                    raw_record,
                    dict
                ):
                    raw_record = {}

                record_text = "<br/>".join(
                    [
                        f"<b>{key}:</b> {value}"
                        for key, value
                        in raw_record.items()
                    ]
                )

                matched_data.append([
                    item.get(
                        "status",
                        ""
                    ),
                    item.get(
                        "match_type",
                        ""
                    ),
                    (
                        f"{item.get('confidence', 0) * 100:.2f}%"
                    ),
                    Paragraph(
                        record_text,
                        normal_style
                    )
                ])

            matched_table = Table(
                matched_data,
                colWidths=[
                    80,
                    120,
                    90,
                    400
                ],
                repeatRows=1
            )

            matched_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                ])
            )

            story.append(
                matched_table
            )

        else:

            story.append(
                Paragraph(
                    "No matched records.",
                    normal_style
                )
            )


        story.append(
            Spacer(
                1,
                20
            )
        )


        # -------------------------------------------------
        # UNMATCHED RECORDS
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Unmatched Records",
                heading_style
            )
        )

        unmatched_records = result.get(
            "unmatched",
            []
        )

        if unmatched_records:

            unmatched_data = [
                [
                    "Status",
                    "Record"
                ]
            ]

            for item in unmatched_records:

                secondary_record = item.get(
                    "secondary_record",
                    {}
                )

                raw_record = secondary_record.get(
                    "raw_record",
                    {}
                )

                if not isinstance(
                    raw_record,
                    dict
                ):
                    raw_record = {}

                record_text = "<br/>".join(
                    [
                        f"<b>{key}:</b> {value}"
                        for key, value
                        in raw_record.items()
                    ]
                )

                unmatched_data.append([
                    item.get(
                        "status",
                        ""
                    ),
                    Paragraph(
                        record_text,
                        normal_style
                    )
                ])

            unmatched_table = Table(
                unmatched_data,
                colWidths=[
                    100,
                    590
                ],
                repeatRows=1
            )

            unmatched_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                ])
            )

            story.append(
                unmatched_table
            )

        else:

            story.append(
                Paragraph(
                    "No unmatched records.",
                    normal_style
                )
            )


        story.append(
            Spacer(
                1,
                20
            )
        )


        # -------------------------------------------------
        # DUPLICATE / AMBIGUOUS RECORDS
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Duplicate / Ambiguous Records",
                heading_style
            )
        )

        duplicate_records = result.get(
            "duplicate",
            []
        )

        if duplicate_records:

            duplicate_data = [
                [
                    "Status",
                    "Match Type",
                    "Confidence",
                    "Candidate",
                    "Record"
                ]
            ]

            for item in duplicate_records:

                matches = item.get(
                    "matches",
                    []
                )

                if not matches:

                    duplicate_data.append([
                        item.get(
                            "status",
                            ""
                        ),
                        item.get(
                            "match_type",
                            ""
                        ),
                        (
                            f"{item.get('confidence', 0) * 100:.2f}%"
                        ),
                        "",
                        ""
                    ])

                    continue

                for index, candidate in enumerate(
                    matches,
                    start=1
                ):

                    raw_record = candidate.get(
                        "raw_record",
                        {}
                    )

                    if not isinstance(
                        raw_record,
                        dict
                    ):
                        raw_record = {}

                    record_text = "<br/>".join(
                        [
                            f"<b>{key}:</b> {value}"
                            for key, value
                            in raw_record.items()
                        ]
                    )

                    duplicate_data.append([
                        item.get(
                            "status",
                            ""
                        ),
                        item.get(
                            "match_type",
                            ""
                        ),
                        (
                            f"{item.get('confidence', 0) * 100:.2f}%"
                        ),
                        str(index),
                        Paragraph(
                            record_text,
                            normal_style
                        )
                    ])

            duplicate_table = Table(
                duplicate_data,
                colWidths=[
                    80,
                    120,
                    90,
                    70,
                    350
                ],
                repeatRows=1
            )

            duplicate_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                ])
            )

            story.append(
                duplicate_table
            )

        else:

            story.append(
                Paragraph(
                    "No duplicate or ambiguous records.",
                    normal_style
                )
            )


        document.build(
            story
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