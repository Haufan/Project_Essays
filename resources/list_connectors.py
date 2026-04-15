# ==========================================
# File: list_connectors.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Provides curated lists of German discourse connectors with
#    CEFR level and discourse function.
# ==========================================


def get_connectors() -> tuple[dict, dict, dict]:
    """
    Return dictionaries of German discourse connectors grouped by grammatical type.

    Returns
    -------
    tuple
        (KONJUNKTIONEN, SUBJUNKTIONEN, KONJUNKTIONALADVERBIEN)

        Each dictionary maps:
            connector -> (CEFR_level, function)
    """

    KONJUNKTIONEN = {
        "und": ("A1", "additiv"),
        "oder": ("A1", "alternativ"),
        "aber": ("A1", "adversativ"),

        "denn": ("A2", "kausal"),

        "sowie": ("B1", "additiv"),
        "sondern": ("B1", "adversativ"),

        "bzw.": ("B2", "alternativ")
    }

    SUBJUNKTIONEN = {
        "dass": ("A2", "komplement"),
        "weil": ("A2", "kausal"),
        "wenn": ("A2", "konditional"),
        "als": ("A2", "temporal"),
        "da": ("A2", "kausal"),

        "während": ("B1", "temporal"),
        "damit": ("B1", "final"),
        "sodass": ("B1", "konsekutiv"),
        "obwohl": ("B1", "konzessiv"),
        "indem": ("B1", "modal"),
        "solange": ("B1", "temporal"),
        "seit": ("B1", "temporal"),
        "seitdem": ("B1", "temporal"),
        "bis": ("B1", "temporal"),
        "bevor": ("B1", "temporal"),
        "ehe": ("B1", "temporal"),
        "nachdem": ("B1", "temporal"),
        "sobald": ("B1", "temporal"),

        "falls": ("B2", "konditional"),
        "sofern": ("B2", "konditional"),
        "wohingegen": ("B2", "adversativ"),
        "wogegen": ("B2", "adversativ"),
        "obgleich": ("B2", "konzessiv"),
        "obschon": ("B2", "konzessiv"),
        "wie": ("B2", "vergleichend"),
        "je": ("B2", "konditional"),
        "zumal": ("B2", "kausal")
    }

    KONJUNKTIONALADVERBIEN = {
        "dann": ("A1", "temporal"),

        "danach": ("A2", "temporal"),
        "davor": ("A2", "temporal"),
        "anschließend": ("A2", "temporal"),
        "deshalb": ("A2", "kausal"),
        "deswegen": ("A2", "kausal"),
        "darum": ("A2", "kausal"),
        "inzwischen": ("A2", "temporal"),

        "dagegen": ("B1", "adversativ"),
        "stattdessen": ("B1", "adversativ"),
        "daher": ("B1", "konsekutiv"),
        "währenddessen": ("B1", "temporal"),
        "nämlich": ("B1", "explikativ"),
        "sonst": ("B1", "konditional"),
        "trotzdem": ("B1", "konzessiv"),

        "folglich": ("B2", "konsekutiv"),
        "infolgedessen": ("B2", "konsekutiv"),
        "demzufolge": ("B2", "konsekutiv"),
        "andernfalls": ("B2", "konditional"),
        "gleichwohl": ("B2", "konzessiv"),
        "allerdings": ("B2", "adversativ"),
        "nichtsdestotrotz": ("B2", "konzessiv"),
        "dennoch": ("B2", "konzessiv")
    }

    return (KONJUNKTIONEN, SUBJUNKTIONEN, KONJUNKTIONALADVERBIEN)