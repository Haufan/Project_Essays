# ==========================================
# File: class_Text.py
# Author: Dietmar Benndorf
# Date: 2026-01-06
# Description:
#    Provides a Text class for basic German text analysis. The class preprocesses
#    raw text (whitespace normalization, sentence splitting, tokenization,
#    lemmatization + POS tagging), computes lexical diversity (MTLD, MATTR),
#    and identifies/counts connectors (conjunctions, subjunctions, adverbial
#    connectors) based on predefined connector lists.
# ==========================================


import nltk
#nltk.download("punkt")
#nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import spacy
import re

from list_connectors import list_connectors


class Text:
    """
    Represents a German text and provides basic linguistic analysis.
    """

    def __init__(self, id: str, text: str):
        self.id = id
        self.text = self.text_processing(text)[0]
        self.sentences = self.text_processing(text)[1]
        self.sentence_count = len(self.text_processing(text)[1])
        self.words = self.text_processing(text)[2]
        self.word_count = len(self.text_processing(text)[2])
        self.sentence_lenght = round(self.word_count / self.sentence_count, 2)
        self.dif_word_count = len(set(self.text_processing(text)[3]))
        self.lemma_pos = self.text_processing(text)[3] #CCONJ = Konjunktion, SCONJ = Subjunktion, ADV = Konjunktionaladverbien
        self.word_mtld = self.mtld(self.lemma_pos)  #[x for x, _ in self.lemma_po])
        self.word_mattr = self.mattr(self.lemma_pos)
        self.all_connectors = list_connectors()
        self.connectors = self.connector_processing()
        self.connector_count = len(self.connector_processing()[0])
        self.dif_connector_count = len(set(self.connector_processing()[0]))


    def text_processing(self, text):
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


    def connector_processing(self):
        """
        ???
        :return:
        """

        connectors = []
        connector_counter = [0, 0, 0]
        KONJUNKTIONEN = [x for x, _ in self.all_connectors[0]]
        SUBJUNKTIONEN = [x for x, _ in self.all_connectors[1]]
        KONJUNKTIONALADVERBIEN = [x for x, _ in self.all_connectors[2]]

        for token in self.lemma_pos:
            if token[0] in KONJUNKTIONEN:
                connectors.append(token[0])
                connector_counter[0] += 1
            elif token[0] in SUBJUNKTIONEN:
                connectors.append(token[0])
                connector_counter[1] += 1
            elif token[0] in KONJUNKTIONALADVERBIEN:
                connectors.append(token[0])
                connector_counter[2] += 1

        return [connectors, connector_counter]


    def mtld(self, tokens, t=0.72):
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
               self.mtld(list(reversed(tokens)), t)) / 2, 2)


    def mattr(self, tokens, window_size=50):
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
