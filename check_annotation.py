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
#    - checks whether REL = RES or ELA points to a target with the same FKT
#    - checks whether in KON = ABW or UEN only TH1 and TH2 point to ZTH
#    - reports an unusual direct connection when PRO or CON points to ZTH
#      in KON = ABW or UEN
#    - compares raw and segmented TXT content after removing whitespace and
#      permitted inserted thesis statements from the segmented text
#    - checks whether annotated CSV files use | as the field delimiter
#    - compares each segmented line with the corresponding annotated Text
#      after removing whitespace and converting both texts to lowercase
#    - checks whether inserted uppercase theses appear in their configured
#      normal spelling in annotated and have ADD = J
#    - checks the reverse direction: every annotated segment with ADD = J
#      must correspond to a recognized inserted uppercase thesis in segmented
#
#    Output:
#    - .txt file with all detected errors
#    - one error per line, including the corresponding folder or file path
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

INSERTED_THESIS_NORMAL_FORMS_BASE = {
    "E-BOOKS SOLLTEN BÜCHER ERSETZEN.": "E-Books sollten Bücher ersetzen.",
    "BÜCHER SOLLTEN NICHT ERSETZT WERDEN.": "Bücher sollten nicht ersetzt werden.",
    "SELBERKOCHEN IST BESSER ALS FAST FOOD.": "Selberkochen ist besser als Fast Food.",
    "FAST FOOD IST BESSER ALS SELBERKOCHEN.": "Fast Food ist besser als Selberkochen.",
    "DARSTELLENDES SPIEL SOLLTE VERPFLICHTEND EINGEFÜHRT WERDEN.":
        "Darstellendes Spiel sollte verpflichtend eingeführt werden.",
    "DARSTELLENDES SPIEL SOLLTE NICHT VERPFLICHTEND EINGEFÜHRT WERDEN.":
        "Darstellendes Spiel sollte nicht verpflichtend eingeführt werden.",
    "MAN SOLLTE EIN EHRENAMT AUSFÜHREN.": "Man sollte ein Ehrenamt ausführen.",
    "MAN SOLLTE KEIN EHRENAMT AUSFÜHREN.": "Man sollte kein Ehrenamt ausführen.",
}

INSERTED_THESIS_NORMAL_FORMS = {
    uppercase_variant: normal_variant
    for uppercase_thesis, normal_thesis in INSERTED_THESIS_NORMAL_FORMS_BASE.items()
    for uppercase_variant, normal_variant in (
        (uppercase_thesis, normal_thesis),
        (uppercase_thesis + ".", normal_thesis + "."),
    )
}

SEGMENTED_INSERTED_ELEMENTS = set(INSERTED_THESIS_NORMAL_FORMS)


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


def remove_all_whitespace(text):
    """Removes spaces, tabs, line breaks, and all other whitespace."""
    return re.sub(r"\s+", "", text)


def normalize_raw_text(lines):
    """Normalizes raw TXT content for comparison."""
    return remove_all_whitespace("".join(lines))


def remove_permitted_inserted_elements(segmented_text):
    """
    Removes every exactly matching permitted thesis from segmented text.

    Processing is deliberately strict:
    - matching is case-sensitive
    - the wording, spaces, umlauts, and punctuation must be identical to one
      of the explicitly configured variants
    - no case conversion, whitespace normalization, or fuzzy matching is
      performed before the search
    - every exact occurrence is removed, even when it is not on a separate line

    The longer variants are checked first so that a version with a final full
    stop is removed completely instead of leaving the full stop behind.
    """
    cleaned_text = segmented_text

    for thesis in sorted(SEGMENTED_INSERTED_ELEMENTS, key=len, reverse=True):
        cleaned_text = cleaned_text.replace(thesis, "")

    return cleaned_text


def normalize_segmented_text(lines):
    """
    Normalizes segmented TXT content in the required order:

    1. Join the original segmented text while preserving line boundaries.
    2. Search for and remove only exactly matching configured uppercase theses.
    3. Remove all remaining whitespace.
    """
    original_segmented_text = "\n".join(lines)
    segmented_without_inserted_elements = remove_permitted_inserted_elements(
        original_segmented_text
    )
    return remove_all_whitespace(segmented_without_inserted_elements)


def get_difference_context(first_text, second_text, position, context_size=30):
    """Returns short excerpts around the first differing character."""
    start = max(0, position - context_size)
    end = position + context_size
    return first_text[start:end], second_text[start:end]


def check_raw_vs_segmented(raw_txt_path, segmented_txt_path, errors):
    """
    Compares raw and segmented TXT content.

    Before comparison:
    - permitted inserted thesis statements are removed from segmented text
    - all remaining whitespace is then removed from both texts
    """
    try:
        raw_lines = safe_read_text_lines(raw_txt_path)
    except Exception as e:
        add_error(errors, raw_txt_path, f"Could not read raw TXT: {e}")
        return

    try:
        segmented_lines = safe_read_text_lines(segmented_txt_path)
    except Exception as e:
        add_error(errors, segmented_txt_path, f"Could not read segmented TXT: {e}")
        return

    normalized_raw = normalize_raw_text(raw_lines)
    normalized_segmented = normalize_segmented_text(segmented_lines)

    if normalized_raw == normalized_segmented:
        return

    common_length = min(len(normalized_raw), len(normalized_segmented))
    difference_position = common_length

    for position in range(common_length):
        if normalized_raw[position] != normalized_segmented[position]:
            difference_position = position
            break

    raw_context, segmented_context = get_difference_context(
        normalized_raw,
        normalized_segmented,
        difference_position,
    )

    add_error(
        errors,
        segmented_txt_path,
        "Segmented text does not match raw text after first removing permitted "
        "inserted elements from segmented and then removing whitespace; "
        f"raw file = '{raw_txt_path}', first difference at normalized character "
        f"{difference_position}, raw length = {len(normalized_raw)}, "
        f"segmented length = {len(normalized_segmented)}, "
        f"raw excerpt = '{raw_context}', segmented excerpt = '{segmented_context}'"
    )


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


def normalize_segment_text_for_comparison(text):
    """Removes all whitespace and converts the text to lowercase."""
    return remove_all_whitespace(text).lower()


def check_segmented_lines_against_annotated(
    segmented_lines,
    segment_rows,
    header_length,
    idx_n,
    idx_text,
    idx_add,
    csv_path,
    errors,
):
    """
    Compares each segmented TXT line with the corresponding annotated segment.

    For the general comparison, all whitespace is removed and both texts are
    converted to lowercase. If a segmented line is an exactly configured
    uppercase inserted thesis, the corresponding annotated segment must contain
    the configured normal spelling of that thesis and ADD must be J.
    """
    comparable_count = min(len(segmented_lines), len(segment_rows))

    for segment_index in range(comparable_count):
        segmented_text = segmented_lines[segment_index]
        row = segment_rows[segment_index]
        if len(row) < header_length:
            row = row + [""] * (header_length - len(row))

        annotated_text = row[idx_text].strip()
        add_value = row[idx_add].strip()
        number_value = row[idx_n].strip()
        segment_label = number_value if number_value else str(segment_index)
        csv_row_number = segment_index + 3
        segmented_line_number = segment_index + 1

        if (
            normalize_segment_text_for_comparison(segmented_text)
            != normalize_segment_text_for_comparison(annotated_text)
        ):
            add_error(
                errors,
                csv_path,
                f"Segment {segment_label} does not match segmented TXT line "
                f"{segmented_line_number} (CSV row {csv_row_number}); "
                f"segmented = '{segmented_text}', annotated = '{annotated_text}'"
            )

        # Inserted theses are recognized only as exact uppercase line content.
        exact_segmented_text = segmented_text.strip()
        inserted_thesis_recognized = (
            exact_segmented_text in SEGMENTED_INSERTED_ELEMENTS
        )

        if inserted_thesis_recognized:
            expected_annotated_text = INSERTED_THESIS_NORMAL_FORMS[
                exact_segmented_text
            ]
            problems = []

            if (
                remove_all_whitespace(annotated_text)
                != remove_all_whitespace(expected_annotated_text)
            ):
                problems.append(
                    "the annotated Text must contain the thesis in its normal "
                    f"spelling: '{expected_annotated_text}'"
                )

            if add_value != "J":
                problems.append(f"ADD must be 'J' (found '{add_value}')")

            if problems:
                add_error(
                    errors,
                    csv_path,
                    f"Segment {segment_label} is an inserted uppercase thesis in "
                    f"segmented TXT line {segmented_line_number}; "
                    + "; ".join(problems)
                    + f"; annotated Text = '{annotated_text}'"
                )

        # Reverse check: ADD = J is valid only when the corresponding
        # segmented line was recognized as an exactly configured uppercase
        # inserted thesis.
        elif add_value == "J":
            add_error(
                errors,
                csv_path,
                f"Segment {segment_label} has ADD = 'J', but segmented TXT line "
                f"{segmented_line_number} is not a recognized inserted uppercase "
                f"thesis; segmented = '{segmented_text}', annotated = '{annotated_text}'"
            )

    # If annotated contains additional rows, ADD = J cannot be justified
    # because there is no corresponding segmented line in which a thesis
    # could have been recognized.
    for segment_index in range(comparable_count, len(segment_rows)):
        row = segment_rows[segment_index]
        if len(row) < header_length:
            row = row + [""] * (header_length - len(row))

        add_value = row[idx_add].strip()
        if add_value != "J":
            continue

        number_value = row[idx_n].strip()
        segment_label = number_value if number_value else str(segment_index)
        csv_row_number = segment_index + 3
        annotated_text = row[idx_text].strip()

        add_error(
            errors,
            csv_path,
            f"Segment {segment_label} (CSV row {csv_row_number}) has ADD = 'J', "
            "but no corresponding segmented TXT line exists; therefore no "
            f"inserted uppercase thesis can be recognized; annotated = '{annotated_text}'"
        )


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


def find_file_with_suffix(file_paths, suffix):
    """Returns the first file with the requested suffix, or None."""
    suffix = suffix.lower()
    for file_path in file_paths:
        if file_path.suffix.lower() == suffix:
            return file_path
    return None


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


def check_segmented_vs_csv(segmented_txt_path, csv_path, errors):
    """
    Checks one annotated CSV file.

    If segmented_txt_path is None or cannot be read, all CSV-only checks
    are still performed. Only the TXT-vs-CSV segment-count comparison is
    skipped in that case.
    """
    txt_lines = None

    if segmented_txt_path is not None:
        try:
            txt_lines = safe_read_text_lines(segmented_txt_path)
        except Exception as e:
            add_error(errors, segmented_txt_path, f"Could not read segmented TXT: {e}")

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

    if txt_lines is not None and len(txt_lines) != len(segment_rows):
        add_error(
            errors,
            csv_path,
            f"Segment count does not match segmented TXT: TXT={len(txt_lines)}, CSV={len(segment_rows)}"
        )

    if txt_lines is not None:
        check_segmented_lines_against_annotated(
            segmented_lines=txt_lines,
            segment_rows=segment_rows,
            header_length=len(csv_data["header"]),
            idx_n=idx_n,
            idx_text=idx_text,
            idx_add=idx_add,
            csv_path=csv_path,
            errors=errors,
        )

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

        # 5) Bei KON = ABW oder UKL:
        #    TH1 darf in REL nur SUP, ELA oder RES haben.
        #    TH2 darf in REL nur ATT, ELA oder RES haben.
        if konstellation in {"ABW", "UEN"}:
            if fkt_value == "TH1" and rel_value not in {"SUP", "ELA", "RES"}:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must be 'SUP', 'ELA', or 'RES' when KON = '{konstellation}' and FKT = 'TH1'"
                )
            if fkt_value == "TH2" and rel_value not in {"ATT", "ELA", "RES"}:
                add_error(
                    errors,
                    csv_path,
                    f"CSV row {row_index}: REL must be 'ATT', 'ELA', or 'RES' when KON = '{konstellation}' and FKT = 'TH2'"
                )

        # 6) Bei KON = UEN müssen TH1 und TH2 in REL SUP, ELA oder RES haben.
        if konstellation == "UEN" and fkt_value in {"TH1", "TH2"} and rel_value not in {"SUP", "ELA", "RES"}:
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


def process_parent_folder(parent_folder, errors):
    raw_folder, segmented_folder, annotated_folder = check_required_subfolders(parent_folder, errors)

    check_same_names_in_three_folders(parent_folder, raw_folder, segmented_folder, annotated_folder, errors)

    raw_map = get_stem_map(raw_folder)
    segmented_map = get_stem_map(segmented_folder)

    common_raw_segmented_names = set(raw_map.keys()) & set(segmented_map.keys())
    for name in sorted(common_raw_segmented_names):
        raw_txt = find_file_with_suffix(raw_map[name], ".txt")
        segmented_txt = find_file_with_suffix(segmented_map[name], ".txt")

        if raw_txt is None:
            add_error(
                errors,
                parent_folder,
                f"Missing .txt file for '{name}' in folder raw; skipping raw-vs-segmented text comparison"
            )
            continue

        if segmented_txt is None:
            add_error(
                errors,
                parent_folder,
                f"Missing .txt file for '{name}' in folder segmented; skipping raw-vs-segmented text comparison"
            )
            continue

        check_raw_vs_segmented(raw_txt, segmented_txt, errors)

    if not annotated_folder.is_dir():
        return

    annotated_map = get_stem_map(annotated_folder)

    for name in sorted(annotated_map.keys()):
        annotated_files = annotated_map[name]
        segmented_files = segmented_map.get(name, [])

        csv_file = find_file_with_suffix(annotated_files, ".csv")

        if csv_file is None:
            add_error(errors, parent_folder, f"Missing .csv file for '{name}' in folder annotated")
            continue

        segmented_txt = find_file_with_suffix(segmented_files, ".txt")

        if segmented_txt is None:
            add_error(
                errors,
                parent_folder,
                f"Missing .txt file for '{name}' in folder segmented; skipping TXT-vs-CSV segment-count check"
            )

        check_segmented_vs_csv(segmented_txt, csv_file, errors)


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
    input_root = r"C:\Users\haufa\Downloads\C 701-750++"
    output_error_file = r"C:\Users\haufa\Downloads\check_data_errors.txt"

    errors = run_checks(input_root, output_error_file)

    print(f"Check completed. Number of errors: {len(errors)}")
    print(f"Error file: {output_error_file}")


if __name__ == "__main__":
    main()