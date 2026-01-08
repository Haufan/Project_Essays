# ==========================================
# File: list_connectors.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Provides a curated list of the German basic vocabulary ("Grundwortschatz 500")
#    for use in linguistic and educational text analysis.
# ==========================================


def get_basic_vocabulary() -> list:
    """
    Return the German basic vocabulary derived from the
    "Grundwortschatz für Brandenburg – Gesamtkorpus (2024)".

    Source:
    Ministerium für Bildung, Jugend und Sport des Landes Brandenburg (MBJS),
    Grundwortschatz für Brandenburg, Gesamtkorpus 2024.
    https://bildungsserver.berlin-brandenburg.de/fileadmin/bbb/unterricht/faecher/sprachen/deutsch/schreiben_rechtschreiben/GWS_Gesamtkorpus_2024.pdf

    Returns
    -------
    list of str
        Basic German vocabulary items.
    """

    GRUNDWORTSCHATZ = [
        "ab", "Abend", "aber", "acht", "alle", "als", "also", "alt", "am", "Ampel", "an", "anders", "Angst", "Antwort",
        "Apfel", "April", "arbeiten", "ärgern", "Arm", "Arzt", "Ast", "auch", "auf", "Aufgabe", "aufwachen", "Auge",
        "August", "aus", "Auto", "Baby", "backen", "baden", "Bahn", "bald", "Ball", "Bank", "Bauch", "bauen", "Baum",
        "beginnen", "Bein", "Beispiel", "beißen", "belohnen", "beobachten", "bequem", "bereits", "Berg", "Beruf",
        "besser", "Bett", "bevor", "bewegen", "bezahlen", "biegen", "Biene", "Bild", "bin", "Birne", "bis", "bisschen",
        "bitten", "Blatt", "blau", "bleiben", "blicken", "blind", "Blitz", "bloß", "blühen", "Blume", "Blüte", "Boden",
        "bohren", "Boot", "böse", "boxen", "Brand", "braun", "brennen", "Brief", "Brille", "bringen", "Brot", "Brücke",
        "Bruder", "Buch", "bunt", "Burg", "Busch", "Cent", "Computer", "da", "danken", "dann", "das", "dass", "Decke",
        "dein", "dem", "den", "denken", "denn", "der", "des", "deutsch", "Dezember", "dich", "dick", "die", "Dienstag",
        "diese", "dieser", "doch", "Donner", "Donnerstag", "Dose", "draußen", "drehen", "drei", "Druck", "du", "dumm",
        "dunkel", "dünn", "durch", "dürfen", "Durst", "Ecke", "ehrlich", "Ei", "eigentlich", "Eimer", "ein", "einmal",
        "eins", "einzelnen", "elf", "Eltern", "Ende", "eng", "entdecken", "Ente", "entfernen", "entwickeln", "er",
        "Erde", "erklären", "erlauben", "erleben", "ernähren", "erschrecken", "erwarten", "erzählen", "es", "essen",
        "euch", "Eule", "Euro", "Europa", "fahren", "Fahrrad", "fallen", "Familie", "fangen", "Februar", "Fehler",
        "Feld", "Fenster", "Ferien", "Fernseher", "fertig", "fett", "feucht", "Feuer", "Feuerwehr", "finden", "Finger",
        "Flasche", "Fleiß", "fliegen", "fließen", "Flügel", "Flugzeug", "Fluss", "flüssig", "fragen", "Frau", "frei",
        "Freitag", "fremd", "fressen", "freuen", "Freund", "Frieden", "frieren", "frisch", "fröhlich", "Frucht",
        "Frühling", "frühstücken", "Fuchs", "fühlen", "füllen", "fünf", "für", "Fuß", "Gabel", "ganz", "Garten",
        "Gebäude", "geben", "Geburt", "Gefahr", "gefallen", "gegen", "geheim", "gehen", "gelb", "Geld", "Gemeinde",
        "Gemüse", "Geschäft", "Gesetz", "Gesicht", "gestern", "gesund", "gewinnen", "Gewitter", "gießen", "glatt",
        "Glück", "glühen", "Gott", "Gras", "groß", "grün", "Gruß", "gut", "Haar", "haben", "Hals", "halten", "Hand",
        "Handy", "hängen", "hart", "Hase", "hat", "hatte", "häufig", "Haus", "Haut", "Hecke", "heiß", "heißen",
        "heizen", "helfen", "hell", "Hemd", "Herbst", "Herr", "heute", "Hexe", "hier", "Hilfe", "Himmel", "Hitze",
        "hoffen", "Höhe", "hohl", "hören", "Hose", "Hund", "hundert", "Hunger", "ich", "Igel", "ihm", "ihn", "ihnen",
        "ihr", "im", "immer", "impfen", "in", "informieren", "Interesse", "ist", "ja", "Jahr", "Januar", "jede",
        "jemand", "jetzt", "Juli", "jung", "Junge", "Juni", "Käfer", "Käfig", "Kalender", "kalt", "Kamm", "kann",
        "kaputt", "Katze", "kaufen", "kennen", "Kind", "klar", "Klasse", "Kleid", "klein", "klettern", "kommen",
        "können", "Kopf", "Körper", "Kraft", "krank", "kratzen", "Kreuzung", "kriechen", "Krieg", "Küche", "Kuh",
        "kühl", "Kuss", "lachen", "Land", "lang", "langsam", "Lärm", "lassen", "Laub", "laufen", "laut", "leben",
        "legen", "Lehrer", "leicht", "leise", "lernen", "lesen", "letzte", "leuchten", "Lexikon", "Licht", "lieb",
        "Lied", "liegen", "links", "Löffel", "machen", "Mädchen", "Magnet", "Mai", "malen", "man", "Mann", "März",
        "Maschine", "Maus", "Meer", "mehr", "meine", "messen", "Messer", "mich", "Miete", "Milch", "Minute", "mir",
        "mit", "Mittag", "Mitte", "Mittwoch", "mixen", "mögen", "Monat", "Montag", "Moos", "morgen", "Müll", "Mund",
        "muss", "müssen", "Mutter", "nach", "Nachmittag", "nächste", "Nacht", "nah", "nähen", "Nahrung", "Name",
        "Nase", "nass", "Natur", "Nebel", "nehmen", "nein", "neu", "neun", "nicht", "nie", "niemand", "noch",
        "November", "Nummer", "nun", "nur", "Nuss", "nützlich", "ob", "Obst", "oder", "offen", "oft", "ohne", "Ohr",
        "Oktober", "Onkel", "Ostern", "packen", "Paket", "Papier", "passen", "Pferd", "pflanzen", "pflegen", "Pilz",
        "Pizza", "Platz", "plötzlich", "Programm", "Puppe", "Quadrat", "quaken", "quälen", "Quelle", "Radio", "raten",
        "Raum", "Raupe", "rechnen", "rechts", "reden", "Regen", "Reh", "reich", "reisen", "reißen", "rennen",
        "richtig", "riechen", "Rock", "rollen", "rot", "Rücken", "rufen", "Ruhe", "rühren", "Saft", "sagen", "Salz",
        "sammeln", "Samstag", "Sand", "Satz", "schalten", "scharf", "Schatten", "schauen", "scheinen", "Schere",
        "schieben", "schief", "Schiff", "schlafen", "schlagen", "schließen", "schließlich", "Schloss", "Schlüssel",
        "schmecken", "Schmutz", "Schnee", "schneiden", "schnell", "schon", "schön", "Schreck", "schreiben",
        "schreien", "Schuh", "Schule", "Schutz", "schwarz", "schweigen", "Schwester", "schwierig", "schwimmen",
        "schwitzen", "sechs", "See", "sehen", "sehr", "Seife", "sein", "seit", "Seite", "Sekunde", "selbst",
        "September",
        "sich", "sie", "sieben", "sind", "singen", "sitzen", "so", "Sohn", "sollen", "Sommer", "Sonne", "Sonntag",
        "Spaß", "spät", "Spaziergang", "Spiegel", "spielen", "spitz", "Sport", "Stadt", "Stamm", "Stange", "stark",
        "stehen", "stellen", "Stiel", "Stift", "still", "stimmen", "Stoff", "Strand", "Straße", "Strauch", "Strauß",
        "streiten", "Stück", "Stuhl", "Stunde", "Sturm", "suchen", "süß", "Tabelle", "Tag", "Tanne", "Tante", "Tasche",
        "Tasse", "tausend", "Taxi", "Technik", "Tee", "Telefon", "Teller", "Temperatur", "Text", "Theater",
        "Thermometer", "tief", "Tier", "Tochter", "toll", "tragen", "Träne", "Traum", "treffen", "trinken", "trocken",
        "turnen", "üben", "über", "überqueren", "Uhr", "um", "und", "ungefähr", "uns", "unter", "Unterricht", "Urlaub",
        "Vase", "Vater", "verbieten", "verbrauchen", "verbrennen", "vergessen", "Verkehr", "verletzen", "verlieren",
        "verpacken", "verschmutzen", "versuchen", "viel", "vielleicht", "vier", "Vogel", "voll", "vom", "von", "vor",
        "Vorfahrt", "Vorsicht", "wachsen", "Wahl", "wählen", "während", "Wald", "wann", "war", "warm", "warten",
        "warum", "was", "waschen", "Wasser", "wechseln", "Wecker", "weg", "Weg", "Weihnachten", "weil", "weiß", "weit",
        "welche", "wenig", "wenn", "wer", "werden", "Wetter", "wichtig", "wie", "wieder", "wiegen", "Wiese", "wild",
        "Wind", "Winter", "wir", "wird", "wissen", "wo", "Woche", "wohnen", "Wolke", "wollen", "Wort", "Wunsch",
        "wünschen", "Wurzel", "Zahl", "Zahn", "Zeh", "zehn", "zeichnen", "zeigen", "Zeit", "Zeitung", "Zeugnis",
        "ziehen",
        "Ziel", "Zimmer", "zu", "Zucker", "Zukunft", "zum", "zur", "zurück", "zusammen", "zwei", "Zwiebel", "zwölf",
        "ähnlich", "ändern", "ärgern"
    ]

    return (GRUNDWORTSCHATZ)