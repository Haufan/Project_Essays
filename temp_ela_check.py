from collections import defaultdict
from pathlib import Path
import csv
import re


#ANNOTATION_ROOT = Path(r"C:\Users\haufa\Downloads\Annotationen")
ANNOTATION_ROOT = Path(r"C:\Users\haufa\Downloads\annotation")
OUTPUT_FILE = ANNOTATION_ROOT / "ela_fehler.txt"


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


def get_target_numbers(value: str) -> set[int]:
    """
    Extrahiert alle Segmentnummern aus ZIE.
    """
    if not value:
        return set()

    return {int(number) for number in re.findall(r"\d+", value)}


def read_annotation_csv(csv_file: Path) -> list[dict[str, str]]:
    """
    Liest eine Annotationsdatei ein.
    """
    encodings = ("utf-8-sig", "utf-8", "cp1252")

    for encoding in encodings:
        try:
            with csv_file.open(
                "r",
                encoding=encoding,
                newline="",
            ) as file:
                reader = csv.DictReader(file, delimiter="|")
                return list(reader)

        except UnicodeDecodeError:
            continue

    raise ValueError(f"Datei konnte nicht gelesen werden: {csv_file}")


def check_ela(csv_file: Path) -> list[int]:
    """
    Prüft alle REL=ELA-Annotationen.

    Rückgabe:
        Liste der fehlerhaften Segmentnummern.
    """
    rows = read_annotation_csv(csv_file)

    segments: dict[int, dict[str, str]] = {}

    for row in rows:
        nr = (row.get("Nr.") or "").strip()

        if nr.isdigit():
            segments[int(nr)] = row

    errors: list[int] = []

    for nr in sorted(segments):
        row = segments[nr]

        rel = (row.get("REL") or "").strip().upper()

        if rel != "ELA":
            continue

        zie_raw = (row.get("ZIE") or "").strip()
        targets = get_target_numbers(zie_raw)

        previous_nr = nr - 1
        previous_row = segments.get(previous_nr)

        # Regel 1:
        # ELA zeigt auf das direkt vorherige Segment.
        if previous_nr in targets:
            continue

        # Regel 2:
        # Das vorherige Segment ist ebenfalls ELA
        # und beide zeigen auf dasselbe Ziel.
        if previous_row is not None:
            previous_rel = (
                previous_row.get("REL") or ""
            ).strip().upper()

            previous_targets = get_target_numbers(
                (previous_row.get("ZIE") or "").strip()
            )

            if (
                previous_rel == "ELA"
                and targets
                and targets == previous_targets
            ):
                continue

        errors.append(nr)

    return errors


def main() -> None:
    annotation_index = build_annotation_index(ANNOTATION_ROOT)

    # Speichert:
    # (Ordnerpfad, Dateipfad, Segmentnummer)
    errors_found: list[tuple[Path, Path, int]] = []

    total_files = 0
    total_errors = 0

    for participant_id, csv_files in annotation_index.items():
        for csv_file in csv_files:
            total_files += 1

            try:
                errors = check_ela(csv_file)

            except Exception as exc:
                print(f"Fehler beim Lesen von {csv_file}: {exc}")
                continue

            for segment_nr in errors:
                errors_found.append(
                    (
                        csv_file.parent,   # annotated-Ordner
                        csv_file,
                        segment_nr,
                    )
                )
                total_errors += 1

    # Zuerst nach Ordner, dann nach Dateiname,
    # dann nach Segmentnummer sortieren.
    errors_found.sort(
        key=lambda item: (
            str(item[0]).lower(),
            item[1].name.lower(),
            item[2],
        )
    )

    error_lines = [
        f"{csv_file} - {segment_nr}"
        for _, csv_file, segment_nr in errors_found
    ]

    OUTPUT_FILE.write_text(
        "\n".join(error_lines),
        encoding="utf-8",
    )

    print(f"Geprüfte CSV-Dateien: {total_files}")
    print(f"Gefundene ELA-Fehler: {total_errors}")
    print(f"Ergebnis gespeichert unter:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()