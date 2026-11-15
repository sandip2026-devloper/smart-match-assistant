from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def collect_columns(records, record_key):
    """
    Collect all unique fields from raw records.
    """

    columns = []

    for item in records:

        if record_key == "matches":

            records_to_check = item.get(
                "matches",
                []
            )

        else:

            records_to_check = [
                item.get(
                    record_key,
                    {}
                )
            ]

        for record in records_to_check:

            if not isinstance(record, dict):
                continue

            raw_record = record.get(
                "raw_record",
                {}
            )

            if not isinstance(raw_record, dict):
                continue

            for column in raw_record.keys():

                column = str(column)

                if column not in columns:
                    columns.append(column)

    return columns


def auto_adjust_columns(sheet):
    """
    Automatically adjust Excel column widths.
    """

    for column_cells in sheet.columns:

        max_length = 0

        column_index = column_cells[0].column

        for cell in column_cells:

            value = cell.value

            if value is None:
                continue

            value_length = len(
                str(value)
            )

            if value_length > max_length:
                max_length = value_length

        adjusted_width = min(
            max(
                max_length + 2,
                12
            ),
            40
        )

        sheet.column_dimensions[
            get_column_letter(column_index)
        ].width = adjusted_width


def export_match_result_to_xlsx(
    result,
    output_path
):
    """
    Export matching results to Excel.

    Creates:
    - Summary
    - Matched
    - Unmatched
    - Duplicate_Ambiguous
    """

    workbook = Workbook()

    # =================================================
    # SUMMARY SHEET
    # =================================================

    summary_sheet = workbook.active

    summary_sheet.title = "Summary"

    summary_sheet.append([
        "Category",
        "Count"
    ])

    summary_sheet.append([
        "Matched",
        result.get(
            "matched_count",
            0
        )
    ])

    summary_sheet.append([
        "Unmatched",
        result.get(
            "unmatched_count",
            0
        )
    ])

    summary_sheet.append([
        "Duplicate / Ambiguous",
        result.get(
            "duplicate_count",
            0
        )
    ])

    auto_adjust_columns(
        summary_sheet
    )

    # =================================================
    # MATCHED SHEET
    # =================================================

    matched_records = result.get(
        "matched",
        []
    )

    matched_columns = collect_columns(
        matched_records,
        "matches"
    )

    matched_sheet = workbook.create_sheet(
        "Matched"
    )

    matched_headers = [
        "Status",
        "Match Type",
        "Confidence"
    ] + matched_columns

    matched_sheet.append(
        matched_headers
    )

    for item in matched_records:

        matches = item.get(
            "matches",
            []
        )

        if not matches:
            continue

        main_record = matches[0]

        raw_record = main_record.get(
            "raw_record",
            {}
        )

        if not isinstance(
            raw_record,
            dict
        ):
            raw_record = {}

        row = [
            item.get(
                "status",
                ""
            ),

            item.get(
                "match_type",
                ""
            ),

            f"{item.get('confidence', 0) * 100:.2f}%"
        ]

        for column in matched_columns:

            row.append(
                raw_record.get(
                    column,
                    ""
                )
            )

        matched_sheet.append(
            row
        )

    auto_adjust_columns(
        matched_sheet
    )

    # =================================================
    # UNMATCHED SHEET
    # =================================================

    unmatched_records = result.get(
        "unmatched",
        []
    )

    unmatched_columns = collect_columns(
        unmatched_records,
        "secondary_record"
    )

    unmatched_sheet = workbook.create_sheet(
        "Unmatched"
    )

    unmatched_headers = [
        "Status"
    ] + unmatched_columns

    unmatched_sheet.append(
        unmatched_headers
    )

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

        row = [
            item.get(
                "status",
                ""
            )
        ]

        for column in unmatched_columns:

            row.append(
                raw_record.get(
                    column,
                    ""
                )
            )

        unmatched_sheet.append(
            row
        )

    auto_adjust_columns(
        unmatched_sheet
    )

    # =================================================
    # DUPLICATE / AMBIGUOUS SHEET
    # =================================================

    duplicate_records = result.get(
        "duplicate",
        []
    )

    duplicate_sheet = workbook.create_sheet(
        "Duplicate_Ambiguous"
    )

    duplicate_sheet.append([
        "Status",
        "Match Type",
        "Confidence",
        "Candidate Number",
        "Candidate Record"
    ])

    for item in duplicate_records:

        matches = item.get(
            "matches",
            []
        )

        if not matches:

            duplicate_sheet.append([
                item.get(
                    "status",
                    ""
                ),

                item.get(
                    "match_type",
                    ""
                ),

                f"{item.get('confidence', 0) * 100:.2f}%",

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

            duplicate_sheet.append([
                item.get(
                    "status",
                    ""
                ),

                item.get(
                    "match_type",
                    ""
                ),

                f"{item.get('confidence', 0) * 100:.2f}%",

                index,

                str(raw_record)
            ])

    auto_adjust_columns(
        duplicate_sheet
    )

    # =================================================
    # SAVE FILE
    # =================================================

    workbook.save(
        output_path
    )

    return {
        "success": True,
        "output_path": output_path
    }