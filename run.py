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


def main(source):
    """
    Process all text files in a directory and analyze them.
    """

    source_path = Path(source)
    out_csv = source_path / "analysis_results.csv"
    rows = []

    for file in tqdm(source_path.iterdir(), desc="Processing", unit=" texts done"):
        id = re.search(r"(\d+)(?=\.txt$)", str(file)).group(1)
        text = file.read_text(encoding="utf-8")

        obj = Text(id, text)
        '''print(f"\nText ID:   {obj.id}\n"
              f"###################\n\n"
              f"WORTSTATISTIK\n"
              f"   Anzahl Wörter:   {obj.word_count}\n"
              f"   Anzahl unterschiedlicher Wörter:   {obj.dif_word_count}\n"
              f"   Measure of Textual Lexical Diversity (0.72):   {obj.word_mtld}\n"
              f"   Moving-Average Type–Token Ratio (50):   {obj.word_mattr}\n"
              f"   Anteil Grundwortschatz (ca. 700):   {obj.word_stats}\n"
              f"   Anteil Wortschatz A1 | A2 | B1:   todo\n"
              f"   Wortschatz Score (Level):   todo\n\n"
              f"SATZTATISTIK\n"
              f"   Anzahl Sätze:   {obj.sentence_length_stats['n_sentences']}\n"
              f"   Länge Sätze (MEAN | MED | STD):   {obj.sentence_length_stats['mean']} | "
                                                 f"{obj.sentence_length_stats['median']} | "
                                                 f"{obj.sentence_length_stats['std']}\n"
              f"   Anteil kurze | lange Sätze:   {obj.sentence_length_stats['share_short']} | "
                                             f"{obj.sentence_length_stats['share_long']}\n"
              f"   Anzahl Nebensätze:   todo\n"
              f"   Wiederholungen:   todo\n\n"
              f"KONNEKTORSTATISTIK\n"
              f"   Anzahl Konnektoren:   {obj.connector_count}\n"
              f"   Anzahl unterschiedlicher Konnektoren:   {obj.connector_stats['unique_connectors_used']}\n"
              f"   Anzahl Konnektortyp (KON | SUB | ADV):   {obj.connector_count_type[0]} | "
                                                          f"{obj.connector_count_type[1]} | "
                                                          f"{obj.connector_count_type[2]}\n"
              f"   Anzahl unterschiedlicher Konnektoren (KON | SUB | ADV):   {obj.dif_connector_count_type[0]} | "
                                                          f"{obj.dif_connector_count_type[1]} | "
                                                          f"{obj.dif_connector_count_type[2]}\n"
              f"   Konnektoren pro Satz:   {obj.connector_per_sentence}\n"
              f"   Anteil 1x | >3x Nutzung:   {obj.connector_stats['pct_connectors_used_once']} | "
                                            f"{obj.connector_stats['pct_connectors_used_more_than_3']}\n"
              f"   Konnektor Score (Level):   {obj.connector_score_level}\n"
              )'''

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
            "unique_connector_type_KON": obj.dif_connector_count_type[0],
            "unique_connector_type_SUB": obj.dif_connector_count_type[1],
            "unique_connector_type_ADV": obj.dif_connector_count_type[2],
            "connectors_per_100_words": obj.connector_per_hundred,
            "pct_connectors_used_once": obj.connector_stats.get("pct_connectors_used_once"),
            "pct_connectors_used_more_than_3": obj.connector_stats.get("pct_connectors_used_more_than_3"),
            "connector_score_level": obj.connector_score_level,
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig", sep=",")
    print(f"\nSaved CSV with {len(df)} rows to: {out_csv}")

    #quit()


if __name__ == "__main__":
    source = 'C:/Users/haufa/PycharmProjects/Project_Essays/test_data/texts all'
    main(source)
