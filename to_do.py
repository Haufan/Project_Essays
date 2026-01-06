# ToDos
# ----------
# bei Konnektoren auch POS checken (z.B. bis)
#
# weitere: allerdings
# also
# andererseits
# anschließend
# außerdem
# beziehungsweise
# dabei
# dadurch
# dafür
# dagegen
# damit
# danach
# dann
# darauf
# darum
# davor
# dazu
# dennoch
# deshalb
# deswegen
# einerseits
# entweder
# ferner
# folglich
# genauso
# immerhin
# inzwischen
# jedoch
# schließlich
# seitdem
# somit
# sonst
# später
# trotzdem
# vorher
# weder … noch
# zuerst
# zuvor
# zwar
#
# zweiteilige Konnektoren
#
# Konnektorenqualität
# Einsortierung nach Typ???
#
# Erkennung Haupt- und Nebensatz
# -> Wiederholung?
#

# Kommentare
# ----------
# ??? Nur Punkte, Komma, Doppelpunkte, ... entfernen (bzw. wird nicht erkannt)
# ??? ABBREVIATIONS = {"bzw.", "z.B.", "u.a.", "d.h."}
#
# erkennen von nicht erkannten wörtern
#
# aspekt der Falschscheibung




if __name__ == "__main__":

    import spacy

    nlp = spacy.load("de_core_news_sm")   # md = medium, lg = large

    text = "Der Fahrer bzw die Fahrerin fuhren schnell nach Hause und in die Wohnung. Ich habe das Auto gesehen. Das Fahren ist gut."
    doc = nlp(text)

    # ??? Nur Punkte, Komma, Doppelpunkte, ... entfernen (bzw. wird nicht erkannt)
    # ??? ABBREVIATIONS = {"bzw.", "z.B.", "u.a.", "d.h."}
    lemmas = [t.lemma_.lower() for t in doc if t.is_alpha]
    print(lemmas)

    # kein Unterschied zwischen Adjektiv und Adverb
    for token in doc:
        if token.is_alpha:
            lemma_pos = [
                (token.lemma_.lower(), token.pos_)
                for token in doc
                if token.is_alpha
            ]

    print(lemma_pos)