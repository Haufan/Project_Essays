# ==========================================
# File: temp_visualisation_csv_to_tree.py
# Author: Dietmar Benndorf
# Date: 2026-06-10
# Description:
#    Reads annotated CSV files from one input folder and creates graphical
#    tree structures of the argumentative relations between the segments.
#
#    The program uses the columns Nr, Text, FKT, REL, and ZIE to build a
#    directed graph. Argumentative segments are shown as nodes, and relations
#    such as support, attack, restatement, and elaboration are shown as edges.
#
#    Special ZIE formats such as multiple targets, joint support, and
#    connection targets are supported. The generated graph images are saved
#    as PNG files in an Output folder.
#
#    The option SHOW_TEXT controls whether the segment text is displayed
#    inside the graph nodes:
#    - 0 = show only segment number and FKT
#    - 1 = show segment number, FKT, and segment text
# ==========================================

from pathlib import Path
import csv
import textwrap
import re

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


ARGUMENTATIVE_FKT = {
    "ZTH", "TH1", "TH2", "PRO", "CON",
    "ZENTRALE THESE", "THESE1", "THESE2",
    "PRO ARGUMENT", "CON ARGUMENT"
}

RELATION_LABELS = {
    "SUP": "support",
    "ATT": "attack",
    "RES": "restatement",
    "ELA": "elaboration",
    "NO": "",
    "REL": "relation"
}


def read_text_with_fallback(csv_path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    for encoding in encodings:
        try:
            return csv_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Keine passende Codierung gefunden für {csv_path}"
    )


def detect_separator(csv_path: Path) -> str:
    sample = read_text_with_fallback(csv_path)[:4096]

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter
    except csv.Error:
        return ";"


def read_csv_with_fallback(csv_path: Path, sep: str) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                csv_path,
                sep=sep,
                encoding=encoding,
                dtype=str
            )
        except UnicodeDecodeError as error:
            last_error = error

    raise last_error


def clean_column_name(column: str) -> str:
    column = str(column)
    column = column.replace("\ufeff", "")
    column = column.strip()
    column = column.lower()

    normalized = (
        column
        .replace(" ", "")
        .replace("-", "_")
        .replace(".", "")
    )

    replacements = {
        "nr": "Nr",
        "nummer": "Nr",
        "segment": "Nr",
        "segmentnr": "Nr",
        "segment_nr": "Nr",
        "id": "Nr",

        "text": "Text",
        "segmenttext": "Text",
        "segment_text": "Text",
        "satz": "Text",

        "fkt": "FKT",
        "funktion": "FKT",
        "textfunktion": "FKT",
        "zone": "FKT",
        "kategorie": "FKT",

        "rel": "REL",
        "relation": "REL",
        "beziehung": "REL",

        "zie": "ZIE",
        "ziel": "ZIE",
        "target": "ZIE",
        "zielsegment": "ZIE",
        "ziel_segment": "ZIE",
    }

    return replacements.get(normalized, column)


def normalize(value: str) -> str:
    return str(value).strip().upper()


def is_argumentative(fkt: str) -> bool:
    return normalize(fkt) in ARGUMENTATIVE_FKT


def load_csv(csv_path: Path) -> pd.DataFrame:
    sep = detect_separator(csv_path)
    df = read_csv_with_fallback(csv_path, sep)

    df.columns = [clean_column_name(c) for c in df.columns]

    print(f"Spalten in {csv_path.name}: {list(df.columns)}")
    print(f"Erkanntes Trennzeichen: {repr(sep)}")

    if "Nr" not in df.columns:
        df.insert(0, "Nr", [str(i) for i in range(len(df))])
        print(f"Hinweis: In {csv_path.name} wurde die Spalte 'Nr' automatisch erzeugt.")

    required_columns = {"Nr", "Text", "FKT", "REL", "ZIE"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Fehlende Spalten in {csv_path.name}: {', '.join(sorted(missing))}. "
            f"Vorhandene Spalten: {', '.join(map(str, df.columns))}"
        )

    for col in required_columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df.replace({"nan": "", "NaN": "", "NAN": ""})

    return df


def make_node_label(row: pd.Series, max_width: int = 34, show_text: bool = True) -> str:
    """
    Erstellt die Beschriftung eines Segmentknotens.

    show_text = True:
        Nr., FKT und Segmenttext werden angezeigt.
    show_text = False:
        Nur Nr. und FKT werden angezeigt.
    """
    nr = row["Nr"]
    fkt = row["FKT"]

    if not show_text:
        return f"{nr} · {fkt}"

    text = row["Text"]
    wrapped_text = "\n".join(textwrap.wrap(text, width=max_width))
    return f"{nr} · {fkt}\n{wrapped_text}"


def split_segment_list(value: str) -> list[str]:
    value = str(value).strip()

    if not value:
        return []

    return [
        part.strip()
        for part in re.split(r"[;,\s]+", value)
        if part.strip()
    ]


def parse_zie(zie: str) -> list[dict]:
    """
    Erkennt die ZIE-Formen:

    3           einzelnes Ziel
    2-3         Verbindung/Kante als Ziel
    1;3         mehrere Ziele
    [1] 2       gemeinsame Stützung
    [12;13] 10  gemeinsame Stützung mit mehreren Partnern
    """
    zie = str(zie).strip()

    if not zie or zie.upper() == "NAN":
        return []

    # Gemeinsame Stützung: [1] 2 oder [12;13] 10
    joint_match = re.fullmatch(r"\[([^\]]+)\]\s*(.+)", zie)

    if joint_match:
        partners_raw = joint_match.group(1).strip()
        target_raw = joint_match.group(2).strip()

        partners = split_segment_list(partners_raw)

        return [{
            "type": "joint",
            "partners": partners,
            "target": target_raw
        }]

    # Mehrere Ziele: 1;3
    if ";" in zie:
        return [
            {"type": "single", "target": part.strip()}
            for part in zie.split(";")
            if part.strip()
        ]

    # Verbindung als Ziel: 2-3 oder 2 - 3
    relation_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", zie)

    if relation_match:
        left = relation_match.group(1).strip()
        right = relation_match.group(2).strip()

        return [{
            "type": "connection_target",
            "target": f"{left}-{right}",
            "left": left,
            "right": right
        }]

    # Einzelnes Ziel: 3
    return [{"type": "single", "target": zie}]


def add_helper_node(
    graph: nx.DiGraph,
    node_id: str,
    label: str,
    fkt: str,
    text: str = "",
    **attributes
):
    if node_id not in graph.nodes:
        graph.add_node(
            node_id,
            label=label,
            fkt=fkt,
            text=text or label,
            **attributes
        )


def add_edge_if_possible(
    graph: nx.DiGraph,
    source: str,
    target: str,
    rel: str,
    warnings: list[str] | None = None
):
    source = str(source).strip()
    target = str(target).strip()
    rel = normalize(rel)

    if not source or not target:
        return

    if source in graph.nodes and target in graph.nodes:
        graph.add_edge(
            source,
            target,
            rel=rel,
            label=RELATION_LABELS.get(rel, rel.lower())
        )
    else:
        if warnings is not None:
            warnings.append(
                f"Kante übersprungen: {source} --{rel}--> {target} "
                f"(Quelle oder Ziel fehlt im argumentativen Graphen)."
            )


def make_connection_node_id(left: str, right: str) -> str:
    return f"CONNECTION_{left}_{right}"


def create_connection_node(
    graph: nx.DiGraph,
    left: str,
    right: str,
    warnings: list[str] | None = None
) -> str:
    """
    Erstellt einen neuen Knoten in der Verbindung left -> right.

    Falls die direkte Kante left -> right schon existiert, wird sie entfernt
    und durch left -> Verbindungsknoten -> right ersetzt. Die ursprüngliche
    Relationsart wird dabei erhalten.

    Beispiel:
        2 --SUP--> 3

    wird zu:
        2 --SUP--> CONNECTION_2_3 --SUP--> 3

    Ein anderes Segment kann dann z. B. so angreifen:
        5 --ATT--> CONNECTION_2_3
    """
    left = str(left).strip()
    right = str(right).strip()
    connection_id = make_connection_node_id(left, right)

    add_helper_node(
        graph=graph,
        node_id=connection_id,
        label=f"{left}→{right}",
        fkt="CONNECTION",
        text=f"Verbindung {left}-{right}",
        left=left,
        right=right
    )

    if left not in graph.nodes or right not in graph.nodes:
        if warnings is not None:
            warnings.append(
                f"Verbindungsknoten {connection_id} wurde erstellt, "
                f"aber {left} oder {right} fehlt im Graphen."
            )
        return connection_id

    # Falls direkte Kante existiert, diese Kante in zwei Kanten aufteilen.
    if graph.has_edge(left, right):
        original_data = dict(graph.get_edge_data(left, right))
        original_rel = original_data.get("rel", "REL")
        original_label = original_data.get(
            "label",
            RELATION_LABELS.get(original_rel, original_rel.lower())
        )

        graph.remove_edge(left, right)

        graph.add_edge(
            left,
            connection_id,
            rel=original_rel,
            label=original_label
        )
        graph.add_edge(
            connection_id,
            right,
            rel=original_rel,
            label=original_label
        )
    else:
        # Falls die Verbindung noch nicht als Kante existiert,
        # wird sie trotzdem sichtbar gemacht.
        graph.add_edge(
            left,
            connection_id,
            rel="REL",
            label="relation"
        )
        graph.add_edge(
            connection_id,
            right,
            rel="REL",
            label="relation"
        )

        if warnings is not None:
            warnings.append(
                f"Für ZIE={left}-{right} gab es keine direkte Kante {left}->{right}. "
                f"Eine neutrale Verbindung wurde ergänzt."
            )

    return connection_id


def build_graph(df: pd.DataFrame, only_argumentative: bool = True, show_text: bool = True) -> nx.DiGraph:
    graph = nx.DiGraph()
    warnings = []
    connection_relations = []

    # 1. Normale argumentative Segmentknoten anlegen
    for _, row in df.iterrows():
        nr = row["Nr"]
        fkt = row["FKT"]

        if not nr or nr.upper() == "X":
            continue

        if only_argumentative and not is_argumentative(fkt):
            continue

        graph.add_node(
            nr,
            label=make_node_label(row, show_text=show_text),
            fkt=fkt,
            text=row["Text"]
        )

    # 2. Zuerst normale Ziele und gemeinsame Stützungen eintragen.
    #    Verbindung-als-Ziel wird gespeichert und danach verarbeitet,
    #    damit direkte Kanten vorher existieren können.
    for _, row in df.iterrows():
        source = row["Nr"]
        rel = normalize(row["REL"])
        zie = row["ZIE"]

        if not source or source.upper() == "X":
            continue

        if rel in {"", "NO", "NAN"}:
            continue

        if source not in graph.nodes:
            warnings.append(
                f"Quelle {source} nicht im Graphen, Relation {rel} mit ZIE={zie} übersprungen."
            )
            continue

        parsed_targets = parse_zie(zie)

        if not parsed_targets:
            warnings.append(
                f"Segment {source} hat REL={rel}, aber kein gültiges ZIE."
            )
            continue

        for item in parsed_targets:
            if item["type"] == "single":
                target = item["target"]
                add_edge_if_possible(graph, source, target, rel, warnings)

            elif item["type"] == "joint":
                # Beispiel:
                # Quelle 7, ZIE = [8] 5
                # 7 und 8 stützen gemeinsam 5.
                partners = item["partners"]
                target = item["target"]

                all_sources = [source] + partners
                joint_id = "JOINT_" + "_".join(sorted(all_sources, key=str)) + "_TO_" + target

                add_helper_node(
                    graph=graph,
                    node_id=joint_id,
                    label="gemeinsame\nStützung",
                    fkt="JOINT",
                    text="gemeinsame Stützung"
                )

                add_edge_if_possible(graph, source, joint_id, rel, warnings)

                for partner in partners:
                    add_edge_if_possible(graph, partner, joint_id, rel, warnings)

                add_edge_if_possible(graph, joint_id, target, "SUP", warnings)

            elif item["type"] == "connection_target":
                # Wird später verarbeitet.
                connection_relations.append({
                    "source": source,
                    "rel": rel,
                    "left": item["left"],
                    "right": item["right"],
                    "zie": zie
                })

    # 3. Jetzt Verbindungsknoten für Ziele wie 2-3 erzeugen
    #    und die Quellsegmente darauf zeigen lassen.
    for item in connection_relations:
        source = item["source"]
        rel = item["rel"]
        left = item["left"]
        right = item["right"]

        connection_id = create_connection_node(
            graph=graph,
            left=left,
            right=right,
            warnings=warnings
        )

        add_edge_if_possible(graph, source, connection_id, rel, warnings)

    if warnings:
        print("\nWarnungen beim Graphaufbau:")
        for warning in warnings:
            print(f"- {warning}")
        print()

    return graph


def hierarchy_layout(graph: nx.DiGraph):
    if len(graph.nodes) == 0:
        return {}

    roots = [
        node for node in graph.nodes
        if graph.out_degree(node) == 0
    ]

    if not roots:
        return nx.spring_layout(graph, seed=42, k=1.2)

    reversed_graph = graph.reverse(copy=True)

    levels = {}
    queue = [(root, 0) for root in roots]
    visited = set()

    while queue:
        node, level = queue.pop(0)

        if node in visited:
            continue

        visited.add(node)
        levels.setdefault(level, []).append(node)

        for child in reversed_graph.successors(node):
            queue.append((child, level + 1))

    unvisited = [
        node for node in graph.nodes
        if node not in visited
    ]

    if unvisited:
        max_level = max(levels.keys(), default=0) + 1
        levels.setdefault(max_level, []).extend(unvisited)

    pos = {}

    for level, nodes in levels.items():
        count = len(nodes)

        for index, node in enumerate(nodes):
            x = index - (count - 1) / 2
            y = -level
            pos[node] = (x, y)

    return pos


def improve_connection_node_positions(graph: nx.DiGraph, pos: dict) -> dict:
    """
    Setzt CONNECTION-Knoten näher in die Mitte zwischen left und right.
    Dadurch wirkt der Knoten tatsächlich wie ein Knoten in der Verbindung.
    """
    pos = dict(pos)

    for node, data in graph.nodes(data=True):
        if data.get("fkt") != "CONNECTION":
            continue

        left = str(data.get("left", "")).strip()
        right = str(data.get("right", "")).strip()

        if left in pos and right in pos:
            x1, y1 = pos[left]
            x2, y2 = pos[right]

            pos[node] = ((x1 + x2) / 2, (y1 + y2) / 2)

    return pos


def get_node_color(fkt: str) -> str:
    fkt = normalize(fkt)

    if fkt in {"ZTH", "ZENTRALE THESE"}:
        return "#ffe6a7"
    if fkt in {"TH1", "THESE1"}:
        return "#cdeffd"
    if fkt in {"TH2", "THESE2"}:
        return "#ffd6d6"
    if fkt in {"PRO", "PRO ARGUMENT"}:
        return "#d8f3dc"
    if fkt in {"CON", "CON ARGUMENT"}:
        return "#f8d7da"
    if fkt == "JOINT":
        return "#eeeeee"
    if fkt == "CONNECTION":
        return "#ffffff"

    return "#eeeeee"


def draw_edges_by_relation(graph: nx.DiGraph, pos: dict):
    support_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") == "SUP"
    ]

    attack_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") == "ATT"
    ]

    restatement_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") == "RES"
    ]

    elaboration_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") == "ELA"
    ]

    relation_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") == "REL"
    ]

    other_edges = [
        (u, v) for u, v, data in graph.edges(data=True)
        if data.get("rel") not in {"SUP", "ATT", "RES", "ELA", "REL"}
    ]

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=support_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=18,
        width=2
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=attack_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=18,
        width=2,
        style="dashed"
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=restatement_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=16,
        width=1.5,
        style="dotted"
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=elaboration_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=16,
        width=1.5,
        style="dashdot"
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=relation_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=14,
        width=1,
        style="solid",
        alpha=0.55
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=other_edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=16,
        width=1
    )


def draw_graph(graph: nx.DiGraph, output_path: Path, title: str):
    if len(graph.nodes) == 0:
        raise ValueError("Der Graph enthält keine argumentativen Knoten.")

    pos = hierarchy_layout(graph)
    pos = improve_connection_node_positions(graph, pos)

    plt.figure(figsize=(22, 13))
    ax = plt.gca()
    ax.set_title(title, fontsize=16, pad=20)

    labels = nx.get_node_attributes(graph, "label")

    segment_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("fkt") not in {"CONNECTION", "JOINT"}
    ]

    joint_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("fkt") == "JOINT"
    ]

    connection_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("fkt") == "CONNECTION"
    ]

    segment_node_colors = [
        get_node_color(graph.nodes[node].get("fkt", ""))
        for node in segment_nodes
    ]

    # Normale argumentative Segmentknoten
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=segment_nodes,
        node_color=segment_node_colors,
        node_size=4300,
        edgecolors="#333333",
        linewidths=1.2
    )

    # Hilfsknoten für gemeinsame Stützung
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=joint_nodes,
        node_color="#eeeeee",
        node_size=2500,
        edgecolors="#333333",
        linewidths=1.0
    )

    # Neue Knoten in Verbindungen, z. B. für ZIE = 2-3
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=connection_nodes,
        node_color="#ffffff",
        node_size=900,
        edgecolors="#333333",
        linewidths=1.2
    )

    # Labels für normale Knoten, Joint-Knoten und Connection-Knoten
    visible_labels = {
        node: labels[node]
        for node in list(segment_nodes) + list(joint_nodes) + list(connection_nodes)
        if node in labels
    }

    nx.draw_networkx_labels(
        graph,
        pos,
        labels=visible_labels,
        font_size=8,
        font_family="sans-serif"
    )

    draw_edges_by_relation(graph, pos)

    edge_labels = {
        (u, v): data.get("label", "")
        for u, v, data in graph.edges(data=True)
        if data.get("label")
    }

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=8
    )

    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def process_csv_file(csv_path: Path, output_folder: Path, show_text: bool = True):
    print(f"\nVerarbeite: {csv_path.name}")

    df = load_csv(csv_path)
    graph = build_graph(df, only_argumentative=True, show_text=show_text)

    output_path = output_folder / f"{csv_path.stem}_baumstruktur.png"

    draw_graph(
        graph=graph,
        output_path=output_path,
        title=f"Baumstruktur: {csv_path.stem}"
    )

    print(f"Gespeichert: {output_path}")


def process_folder(folder_path: str, show_text: bool = True):
    input_folder = Path(folder_path)

    if not input_folder.exists():
        raise FileNotFoundError(f"Der Ordner existiert nicht: {input_folder}")

    if not input_folder.is_dir():
        raise NotADirectoryError(f"Der Pfad ist kein Ordner: {input_folder}")

    csv_files = sorted(input_folder.glob("*.csv"))

    if not csv_files:
        print(f"Keine CSV-Dateien gefunden in: {input_folder}")
        return

    output_folder = input_folder / "Output"
    output_folder.mkdir(exist_ok=True)

    successful = 0
    failed = 0

    for csv_path in csv_files:
        try:
            process_csv_file(csv_path, output_folder, show_text=show_text)
            successful += 1
        except Exception as error:
            failed += 1
            print(f"Fehler bei {csv_path.name}: {error}")

    print("\nFertig.")
    print(f"Erfolgreich verarbeitet: {successful}")
    print(f"Fehlgeschlagen: {failed}")
    print(f"Ausgabeordner: {output_folder}")


if __name__ == "__main__":
    # Option:
    # 0 = Segmenttext wird nicht in den Knoten angezeigt
    # 1 = Segmenttext wird in den Knoten angezeigt
    SHOW_TEXT = 1

    INPUT_FOLDER = r"C:\Users\haufa\Downloads\annotated\Mariesa"
    #INPUT_FOLDER = r"C:\Users\haufa\Downloads\C 701-750+\C 701-750+\annotated"

    process_folder(INPUT_FOLDER, show_text=bool(SHOW_TEXT))
