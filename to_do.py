# ??? Nur Punkte, Komma, Doppelpunkte, ... entfernen (bzw. wird nicht erkannt)
# ??? ABBREVIATIONS = {"bzw.", "z.B.", "u.a.", "d.h."}

# erkennen von nicht erkannten wörtern

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