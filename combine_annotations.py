# File: collect_all_texts.py
# Author: Dietmar Benndorf
# Date: 2026-05-13
# Description:
#    Collects files from multiple annotation group folders into one folder
#    named alle_texte.
#
#    If a file name occurs more than once inside the same target subfolder
#    raw, segmented, or annotated, the program raises an error and reports
#    both the original file and the duplicate file.
# ==========================================

from pathlib import Path
import shutil


REQUIRED_SUBFOLDERS = ["raw", "segmented", "annotated"]


def find_data_groups(root_path):
    """
    Returns all direct subfolders of root_path except alle_texte.
    """
    subfolders = [
        p for p in root_path.iterdir()
        if p.is_dir() and p.name != "alle_texte"
    ]

    return sorted(subfolders, key=lambda p: p.name)


def copy_files_from_subfolder(source_subfolder, target_subfolder, seen_files, subfolder_name):
    """
    Copies all files from one source subfolder into the corresponding
    target subfolder.

    If a file name already occurred in the same target subfolder,
    a ValueError is raised.

    Only direct files are copied. Nested folders are ignored.
    """
    copied_files = []

    if not source_subfolder.is_dir():
        return copied_files

    for source_file in sorted(source_subfolder.iterdir(), key=lambda p: p.name):
        if not source_file.is_file():
            continue

        file_name = source_file.name

        if file_name in seen_files[subfolder_name]:
            first_file = seen_files[subfolder_name][file_name]

            raise ValueError(
                "Duplicate file detected\n"
                f"Subfolder: {subfolder_name}\n"
                f"File name: {file_name}\n"
                f"First occurrence: {first_file}\n"
                f"Duplicate occurrence: {source_file}"
            )

        seen_files[subfolder_name][file_name] = source_file

        target_file = target_subfolder / file_name
        shutil.copy2(source_file, target_file)
        copied_files.append((source_file, target_file))

    return copied_files


def collect_all_texts(input_root, output_folder_name="alle_texte"):
    """
    Creates:
        input_root / alle_texte / raw
        input_root / alle_texte / segmented
        input_root / alle_texte / annotated

    Then copies all files from the group folders into the corresponding
    target folders.

    Duplicate file names inside the same target subfolder cause an error.
    """
    root_path = Path(input_root)

    if not root_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {root_path}")

    output_root = root_path / output_folder_name

    for subfolder_name in REQUIRED_SUBFOLDERS:
        target_subfolder = output_root / subfolder_name
        target_subfolder.mkdir(parents=True, exist_ok=True)

    seen_files = {
        "raw": {},
        "segmented": {},
        "annotated": {},
    }

    parent_folders = find_data_groups(root_path)

    if not parent_folders:
        print(f"No source folders found in: {root_path}")
        return []

    all_copied_files = []

    for parent_folder in parent_folders:
        print(f"Processing folder: {parent_folder}")

        for subfolder_name in REQUIRED_SUBFOLDERS:
            source_subfolder = parent_folder / subfolder_name
            target_subfolder = output_root / subfolder_name

            if not source_subfolder.is_dir():
                print(f"  Warning: missing subfolder: {source_subfolder}")
                continue

            copied_files = copy_files_from_subfolder(
                source_subfolder=source_subfolder,
                target_subfolder=target_subfolder,
                seen_files=seen_files,
                subfolder_name=subfolder_name
            )

            all_copied_files.extend(copied_files)

            print(f"  {subfolder_name}: copied {len(copied_files)} file(s)")

    return all_copied_files


def main():
    input_root = r"C:\Users\haufa\Downloads\Annotationen\Annotationen"

    try:
        copied_files = collect_all_texts(input_root)

        print()
        print("Collection completed.")
        print(f"Number of copied files: {len(copied_files)}")
        print(f"Target folder: {Path(input_root) / 'alle_texte'}")

    except Exception as e:
        print()
        print("ERROR:")
        print(e)


if __name__ == "__main__":
    main()