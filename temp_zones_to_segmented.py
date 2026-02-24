### TEMPORARY ###

# Date: 2026-02-10
# Description:
#    Reads text files line by line, removes everything outside square brackets [],
#    and saves the processed files with the same names into annotation_data/segmented
# ==========================================

from tqdm import tqdm
from pathlib import Path
import re


def main(source):
    """
    Process each text file in `source`, keeping only content inside square brackets [],
    and save the result to annotation_data/segmented with the same filenames.
    """

    source_path = Path(source)
    target_path = source_path.parent / "segmented"
    target_path.mkdir(exist_ok=True)

    pattern = re.compile(r"\[.*?\]")

    for file in tqdm(source_path.iterdir(), desc="Processing", unit=" file"):
        if not file.is_file():
            continue

        cleaned_lines = []

        with file.open("r", encoding="utf-8") as f:
            for line in f:
                matches = pattern.findall(line)
                if matches:
                    cleaned_lines.append("".join(matches) + "\n")

        output_file = target_path / file.name
        output_file.write_text("".join(cleaned_lines), encoding="utf-8")


if __name__ == "__main__":
    source = "C:/Users/haufa/PycharmProjects/Project_Essays/annotation_data/zones"
    main(source)