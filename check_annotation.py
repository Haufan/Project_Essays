# ==========================================
# File: check_annotation.py
# Author: Dietmar Benndorf
# Date: 2026-04-15
# Description:
#    Reads every data group folder from the source directory, checks the
#    folder and file structure, validates the segmented .txt files and
#    annotated .csv files, and writes all detected errors to a text file.
#
#    For each group folder (e.g. 1-50, 51-100, ...), the script:
#    - checks whether the subfolders raw, segmented, and annotated exist
#    - checks whether each file name exists in all three folders
#      (comparison is based only on the file name without extension)
#    - checks whether each .txt file in segmented has the same number of
#      lines as there are segments in the corresponding .csv file
#    - checks whether every segment in the .csv file has a number
#      and whether the numbering is continuous starting from 0
#    - checks whether each existing segment number has a non-empty text field
#    - checks whether each .csv file contains at least one segment
#    - checks whether each .csv file contains a valid value for Thema
#    - checks whether each .csv file contains a valid value for Konstellation
#    - checks whether ADD is filled with J or N whenever a segment has
#      both a number and a non-empty text field
#    - checks whether AUF is filled with EIN, HAU, or SCH whenever a
#      segment has both a number and a non-empty text field
#    - checks whether only the allowed zone labels
#      AHG, WHG, SON, GLD, TH1, TH2, ZTH, PRO, and CON
#      are used in the column FKT
#    - checks whether KON = ABW or UEN has at least one TH1 and one TH2 in FKT
#    - checks whether ADD = J does not allow a text consisting only of uppercase letters
#    - checks whether KON = EIN does not contain TH1 or TH2 in FKT
#    - checks whether a non-empty Text requires ADD = J or N
#    - checks whether KON = EIN, ABW, or UEN has at least one ZTH in FKT
#
#    Output:
#    - .txt file with all detected errors
#    - one error per line, including the corresponding folder or file path
# ==========================================

import csv
from pathlib import Path


ALLOWED_ADD_VALUES = {"J", "N"}
ALLOWED_AUF_VALUES = {"EIN", "HAU", "SCH"}
ALLOWED_FKT_VALUES = {"AHG", "WHG", "SON", "GLD", "TH1", "TH2", "ZTH", "PRO", "CON"}
ALLOWED_THE_VALUES = {"BOOK", "FAST", "ARTS", "VOLU"}
ALLOWED_KON_VALUES = {"EIN", "ABW", "UEN", "UKL"}


def add_error(errors, path, message):
    errors.append(f"{path} | {message}")


def safe_read_text_lines(file_path):
    """
    Reads TXT files robustly.
    Removes only line breaks, not other whitespace.
    """
    encodings = ["utf-8", "cp1252", "latin1"]

    last_error = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return [line.rstrip("\r\n") for line in f.readlines()]
        except Exception as e:
            last_error = e

    raise last_error


def safe_read_csv_rows(file_path):
    """
    Reads CSV files robustly.
    Expects pipe-separated files: |
    """
    encodings = ["utf-8", "cp1252", "latin1"]

    last_error = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.reader(f, delimiter="|")
                return list(reader)
        except Exception as e:
            last_error = e

    raise last_error


def get_stem_map(folder_path):
    """
    Returns a dict:
    stem -> [file paths]
    where stem is the file name without extension.
    """
    stem_map = {}
    if not folder_path.exists() or not folder_path.is_dir():
        return stem_map

    for file_path in folder_path.iterdir():
        if file_path.is_file():
            stem = file_path.stem
            stem_map.setdefault(stem, []).append(file_path)

    return stem_map


def find_column_index(header, column_name):
    try:
        return header.index(column_name)
    except ValueError:
        return None


def parse_annotated_csv(csv_path, errors):
    """
    Expected structure:
    Row 0: header
    Row 1: metadata row
    From row 2 onwards: segment rows
    """
    try:
        rows = safe_read_csv_rows(csv_path)
    except Exception as e:
        add_error(errors, csv_path, f"Could not read CSV: {e}")
        return None

    if len(rows) == 0:
        add_error(errors, csv_path, "CSV is empty")
        return None

    header = rows[0]

    idx_n = find_column_index(header, "Nr.")
    idx_text = find_column_index(header, "Text")
    idx_add = find_column_index(header, "ADD")
    idx_auf = find_column_index(header, "AUF")
    idx_fkt = find_column_index(header, "FKT")
    idx_the = find_column_index(header, "THE")
    idx_kon = find_column_index(header, "KON")

    required_columns = {
        "Nr.": idx_n,
        "Text": idx_text,
        "ADD": idx_add,
        "AUF": idx_auf,
        "FKT": idx_fkt,
        "THE": idx_the,
        "KON": idx_kon,
    }

    missing_columns = [name for name, idx in required_columns.items() if idx is None]
    if missing_columns:
        add_error(
            errors,
            csv_path,
            f"CSV header is incomplete, missing columns: {', '.join(missing_columns)}"
        )
        return None

    if len(rows) < 2:
        add_error(errors, csv_path, "CSV does not contain a metadata row (row 2)")
        return None

    meta_row = rows[1]

    if len(meta_row) < len(header):
        meta_row = meta_row + [""] * (len(header) - len(meta_row))

    segment_rows = rows[2:]

    return {
        "rows": rows,
        "header": header,
        "meta_row": meta_row,
        "segment_rows": segment_rows,
        "idx_n": idx_n,
        "idx_text": idx_text,
        "idx_add": idx_add,
        "idx_auf": idx_auf,
        "idx_fkt": idx_fkt,
        "idx_the": idx_the,
        "idx_kon": idx_kon,
    }


def check_required_subfolders(parent_folder, errors):
    raw_folder = parent_folder / "raw"
    segmented_folder = parent_folder / "segmented"
    annotated_folder = parent_folder / "annotated"

    missing = []
    if not raw_folder.is_dir():
        missing.append("raw")
    if not segmented_folder.is_dir():
        missing.append("segmented")
    if not annotated_folder.is_dir():
        missing.append("annotated")

    if missing:
        add_error(
            errors,
            parent_folder,
            f"Missing subfolders: {', '.join(missing)}"
        )

    return raw_folder, segmented_folder, annotated_folder


def check_same_names_in_three_folders(parent_folder, raw_folder, segmented_folder, annotated_folder, errors):
    raw_names = set(get_stem_map(raw_folder).keys())
    segmented_names = set(get_stem_map(segmented_folder).keys())
    annotated_names = set(get_stem_map(annotated_folder).keys())

    all_names = raw_names | segmented_names | annotated_names

    for name in sorted(all_names):
        missing_in = []
        if name not in raw_names:
            missing_in.append("raw")
        if name not in segmented_names:
            missing_in.append("segmented")
        if name not in annotated_names:
            missing_in.append("annotated")

        if missing_in:
            add_error(
                errors,
                parent_folder,
                f"File name '{name}' is missing in: {', '.join(missing_in)}"
            )


def is_text_only_uppercase(text):
    """
    Returns True if the text contains at least one alphabetic character
    and all alphabetic characters are uppercase.
    Non-letter characters are ignored.
    """
    letters = [ch for ch in text if ch.isalpha()]
    return bool(letters) and all(ch.isupper() for ch in letters)


def check_segmented_vs_csv(segmented_txt_path, csv_path, errors):
    try:
        txt_lines = safe_read_text_lines(segmented_txt_path)
    except Exception as e:
        add_error(errors, segmented_txt_path, f"Could not read segmented TXT: {e}")
        return

    csv_data = parse_annotated_csv(csv_path, errors)
    if csv_data is None:
        return

    meta_row = csv_data["meta_row"]
    segment_rows = csv_data["segment_rows"]
    idx_n = csv_data["idx_n"]
    idx_text = csv_data["idx_text"]
    idx_add = csv_data["idx_add"]
    idx_auf = csv_data["idx_auf"]
    idx_fkt = csv_data["idx_fkt"]
    idx_the = csv_data["idx_the"]
    idx_kon = csv_data["idx_kon"]

    if len(segment_rows) == 0:
        add_error(errors, csv_path, "CSV does not contain any segments")
        return

    thema = meta_row[idx_the].strip() if idx_the < len(meta_row) else ""
    if thema == "":
        add_error(errors, csv_path, "CSV does not contain a value for Thema (THE)")
    elif thema not in ALLOWED_THE_VALUES:
        add_error(
            errors,
            csv_path,
            f"Invalid THE value '{thema}', allowed values are: {', '.join(sorted(ALLOWED_THE_VALUES))}"
        )

    konstellation = meta_row[idx_kon].strip() if idx_kon < len(meta_row) else ""
    if konstellation == "":
        add_error(errors, csv_path, "CSV does not contain a value for Konstellation (KON)")
    elif konstellation not in ALLOWED_KON_VALUES:
        add_error(
            errors,
            csv_path,
            f"Invalid KON value '{konstellation}', allowed values are: {', '.join(sorted(ALLOWED_KON_VALUES))}"
        )

    if len(txt_lines) != len(segment_rows):
        add_error(
            errors,
            csv_path,
            f"Segment count does not match segmented TXT: TXT={len(txt_lines)}, CSV={len(segment_rows)}"
        )

    expected_number = 0
    found_th1 = False
    found_th2 = False
    found_zth = False

    for row_index, row in enumerate(segment_rows, start=3):
        if len(row) < len(csv_data["header"]):
            row = row + [""] * (len(csv_data["header"]) - len(row))

        number_value = row[idx_n].strip()
        text_value = row[idx_text].strip()
        add_value = row[idx_add].strip()
        auf_value = row[idx_auf].strip()
        fkt_value = row[idx_fkt].strip()

        has_number = number_value != "" and number_value != "X"
        has_text = text_value != ""

        if fkt_value == "TH1":
            found_th1 = True
        if fkt_value == "TH2":
            found_th2 = True
        if fkt_value == "ZTH":
            found_zth = True

        if number_value == "":
            add_error(errors, csv_path, f"CSV row {row_index}: segment number (Nr.) is missing")
        else:
            try:
                number_int = int(number_value)
                if number_int != expected_number:
                    add_error(
                        errors,
                        csv_path,
                        f"CSV row {row_index}: segment number is not continuous, expected {expected_number}, found {number_int}"
                    )
                    expected_number = number_int + 1
                else:
                    expected_number += 1
            except ValueError:
                if number_value != "X":
                    add_error(
                        errors,
                        csv_path,
                        f"CSV row {row_index}: segment number is not an integer: '{number_value}'"
                    )

        if has_number and not has_text:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: segment number exists, but text field is empty"
            )

        # Neue Regel 3:
        # Wenn Text vorhanden ist, muss ADD = J oder N sein
        if has_text and add_value not in ALLOWED_ADD_VALUES:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: ADD must be 'J' or 'N' when text exists"
            )

        if has_number and has_text:
            if add_value not in ALLOWED_ADD_VALUES:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: ADD must be 'J' or 'N' when number and text exist"
                )

            if auf_value not in ALLOWED_AUF_VALUES:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: AUF must be 'EIN', 'HAU', or 'SCH' when number and text exist"
                )

            if fkt_value == "":
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: FKT is missing although number and text exist"
                )
            elif fkt_value not in ALLOWED_FKT_VALUES:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: invalid FKT value '{fkt_value}', allowed values are: {', '.join(sorted(ALLOWED_FKT_VALUES))}"
                )

        # Neue Regel 1:
        # Wenn ADD = J, darf Text nicht nur aus Großbuchstaben bestehen
        if add_value == "J" and has_text and is_text_only_uppercase(text_value):
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: text must not consist only of uppercase letters when ADD = 'J'"
            )

    if konstellation in {"ABW", "UEN"}:
        missing_parts = []
        if not found_th1:
            missing_parts.append("TH1")
        if not found_th2:
            missing_parts.append("TH2")

        if missing_parts:
            add_error(
                errors,
                csv_path,
                f"KON is '{konstellation}', therefore FKT must contain at least one TH1 and one TH2; missing: {', '.join(missing_parts)}"
            )

    # Neue Regel 2:
    # Wenn KON = EIN, dann darf es kein TH1 oder TH2 geben
    if konstellation == "EIN":
        forbidden_parts = []
        if found_th1:
            forbidden_parts.append("TH1")
        if found_th2:
            forbidden_parts.append("TH2")

        if forbidden_parts:
            add_error(
                errors,
                csv_path,
                f"KON is 'EIN', therefore FKT must not contain: {', '.join(forbidden_parts)}"
            )

    # Neue Regel 4:
    # Wenn KON = EIN, ABW oder UEN, dann muss mindestens ein ZTH existieren
    if konstellation in {"EIN", "ABW", "UEN"} and not found_zth:
        add_error(
            errors,
            csv_path,
            f"KON is '{konstellation}', therefore FKT must contain at least one ZTH"
        )


def process_parent_folder(parent_folder, errors):
    raw_folder, segmented_folder, annotated_folder = check_required_subfolders(parent_folder, errors)

    if not raw_folder.is_dir() or not segmented_folder.is_dir() or not annotated_folder.is_dir():
        return

    check_same_names_in_three_folders(parent_folder, raw_folder, segmented_folder, annotated_folder, errors)

    segmented_map = get_stem_map(segmented_folder)
    annotated_map = get_stem_map(annotated_folder)

    common_names = set(segmented_map.keys()) & set(annotated_map.keys())

    for name in sorted(common_names):
        segmented_files = segmented_map[name]
        annotated_files = annotated_map[name]

        segmented_txt = None
        for file_path in segmented_files:
            if file_path.suffix.lower() == ".txt":
                segmented_txt = file_path
                break

        if segmented_txt is None:
            add_error(errors, parent_folder, f"Missing .txt file for '{name}' in folder segmented")
            continue

        csv_file = None
        for file_path in annotated_files:
            if file_path.suffix.lower() == ".csv":
                csv_file = file_path
                break

        if csv_file is None:
            add_error(errors, parent_folder, f"Missing .csv file for '{name}' in folder annotated")
            continue

        check_segmented_vs_csv(segmented_txt, csv_file, errors)


def write_errors(errors, output_file):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for error in errors:
            f.write(error + "\n")


def find_data_groups(root_path):
    subfolders = [p for p in root_path.iterdir() if p.is_dir()]
    return sorted(subfolders, key=lambda p: p.name)


def run_checks(input_root, output_error_file):
    errors = []
    root_path = Path(input_root)

    if not root_path.exists():
        add_error(errors, root_path, "Input path does not exist")
        write_errors(errors, output_error_file)
        return errors

    if not root_path.is_dir():
        add_error(errors, root_path, "Input path is not a folder")
        write_errors(errors, output_error_file)
        return errors

    parent_folders = find_data_groups(root_path)

    if not parent_folders:
        add_error(errors, root_path, "No subfolders found")
        write_errors(errors, output_error_file)
        return errors

    for parent_folder in parent_folders:
        process_parent_folder(parent_folder, errors)

    write_errors(errors, output_error_file)
    return errors


def main():
    input_root = r"C:\Users\haufa\Downloads\Annotationen\Annotationen"
    output_error_file = r"C:\Users\haufa\Downloads\check_data_errors.txt"

    errors = run_checks(input_root, output_error_file)

    print(f"Check completed. Number of errors: {len(errors)}")
    print(f"Error file: {output_error_file}")


if __name__ == "__main__":
    main()