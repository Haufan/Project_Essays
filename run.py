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

    for file in tqdm(source_path.iterdir(), desc="Processing", unit=" texts"):
        id = re.search(r"(\d+)(?=\.txt$)", str(file)).group(1)
        text = file.read_text(encoding="utf-8")

        obj = Text(id, text)
        '''print(f"Text ID:   {obj.id}\n"
              f"Anzahl Sätze:   {obj.sentence_count}\n"
              f"Länge Sätze:   {obj.sentence_lenght}\n"
              f"Anzahl Wörter:   {obj.word_count}\n"
              f"Anzahl unterschiedlicher Wörter:   {obj.dif_word_count}\n"
              f"Measure of Textual Lexical Diversity (0.72):   {obj.word_mtld}\n"
              f"Moving-Average Type–Token Ratio (50):   {obj.word_mattr}\n"
              f"Anzahl Konnektoren:   {obj.connector_count}\n"
              f"Anzahl unterschiedlicher Konnektoren:   {obj.dif_connector_count}\n"
              f"Anzahl Konnektortyp (KON, SUB, ADV):   {obj.connectors[1]}\n")

        quit()'''


if __name__ == "__main__":
    source = 'C:/Users/haufa/PycharmProjects/Project_Essays/test_data'
    main(source)
