
import csv
from pathlib import Path
from collections import Counter

# ==========================================
# KONFIGURATION
# ==========================================

ANNOTATION_ROOT = Path(
    r"C:\Users\haufa\Downloads\Annotationen"
)

OUTPUT_FILE = ANNOTATION_ROOT / "kon_ukl_auswertung.csv"

ARGUMENTATIVE_FKT = {"ZTH", "TH1", "TH2", "PRO", "CON"}


# ==========================================
# CSV EINLESEN
# ==========================================

def safe_read_csv_rows(file_path):
    """Liest pipe-separierte CSV-Dateien mit mehreren Encodings."""

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    last_error = None

    for encoding in encodings:
        try:
            with open(
                file_path,
                "r",
                encoding=encoding,
                newline=""
            ) as f:
                reader = csv.reader(f, delimiter="|")
                return list(reader)

        except (UnicodeError, OSError) as e:
            last_error = e

    raise last_error


# ==========================================
# CSV ANALYSIEREN
# ==========================================

def analyze_csv(csv_path):
    """Prüft KON und argumentative Funktionen einer CSV-Datei."""

    rows = safe_read_csv_rows(csv_path)

    if len(rows) < 2:
        raise ValueError("Header oder Metadatenzeile fehlt")

    header = [
        column.strip().lstrip("\ufeff")
        for column in rows[0]
    ]

    if "KON" not in header or "FKT" not in header:
        raise ValueError("Spalte KON oder FKT fehlt")

    idx_kon = header.index("KON")
    idx_fkt = header.index("FKT")

    # KON steht in der zweiten Zeile (Metadaten).
    metadata = rows[1]
    kon = metadata[idx_kon].strip() if idx_kon < len(metadata) else ""

    # Nur leere KON-Werte oder UKL berücksichtigen.
    if kon not in {"", "UKL"}:
        return None

    # Argumentative Funktionen aus den Segmentzeilen.
    segment_rows = rows[2:]

    fkt_counter = Counter()

    for row in segment_rows:
        if idx_fkt >= len(row):
            continue

        fkt = row[idx_fkt].strip()

        if fkt in ARGUMENTATIVE_FKT:
            fkt_counter[fkt] += 1

    found_fkt = sorted(fkt_counter.keys())

    return {
        "Dateiname": csv_path.name,
        "Pfad": str(csv_path),
        "KON": kon if kon else "LEER",
        "Argumentative_FKT": "JA" if found_fkt else "NEIN",
        "FKT_Typen": ", ".join(found_fkt),
        "ZTH": fkt_counter["ZTH"],
        "TH1": fkt_counter["TH1"],
        "TH2": fkt_counter["TH2"],
        "PRO": fkt_counter["PRO"],
        "CON": fkt_counter["CON"],
        "Argumentative_Segmente": sum(fkt_counter.values())
    }


# ==========================================
# ALLE ORDNER DURCHSUCHEN
# ==========================================

def main():

    if not ANNOTATION_ROOT.is_dir():
        print(f"Ordner nicht gefunden: {ANNOTATION_ROOT}")
        return

    results = []
    errors = []
    checked_files = 0

    # Rekursiv alle annotated-Ordner finden.
    annotated_folders = sorted(
        folder
        for folder in ANNOTATION_ROOT.rglob("annotated")
        if folder.is_dir()
    )

    print(f"Gefundene annotated-Ordner: {len(annotated_folders)}")

    for folder in annotated_folders:

        for csv_path in sorted(folder.iterdir()):

            if not csv_path.is_file() or csv_path.suffix.lower() != ".csv":
                continue

            checked_files += 1

            try:
                result = analyze_csv(csv_path)

                if result is not None:
                    results.append(result)

                    print(
                        f"{result['KON']:5} | "
                        f"FKT: {result['Argumentative_FKT']:4} | "
                        f"{csv_path.name}"
                    )

            except (OSError, ValueError, csv.Error) as e:
                errors.append((str(csv_path), str(e)))
                print(f"FEHLER: {csv_path} - {e}")

    # ==========================================
    # ERGEBNIS SPEICHERN
    # ==========================================

    columns = [
        "Dateiname",
        "Pfad",
        "KON",
        "Argumentative_FKT",
        "FKT_Typen",
        "ZTH",
        "TH1",
        "TH2",
        "PRO",
        "CON",
        "Argumentative_Segmente"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columns,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(results)

    # ==========================================
    # ZUSAMMENFASSUNG
    # ==========================================

    print("\n" + "=" * 60)
    print("AUSWERTUNG ABGESCHLOSSEN")
    print("=" * 60)

    print(f"Geprüfte CSV-Dateien: {checked_files}")
    print(f"Dateien mit KON leer oder UKL: {len(results)}")

    print(
        "Davon mit argumentativer FKT: "
        f"{sum(r['Argumentative_FKT'] == 'JA' for r in results)}"
    )

    print(
        "Davon ohne argumentative FKT: "
        f"{sum(r['Argumentative_FKT'] == 'NEIN' for r in results)}"
    )

    print(f"Nicht auswertbare Dateien: {len(errors)}")
    print(f"\nErgebnisdatei: {OUTPUT_FILE}")

    if errors:
        print("\nFehlerhafte Dateien:")
        for path, message in errors:
            print(f"  {path}: {message}")


if __name__ == "__main__":
    main()
