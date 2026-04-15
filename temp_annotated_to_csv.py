# ==========================================
# File: txt_to_segmented_and_csv.py
# Author: Dietmar Benndorf
# Date: 2026-04-01
# Description:
#    Reads every .txt file from the source directory, processes each file,
#    and saves the result in two output formats.
#
#    For each input file, the script:
#    - removes leading number + whitespace
#      (e.g. "1 ", "22 ")
#    - removes square brackets [] from each line
#    - extracts zone labels at the end of a line
#      (WHG, AHG, SON, TH1, TH2, PRO, CON, GLD, ZTH)
#    - removes the extracted zone from the text stored in segmented files
#
#    Output:
#    - segmented/: cleaned .txt files without brackets and without zones
#    - csv/: .csv files with the columns Text and FKT (= extracted zone)
# ==========================================

from pathlib import Path
import re
import pandas as pd


LEADING_NUMBER_RE = re.compile(r"^\d+\s+")
ZONE_RE = re.compile(r"\s*(WHG|AHG|SON|TH1|TH2|PRO|CON|GLD|ZTH)\??\s*$")
TRAILING_TAG_RE = re.compile(r"\s*[A-Z]{3}\??\s*$")


def parse_line(raw: str) -> tuple[str, str]:
    line = raw.strip()
    if not line:
        return "", ""

    # Schritt 1: Führende Zahl + Leerzeichen entfernen
    # Beispiele: "1 Text" -> "Text", "22 Beispiel" -> "Beispiel"
    line = LEADING_NUMBER_RE.sub("", line).strip()

    if not line:
        return "", ""

    # Schritt 2: Brackets entfernen
    line = line.replace("[", "").replace("]", "").strip()

    zone = ""

    # Schritt 3: Gültige Zone extrahieren
    match = ZONE_RE.search(line)
    if match:
        zone = match.group(1)
        line = line[:match.start()].rstrip()
    else:
        # Schritt 4: Ungültige 3-Buchstaben-Markierung am Ende löschen
        line = TRAILING_TAG_RE.sub("", line).rstrip()

    text = line.strip()
    return text, zone


def process_file(txt_path: Path, segmented_dir: Path, csv_dir: Path) -> None:
    lines = txt_path.read_text(encoding="utf-8").splitlines()

    cleaned_lines = []
    rows = []

    for raw_line in lines:
        text, zone = parse_line(raw_line)

        if text:
            cleaned_lines.append(text)
            rows.append({
                "Text": text,
                "FKT": zone
            })

    # Bereinigte TXT speichern
    segmented_path = segmented_dir / txt_path.name
    segmented_path.write_text("\n".join(cleaned_lines), encoding="utf-8")

    # CSV speichern
    df = pd.DataFrame(rows, columns=["Text", "FKT"])
    csv_path = csv_dir / f"{txt_path.stem}.csv"
    df.to_csv(csv_path, sep="|", index=False, encoding="utf-8-sig")


def main(source: str) -> None:
    source_path = Path(source)
    txt_files = sorted(source_path.glob("*.txt"))

    segmented_dir = source_path / "segmented"
    csv_dir = source_path / "csv"

    segmented_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    for txt_file in txt_files:
        process_file(txt_file, segmented_dir, csv_dir)


if __name__ == "__main__":
    source = r"C:/Users/haufa/PycharmProjects/Project_Essays/data_input"
    main(source)