# ==========================================
# File: list_connectors.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Provides curated lists of German discourse connectors (conjunctions,
#    subordinating conjunctions, and adverbial connectors) for use in
#    linguistic text analysis.
# ==========================================


def get_connectors() -> list[list]:
    """
    Return lists of German discourse connectors grouped by grammatical type.

    Returns
    -------
    tuple
        A tuple containing three lists:
        - KONJUNKTIONEN : list of tuples [str, str]
        - SUBJUNKTIONEN : list of tuples [str, str]
        - ADVERBIALVERBINDUNGEN : list of tuples [str, str]
    """

    KONJUNKTIONEN = {
        "und": "A1",
        "oder": "A1",
        "aber": "A1",

        "denn": "A2",

        "sowie": "B1",
        "sondern": "B1",

        "bzw.": "B2"
    }

    SUBJUNKTIONEN = {
        "dass": "A2",
        "weil": "A2",
        "wenn": "A2",
        "als": "A2",
        "da": "A2",

        "während": "B1",
        "damit": "B1",
        "sodass": "B1",
        "obwohl": "B1",
        "indem": "B1",
        "solange": "B1",
        "seit": "B1",
        "seitdem": "B1",
        "bis": "B1",
        "bevor": "B1",
        "ehe": "B1",
        "nachdem": "B1",
        "sobald": "B1",

        "falls": "B2",
        "sofern": "B2",
        "wohingegen": "B2",
        "wogegen": "B2",
        "obgleich": "B2",
        "obschon": "B2",
        "wie": "B2",
        "je": "B2",
        "zumal": "B2"
    }

    KONJUNKTIONALADVERBIEN = {
        "dann": "A1",

        "danach": "A2",
        "davor": "A2",
        "anschließend": "A2",
        "deshalb": "A2",
        "deswegen": "A2",
        "darum": "A2",
        "inzwischen": "A2",

        "dagegen": "B1",
        "stattdessen": "B1",
        "daher": "B1",
        "währenddessen": "B1",
        "nämlich": "B1",
        "sonst": "B1",
        "trotzdem": "B1",

        "folglich": "B2",
        "infolgedessen": "B2",
        "demzufolge": "B2",
        "andernfalls": "B2",
        "gleichwohl": "B2",
        "allerdings": "B2",
        "nichtsdestotrotz": "B2",
        "dennoch": "B2"
    }

    return (KONJUNKTIONEN, SUBJUNKTIONEN, KONJUNKTIONALADVERBIEN)