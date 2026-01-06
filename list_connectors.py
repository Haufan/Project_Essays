# ==========================================
# File: list_connectors.py
# Author: Dietmar Benndorf
# Date: 2026-01-06
# Description:
#    Provides curated lists of German discourse connectors (conjunctions,
#    subordinating conjunctions, and adverbial connectors) for use in
#    linguistic text analysis.
# ==========================================


def list_connectors():
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

    KONJUNKTIONEN = [
        ("und", "A1"),
        ("oder", "A1"),
        ("aber", "A1"),

        ("denn", "A2"),

        ("sowie", "B1"),
        ("sondern", "B1"),

        ("bzw.", "B2")
    ]

    SUBJUNKTIONEN = [
        ("dass", "A2"),
        ("weil", "A2"),
        ("wenn", "A2"),
        ("ob", "A2"),
        ("als", "A2"),
        ("da", "A2"),

        ("bevor", "B1"),
        ("nachdem", "B1"),
        ("während", "B1"),
        ("obwohl", "B1"),
        ("bis", "B1"),
        ("seit", "B1"),
        ("seitdem", "B1"),
        ("sobald", "B1"),
        ("solange", "B1"),
        ("damit", "B1"),
        ("sodass", "B1"),
        ("ehe", "B1"),
        ("sooft", "B1"),
        ("soweit", "B1"),
        ("soviel", "B1"),

        ("falls", "B2"),
        ("sofern", "B2"),
        ("indem", "B2"),
        ("wohingegen", "B2"),
        ("wie", "B2"),
        ("obgleich", "B2"),
        ("obschon", "B2")
    ]

    KONJUNKTIONALADVERBIEN = [
        ("danach", "A1"),
        ("zunächst", "A1"),

        ("anschließend", "A2"),
        ("außerdem", "A2"),
        ("ebenfalls", "A2"),
        ("deshalb", "A2"),
        ("deswegen", "A2"),
        ("trotzdem", "A2"),

        ("daher", "B1"),
        ("somit", "B1"),
        ("dennoch", "B1"),
        ("hingegen", "B1"),
        ("zudem", "B1"),
        ("schließlich", "B1"),

        ("allerdings", "B2"),
        ("folglich", "B2"),
        ("insgesamt", "B2")
    ]

    return(KONJUNKTIONEN, SUBJUNKTIONEN, KONJUNKTIONALADVERBIEN)