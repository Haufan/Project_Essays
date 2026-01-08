# ==========================================
# File: list_connectors.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Provides a curated list of the German basic vocabulary ("Grundwortschatz 500")
#    for use in linguistic and educational text analysis.
# ==========================================


def list_basic_vocabulary() -> list:
    """
    Return the German basic vocabulary ("Grundwortschatz 500") as a list of strings.

    Returns
    -------
    list of str
        Basic German vocabulary items.
    """

    GRUNDWORTSCHATZ = [
        "ab", "Abend", "acht", "alle", "allein", "als", "also", "alt", "an", "andere", "anfangen",
        "Angst", "antworten", "Apfel", "Arbeit", "arbeiten", "Arzt", "auch", "auf", "Auge", "aus",
        "Auto", "baden", "bald", "Ball", "bauen", "Bauer", "Baum", "beginnen", "bei", "beide", "Bein",
        "Beispiel", "beißen", "bekommen", "Berg", "besser", "Bett", "Bild", "bin", "bis", "blau",
        "bleiben", "Blume", "Boden", "böse", "brauchen", "braun", "Brief", "bringen", "Brot",
        "Bruder", "Buch", "da", "dabei", "dafür", "damit", "danach", "dann", "daran", "darauf",
        "darin", "dauern", "davon", "dazu", "dem", "den", "denken", "deshalb", "dick", "diese",
        "Ding", "dir", "doch", "Dorf", "dort", "draußen", "drehen", "drei", "dumm", "dunkel", "durch",
        "dürfen", "eigentlich", "ein", "einer", "einfach", "einige", "Eis", "Eltern", "Ende",
        "endlich", "er", "Erde", "erklären", "erschrecken", "erst", "erzählen", "es", "essen",
        "etwas", "fahren", "Fahrrad", "fallen", "Familie", "fangen", "fast", "fehlen", "Fehler",
        "Feld", "Fenster", "Ferien", "fest", "fertig", "Feuer", "fiel", "finden", "fing", "Finger",
        "Fisch", "Flasche", "fliegen", "fressen", "frei", "Freude", "freuen", "Freund", "fröhlich",
        "früh", "fuhr", "führen", "fünf", "für", "Fuß", "Fußball", "gab", "ganz", "gar", "Garten",
        "gefährlich", "geben", "gehören", "gehen", "gelb", "Geld", "genau", "Geschichte", "Geschenk",
        "gestern", "Gesicht", "gibt", "ging", "Glas", "glauben", "gleich", "Glück", "glücklich",
        "Gott", "grad", "groß", "grün", "gut", "halb", "Haar", "Hand", "hängen", "hart", "Hase",
        "hast", "hat", "hatte", "Haus", "heißen", "heiß", "helfen", "Herr", "Herz", "hier", "Hilfe",
        "Himmel", "hin", "hinein", "hinter", "hoch", "holen", "Holz", "hören", "Hunger", "Hund",
        "ich", "ihm", "ihr", "im", "in", "ins", "ist", "ja", "Jahr", "jeder", "jetzt", "jung", "Junge",
        "kam", "kalt", "kann", "Katze", "kein", "kennen", "Kind", "Klasse", "klettern", "kochen",
        "Kopf", "kommen", "können", "krank", "kurz", "Land", "lang", "lassen", "laufen", "laut",
        "leben", "legen", "Lehrer", "Lehrerin", "leicht", "lernen", "letzte", "Leute", "Licht",
        "liegen", "ließ", "Loch", "los", "Luft", "lustig", "machen", "mal", "Mann", "Maus", "Meer",
        "mehr", "mein", "Mensch", "merken", "mich", "Milch", "Minute", "mir", "mit", "möglich",
        "mögen", "Monat", "Musik", "müde", "muss", "müssen", "nach", "Nacht", "nah", "Name", "nämlich",
        "natürlich", "neben", "nehmen", "nein", "neu", "neun", "nie", "nicht", "nichts", "noch",
        "nun", "nur", "oben", "ob", "oft", "ohne", "Oma", "Onkel", "Opa", "offen", "öffnen", "oder",
        "Ort", "packen", "Platz", "Polizei", "Rad", "rechnen", "reden", "reich", "rennen", "richtig",
        "rot", "rufen", "rund", "ruhig", "sagen", "sah", "Sache", "sammeln", "schaffen", "schauen",
        "schicken", "schlafen", "schlecht", "schließen", "schnell", "schon", "schreiben",
        "schrie", "Schule", "Schüler", "schwarz", "schwer", "schwimmen", "sechs", "See", "sehen",
        "sein", "Seite", "selbst", "setzen", "sich", "sieben", "sicher", "singen", "sind", "Sohn",
        "sofort", "sollen", "Sommer", "sonst", "Spaß", "spielen", "sprechen", "springen", "spät",
        "Stadt", "stehen", "Stelle", "stellen", "Stein", "stark", "Straße", "Stück", "Stunde",
        "suchen", "Tag", "Tante", "Teller", "Tier", "tief", "tragen", "treffen", "trinken", "tun",
        "Tür", "über", "überall", "um", "uns", "unser", "unten", "unter", "Vater", "verkaufen",
        "verlieren", "verstehen", "verstecken", "viel", "vielleicht", "vier", "Vogel", "voll",
        "vom", "von", "vor", "vorbei", "Wagen", "Wald", "warm", "war", "warten", "warum", "was",
        "waschen", "Wasser", "Weihnachten", "weit", "wenig", "wenn", "wer", "werden", "werfen",
        "Wetter", "wie", "wichtig", "wieder", "will", "Wind", "Winter", "wir", "wird", "wirklich",
        "wissen", "wo", "wohnen", "Woche", "wohl", "Wollen", "Wort", "wünschen", "Zeit", "Zeitung",
        "ziehen", "Zimmer", "zu", "Zug", "zum", "zur", "zurück", "zusammen", "zwei"
    ]

    return (GRUNDWORTSCHATZ)