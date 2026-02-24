### TEMPORARY ###

# Date: 2026-02-24
# Description:
#    Converts zone-annotated .txt files to Sampletext-style CSVs.
#    Input line format expected:
#        [some sentence / ADU text] ZONE
#    Output columns:
#        N;Text;ADD;SCH;FKT;REL;ZIE
#    - Text: extracted without brackets
#    - FKT: zone label
#    - ADD/SCH/REL/ZIE: created but empty
# ==========================================

from tqdm import tqdm
import pandas as pd
from pathlib import Path
import re

# from class_Text import Text  # not needed for this conversion

LINE_RE = re.compile(r"^\[(?P<text>.*)\]\s*(?P<zone>[A-Za-z0-9]+)\s*$")


def convert_file_to_df(txt_path: Path) -> pd.DataFrame:
    rows = []

    for raw in txt_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue

        m = LINE_RE.match(line)
        if m:
            text = m.group("text").strip()
            zone = m.group("zone").strip()
        else:
            # If a line doesn't match the expected pattern, keep it as text and leave zone empty
            text = line
            zone = ""

        rows.append({"Text": text, "FKT": zone})

    df = pd.DataFrame(rows)

    # Build sample-format columns
    df.insert(0, "N", range(len(df)))
    for col in ["ADD", "SCH", "REL", "ZIE"]:
        df[col] = ""

    # Order columns exactly like sample
    df = df[["N", "Text", "ADD", "SCH", "FKT", "REL", "ZIE"]]
    return df


def main(source: str) -> None:
    """
    Process all text files in a directory and convert them to CSV.
    """
    source_path = Path(source)
    out_folder = Path(r"C:/Users/haufa/PycharmProjects/Project_Essays/annotation_data/csv")
    out_folder.mkdir(parents=True, exist_ok=True)

    # Only process .txt files
    txt_files = [p for p in source_path.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]

    for file in tqdm(txt_files, desc="Processing", unit=" texts done"):
        df = convert_file_to_df(file)

        out_path = out_folder / f"{file.stem}.csv"
        df.to_csv(out_path, sep="|", index=False, encoding="utf-8")


if __name__ == "__main__":
    source = r"C:/Users/haufa/PycharmProjects/Project_Essays/annotation_data/zones"
    main(source)