def add_record_lines(lines, record):
    """
    Add dictionary record as readable TXT lines.
    """

    if not isinstance(record, dict):
        return

    for key, value in record.items():
        lines.append(
            f"{key}: {value}"
        )


def export_match_result_to_txt(result, output_path):
    """
    Export matching results to TXT.
    """

    try:

        lines = []

        lines.append(
            "SMART MATCH ASSISTANT - MATCH RESULTS"
        )

        lines.append(
            "=" * 60
        )

        lines.append("")

        # -----------------------------
        # Summary
        # -----------------------------

        lines.append("SUMMARY")
        lines.append("-" * 60)

        lines.append(
            f"Matched: {result.get('matched_count', 0)}"
        )

        lines.append(
            f"Unmatched: {result.get('unmatched_count', 0)}"
        )

        lines.append(
            "Duplicate / Ambiguous: "
            f"{result.get('duplicate_count', 0)}"
        )

        lines.append("")


        # -----------------------------
        # Matched
        # -----------------------------

        lines.append("MATCHED RECORDS")
        lines.append("-" * 60)

        matched_records = result.get(
            "matched",
            []
        )

        if matched_records:

            for index, item in enumerate(
                matched_records,
                start=1
            ):

                lines.append(
                    f"Matched Record {index}"
                )

                lines.append(
                    f"Status: {item.get('status', '')}"
                )

                lines.append(
                    f"Match Type: {item.get('match_type', '')}"
                )

                lines.append(
                    "Confidence: "
                    f"{item.get('confidence', 0) * 100:.2f}%"
                )

                lines.append(
                    "Main Record:"
                )

                matches = item.get(
                    "matches",
                    []
                )

                if matches:

                    raw_record = matches[0].get(
                        "raw_record",
                        {}
                    )

                    add_record_lines(
                        lines,
                        raw_record
                    )

                lines.append("")

        else:

            lines.append(
                "No matched records."
            )

            lines.append("")


        # -----------------------------
        # Unmatched
        # -----------------------------

        lines.append("UNMATCHED RECORDS")
        lines.append("-" * 60)

        unmatched_records = result.get(
            "unmatched",
            []
        )

        if unmatched_records:

            for index, item in enumerate(
                unmatched_records,
                start=1
            ):

                lines.append(
                    f"Unmatched Record {index}"
                )

                lines.append(
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

                add_record_lines(
                    lines,
                    raw_record
                )

                lines.append("")

        else:

            lines.append(
                "No unmatched records."
            )

            lines.append("")


        # -----------------------------
        # Duplicate / Ambiguous
        # -----------------------------

        lines.append(
            "DUPLICATE / AMBIGUOUS RECORDS"
        )

        lines.append(
            "-" * 60
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

                lines.append(
                    f"Duplicate / Ambiguous Record {index}"
                )

                lines.append(
                    f"Status: {item.get('status', '')}"
                )

                lines.append(
                    f"Match Type: {item.get('match_type', '')}"
                )

                lines.append(
                    "Confidence: "
                    f"{item.get('confidence', 0) * 100:.2f}%"
                )

                lines.append(
                    "Possible Candidates:"
                )

                matches = item.get(
                    "matches",
                    []
                )

                if matches:

                    for candidate_index, candidate in enumerate(
                        matches,
                        start=1
                    ):

                        lines.append(
                            f"Candidate {candidate_index}:"
                        )

                        raw_record = candidate.get(
                            "raw_record",
                            {}
                        )

                        add_record_lines(
                            lines,
                            raw_record
                        )

                        lines.append("")

                else:

                    lines.append(
                        "No candidate records available."
                    )

                lines.append("")

        else:

            lines.append(
                "No duplicate or ambiguous records."
            )

            lines.append("")


        # -----------------------------
        # Save TXT
        # -----------------------------

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(lines)
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