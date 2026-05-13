# ==========================================
# File: read_all_csv.py
# Author: Dietmar Benndorf
# Date: 2026-04-28
# Description:
#    Reads all CSV files from the source directory recursively.
#    For each CSV file, counts and calculates:
#    - ID from file name, e.g. 12345.csv -> 12345
#    - THE and KON from CSV metadata row
#    - segments
#    - non-disc = count(AHG, WHG, GLD, SON) / segments
#    - disc = count(ZTH, TH1, TH2, PRO, CON) / segments
#    - PRO segments
#    - CON segments
#    - PRO_words = words in PRO / words in PRO and CON
#    - CON_words = words in CON / words in PRO and CON
#    - structur: 1 if EIN, HAU and SCH exist, otherwise 0
#    - EIN_words = words in EIN / words in EIN, HAU and SCH
#    - HAU_words = words in HAU / words in EIN, HAU and SCH
#    - SCH_words = words in SCH / words in EIN, HAU and SCH
#    Saves the result to a CSV file.
# ==========================================

import csv
import sys
from pathlib import Path


NON_DISC_VALUES = {"AHG", "WHG", "GLD", "SON"}
DISC_VALUES = {"ZTH", "TH1", "TH2", "PRO", "CON"}
STRUCTURE_PARTS = {"EIN", "HAU", "SCH"}


def safe_read_csv_rows(file_path):
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


def find_csv_files(input_root):
    root_path = Path(input_root)

    if not root_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {root_path}")

    return sorted(root_path.rglob("*.csv"))


def find_column_index(header, column_name):
    try:
        return header.index(column_name)
    except ValueError:
        return None


def get_id_from_csv_filename(csv_path):
    return csv_path.stem


def count_words(text):
    return len(text.strip().split())


def get_cell_value(row, index):
    if index is None:
        return ""

    if index >= len(row):
        return ""

    return row[index].strip()


def print_progress_bar(current, total, bar_length=40):
    if total == 0:
        percent = 1
        filled_length = bar_length
    else:
        percent = current / total
        filled_length = int(bar_length * percent)

    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    percent_display = percent * 100

    sys.stdout.write(
        f"\r[{bar}] {current}/{total} {percent_display:.1f}%"
    )
    sys.stdout.flush()

    if current == total:
        print()


def format_ratio(value):
    return round(value, 2)


def create_empty_result(csv_path):
    return {
        "ID": get_id_from_csv_filename(csv_path),
        "THE": "",
        "KON": "",
        "segments": 0,
        "non-disc": 0,
        "disc": 0,
        "PRO": 0,
        "CON": 0,
        "PRO_words": 0,
        "CON_words": 0,
        "structur": 0,
        "EIN_words": 0,
        "HAU_words": 0,
        "SCH_words": 0,
    }


def analyze_csv_file(csv_path):
    rows = safe_read_csv_rows(csv_path)

    result = create_empty_result(csv_path)

    if len(rows) < 2:
        return result

    header = rows[0]
    meta_row = rows[1]

    idx_fkt = find_column_index(header, "FKT")
    idx_text = find_column_index(header, "Text")
    idx_auf = find_column_index(header, "AUF")
    idx_the = find_column_index(header, "THE")
    idx_kon = find_column_index(header, "KON")

    result["THE"] = get_cell_value(meta_row, idx_the)
    result["KON"] = get_cell_value(meta_row, idx_kon)

    if len(rows) < 3:
        return result

    segment_rows = rows[2:]

    existing_structure_parts = set()

    non_disc_count = 0
    disc_count = 0

    pro_words_count = 0
    con_words_count = 0

    ein_words_count = 0
    hau_words_count = 0
    sch_words_count = 0

    for row in segment_rows:
        result["segments"] += 1

        fkt_value = get_cell_value(row, idx_fkt)
        text_value = get_cell_value(row, idx_text)
        auf_value = get_cell_value(row, idx_auf)

        word_count = count_words(text_value)

        if fkt_value in NON_DISC_VALUES:
            non_disc_count += 1

        elif fkt_value in DISC_VALUES:
            disc_count += 1

        if fkt_value == "PRO":
            result["PRO"] += 1
            pro_words_count += word_count

        elif fkt_value == "CON":
            result["CON"] += 1
            con_words_count += word_count

        if auf_value in STRUCTURE_PARTS:
            existing_structure_parts.add(auf_value)

        if auf_value == "EIN":
            ein_words_count += word_count

        elif auf_value == "HAU":
            hau_words_count += word_count

        elif auf_value == "SCH":
            sch_words_count += word_count

    if result["segments"] > 0:
        result["non-disc"] = format_ratio(non_disc_count / result["segments"])
        result["disc"] = format_ratio(disc_count / result["segments"])

    pro_con_words_total = pro_words_count + con_words_count

    if pro_con_words_total > 0:
        result["PRO_words"] = format_ratio(pro_words_count / pro_con_words_total)
        result["CON_words"] = format_ratio(con_words_count / pro_con_words_total)

    ein_hau_sch_words_total = ein_words_count + hau_words_count + sch_words_count

    if ein_hau_sch_words_total > 0:
        result["EIN_words"] = format_ratio(ein_words_count / ein_hau_sch_words_total)
        result["HAU_words"] = format_ratio(hau_words_count / ein_hau_sch_words_total)
        result["SCH_words"] = format_ratio(sch_words_count / ein_hau_sch_words_total)

    if STRUCTURE_PARTS.issubset(existing_structure_parts):
        result["structur"] = 1
    else:
        result["structur"] = 0

    return result


def write_result_csv(results, output_file):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "ID",
        "THE",
        "KON",
        "segments",
        "non-disc",
        "disc",
        "PRO",
        "CON",
        "PRO_words",
        "CON_words",
        "structur",
        "EIN_words",
        "HAU_words",
        "SCH_words",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(results)


def process_all_csv_files(input_root, output_file):
    csv_files = find_csv_files(input_root)

    results = []
    total_files = len(csv_files)

    print(f"CSV files found: {total_files}")
    print_progress_bar(0, total_files)

    for index, csv_path in enumerate(csv_files, start=1):
        try:
            result = analyze_csv_file(csv_path)
            results.append(result)

        except Exception as e:
            result = create_empty_result(csv_path)
            results.append(result)

            print()
            print(f"Could not process CSV: {csv_path}")
            print(f"Error: {e}")

        print_progress_bar(index, total_files)

    write_result_csv(results, output_file)

    return results


def main():
    input_root = r"C:\Users\haufa\Downloads\Annotationen\Annotationen\alle_texte"
    output_file = r"C:\Users\haufa\Downloads\csv_segment_summary.csv"

    results = process_all_csv_files(input_root, output_file)

    print()
    print("CSV analysis completed.")
    print(f"Number of CSV files analyzed: {len(results)}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()


# Anzahl Segmente
# Anzahl Diskurs
# Anzahl Nicht-Diskurs
# Anzahl einzelner Diskurselemente
# Wortzahl / Länge einzelner Diskurselemente
# Thema erkennbar
# Konstellation erkennbar
# Konstellation
# Aufbau vorhanden
# Aufbau Länge