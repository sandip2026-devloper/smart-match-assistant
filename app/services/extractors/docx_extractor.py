from docx import Document


def extract_docx(file_path):
    """
    Extract text and tables from a DOCX file.
    """

    try:
        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        tables = []

        for table in document.tables:

            table_rows = []

            for row in table.rows:

                row_data = []

                for cell in row.cells:

                    row_data.append(
                        cell.text.strip()
                    )

                table_rows.append(row_data)

            if table_rows:
                tables.append(table_rows)

        return {
            "success": True,
            "paragraphs": paragraphs,
            "tables": tables,
            "paragraph_count": len(paragraphs),
            "table_count": len(tables)
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }
    