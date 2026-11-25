# ==========================================
# File: check_annotation_csv.py
# Author: Dietmar Benndorf (angepasste CSV-only-Version)
# Description:
#   Prueft ausschliesslich annotierte CSV-Dateien im angegebenen Ordner.
#   Keine raw-/segmented-Ordner oder TXT-Dateien erforderlich.
#   Alle bisherigen unabhaengigen CSV-Pruefungen bleiben erhalten.
# ==========================================

import csv
import re
from pathlib import Path

ALLOWED_ADD_VALUES = {"J", "N"}
ALLOWED_AUF_VALUES = {"EIN", "HAU", "SCH"}
ALLOWED_FKT_VALUES = {"AHG", "WHG", "SON", "GLD", "TH1", "TH2", "ZTH", "PRO", "CON"}
ALLOWED_THE_VALUES = {"BOOK", "FAST", "ARTS", "VOLU"}
ALLOWED_KON_VALUES = {"EIN", "ABW", "UEN", "UKL"}
ALLOWED_REL_VALUES = {"SUP", "ATT", "RES", "ELA", "NO"}

EXPECTED_CSV_COLUMNS = ("Nr.", "Text", "ADD", "AUF", "FKT", "REL", "ZIE", "THE", "KON")


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
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    last_error = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.reader(f, delimiter="|")
                return list(reader)
        except Exception as e:
            last_error = e

    raise last_error


def check_csv_field_delimiter(csv_path, errors):
    """
    Checks whether the CSV header uses | as its field delimiter.

    The delimiter is inferred from the known column names in the first
    non-empty line. This is more reliable than counting commas or semicolons,
    because those characters may also occur inside text fields.

    Returns True when | is used, otherwise False.
    """
    try:
        lines = safe_read_text_lines(csv_path)
    except Exception as e:
        add_error(errors, csv_path, f"Could not inspect CSV delimiter: {e}")
        return False

    header_line = next((line for line in lines if line.strip()), "")
    if header_line == "":
        # The empty-file error is produced later by parse_annotated_csv.
        return True

    expected_columns = set(EXPECTED_CSV_COLUMNS)
    candidates = ("|", ";", "\t", ",")
    scores = {}

    for delimiter in candidates:
        fields = next(csv.reader([header_line], delimiter=delimiter))
        cleaned_fields = [field.strip().lstrip("\ufeff") for field in fields]
        scores[delimiter] = sum(
            field in expected_columns for field in cleaned_fields
        )

    # In a tie, | wins because it is the required delimiter.
    best_delimiter = max(candidates, key=lambda delimiter: (scores[delimiter], delimiter == "|"))

    if best_delimiter != "|" or scores["|"] < 2:
        delimiter_names = {";": "semicolon", ",": "comma", "\t": "tab"}
        detected = delimiter_names.get(best_delimiter, repr(best_delimiter))
        add_error(
            errors,
            csv_path,
            "CSV field delimiter must be '|'; "
            f"detected delimiter: {detected}"
        )
        return False

    return True


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
    if not check_csv_field_delimiter(csv_path, errors):
        return None

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
    idx_rel = find_column_index(header, "REL")
    idx_zie = find_column_index(header, "ZIE")

    required_columns = {
        "Nr.": idx_n,
        "Text": idx_text,
        "ADD": idx_add,
        "AUF": idx_auf,
        "FKT": idx_fkt,
        "THE": idx_the,
        "KON": idx_kon,
        "REL": idx_rel,
        "ZIE": idx_zie,
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
        "idx_rel": idx_rel,
        "idx_zie": idx_zie,
    }


def is_text_only_uppercase(text):
    """
    Returns True if the text contains at least one alphabetic character
    and all alphabetic characters are uppercase.
    Non-letter characters are ignored.
    """
    letters = [ch for ch in text if ch.isalpha()]
    return bool(letters) and all(ch.isupper() for ch in letters)


def parse_zie_targets(zie_value):
    """
    Validates and parses the ZIE column.

    Allowed ZIE formats:
    - one target: 3
    - multiple targets: 3;4;5
    - one connection: 3-4
    - combination with target: [1] 3
    - combination with multiple values and multiple targets: [1;2] 3;4

    Returns:
    - (True, target_numbers) if the format is valid
    - (False, []) if the format is invalid

    For combination syntax, only the numbers after the closing bracket are
    treated as targets. The numbers inside [...] describe the combination.
    """
    value = zie_value.strip()

    if value == "":
        return True, []

    number_list_pattern = r"\d+(?:;\d+)*"

    if re.fullmatch(number_list_pattern, value):
        return True, [int(part) for part in value.split(";")]

    match = re.fullmatch(r"(\d+)-(\d+)", value)
    if match:
        return True, [int(match.group(1)), int(match.group(2))]

    match = re.fullmatch(r"\[(\d+(?:;\d+)*)\]\s+(\d+(?:;\d+)*)", value)
    if match:
        target_part = match.group(2)
        return True, [int(part) for part in target_part.split(";")]

    return False, []


def check_annotated_csv(csv_path, errors):
    """Prueft eine CSV unabhaengig von TXT-Dateien."""
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
    idx_rel = csv_data["idx_rel"]
    idx_zie = csv_data["idx_zie"]

    if not segment_rows:
        add_error(errors, csv_path, "CSV does not contain any segments")
        return

    thema = meta_row[idx_the].strip() if idx_the < len(meta_row) else ""
    if not thema:
        add_error(errors, csv_path, "CSV does not contain a value for Thema (THE)")
    elif thema not in ALLOWED_THE_VALUES:
        add_error(errors, csv_path,
                  f"Invalid THE value '{thema}', allowed values are: {', '.join(sorted(ALLOWED_THE_VALUES))}")

    konstellation = meta_row[idx_kon].strip() if idx_kon < len(meta_row) else ""
    if not konstellation:
        add_error(errors, csv_path, "CSV does not contain a value for Konstellation (KON)")
    elif konstellation not in ALLOWED_KON_VALUES:
        add_error(errors, csv_path,
                  f"Invalid KON value '{konstellation}', allowed values are: {', '.join(sorted(ALLOWED_KON_VALUES))}")

    expected_number = 0
    found_th1 = False
    found_th2 = False
    found_zth = False
    zth_without_rel_and_zie_count = 0

    # Stores parsed row data for cross-reference checks that need to compare
    # a segment with the FKT value of its ZIE target(s).
    segment_records = []

    for row_index, row in enumerate(segment_rows, start=3):
        if len(row) < len(csv_data["header"]):
            row = row + [""] * (len(csv_data["header"]) - len(row))

        number_value = row[idx_n].strip()
        text_value = row[idx_text].strip()
        add_value = row[idx_add].strip()
        auf_value = row[idx_auf].strip()
        fkt_value = row[idx_fkt].strip()
        rel_value = row[idx_rel].strip()
        zie_value = row[idx_zie].strip()

        has_number = number_value != "" and number_value != "X"
        has_text = text_value != ""

        # ZIE-Format pruefen und Zielnummern extrahieren.
        zie_format_is_valid, zie_target_numbers = parse_zie_targets(zie_value)
        if not zie_format_is_valid:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: invalid ZIE format '{zie_value}'. Allowed examples: 3, 3;4, 3-4, [1] 3, [1;2] 3;4"
            )

        # Das Ziel darf nie mit der eigenen Nr. identisch sein.
        try:
            current_number_int = int(number_value)
        except ValueError:
            current_number_int = None

        if current_number_int is not None and current_number_int in zie_target_numbers:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: ZIE must not contain the same number as Nr. ({current_number_int})"
            )

        segment_records.append({
            "row_index": row_index,
            "nr": current_number_int,
            "fkt": fkt_value,
            "rel": rel_value,
            "zie": zie_value,
            "zie_format_is_valid": zie_format_is_valid,
            "zie_target_numbers": zie_target_numbers,
        })

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

        # Neue REL/ZIE-Regeln:
        # 1) In REL sind nur SUP, ATT, RES, ELA, NO oder leer erlaubt.
        if rel_value != "" and rel_value not in ALLOWED_REL_VALUES:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: invalid REL value '{rel_value}', allowed values are: {', '.join(sorted(ALLOWED_REL_VALUES))} or empty"
            )

        # 2) Es darf höchstens eine ZTH geben, bei der REL und ZIE leer sind.
        if fkt_value == "ZTH" and rel_value == "" and zie_value == "":
            zth_without_rel_and_zie_count += 1

        # 3) TH1, TH2, PRO und CON müssen Werte in REL und ZIE haben.
        if fkt_value in {"TH1", "TH2", "PRO", "CON"}:
            if rel_value == "":
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must not be empty when FKT = '{fkt_value}'"
                )
            if zie_value == "":
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: ZIE must not be empty when FKT = '{fkt_value}'"
                )

        # 4) WHG, AHG, GLD und SON müssen REL = NO haben; ZIE muss leer sein.
        if fkt_value in {"WHG", "AHG", "GLD", "SON"}:
            if rel_value != "NO":
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must be 'NO' when FKT = '{fkt_value}'"
                )
            if zie_value != "":
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: ZIE must be empty when FKT = '{fkt_value}'"
                )

        # 5) Bei KON = ABW:
        #    TH1 darf in REL nur SUP, ELA oder RES haben.
        #    TH2 darf in REL nur ATT, ELA oder RES haben.
        if konstellation == "ABW":
            if fkt_value == "TH1" and rel_value not in {"SUP", "ELA", "RES"}:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must be 'SUP', 'ELA', or 'RES' when KON = 'ABW' and FKT = 'TH1'"
                )
            if fkt_value == "TH2" and rel_value not in {"ATT", "ELA", "RES"}:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must be 'ATT', 'ELA', or 'RES' when KON = 'ABW' and FKT = 'TH2'"
                )

        # 6) Bei KON = UEN:
        #    TH1 und TH2 dürfen in REL nur SUP, ELA oder RES haben.
        if (
                konstellation == "UEN"
                and fkt_value in {"TH1", "TH2"}
                and rel_value not in {"SUP", "ELA", "RES"}
        ):
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: REL must be 'SUP', 'ELA', or 'RES' when KON = 'UEN' and FKT = '{fkt_value}'"
            )

        if fkt_value == "ZTH" and rel_value not in {"ELA", "RES", ""}:
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: REL must be 'ELA', 'RES', or empty when FKT = 'ZTH'"
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

        if add_value == "J" and has_text and is_text_only_uppercase(text_value):
            add_error(
                errors,
                csv_path,
                f"CSV row {row_index}: text must not consist only of uppercase letters when ADD = 'J'"
            )

    number_to_fkt = {}
    number_to_row_index = {}
    duplicate_numbers = set()

    for record in segment_records:
        nr = record["nr"]
        if nr is None:
            continue
        if nr in number_to_fkt:
            duplicate_numbers.add(nr)
        else:
            number_to_fkt[nr] = record["fkt"]
            number_to_row_index[nr] = record["row_index"]

    for record in segment_records:
        row_index = record["row_index"]
        source_fkt = record["fkt"]
        rel_value = record["rel"]
        zie_value = record["zie"]

        if not record["zie_format_is_valid"] or zie_value == "":
            continue

        for target_number in record["zie_target_numbers"]:
            target_fkt = number_to_fkt.get(target_number)
            target_row_index = number_to_row_index.get(target_number)

            if target_fkt is None:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: ZIE target {target_number} does not exist as Nr. in this CSV"
                )
                continue

            if rel_value in {"RES", "ELA"} and source_fkt != target_fkt:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL = '{rel_value}' requires target {target_number} "
                    f"(CSV row {target_row_index}) to have the same FKT as the source; "
                    f"source FKT = '{source_fkt}', target FKT = '{target_fkt}'"
                )

            if konstellation in {"ABW", "UEN"} and target_fkt == "ZTH":
                if source_fkt in {"PRO", "CON"}:
                    add_error(
                        errors,
                        csv_path,
                        f"CSV row {row_index}: unusual direct connection in KON = '{konstellation}': "
                        f"FKT = '{source_fkt}' points directly to target {target_number} with FKT = 'ZTH'"
                    )
                elif source_fkt not in {"TH1", "TH2", "ZTH"}:
                    add_error(
                        errors,
                        csv_path,
                        f"CSV row {row_index}: in KON = '{konstellation}', only TH1 and TH2 may point to ZTH; "
                        f"source FKT = '{source_fkt}', target {target_number} has FKT = 'ZTH'"
                    )

    if duplicate_numbers:
        add_error(
            errors,
            csv_path,
            f"Duplicate segment numbers found; ZIE target checks may be ambiguous for Nr.: {', '.join(str(n) for n in sorted(duplicate_numbers))}"
        )

    if zth_without_rel_and_zie_count > 1:
        add_error(
            errors,
            csv_path,
            f"Only one ZTH may have empty REL and empty ZIE; found {zth_without_rel_and_zie_count}"
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

    if konstellation in {"EIN", "ABW", "UEN"} and not found_zth:
        add_error(
            errors,
            csv_path,
            f"KON is '{konstellation}', therefore FKT must contain at least one ZTH"
        )


def write_errors(errors, output_file):
    """
    Writes the collected errors to a TXT file.

    If output_file is accidentally given as a folder path, the function
    automatically writes to check_data_errors.txt inside that folder.
    This prevents PermissionError when trying to open a directory as a file.
    """
    output_path = Path(output_file)

    if output_path.exists() and output_path.is_dir():
        output_path = output_path / "check_data_errors.txt"

    elif output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)
        output_path = output_path / "check_data_errors.txt"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for error in errors:
            f.write(error + "\n")

    return output_path


def run_checks(input_root, output_error_file):
    """Prueft alle CSV-Dateien direkt im angegebenen Ordner."""
    errors = []
    root = Path(input_root)

    if not root.is_dir():
        add_error(errors, root, "Input path does not exist or is not a folder")
        write_errors(errors, output_error_file)
        return errors

    csv_files = sorted(
        (p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".csv"),
        key=lambda p: p.name.lower(),
    )
    print(f"Gefundene CSV-Dateien: {len(csv_files)}")
    if not csv_files:
        add_error(errors, root, "No CSV files found")

    for number, csv_path in enumerate(csv_files, start=1):
        print(f"[{number}/{len(csv_files)}] Pruefe: {csv_path.name}")
        try:
            check_annotated_csv(csv_path, errors)
        except Exception as exc:
            add_error(errors, csv_path, f"Unexpected error while checking CSV: {exc}")

    write_errors(errors, output_error_file)
    return errors


def main():
    ANNOTATION_ROOT = Path(r"C:\Users\haufa\Downloads\Annotationen\Annotationen\IAA\Mariesa")
    OUTPUT_FILE = ANNOTATION_ROOT / "check_data_errors.txt"

    print("=" * 80)
    print("ANNOTATION CHECK - CSV ONLY")
    print("=" * 80)
    print(f"Root: {ANNOTATION_ROOT}")
    print()

    errors = run_checks(ANNOTATION_ROOT, OUTPUT_FILE)
    print()
    print("=" * 80)
    print("PRUEFUNG ABGESCHLOSSEN")
    print("=" * 80)
    print(f"Anzahl gefundener Fehler: {len(errors)}")
    print(f"Fehlerdatei: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
