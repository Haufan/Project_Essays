# ==========================================
# File: class_Text.py
# Author: Dietmar Benndorf
# Date: 2026-01-08
# Description:
#    Provides a Text class for basic German text analysis. The class preprocesses
#    raw text (whitespace normalization, sentence splitting, tokenization,
#    lemmatization + POS tagging), computes lexical diversity (MTLD, MATTR),
#    and identifies/counts connectors (conjunctions, subjunctions, adverbial
#    connectors) based on predefined connector lists.
# ==========================================


from collections import Counter
import nltk
#nltk.download("punkt")
#nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import spacy
import statistics as stats
import re

from resources.list_basic_vocabulary import list_basic_vocabulary
from resources.list_connectors import list_connectors


class Text:
    """
    Represents a German text and provides basic linguistic analysis.
    """

    def __init__(self, id: str, text: str):
        self.id = id

        self.text = self.get_text_stats(text)[0]

        self.words = self.get_text_stats(text)[2]
        self.word_count = len(self.get_text_stats(text)[2])
        self.dif_word_count = len(set(self.get_text_stats(text)[3]))
        self.lemma_pos = self.get_text_stats(text)[3]
        self.word_mtld = self.get_mtld(self.lemma_pos)  #[x for x, _ in self.lemma_po])
        self.word_mattr = self.get_mattr(self.lemma_pos)

        self.sentences = self.get_text_stats(text)[1]
        self.sentence_count = len(self.get_text_stats(text)[1])
        self.sentence_lenght = round(self.word_count / self.sentence_count, 2)
        self.sentence_length_stats = self.get_sentence_length_stats(short_lt=6, long_gt=25)

        self.all_connectors = list_connectors()
        self.connectors = self.get_connector_stats()
        self.connector_count = len(self.get_connector_stats()[0])
        self.connector_count_type = [len(lst) for lst in self.get_connector_stats()[1]]
        self.dif_connector_count_type = [len(set(lst)) for lst in self.get_connector_stats()[1]]
        self.connector_per_sentence = round(self.connector_count / self.sentence_count, 2)
        self.connector_stats = self.get_connector_stats()[3]
        self.connector_score_level = self.get_connector_stats()[2]


    def get_text_stats(self, text: str):
        """
        Preprocess a German text and return multiple linguistic representations.

        The function normalizes whitespace, segments the text into sentences,
        tokenizes alphabetic word forms, and performs lemmatization with
        part-of-speech tagging using spaCy.

        Processing steps
        ----------------
        1. Normalize whitespace (collapse multiple spaces into a single space).
        2. Segment the text into German sentences using NLTK.
        3. Tokenize the text into alphabetic word forms (no punctuation or digits).
        4. Lemmatize alphabetic tokens and assign coarse-grained POS tags
        using the spaCy German language model.

        Parameters
        ----------
        text : str
            Raw input text in German.

        Returns
        -------
        tuple
            A tuple containing:
            - text : str
                The normalized plain text.
            - sentences : list of str
                Sentence strings obtained via German sentence segmentation.
            - words : list of str
                Alphabetic word tokens (surface forms) in sequential order.
            - lemma_pos : list of tuples [str, str]
                Tuples of (lemma, POS) for each alphabetic token, with lemmas
                lowercased.
        """

        # plain text
        text = re.sub(r"\s+", " ", text)

        # list sentences
        sentences = sent_tokenize(text, language="german")

        # list words
        words = [w for w in word_tokenize(text, language="german") if w.isalpha()]

        # list words (lemma, pos)
        nlp = spacy.load("de_core_news_sm")  # md = medium, lg = large
        doc = nlp(text)
        for token in doc:
            if token.is_alpha:
                lemma_pos = [
                    (token.lemma_.lower(), token.pos_)
                    for token in doc
                    if token.is_alpha
                ]

        return [text, sentences, words, lemma_pos]


    def get_sentence_length_stats(self, short_lt: int = 6, long_gt: int = 25) -> dict:
        """
        Compute sentence length statistics.

        Parameters
        ----------
        short_lt : int
            Threshold: sentences with fewer than this number of words are "short".
        long_gt : int
            Threshold: sentences with more than this number of words are "long".

        Returns
        -------
        dict
            Sentence length metrics (mean/median/std/min/max + share short/long).
        """
        if not self.sentences:
            return {
                "n_sentences": 0,
                "lengths": [],
                "mean": 0,
                "median": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "short_lt": short_lt,
                "long_gt": long_gt,
                "share_short": 0,
                "share_long": 0,
            }

        lengths = []
        for s in self.sentences:
            ws = [w for w in word_tokenize(s, language="german") if w.isalpha()]
            lengths.append(len(ws))

        n = len(lengths)
        mean = sum(lengths) / n
        median = stats.median(lengths)
        std = stats.pstdev(lengths)
        min_len = min(lengths)
        max_len = max(lengths)

        short_count = sum(1 for L in lengths if L < short_lt)
        long_count = sum(1 for L in lengths if L > long_gt)

        return {
            "n_sentences": n,
            "lengths": lengths,
            "mean": round(mean, 2),
            "median": round(median, 2),
            "std": round(std, 2),
            "min": min_len,
            "max": max_len,
            "short_lt": short_lt,
            "long_gt": long_gt,
            "share_short": round(short_count / n, 3),
            "share_long": round(long_count / n, 3),
        }


    def get_connector_stats(self) -> list:
        """
        Extract connectors from lemma/POS tuples, compute a CEFR-based connector score,
        and compute connector frequency statistics.

        Returns
        -------
        list
            [connectors, connector_type, connector_score, stats]
            where stats is a dict with percentages for connectors used once and >3 times.
        """

        connectors = []
        connector_type = [[], [], []]
        connector_score = []
        KONJUNKTIONEN = list(self.all_connectors[0])
        SUBJUNKTIONEN = list(self.all_connectors[1])
        KONJUNKTIONALADVERBIEN = list(self.all_connectors[2])
        CONNECTOR_LEVEL = ((self.all_connectors[0] |
                           self.all_connectors[1]) |
                           self.all_connectors[2])

        for token in self.lemma_pos:
            if token[0] in KONJUNKTIONEN and token[1] == "CCONJ":
                connectors.append(token[0])
                connector_type[0].append(token[0])
                connector_score.append(CONNECTOR_LEVEL[token[0]])
            elif token[0] in SUBJUNKTIONEN and token[1] == "SCONJ":
                connectors.append(token[0])
                connector_type[1].append(token[0])
                connector_score.append(CONNECTOR_LEVEL[token[0]])
            elif token[0] in KONJUNKTIONALADVERBIEN and token[1] == "ADV":
                connectors.append(token[0])
                connector_type[2].append(token[0])
                connector_score.append(CONNECTOR_LEVEL[token[0]])
        connector_score = self.get_score_levels(connector_score)

        freq = Counter(connectors)  # counts per connector token
        unique_used = len(freq)  # number of distinct connectors used

        if unique_used == 0:
            pct_once = 0.0
            pct_more_than_3 = 0.0
        else:
            once = sum(1 for c in freq.values() if c == 1)
            more_than_3 = sum(1 for c in freq.values() if c > 3)

            pct_once = round((once / unique_used) * 100, 2)
            pct_more_than_3 = round((more_than_3 / unique_used) * 100, 2)

        stats = {
            "unique_connectors_used": unique_used,
            "pct_connectors_used_once": pct_once,
            "pct_connectors_used_more_than_3": pct_more_than_3,
        }

        return [connectors, connector_type, connector_score, stats]


    def get_score_levels(self, levels: list[str]) -> float:
        """
        Convert CEFR levels (A1–C2) into numeric scores and return the total.

        Parameters
        ----------
        levels : list of str
            CEFR level labels (e.g., ["A2", "B1", "C1"]).

        Returns
        -------
        float
            Average numeric CEFR score
        """


        LEVEL_SCORES = {
            "A1": 0,
            "A2": 1,
            "B1": 2,
            "B2": 3,
            "C1": 4,
            "C2": 5,
        }
        total = 0

        for level in levels:
            total += LEVEL_SCORES.get(level, 0)
        score = total / len(levels)

        return score


    def get_mtld(self, tokens: list[str], t=0.72) -> float:
        """
        Compute the Measure of Textual Lexical Diversity (MTLD) for a tokenized text.

        MTLD estimates lexical diversity by measuring the average length of
        sequential word segments that maintain a type–token ratio (TTR)
        above a given threshold. The final MTLD value is calculated as the
        total number of tokens divided by the number of completed and partial
        segments ("factors").

        Parameters
        ----------
        tokens : list of str
            A list of word tokens representing the text in sequential order.
            Tokens should be preprocessed consistently (e.g., lowercased,
            punctuation removed, optional lemmatization).
        t : float, optional (default=0.72)
            The TTR threshold at which a segment is considered complete.
            The value 0.72 is the standard used in most MTLD studies.

        Returns
        -------
        float
            The MTLD value. Higher values indicate greater lexical diversity.
            Returns 0.0 if the text is too short to form any segment.

        References
        ----------
        McCarthy, P. M., & Jarvis, S. (2010).
        MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches
        to lexical diversity assessment.
        Behavior Research Methods, 42(2), 381–392.
        """

        factors = 0.0
        types = set()
        seg_len = 0

        for token in tokens:
            seg_len += 1
            types.add(token)
            ttr = len(types) / seg_len
            if ttr <= t:
                factors += 1.0
                types.clear()
                seg_len = 0

        # partial factor
        if seg_len > 0:
            ttr_end = len(types) / seg_len
            # avoid division issues if t==1
            partial = (1.0 - ttr_end) / (1.0 - t)
            factors += partial

        #return len(tokens) / factors if factors > 0 else 0.0
        # bidirectional
        return round((len(tokens) / factors if factors > 0 else 0.0 +
               self.get_mtld(list(reversed(tokens)), t)) / 2, 2)


    def get_mattr(self, tokens: list[str], window_size=50) -> float:
        """
        Compute the Moving-Average Type–Token Ratio (MATTR) for a tokenized text.

        MATTR is a lexical diversity measure that reduces the strong text-length
        dependency of the simple Type–Token Ratio (TTR) by computing TTR over a
        sliding window of fixed size and averaging across all windows.

        Parameters
        ----------
        tokens : list of str
            A list of word tokens in sequential order (e.g., already lowercased and
            consistently preprocessed).
        window_size : int, optional (default=50)
            The size (in tokens) of the sliding window. Common values are 25–100.

        Returns
        -------
        float
            The MATTR value in the range (0, 1]. Higher values indicate greater
            lexical diversity.
            If the text length is shorter than `window_size`, returns the simple
            TTR over the whole text (types / tokens). If `tokens` is empty,
            returns 0.0.

        References
        ----------
        McCarthy, P. M., & Jarvis, S. (2010).
        MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches
        to lexical diversity assessment.
        Behavior Research Methods, 42(2), 381–392.
        """

        n = len(tokens)
        if n == 0:
            return 0.0

        # If the text is shorter than the window, fall back to simple TTR.
        if n < window_size:
            return len(set(tokens)) / n

        # Initial window
        ttrs_sum = 0.0
        num_windows = 0

        # Compute TTR for each window and average.
        for i in range(0, n - window_size + 1):
            window = tokens[i:i + window_size]
            ttrs_sum += len(set(window)) / window_size
            num_windows += 1

        return round(ttrs_sum / num_windows, 2)
