def extract_txt(file_path):
    """
    Extract text from a UTF-8 TXT file.
    """

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return {
            "success": True,
            "text": text,
            "lines": lines,
            "line_count": len(lines)
        }

    except UnicodeDecodeError:
        return {
            "success": False,
            "error": "TXT file must be UTF-8 encoded."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }