# ==========================================
# File: run.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Entry point of the project. Iterates over a directory of German text files,
#    creates a Text object for each file, and triggers linguistic analysis such
#    as tokenization, lexical diversity measures, and connector statistics.
# ==========================================


from tqdm import tqdm
import pandas as pd
from pathlib import Path
import re

from class_Text import Text


def safe_divide(numerator, denominator):
    """
    Divide safely. Returns 0 if denominator is 0.
    """
    if denominator == 0:
        return 0
    return numerator / denominator


def main(source):
    """
    Process all text files in a directory and analyze them.
    """

    source_path = Path(source)
    out_csv = source_path / "analysis_results.csv"
    rows = []

    for file in tqdm(source_path.iterdir(), desc="Processing", unit=" texts done"):

        # Nur TXT-Dateien verarbeiten
        if not file.is_file() or file.suffix.lower() != ".txt":
            continue

        match = re.search(r"(\d+)(?=\.txt$)", file.name)

        # Dateien ohne numerische ID überspringen
        if not match:
            continue

        id = match.group(1)
        text = file.read_text(encoding="utf-8")

        obj = Text(id, text)

        connector_freq = obj.connector_stats.get("connector_frequencies", {})
        connector_level_freq = obj.connector_stats.get("connector_level_frequencies", {})
        connector_function_freq = obj.connector_stats.get("connector_function_frequencies", {})

        row = {
            "text_id": obj.id,
            "filename": file.name,

            # WORTSTATISTIK
            "word_count": obj.word_count,
            "dif_word_count": obj.dif_word_count,
            "word_mtld_0.72": obj.word_mtld,
            "word_mattr_50": obj.word_mattr,
            "share_basic_vocab_700": obj.word_stats,

            # SATZTATISTIK
            "n_sentences": obj.sentence_length_stats.get("n_sentences"),
            "sentence_len_mean": obj.sentence_length_stats.get("mean"),
            "sentence_len_median": obj.sentence_length_stats.get("median"),
            "sentence_len_std": obj.sentence_length_stats.get("std"),
            "share_short_sentences": obj.sentence_length_stats.get("share_short"),
            "share_long_sentences": obj.sentence_length_stats.get("share_long"),

            # KONNEKTORSTATISTIK
            "connector_count": obj.connector_count,
            "unique_connectors_used": obj.connector_stats.get("unique_connectors_used"),

            "connector_type_KON": obj.connector_count_type[0],
            "connector_type_SUB": obj.connector_count_type[1],
            "connector_type_ADV": obj.connector_count_type[2],

            "unique_connector_type_KON": safe_divide(
                obj.dif_connector_count_type[0],
                obj.connector_count
            ),
            "unique_connector_type_SUB": safe_divide(
                obj.dif_connector_count_type[1],
                obj.connector_count
            ),
            "unique_connector_type_ADV": safe_divide(
                obj.dif_connector_count_type[2],
                obj.connector_count
            ),

            "connectors_per_100_words": obj.connector_per_hundred,

            "pct_connectors_used_once": obj.connector_stats.get("pct_connectors_used_once"),
            "pct_connectors_used_more_than_3": obj.connector_stats.get("pct_connectors_used_more_than_3"),

            "connector_score_level": obj.connector_score_level,

            # EINZELNE KONNEKTOREN
            "connector_und": connector_freq.get("und", 0),
            "connector_oder": connector_freq.get("oder", 0),
            "connector_aber": connector_freq.get("aber", 0),
            "connector_denn": connector_freq.get("denn", 0),
            "connector_sowie": connector_freq.get("sowie", 0),
            "connector_sondern": connector_freq.get("sondern", 0),
            "connector_bzw": connector_freq.get("bzw.", 0),
            "connector_dass": connector_freq.get("dass", 0),
            "connector_weil": connector_freq.get("weil", 0),
            "connector_wenn": connector_freq.get("wenn", 0),
            "connector_als": connector_freq.get("als", 0),
            "connector_da": connector_freq.get("da", 0),
            "connector_während": connector_freq.get("während", 0),
            "connector_damit": connector_freq.get("damit", 0),
            "connector_sodass": connector_freq.get("sodass", 0),
            "connector_obwohl": connector_freq.get("obwohl", 0),
            "connector_indem": connector_freq.get("indem", 0),
            "connector_solange": connector_freq.get("solange", 0),
            "connector_seit": connector_freq.get("seit", 0),
            "connector_seitdem": connector_freq.get("seitdem", 0),
            "connector_bis": connector_freq.get("bis", 0),
            "connector_bevor": connector_freq.get("bevor", 0),
            "connector_ehe": connector_freq.get("ehe", 0),
            "connector_nachdem": connector_freq.get("nachdem", 0),
            "connector_sobald": connector_freq.get("sobald", 0),
            "connector_falls": connector_freq.get("falls", 0),
            "connector_sofern": connector_freq.get("sofern", 0),
            "connector_wohingegen": connector_freq.get("wohingegen", 0),
            "connector_wogegen": connector_freq.get("wogegen", 0),
            "connector_obgleich": connector_freq.get("obgleich", 0),
            "connector_obschon": connector_freq.get("obschon", 0),
            "connector_wie": connector_freq.get("wie", 0),
            "connector_je": connector_freq.get("je", 0),
            "connector_zumal": connector_freq.get("zumal", 0),
            "connector_dann": connector_freq.get("dann", 0),
            "connector_danach": connector_freq.get("danach", 0),
            "connector_davor": connector_freq.get("davor", 0),
            "connector_anschließend": connector_freq.get("anschließend", 0),
            "connector_deshalb": connector_freq.get("deshalb", 0),
            "connector_deswegen": connector_freq.get("deswegen", 0),
            "connector_darum": connector_freq.get("darum", 0),
            "connector_inzwischen": connector_freq.get("inzwischen", 0),
            "connector_dagegen": connector_freq.get("dagegen", 0),
            "connector_stattdessen": connector_freq.get("stattdessen", 0),
            "connector_daher": connector_freq.get("daher", 0),
            "connector_währenddessen": connector_freq.get("währenddessen", 0),
            "connector_nämlich": connector_freq.get("nämlich", 0),
            "connector_sonst": connector_freq.get("sonst", 0),
            "connector_trotzdem": connector_freq.get("trotzdem", 0),
            "connector_folglich": connector_freq.get("folglich", 0),
            "connector_infolgedessen": connector_freq.get("infolgedessen", 0),
            "connector_demzufolge": connector_freq.get("demzufolge", 0),
            "connector_andernfalls": connector_freq.get("andernfalls", 0),
            "connector_gleichwohl": connector_freq.get("gleichwohl", 0),
            "connector_allerdings": connector_freq.get("allerdings", 0),
            "connector_nichtsdestotrotz": connector_freq.get("nichtsdestotrotz", 0),
            "connector_dennoch": connector_freq.get("dennoch", 0),

            # CEFR-LEVEL ALS ANTEILE AN ALLEN KONNEKTOREN
            "connector_level_A1": safe_divide(
                connector_level_freq.get("A1", 0),
                obj.connector_count
            ),
            "connector_level_A2": safe_divide(
                connector_level_freq.get("A2", 0),
                obj.connector_count
            ),
            "connector_level_B1": safe_divide(
                connector_level_freq.get("B1", 0),
                obj.connector_count
            ),
            "connector_level_B2": safe_divide(
                connector_level_freq.get("B2", 0),
                obj.connector_count
            ),
            "connector_level_C1": safe_divide(
                connector_level_freq.get("C1", 0),
                obj.connector_count
            ),
            "connector_level_C2": safe_divide(
                connector_level_freq.get("C2", 0),
                obj.connector_count
            ),

            # FUNKTIONEN ALS ANTEILE AN ALLEN KONNEKTOREN
            "connector_function_additiv": safe_divide(
                connector_function_freq.get("additiv", 0),
                obj.connector_count
            ),
            "connector_function_alternativ": safe_divide(
                connector_function_freq.get("alternativ", 0),
                obj.connector_count
            ),
            "connector_function_adversativ": safe_divide(
                connector_function_freq.get("adversativ", 0),
                obj.connector_count
            ),
            "connector_function_kausal": safe_divide(
                connector_function_freq.get("kausal", 0),
                obj.connector_count
            ),
            "connector_function_komplement": safe_divide(
                connector_function_freq.get("komplement", 0),
                obj.connector_count
            ),
            "connector_function_konditional": safe_divide(
                connector_function_freq.get("konditional", 0),
                obj.connector_count
            ),
            "connector_function_temporal": safe_divide(
                connector_function_freq.get("temporal", 0),
                obj.connector_count
            ),
            "connector_function_final": safe_divide(
                connector_function_freq.get("final", 0),
                obj.connector_count
            ),
            "connector_function_konsekutiv": safe_divide(
                connector_function_freq.get("konsekutiv", 0),
                obj.connector_count
            ),
            "connector_function_konzessiv": safe_divide(
                connector_function_freq.get("konzessiv", 0),
                obj.connector_count
            ),
            "connector_function_modal": safe_divide(
                connector_function_freq.get("modal", 0),
                obj.connector_count
            ),
            "connector_function_vergleichend": safe_divide(
                connector_function_freq.get("vergleichend", 0),
                obj.connector_count
            ),
            "connector_function_explikativ": safe_divide(
                connector_function_freq.get("explikativ", 0),
                obj.connector_count
            ),
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig", sep=",")

    print(f"\nSaved CSV with {len(df)} rows to: {out_csv}")


if __name__ == "__main__":
    source = "C:/Users/haufa/PycharmProjects/Project_Essays/test_data/texts test"
    main(source)
