import pandas as pd


def looks_like_header(row):
    """
    Decide whether a row looks like a real column header.
    """

    if row is None:
        return False

    values = []

    for value in row:
        if pd.isna(value):
            continue

        text = str(value).strip()

        if not text:
            continue

        values.append(text)

    if not values:
        return False

    header_keywords = {
        "sl",
        "sl no",
        "sln",
        "serial",
        "serial no",
        "student",
        "student code",
        "student name",
        "name",
        "code",
        "roll",
        "roll no",
        "id",
        "student id",
        "email",
        "phone",
        "mobile",
        "contact",
        "address",
        "course",
        "department",
        "branch",
        "age",
        "gender",
        "dob",
        "date",
        "attendance",
        "status",
        "semester",
        "year",
    }

    keyword_matches = 0

    for value in values:

        normalized = value.lower().strip()

        if normalized in header_keywords:
            keyword_matches += 1
            continue

        compact = (
            normalized
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        for keyword in header_keywords:

            keyword_compact = (
                keyword
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
            )

            if keyword_compact in compact:
                keyword_matches += 1
                break

    # A row with at least one clear header keyword
    # is probably a real header.
    if keyword_matches >= 1:
        return True

    # Rows containing mostly numeric values
    # are probably data.
    numeric_count = 0

    for value in values:

        try:
            float(value)
            numeric_count += 1
        except (ValueError, TypeError):
            pass

    if len(values) > 0:
        numeric_ratio = numeric_count / len(values)

        if numeric_ratio >= 0.5:
            return False

    # Student-code pattern usually means data.
    code_like_count = 0

    for value in values:

        text = value.upper().replace(" ", "")

        if "/" in text and len(text) >= 8:
            code_like_count += 1

    if code_like_count >= 1:
        return False

    return False


def make_unique_columns(columns):
    """
    Make sure duplicate Excel column names become unique.
    """

    result = []
    used = {}

    for column in columns:

        column = str(column).strip()

        if not column:
            column = "column"

        if column not in used:

            used[column] = 1
            result.append(column)

        else:

            used[column] += 1

            result.append(
                f"{column}_{used[column]}"
            )

    return result


def clean_dataframe(dataframe):
    """
    Clean empty rows, empty columns and NaN values.
    """

    dataframe = dataframe.dropna(
        how="all"
    )

    dataframe = dataframe.dropna(
        axis=1,
        how="all"
    )

    dataframe = dataframe.where(
        pd.notna(dataframe),
        None
    )

    return dataframe


def extract_sheet(file_path, sheet_name):
    """
    Extract one Excel sheet.

    The first few rows are inspected to determine
    whether the sheet contains a real header.
    """

    raw_dataframe = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None
    )

    raw_dataframe = raw_dataframe.dropna(
        how="all"
    )

    raw_dataframe = raw_dataframe.dropna(
        axis=1,
        how="all"
    )

    if raw_dataframe.empty:

        return {
            "records": [],
            "header_detected": False,
            "header_row": None
        }

    # Inspect the first 5 rows.
    max_rows_to_check = min(
        5,
        len(raw_dataframe)
    )

    header_row_index = None

    for index in range(
        max_rows_to_check
    ):

        row = raw_dataframe.iloc[
            index
        ].tolist()

        if looks_like_header(row):

            header_row_index = index
            break

    # --------------------------------
    # CASE 1: REAL HEADER FOUND
    # --------------------------------

    if header_row_index is not None:

        headers = raw_dataframe.iloc[
            header_row_index
        ].tolist()

        headers = [
            str(value).strip()
            if value is not None
            else ""
            for value in headers
        ]

        headers = make_unique_columns(
            headers
        )

        data = raw_dataframe.iloc[
            header_row_index + 1:
        ].copy()

        data.columns = headers

        data = clean_dataframe(
            data
        )

        return {
            "records": data.to_dict(
                orient="records"
            ),
            "header_detected": True,
            "header_row": header_row_index + 1
        }

    # --------------------------------
    # CASE 2: NO REAL HEADER
    # --------------------------------

    # Preserve the original structure.
    # Generic column names are used so
    # data is not incorrectly treated
    # as column names.

    data = raw_dataframe.copy()

    data.columns = [
        f"column_{index + 1}"
        for index in range(
            len(data.columns)
        )
    ]

    data = clean_dataframe(
        data
    )

    return {
        "records": data.to_dict(
            orient="records"
        ),
        "header_detected": False,
        "header_row": None
    }


def extract_excel(file_path):
    """
    Read an Excel file and return structured
    data for every sheet.
    """

    try:

        excel_file = pd.ExcelFile(
            file_path
        )

        sheets = {}

        sheet_metadata = {}

        for sheet_name in excel_file.sheet_names:

            result = extract_sheet(
                file_path,
                sheet_name
            )

            sheets[sheet_name] = (
                result["records"]
            )

            sheet_metadata[sheet_name] = {
                "header_detected": result[
                    "header_detected"
                ],
                "header_row": result[
                    "header_row"
                ],
                "record_count": len(
                    result["records"]
                )
            }

        return {
            "success": True,
            "sheets": sheets,
            "sheet_metadata": sheet_metadata
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }