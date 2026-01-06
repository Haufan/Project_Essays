# ==========================================
# File: run.py
# Author: Dietmar Benndorf
# Date: 2026-01-06
# Description:
#    ???
# ==========================================


from pathlib import Path
import re

from class_Text import Text


def main(source):
    '''
    ???
    :param source:
    :return:
    '''

    source_path = Path(source)

    for file in source_path.iterdir():
        id = re.search(r"(\d+)(?=\.txt$)", str(file)).group(1)
        text = file.read_text(encoding="utf-8")

        obj = Text(id, text)
        print(obj.word_count, obj.dif_word_count, obj.word_mtld, obj.word_mattr)

        quit()


if __name__ == "__main__":
    source = 'C:/Users/haufa/PycharmProjects/Project_Essays/test_data'
    main(source)
