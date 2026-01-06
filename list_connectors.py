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
        - KONJUNKTIONEN : list of str
        - SUBJUNKTIONEN : list of str
        - ADVERBIALVERBINDUNGEN : list of str
    """

    KONJUNKTIONEN = [
        "und",
        "oder",
        "aber",
        "denn",
        "sowie",
        "sondern",
        "bzw"
    ]

    SUBJUNKTIONEN = [
        "bevor",
        "bis",
        "damit",
        "dass",
        "falls",
        "indem",
        "nachdem",
        "ob",
        "obwohl",
        "seit",
        "sobald",
        "sofern",
        "sodass",
        "wenn",
        "während",
        "weil"
    ]

    ADVERBIALVERBINDUNGEN = [
        "allerdings",
        "anschließend",
        "außerdem",
        "danach",
        "daher",
        "dennoch",
        "deshalb",
        "deswegen",
        "ebenfalls",
        "folglich",
        "hingegen",
        "insgesamt",
        "schließlich",
        "somit",
        "trotzdem",
        "zudem",
        "zunächst"
    ]

    return(KONJUNKTIONEN, SUBJUNKTIONEN, ADVERBIALVERBINDUNGEN)