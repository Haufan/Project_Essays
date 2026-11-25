from pathlib import Path


def read_file(input_file: Path):
    """Liest eine Datei und probiert typische Encodings aus."""

    encodings = ["utf-8-sig", "cp1252", "latin-1"]

    for encoding in encodings:
        try:
            with input_file.open("r", encoding=encoding, newline="") as infile:
                return infile.readlines(), encoding

        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Datei konnte mit keinem unterstützten Encoding gelesen werden: {input_file}"
    )


def convert_file(input_file: Path, output_file: Path):
    """Entfernt äußere Anführungszeichen aus jeder Zeile."""

    lines, encoding = read_file(input_file)

    print(f"Encoding: {encoding} | Datei: {input_file.name}")

    converted_lines = []

    for line in lines:
        # Zeilenende separat behandeln
        if line.endswith("\r\n"):
            content = line[:-2]
            newline = "\r\n"

        elif line.endswith("\n"):
            content = line[:-1]
            newline = "\n"

        else:
            content = line
            newline = ""

        # Äußere Anführungszeichen entfernen
        if (
            len(content) >= 2
            and content.startswith('"')
            and content.endswith('"')
        ):
            content = content[1:-1]

        converted_lines.append(content + newline)

    # Ausgabe bewusst als UTF-8 speichern
    with output_file.open("w", encoding="utf-8", newline="") as outfile:
        outfile.writelines(converted_lines)


def main():
    input_folder = Path(
        r"C:\Users\haufa\Downloads\C 551-600+\C 551-600+\annotated"
    )

    output_folder = input_folder / "converted"
    output_folder.mkdir(exist_ok=True)

    for input_file in input_folder.glob("*.csv"):
        output_file = output_folder / input_file.name

        convert_file(input_file, output_file)

        print(f"Konvertiert: {input_file.name}")

    print()
    print("Fertig.")
    print(f"Ausgabeordner: {output_folder}")


if __name__ == "__main__":
    main()