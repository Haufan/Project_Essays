# ==========================================
# File: run.py
# Author: Dietmar Benndorf
# Date: 2026-01-06
# Description:
#    Entry point of the project. Iterates over a directory of German text files,
#    creates a Text object for each file, and triggers linguistic analysis such
#    as tokenization, lexical diversity measures, and connector statistics.
# ==========================================


from tqdm import tqdm
from pathlib import Path
import re

from class_Text import Text


def main(source):
    """
    Process all text files in a directory and analyze them.
    """

    source_path = Path(source)

    for file in tqdm(source_path.iterdir(), desc="Processing", unit=" texts done"):
        id = re.search(r"(\d+)(?=\.txt$)", str(file)).group(1)
        text = file.read_text(encoding="utf-8")

        obj = Text(id, text)
        print(f"\nText ID:   {obj.id}\n"
              f"###################\n\n"
              f"WORTSTATISTIK\n"
              f"   Anzahl Wörter:   {obj.word_count}\n"
              f"   Anzahl unterschiedlicher Wörter:   {obj.dif_word_count}\n"
              f"   Measure of Textual Lexical Diversity (0.72):   {obj.word_mtld}\n"
              f"   Moving-Average Type–Token Ratio (50):   {obj.word_mattr}\n\n"
              f"SATZTATISTIK\n"
              f"   Anzahl Sätze:   {obj.sentence_length_stats['n_sentences']}\n"
              f"   Länge Sätze (MEAN | MED | STD):   {obj.sentence_length_stats['mean']} | "
                                                 f"{obj.sentence_length_stats['median']} | "
                                                 f"{obj.sentence_length_stats['std']}\n"
              f"   Anteil kurze | lange Sätze:   {obj.sentence_length_stats['share_short']} | "
                                             f"{obj.sentence_length_stats['share_long']}\n\n"
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
              )

        quit()


if __name__ == "__main__":
    source = 'C:/Users/haufa/PycharmProjects/Project_Essays/test_data'
    main(source)
