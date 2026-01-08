# ToDos
# ----------
# Wort
#    Wort Score (Level, Grundwortschatz)
#
# Satz
#    Hauptsatz / Nebensatz
#    Schachtelkonstruktionen
#    Verbal- Nominalstrukturen
#    Wiederholungen
#
# Konnektoren
#    zweiteilige Konnektoren
#
# Umbau Ausgabe in dicts
#
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

    text = "Er hat weder ein Auto, noch ein Fahrrad."
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