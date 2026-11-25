from pathlib import Path
import csv


BASE_PATH = Path(r"C:\Users\haufa\Downloads\Annotationen\Annotationen")

SOURCE_FOLDERS = [
    "A 1-50++",
    "A 151-200++",
    "A 301-350++",
    "B 51-100++",
    "B 201-250++",
    "B 351-400++",
]

IAA_FOLDER = BASE_PATH / "IAA"
MARIESA_FOLDER = IAA_FOLDER / "Mariesa"
DIETMAR_FOLDER = IAA_FOLDER / "Dietmar"


def detect_encoding(csv_file: Path) -> str:
    """
    Ermittelt eine geeignete Zeichenkodierung.
    """
    encodings = ("utf-8-sig", "utf-8", "cp1252")

    for encoding in encodings:
        try:
            csv_file.read_text(encoding=encoding)
            return encoding
        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Zeichenkodierung konnte nicht erkannt werden: {csv_file}"
    )


def process_csv(source_file: Path, destination_file: Path) -> None:
    """
    Liest eine CSV-Datei ein, leert die Spalten REL und ZIE
    und speichert die bearbeitete Datei im Zielordner.

    Das verwendete Trennzeichen ist |.
    """
    encoding = detect_encoding(source_file)

    with source_file.open(
        "r",
        encoding=encoding,
        newline="",
    ) as infile:

        reader = csv.DictReader(infile, delimiter="|")

        if reader.fieldnames is None:
            raise ValueError(
                f"Keine Kopfzeile gefunden: {source_file}"
            )

        fieldnames = reader.fieldnames

        if "REL" not in fieldnames:
            raise ValueError(
                f"Spalte REL fehlt: {source_file}"
            )

        if "ZIE" not in fieldnames:
            raise ValueError(
                f"Spalte ZIE fehlt: {source_file}"
            )

        rows = list(reader)

    # REL und ZIE vollständig leeren
    for row in rows:
        row["REL"] = ""
        row["ZIE"] = ""

    with destination_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
            delimiter="|",
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)


def get_destination_folder(source_folder_name: str) -> Path:
    """
    Ordner, die mit A beginnen -> Mariesa
    Ordner, die mit B beginnen -> Dietmar
    """
    name = source_folder_name.strip().upper()

    if name.startswith("A"):
        return MARIESA_FOLDER

    if name.startswith("B"):
        return DIETMAR_FOLDER

    raise ValueError(
        f"Ordner beginnt weder mit A noch mit B: {source_folder_name}"
    )


def main() -> None:
    # Zielordner erstellen
    MARIESA_FOLDER.mkdir(parents=True, exist_ok=True)
    DIETMAR_FOLDER.mkdir(parents=True, exist_ok=True)

    copied_mariesa = 0
    copied_dietmar = 0
    errors = 0

    for source_folder_name in SOURCE_FOLDERS:

        source_folder = BASE_PATH / source_folder_name
        annotated_folder = source_folder / "annotated"

        print("=" * 80)
        print(f"Bearbeite: {source_folder_name}")

        if not source_folder.exists():
            print(f"FEHLER: Ordner existiert nicht:")
            print(source_folder)
            errors += 1
            continue

        if not annotated_folder.exists():
            print(f"FEHLER: annotated-Ordner existiert nicht:")
            print(annotated_folder)
            errors += 1
            continue

        destination_folder = get_destination_folder(
            source_folder_name
        )

        csv_files = sorted(
            annotated_folder.glob("*.csv"),
            key=lambda path: path.name.lower(),
        )

        print(f"Gefundene CSV-Dateien: {len(csv_files)}")

        for source_file in csv_files:

            destination_file = (
                destination_folder / source_file.name
            )

            # Sicherheit gegen gleichnamige Dateien
            if destination_file.exists():
                print(
                    f"WARNUNG: Datei existiert bereits: "
                    f"{destination_file.name}"
                )
                print(
                    f"         Quelle: {source_file}"
                )
                print(
                    "         Datei wird überschrieben."
                )

            try:
                process_csv(
                    source_file,
                    destination_file,
                )

                print(
                    f"  OK: {source_file.name}"
                )

                if destination_folder == MARIESA_FOLDER:
                    copied_mariesa += 1
                else:
                    copied_dietmar += 1

            except Exception as exc:
                print(
                    f"  FEHLER: {source_file.name}: {exc}"
                )
                errors += 1

    print()
    print("=" * 80)
    print("FERTIG")
    print("=" * 80)
    print(
        f"Mariesa: {copied_mariesa} Dateien"
    )
    print(
        f"Dietmar: {copied_dietmar} Dateien"
    )
    print(
        f"Fehler: {errors}"
    )
    print()
    print("Ausgabe:")
    print(IAA_FOLDER)


if __name__ == "__main__":
    main()