from __future__ import annotations

import csv
import shutil
from collections import defaultdict
from pathlib import Path


ID_COLUMN = "participant_private_id"
FOLDER_COLUMN = "annotation_subfolder"
DOUBLE_PLUS_COLUMN = "double_plus"


def build_annotation_index(annotation_root: Path) -> dict[str, list[Path]]:
    """
    Sucht rekursiv nach Dateien mit der Struktur:

        annotation/<Unterordner>/annotated/<ID>.csv

    Rückgabe:
        participant_id -> Liste der gefundenen CSV-Dateien
    """
    index: dict[str, list[Path]] = defaultdict(list)

    for annotated_dir in annotation_root.rglob("annotated"):
        if not annotated_dir.is_dir():
            continue

        for csv_file in annotated_dir.glob("*.csv"):
            participant_id = csv_file.stem.strip()

            if participant_id:
                index[participant_id].append(csv_file)

    return dict(index)


def update_sample_csv(
    sample_csv: Path,
    annotation_index: dict[str, list[Path]],
) -> None:
    """
    Ergänzt die Sample-CSV um:

    - annotation_subfolder
    - double_plus

    Die bestehende Sample-CSV wird direkt aktualisiert.
    """
    with sample_csv.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as infile:
        reader = csv.DictReader(infile, delimiter="|")

        if not reader.fieldnames:
            raise ValueError("Die Sample-CSV enthält keine Kopfzeile.")

        if ID_COLUMN not in reader.fieldnames:
            raise ValueError(
                f"Die Spalte '{ID_COLUMN}' wurde nicht gefunden.\n"
                f"Vorhandene Spalten: {reader.fieldnames}"
            )

        fieldnames = list(reader.fieldnames)

        if FOLDER_COLUMN not in fieldnames:
            fieldnames.append(FOLDER_COLUMN)

        if DOUBLE_PLUS_COLUMN not in fieldnames:
            fieldnames.append(DOUBLE_PLUS_COLUMN)

        rows = list(reader)

    found = 0
    not_found = 0
    multiple = 0

    for row in rows:
        participant_id = (row.get(ID_COLUMN) or "").strip()
        matches = annotation_index.get(participant_id, [])

        if len(matches) == 1:
            csv_file = matches[0]
            folder_name = csv_file.parent.parent.name

            row[FOLDER_COLUMN] = folder_name
            row[DOUBLE_PLUS_COLUMN] = (
                "x" if folder_name.endswith("++") else ""
            )

            found += 1

        elif len(matches) == 0:
            row[FOLDER_COLUMN] = ""
            row[DOUBLE_PLUS_COLUMN] = ""

            not_found += 1
            print(f"NICHT GEFUNDEN: {participant_id}")

        else:
            folder_names = sorted(
                {csv_file.parent.parent.name for csv_file in matches}
            )

            row[FOLDER_COLUMN] = "; ".join(folder_names)
            row[DOUBLE_PLUS_COLUMN] = (
                "x"
                if any(name.endswith("++") for name in folder_names)
                else ""
            )

            multiple += 1
            print(
                f"MEHRFACH GEFUNDEN: {participant_id} -> "
                f"{', '.join(folder_names)}"
            )

    temp_csv = sample_csv.with_name(
        sample_csv.stem + "_temp" + sample_csv.suffix
    )

    with temp_csv.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
            delimiter="|",
        )
        writer.writeheader()
        writer.writerows(rows)

    temp_csv.replace(sample_csv)

    print()
    print("Sample-CSV aktualisiert.")
    print(f"Gefunden: {found}")
    print(f"Nicht gefunden: {not_found}")
    print(f"Mehrfach gefunden: {multiple}")


def copy_sample_files_from_double_plus_folders(
    sample_csv: Path,
    annotation_index: dict[str, list[Path]],
    destination_dir: Path,
) -> None:
    """
    Kopiert NUR Dateien, deren ID in der Sample-CSV vorkommt
    UND die in einem Unterordner gefunden wurden, dessen Name
    mit '++' endet.

    Beispiel:

        Sample-CSV enthält ID 5433437

        Gefundene Datei:
        annotation/B 201-250++/annotated/5433437.csv

        Ziel:
        C:/Users/haufa/Downloads/Sample_15/5433437.csv
    """
    destination_dir.mkdir(parents=True, exist_ok=True)

    with sample_csv.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as infile:
        reader = csv.DictReader(infile, delimiter="|")
        rows = list(reader)

    copied = 0
    not_copied = 0

    for row in rows:
        participant_id = (row.get(ID_COLUMN) or "").strip()

        if not participant_id:
            continue

        matches = annotation_index.get(participant_id, [])

        # Nur Treffer aus ++-Ordnern auswählen
        double_plus_matches = [
            csv_file
            for csv_file in matches
            if csv_file.parent.parent.name.endswith("++")
        ]

        if not double_plus_matches:
            not_copied += 1
            continue

        for source_file in double_plus_matches:
            destination_file = destination_dir / source_file.name

            shutil.copy2(
                source_file,
                destination_file,
            )

            print(
                f"KOPIERT: {participant_id} "
                f"({source_file.parent.parent.name})"
            )

            copied += 1

    print()
    print("Kopieren abgeschlossen.")
    print(f"Zielordner: {destination_dir}")
    print(f"Kopierte Dateien: {copied}")
    print(
        "Sample-Einträge ohne Datei in ++-Ordner: "
        f"{not_copied}"
    )


def main() -> None:
    # ------------------------------------------------------------
    # PFADE
    # ------------------------------------------------------------

    sample_csv = Path(
        r"C:\Users\haufa\Downloads\level1.csv"
    )

    annotation_root = Path(
        r"C:\Users\haufa\Downloads\Annotationen"
    )

    destination_dir = Path(
        r"C:\Users\haufa\Downloads\Samples"
    )

    # ------------------------------------------------------------

    if not sample_csv.is_file():
        raise FileNotFoundError(
            f"Sample-CSV nicht gefunden:\n{sample_csv}"
        )

    if not annotation_root.is_dir():
        raise NotADirectoryError(
            f"Annotation-Ordner nicht gefunden:\n{annotation_root}"
        )

    # Einmal alle vorhandenen Annotationen indexieren
    annotation_index = build_annotation_index(annotation_root)

    # 1. Sample-CSV um Ordner und ++-Markierung ergänzen
    update_sample_csv(
        sample_csv=sample_csv,
        annotation_index=annotation_index,
    )

    # 2. NUR Sample-Dateien aus ++-Ordnern kopieren
    copy_sample_files_from_double_plus_folders(
        sample_csv=sample_csv,
        annotation_index=annotation_index,
        destination_dir=destination_dir,
    )


if __name__ == "__main__":
    main()