# ==========================================
# File: read_all_csv.py
# Author: Dietmar Benndorf
# Date: 2026-11-18
# Description:
#   Recursively analyze pipe-delimited annotation CSV files.
#   Preserves the original summary fields and adds counts, averages,
#   relation statistics, and distribution by text section.
# ==========================================

import csv
import re
import statistics
import sys
from collections import Counter
from pathlib import Path


NON_DISC_VALUES = {"AHG", "WHG", "GLD", "SON"}
DISC_VALUES = {"ZTH", "TH1", "TH2", "PRO", "CON"}
STRUCTURE_PARTS = {"EIN", "HAU", "SCH"}
RELATION_TYPES = ("SUP", "ATT", "ELA", "RES")
FUNCTION_TYPES = ("ZTH", "TH1", "TH2", "AHG", "WHG", "GLD", "SON")

# Output columns grouped by content rather than by implementation history.
# Naming convention:
#   *_count = absolute number (including word counts)
#   *_ratio = proportion or ratio between counts
#   *_relative = relative share of words
#   *_avg / *_median / *_max = descriptive statistics
METADATA_FIELDS = ["ID", "THE", "KON", "first_thesis"]
TEXT_FIELDS = [
    "segments_count", "total_words_count",
    "segment_avg_words", "segment_words_median", "segment_words_min", "segment_words_max",
]
FUNCTION_FIELDS = [
    "disc_count", "non_disc_count", "disc_ratio", "non_disc_ratio",
    "ZTH_count", "TH1_count", "TH2_count", "PRO_count", "CON_count",
    "AHG_count", "WHG_count", "GLD_count", "SON_count", "ADD_J_count",
    "PRO_CON_ratio", "PRO_CON_balance", "PRO_CON_words_balance",
    "PRO_CON_switch_count", "PRO_CON_switch_ratio",
    "TH1_TH2_words_ratio", "PRO_avg_words", "CON_avg_words",
    "PRO_words_relative", "CON_words_relative",
]
RELATION_FIELDS = [
    *(f"{rel}_count" for rel in RELATION_TYPES),
    *(f"{rel}_ratio" for rel in RELATION_TYPES),
    *(f"{rel}_{fkt}_count" for rel in RELATION_TYPES
      for fkt in ("PRO", "CON", "TH1", "TH2", "ZTH")
      if not (rel in ("SUP", "ATT") and fkt == "ZTH")),
]
SECTION_FIELDS = ["structure_complete"] + [
    field
    for section in ("EIN", "HAU", "SCH")
    for field in (
        f"{section}_segments_count", f"{section}_words_count",
        f"{section}_words_relative",
        f"PRO_{section}_count", f"CON_{section}_count", f"ZTH_{section}_count",
    )
]
MAIN_ARGUMENT_FIELDS = [
    "main_arguments_count", "main_arguments_PRO_count", "main_arguments_CON_count",
    "main_PRO_ratio", "main_CON_ratio", "main_arg_balance",
    "complex_main_arg_ratio", "branching_avg", "branching_max",
]
DEPTH_FIELDS = [
    *(f"{prefix}depth_{metric}" for prefix in ("", "PRO_", "CON_")
      for metric in ("avg", "median", "max")),
    "PRO_depth_CON_depth_difference",
]
DENSITY_FIELDS = [
    *(f"{prefix}density_{metric}" for prefix in ("", "PRO_", "CON_")
      for metric in ("avg", "median", "max")),
    "PRO_density_CON_density_difference",
]
IN_DEGREE_FIELDS = [
    f"{prefix}argument_in_degree_{metric}"
    for prefix in ("", "PRO_", "CON_")
    for metric in ("avg", "median", "max")
]
STRUCTURE_FIELDS = MAIN_ARGUMENT_FIELDS + DEPTH_FIELDS + DENSITY_FIELDS
SUPPORT_FIELDS = [
    "support_simple_count", "support_joint_count",
    "support_multiple_count", "support_serial_count",
]
FIELDNAMES = (METADATA_FIELDS + TEXT_FIELDS + FUNCTION_FIELDS +
              RELATION_FIELDS + SECTION_FIELDS + STRUCTURE_FIELDS +
              IN_DEGREE_FIELDS + SUPPORT_FIELDS)


def safe_read_csv_rows(file_path):
    """Read a pipe-separated CSV; fall back to common Windows encodings."""
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            with open(file_path, "r", encoding=encoding, newline="") as handle:
                return list(csv.reader(handle, delimiter="|"))
        except (UnicodeError, OSError, csv.Error) as exc:
            last_error = exc
    raise last_error


def find_csv_files(input_root):
    """Find CSVs only in directories named 'annotated', at any depth.

    This follows the directory discovery used in check_annotation.py.
    Sibling folders such as 'raw' and 'segmented' are not processed.
    CSV files are read directly from each annotated directory.
    """
    root = Path(input_root)
    if not root.exists():
        raise FileNotFoundError(f"Input path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {root}")

    annotated_folders = [
        folder for folder in (root, *root.rglob("*"))
        if folder.is_dir() and folder.name.lower() == "annotated"
    ]
    annotated_folders.sort(key=lambda folder: str(folder).lower())

    csv_files = []
    for annotated_folder in annotated_folders:
        csv_files.extend(
            path for path in annotated_folder.iterdir()
            if path.is_file() and path.suffix.lower() == ".csv"
        )

    return sorted(csv_files, key=lambda path: str(path).lower())


def get_cell_value(row, index):
    if index is None or index >= len(row):
        return ""
    return row[index].strip()


def count_words(text):
    """Whitespace-delimited word count, matching the original program."""
    return len(text.split())


def format_ratio(value):
    return round(value, 2)


def safe_ratio(numerator, denominator):
    return format_ratio(numerator / denominator) if denominator else 0


def balance_index(a, b):
    """1 = perfectly balanced; 0 = only one side; NA when both absent."""
    return format_ratio(1 - abs(a - b) / (a + b)) if a + b else "NA"


def create_empty_result(csv_path):
    result = {field: 0 for field in FIELDNAMES}
    result.update({"ID": Path(csv_path).stem, "THE": "", "KON": "", "PRO_CON_ratio": "", "TH1_TH2_words_ratio": "NA", "PRO_CON_balance": "NA", "PRO_CON_words_balance": "NA"})
    result.update({field: "NA" for field in STRUCTURE_FIELDS})
    result["first_thesis"] = "NA"
    result.update({field: "NA" for field in IN_DEGREE_FIELDS})
    result["PRO_CON_switch_ratio"] = "NA"
    return result


def parse_zie_targets(zie_value):
    """Read target segment numbers using check_annotation.py's ZIE formats.

    Examples: 3, 3;4, 3-4, [1] 3, [1;2] 3;4.
    For bracketed combinations, only numbers AFTER ] are targets.
    An invalid/missing value yields no edges.
    """
    value = zie_value.strip()
    if not value:
        return []
    if re.fullmatch(r"\d+(?:;\d+)*", value):
        return [int(num) for num in value.split(";")]
    match = re.fullmatch(r"(\d+)-(\d+)", value)
    if match:
        return [int(match.group(1)), int(match.group(2))]
    match = re.fullmatch(r"\[(?:\d+)(?:;\d+)*\]\s+(\d+(?:;\d+)*)", value)
    if match:
        return [int(num) for num in match.group(1).split(";")]
    return []



def parse_zie_combination(zie_value):
    """Parse '[2] 1' as partners=(2,), targets=(1,).

    These partner IDs are NOT additional targets. A source row with Nr.=3
    and ZIE='[2] 1' describes the joint-support group {2,3} -> 1.
    """
    match = re.fullmatch(r"\[(\d+(?:;\d+)*)\]\s+(\d+(?:;\d+)*)", zie_value.strip())
    if not match:
        return None
    partners = tuple(int(n) for n in match.group(1).split(";"))
    targets = tuple(int(n) for n in match.group(2).split(";"))
    return partners, targets


def calculate_support_patterns(records):
    """Count patterns in the SUP subgraph of PRO/CON argument segments.

    SIMPLE: isolated directed SUP connection between two argument nodes,
      not part of a joint group, multiple support, or serial chain.
    JOINT: distinct (group of participants, target) from bracketed ZIE syntax.
    MULTIPLE: one target supported independently by >=2 source arguments.
      Each target counts once, excluding members of any joint-support group.
    SERIAL: distinct two-link paths A -> B -> C with REL=SUP at both links.
      Each distinct ordered triple counts once, without cycles or joint edges.

    Categories may overlap at the level of entire graphs (not individual
    edges); counts are occurrences, not a partition of SUP_count.
    """
    output = {name: 0 for name in (
        "support_simple_count", "support_joint_count",
        "support_multiple_count", "support_serial_count"
    )}
    by_number = {rec["nr"]: rec for rec in records if rec["nr"] is not None}
    arg_ids = {nr for nr, rec in by_number.items() if rec["fkt"] in {"PRO", "CON"}}

    # Derive and deduplicate joint groups, independently of which partner row
    # encodes the combination. A group requires >=2 distinct known arguments.
    joint_groups = set()
    joint_edges = set()
    for rec in records:
        source = rec["nr"]
        if source not in arg_ids or rec["rel"] != "SUP":
            continue
        combination = parse_zie_combination(rec["zie_raw"])
        if combination is None:
            continue
        partners, targets = combination
        members = frozenset({source, *partners})
        if len(members) < 2 or not members.issubset(arg_ids):
            continue
        for target in targets:
            if target in arg_ids and target not in members:
                joint_groups.add((members, target))
                joint_edges.update((member, target) for member in members)
    output["support_joint_count"] = len(joint_groups)

    # Ordinary edges are only unbracketed direct SUP references. A reference
    # to several targets represents separate outgoing edges, not joint support.
    ordinary_edges = set()
    for rec in records:
        source = rec["nr"]
        if source not in arg_ids or rec["rel"] != "SUP":
            continue
        if parse_zie_combination(rec["zie_raw"]) is not None:
            continue
        for target in rec["targets"]:
            if target in arg_ids and source != target:
                ordinary_edges.add((source, target))
    ordinary_edges -= joint_edges

    by_target = {}
    for source, target in ordinary_edges:
        by_target.setdefault(target, set()).add(source)
    multiple_targets = {target for target, sources in by_target.items() if len(sources) >= 2}
    output["support_multiple_count"] = len(multiple_targets)

    # A serial pattern consists of two consecutive distinct SUP links.
    serial_paths = {
        (a, b, c)
        for a, b in ordinary_edges
        for b2, c in ordinary_edges
        if b == b2 and len({a, b, c}) == 3
    }
    output["support_serial_count"] = len(serial_paths)
    serial_edges = {(a, b) for a, b, c in serial_paths} | {
        (b, c) for a, b, c in serial_paths
    }
    output["support_simple_count"] = sum(
        1 for edge in ordinary_edges
        if edge not in serial_edges and edge[1] not in multiple_targets
    )
    return output


def find_first_thesis(records):
    """Compare first numeric segment IDs for TH1 and TH2; otherwise NA."""
    th1 = [r["nr"] for r in records if r["fkt"] == "TH1" and r["nr"] is not None]
    th2 = [r["nr"] for r in records if r["fkt"] == "TH2" and r["nr"] is not None]
    if not th1 or not th2 or min(th1) == min(th2):
        return "NA"
    return "TH1" if min(th1) < min(th2) else "TH2"

def calculate_argument_in_degree(records):
    """Incoming directed relations at PRO/CON argument nodes.

    Each ZIE link points from the referring source segment to its target.
    Only PRO/CON sources and PRO/CON targets are considered; every distinct
    source-target pair counts once, regardless of SUP/ATT/ELA/RES. For joint
    references '[2] 1', the listed partner is also treated as a source of the
    joint relation. Zero incoming links are included in the statistics.
    """
    result = {field: "NA" for field in IN_DEGREE_FIELDS}
    by_number = {r["nr"]: r for r in records if r["nr"] is not None}
    argument_ids = {
        nr for nr, rec in by_number.items() if rec["fkt"] in {"PRO", "CON"}
    }
    if not argument_ids:
        return result

    incoming = {nr: set() for nr in argument_ids}
    for rec in records:
        source = rec["nr"]
        if source not in argument_ids:
            continue
        sources = {source}
        combination = parse_zie_combination(rec["zie_raw"])
        if combination is not None:
            partners, _ = combination
            sources.update(partner for partner in partners if partner in argument_ids)
        for target in rec["targets"]:
            if target in argument_ids:
                incoming[target].update(src for src in sources if src != target)

    for prefix, ids in (
        ("", sorted(argument_ids)),
        ("PRO_", sorted(n for n in argument_ids if by_number[n]["fkt"] == "PRO")),
        ("CON_", sorted(n for n in argument_ids if by_number[n]["fkt"] == "CON")),
    ):
        if not ids:
            continue
        values = [len(incoming[n]) for n in ids]
        result[f"{prefix}argument_in_degree_avg"] = format_ratio(statistics.mean(values))
        result[f"{prefix}argument_in_degree_median"] = format_ratio(statistics.median(values))
        result[f"{prefix}argument_in_degree_max"] = max(values)
    return result


def calculate_argument_structure(segment_records, kon):
    """Compute direct main arguments, root-to-leaf depths and branch sizes.

    Depth: number of argument nodes in a root-to-leaf path, starting at 1.
    Density: count of DISTINCT PRO/CON nodes reachable below a main argument,
    including the root. Branches with shared nodes are counted separately per
    main argument, not multiple times inside the same branch.
    PRO/CON classification follows the root/main argument, even if a deeper
    node uses the other FKT label. Cycles are cut off at the first repeated node.
    """
    result = {field: "NA" for field in STRUCTURE_FIELDS}
    by_number = {r["nr"]: r for r in segment_records if r["nr"] is not None}
    children = {nr: set() for nr in by_number}
    for record in segment_records:
        source = record["nr"]
        if source is None or source not in by_number:
            continue
        for target in record["targets"]:
            if target in by_number and target != source:
                children[target].add(source)  # ZIE points from child to parent

    # For unilateral argumentation (KON EIN), the central thesis is the anchor.
    # Otherwise main arguments directly target TH1 or TH2.
    anchor_types = {"ZTH"} if kon == "EIN" else {"TH1", "TH2"}
    anchor_numbers = {
        nr for nr, rec in by_number.items() if rec["fkt"] in anchor_types
    }
    main_arguments = sorted({
        node for anchor in anchor_numbers for node in children[anchor]
        if by_number[node]["fkt"] in {"PRO", "CON"}
    })
    # Branching counts direct PRO/CON children of each PRO/CON node.
    # Include leaf arguments (zero children); distinct segment IDs count once.
    arg_ids = [nr for nr, rec in by_number.items() if rec["fkt"] in {"PRO", "CON"}]
    if arg_ids:
        branching = [sum(by_number[c]["fkt"] in {"PRO", "CON"}
                         for c in children[nr]) for nr in arg_ids]
        result["branching_avg"] = format_ratio(statistics.mean(branching))
        result["branching_max"] = max(branching)
    if not main_arguments:
        return result

    pro_roots = [nr for nr in main_arguments if by_number[nr]["fkt"] == "PRO"]
    con_roots = [nr for nr in main_arguments if by_number[nr]["fkt"] == "CON"]
    result["main_arguments_count"] = len(main_arguments)
    result["main_arguments_PRO_count"] = len(pro_roots)
    result["main_arguments_CON_count"] = len(con_roots)
    result["main_arg_balance"] = balance_index(len(pro_roots), len(con_roots))
    # A complex main argument receives at least one direct SUP/ATT child.
    complex_roots = sum(any(
        by_number[child]["fkt"] in {"PRO", "CON"}
        and by_number[child]["rel"] in {"SUP", "ATT"}
        for child in children[root]
    ) for root in main_arguments)
    result["complex_main_arg_ratio"] = safe_ratio(complex_roots, len(main_arguments))
    result["main_PRO_ratio"] = safe_ratio(len(pro_roots), len(main_arguments))
    result["main_CON_ratio"] = safe_ratio(len(con_roots), len(main_arguments))

    def argument_children(number):
        return sorted(n for n in children.get(number, ())
                      if by_number[n]["fkt"] in {"PRO", "CON"})

    def leaf_depths(number, visited):
        next_nodes = [n for n in argument_children(number) if n not in visited]
        if not next_nodes:
            return [1]
        return [1 + depth for child in next_nodes
                for depth in leaf_depths(child, visited | {child})]

    def branch_density(root):
        visited = set()
        pending = [root]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(argument_children(current))
        return len(visited)

    for prefix, roots in (("", main_arguments), ("PRO_", pro_roots), ("CON_", con_roots)):
        if not roots:
            continue  # No corresponding argument structures: NA.
        depths = [depth for root in roots for depth in leaf_depths(root, {root})]
        densities = [branch_density(root) for root in roots]
        for name, values in (("depth", depths), ("density", densities)):
            result[f"{prefix}{name}_avg"] = format_ratio(statistics.mean(values))
            result[f"{prefix}{name}_median"] = format_ratio(statistics.median(values))
            result[f"{prefix}{name}_max"] = max(values)
    if pro_roots and con_roots:
        result["PRO_depth_CON_depth_difference"] = format_ratio(
            result["PRO_depth_avg"] - result["CON_depth_avg"])
        result["PRO_density_CON_density_difference"] = format_ratio(
            result["PRO_density_avg"] - result["CON_density_avg"])
    return result


def analyze_csv_file(csv_path):
    rows = safe_read_csv_rows(csv_path)
    result = create_empty_result(csv_path)
    if not rows:
        raise ValueError("Empty CSV file")

    header = [cell.strip().lstrip("\ufeff") for cell in rows[0]]
    indices = {name: header.index(name) if name in header else None
               for name in ("Nr.", "Text", "FKT", "AUF", "ADD", "REL", "ZIE", "THE", "KON")}
    if indices["Text"] is None or indices["FKT"] is None or indices["AUF"] is None:
        raise ValueError("Required columns missing: Text, FKT and/or AUF")

    if len(rows) >= 2:
        result["THE"] = get_cell_value(rows[1], indices["THE"])
        result["KON"] = get_cell_value(rows[1], indices["KON"])

    function_counts = Counter()
    section_counts = Counter()
    section_word_counts = Counter()
    function_word_counts = Counter()
    relation_counts = Counter()
    position_counts = Counter()
    segment_records = []
    segment_word_lengths = []
    argument_sequence = []

    # Row 0 = header; row 1 = metadata; row 2 onward = segments.
    for row in rows[2:]:
        if not any(cell.strip() for cell in row):
            continue  # Ignore completely empty lines, not genuine segments.

        text = get_cell_value(row, indices["Text"])
        fkt = get_cell_value(row, indices["FKT"]).upper()
        auf = get_cell_value(row, indices["AUF"]).upper()
        add = get_cell_value(row, indices["ADD"]).upper()
        rel = get_cell_value(row, indices["REL"]).upper()
        words = count_words(text)
        if words:
            segment_word_lengths.append(words)
        if fkt in {"PRO", "CON"}:
            argument_sequence.append(fkt)
        nr_text = get_cell_value(row, indices["Nr."])
        try:
            nr = int(nr_text)
        except ValueError:
            nr = None
        segment_records.append({
            "nr": nr, "fkt": fkt, "rel": rel,
            "zie_raw": get_cell_value(row, indices["ZIE"]),
            "targets": parse_zie_targets(get_cell_value(row, indices["ZIE"])),
        })

        result["segments_count"] += 1
        result["total_words_count"] += words
        function_counts[fkt] += 1
        function_word_counts[fkt] += words
        if auf in STRUCTURE_PARTS:
            section_counts[auf] += 1
            section_word_counts[auf] += words
            if fkt in {"PRO", "CON", "ZTH"}:
                position_counts[(fkt, auf)] += 1
        if add == "J":
            result["ADD_J_count"] += 1
        if rel in RELATION_TYPES:
            relation_counts[rel] += 1
        if (rel in RELATION_TYPES and fkt in {"PRO", "CON", "TH1", "TH2", "ZTH"}
                and not (rel in {"SUP", "ATT"} and fkt == "ZTH")):
            result[f"{rel}_{fkt}_count"] += 1

    segments = result["segments_count"]
    disc_count = sum(function_counts[fkt] for fkt in DISC_VALUES)
    non_disc_count = sum(function_counts[fkt] for fkt in NON_DISC_VALUES)
    result["disc_count"] = disc_count
    result["non_disc_count"] = non_disc_count
    result["disc_ratio"] = safe_ratio(disc_count, segments)
    result["non_disc_ratio"] = safe_ratio(non_disc_count, segments)

    for fkt in FUNCTION_TYPES:
        result[f"{fkt}_count"] = function_counts[fkt]

    pro_count = function_counts["PRO"]
    con_count = function_counts["CON"]
    pro_words = function_word_counts["PRO"]
    con_words = function_word_counts["CON"]
    pro_con_words = pro_words + con_words

    result["segment_avg_words"] = safe_ratio(result["total_words_count"], segments)
    if segment_word_lengths:
        result["segment_words_median"] = format_ratio(statistics.median(segment_word_lengths))
        result["segment_words_min"] = min(segment_word_lengths)
        result["segment_words_max"] = max(segment_word_lengths)
    # Compare adjacent PRO/CON segments; other FKT labels are skipped.
    result["PRO_CON_switch_count"] = sum(
        left != right for left, right in zip(argument_sequence, argument_sequence[1:])
    )
    result["PRO_CON_switch_ratio"] = (
        safe_ratio(result["PRO_CON_switch_count"], len(argument_sequence) - 1)
        if len(argument_sequence) >= 2 else "NA"
    )
    result["PRO_CON_balance"] = balance_index(pro_count, con_count)
    result["PRO_CON_words_balance"] = balance_index(pro_words, con_words)
    th1_words, th2_words = function_word_counts["TH1"], function_word_counts["TH2"]
    result["TH1_TH2_words_ratio"] = safe_ratio(th1_words, th2_words) if th2_words else "NA"
    result["PRO_count"] = pro_count
    result["CON_count"] = con_count
    result["PRO_words_relative"] = safe_ratio(pro_words, pro_con_words)
    result["CON_words_relative"] = safe_ratio(con_words, pro_con_words)
    result["PRO_avg_words"] = safe_ratio(pro_words, pro_count)
    result["CON_avg_words"] = safe_ratio(con_words, con_count)
    # Undefined when there are no CON segments; leave blank instead of reporting 0.
    result["PRO_CON_ratio"] = safe_ratio(pro_count, con_count) if con_count else ""

    relation_total = sum(relation_counts[rel] for rel in RELATION_TYPES)
    for rel in RELATION_TYPES:
        result[f"{rel}_count"] = relation_counts[rel]
        result[f"{rel}_ratio"] = safe_ratio(relation_counts[rel], relation_total)

    structure_words_total = sum(section_word_counts[auf] for auf in STRUCTURE_PARTS)
    result["structure_complete"] = int(all(section_counts[auf] > 0 for auf in STRUCTURE_PARTS))
    for auf in ("EIN", "HAU", "SCH"):
        result[f"{auf}_segments_count"] = section_counts[auf]
        result[f"{auf}_words_count"] = section_word_counts[auf]
        result[f"{auf}_words_relative"] = safe_ratio(section_word_counts[auf], structure_words_total)
        for fkt in ("PRO", "CON", "ZTH"):
            result[f"{fkt}_{auf}_count"] = position_counts[(fkt, auf)]

    result.update(calculate_argument_structure(segment_records, result["KON"].upper()))
    result.update(calculate_argument_in_degree(segment_records))
    result["first_thesis"] = find_first_thesis(segment_records)
    result.update(calculate_support_patterns(segment_records))
    return result


def print_progress_bar(current, total, bar_length=40):
    fraction = current / total if total else 1
    filled = int(bar_length * fraction)
    sys.stdout.write(f"\r[{'#' * filled}{'-' * (bar_length - filled)}] {current}/{total} {fraction * 100:.1f}%")
    sys.stdout.flush()
    if current == total:
        print()


def write_result_csv(results, output_file):
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="|")
        writer.writeheader()
        writer.writerows(results)


def process_all_csv_files(input_root, output_file):
    output_path = Path(output_file).resolve()
    csv_files = [path for path in find_csv_files(input_root)
                 if path.resolve() != output_path]
    results = []
    print(f"CSV files found in annotated folders: {len(csv_files)}")
    print_progress_bar(0, len(csv_files))
    for index, csv_path in enumerate(csv_files, start=1):
        try:
            results.append(analyze_csv_file(csv_path))
        except Exception as exc:
            # Preserve a row for every unreadable file, as in the original script.
            results.append(create_empty_result(csv_path))
            print(f"\nCould not process CSV: {csv_path}\nError: {exc}")
        print_progress_bar(index, len(csv_files))
    write_result_csv(results, output_file)
    return results


def main():
    input_root = r"C:\Users\haufa\Downloads\Annotationen"
    output_file = r"C:\Users\haufa\Downloads\csv_segment_summary.csv"
    results = process_all_csv_files(input_root, output_file)
    print("\nCSV analysis completed.")
    print(f"Number of CSV files analyzed: {len(results)}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
