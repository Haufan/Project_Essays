# ==========================================
# File: merge_original_with_summary_no_openpyxl.py
# Author: Dietmar Benndorf
# Date: 2026-04-28
# Description:
#    Reads:
#    - Original Data.xlsx without openpyxl or pandas
#    - csv_segment_summary.csv
#
#    If ID in the summary CSV is identical with
#    Participant Private ID in the Excel file, the Excel row
#    is extended with the matching values from the summary CSV.
#
#    The merged result is saved as a CSV file.
# ==========================================

import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


EXCEL_PATH = r"C:\Users\haufa\Downloads\Original Data.xlsx"
SUMMARY_CSV_PATH = r"C:\Users\haufa\Downloads\csv_segment_summary.csv"
#SUMMARY_CSV_PATH = r"C:\Users\haufa\Downloads\analysis_results.csv"
OUTPUT_CSV_PATH = r"C:\Users\haufa\Downloads\original_data_extended.csv"


def normalize_id(value):
    """
    Normalizes IDs so that values like 12345, 12345.0 and '12345'
    can be matched safely.
    """
    if value is None:
        return ""

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    return value


def strip_namespace(tag):
    """
    Removes XML namespace from a tag name.
    Example:
        {namespace}sheet -> sheet
    """
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def column_letters_to_index(cell_reference):
    """
    Converts Excel column letters to zero-based column index.

    Examples:
        A1  -> 0
        B1  -> 1
        AA1 -> 26
    """
    letters = re.match(r"[A-Z]+", cell_reference).group(0)

    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)

    return index - 1


def read_shared_strings(xlsx_zip):
    """
    Reads xl/sharedStrings.xml if it exists.
    Returns a list of shared string values.
    """
    shared_strings = []

    try:
        xml_data = xlsx_zip.read("xl/sharedStrings.xml")
    except KeyError:
        return shared_strings

    root = ET.fromstring(xml_data)

    for si in root:
        text_parts = []

        for element in si.iter():
            if strip_namespace(element.tag) == "t" and element.text is not None:
                text_parts.append(element.text)

        shared_strings.append("".join(text_parts))

    return shared_strings


def get_first_sheet_path(xlsx_zip):
    """
    Finds the XML path of the first worksheet in the workbook.
    """
    workbook_xml = xlsx_zip.read("xl/workbook.xml")
    workbook_root = ET.fromstring(workbook_xml)

    first_sheet_rid = None

    for element in workbook_root.iter():
        if strip_namespace(element.tag) == "sheet":
            first_sheet_rid = element.attrib.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            break

    if first_sheet_rid is None:
        raise ValueError("No worksheet found in Excel file.")

    rels_xml = xlsx_zip.read("xl/_rels/workbook.xml.rels")
    rels_root = ET.fromstring(rels_xml)

    target = None

    for rel in rels_root:
        if rel.attrib.get("Id") == first_sheet_rid:
            target = rel.attrib.get("Target")
            break

    if target is None:
        raise ValueError("Worksheet relationship not found.")

    if target.startswith("/"):
        sheet_path = target.lstrip("/")
    else:
        sheet_path = "xl/" + target

    return sheet_path


def get_cell_value(cell, shared_strings):
    """
    Reads one Excel cell value.
    Supports:
    - shared strings
    - inline strings
    - normal numeric/string values
    """
    cell_type = cell.attrib.get("t")

    if cell_type == "s":
        value_element = None

        for child in cell:
            if strip_namespace(child.tag) == "v":
                value_element = child
                break

        if value_element is None or value_element.text is None:
            return ""

        shared_string_index = int(value_element.text)

        if shared_string_index < len(shared_strings):
            return shared_strings[shared_string_index]

        return ""

    if cell_type == "inlineStr":
        text_parts = []

        for element in cell.iter():
            if strip_namespace(element.tag) == "t" and element.text is not None:
                text_parts.append(element.text)

        return "".join(text_parts)

    for child in cell:
        if strip_namespace(child.tag) == "v":
            return child.text if child.text is not None else ""

    return ""


def read_xlsx_first_sheet(xlsx_path):
    """
    Reads the first worksheet of an .xlsx file.

    Returns:
        header, rows

    header:
        list of column names

    rows:
        list of dictionaries
    """
    with zipfile.ZipFile(xlsx_path, "r") as xlsx_zip:
        shared_strings = read_shared_strings(xlsx_zip)
        sheet_path = get_first_sheet_path(xlsx_zip)

        sheet_xml = xlsx_zip.read(sheet_path)
        sheet_root = ET.fromstring(sheet_xml)

        table_rows = []

        for row in sheet_root.iter():
            if strip_namespace(row.tag) != "row":
                continue

            row_values = []

            for cell in row:
                if strip_namespace(cell.tag) != "c":
                    continue

                cell_reference = cell.attrib.get("r", "")
                if not cell_reference:
                    continue

                column_index = column_letters_to_index(cell_reference)

                while len(row_values) <= column_index:
                    row_values.append("")

                row_values[column_index] = get_cell_value(cell, shared_strings)

            table_rows.append(row_values)

    if not table_rows:
        return [], []

    header = table_rows[0]

    data_rows = []

    for row_values in table_rows[1:]:
        row_dict = {}

        for index, column_name in enumerate(header):
            if column_name == "":
                continue

            if index < len(row_values):
                row_dict[column_name] = row_values[index]
            else:
                row_dict[column_name] = ""

        data_rows.append(row_dict)

    return header, data_rows


def read_summary_csv(summary_csv_path):
    """
    Reads csv_segment_summary.csv.

    Returns:
        summary_data:
            ID -> row dictionary

        summary_columns:
            columns from summary CSV except ID
    """
    summary_data = {}
    summary_columns = []

    with open(summary_csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="|")

        if reader.fieldnames is None:
            return summary_data, summary_columns

        summary_columns = [
            column for column in reader.fieldnames
            if column != "ID"
        ]

        for row in reader:
            summary_id = normalize_id(row.get("ID", ""))

            if summary_id != "":
                summary_data[summary_id] = row

    return summary_data, summary_columns


def merge_original_with_summary(excel_path, summary_csv_path, output_csv_path):
    """
    Merges Original Data.xlsx with csv_segment_summary.csv.

    Match condition:
        Excel column: Participant Private ID
        Summary CSV column: ID
    """
    original_header, original_rows = read_xlsx_first_sheet(excel_path)
    summary_data, summary_columns = read_summary_csv(summary_csv_path)

    id_column = "Participant Private ID"

    if id_column not in original_header:
        raise ValueError(
            f"Column '{id_column}' was not found in the Excel file."
        )

    output_header = list(original_header)

    for column in summary_columns:
        if column not in output_header:
            output_header.append(column)

    merged_rows = []

    for original_row in original_rows:
        merged_row = {}

        for column in output_header:
            merged_row[column] = original_row.get(column, "")

        participant_id = normalize_id(original_row.get(id_column, ""))

        if participant_id in summary_data:
            matching_summary_row = summary_data[participant_id]

            for column in summary_columns:
                merged_row[column] = matching_summary_row.get(column, "")

        merged_rows.append(merged_row)

    output_path = Path(output_csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=output_header,
            delimiter=",",
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(merged_rows)

    return len(original_rows), len(summary_data), len(merged_rows)


def main():
    original_count, summary_count, merged_count = merge_original_with_summary(
        EXCEL_PATH,
        SUMMARY_CSV_PATH,
        OUTPUT_CSV_PATH
    )

    print("Merge completed.")
    print(f"Rows in Excel file: {original_count}")
    print(f"Rows in summary CSV file: {summary_count}")
    print(f"Rows written: {merged_count}")
    print(f"Output file: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()