#!/usr/bin/env python3

import regex as re

from somajo import utils


class SentenceSplitter(object):
    def __init__(self, is_tuple=False):
        """Create a SentenceSplitter object. If the tokenized paragraphs
        contain token classes or extra info, set is_tuple=True.

        """
        self.is_tuple = is_tuple
        # full stop, ellipsis, exclamation and question marks
        self.sentence_ending_punct = re.compile(r"^(?:\.+|…+\.*|[!?]+)$")
        self.opening_punct = re.compile(r"^(?:['\"¿¡\p{Pi}\p{Ps}–—]|-{2,})$")
        self.closing_punct = re.compile(r"^(?:['\"“\p{Pf}\p{Pe}])$")
        self.eos_abbreviations = utils.read_abbreviation_file("eos_abbreviations.txt")

    def split(self, tokenized_paragraph):
        """Split tokenized_paragraph into sentences."""
        sentence_boundaries = []
        paragraph_length = len(tokenized_paragraph)
        tokens = tokenized_paragraph
        # closing* opening* upper
        if self.is_tuple:
            tokens = [t[0] for t in tokenized_paragraph]
        for i, token in enumerate(tokens):
            if self.sentence_ending_punct.search(token) or token.lower() in self.eos_abbreviations:
                last = None
                boundary = i + 1
                for j in range(i + 1, paragraph_length):
                    token_j = tokens[j]
                    if token_j[0].isupper():
                        sentence_boundaries.append(boundary)
                        break
                    elif self.opening_punct.search(token_j) and token_j != "“":
                        last = "opening"
                    elif self.closing_punct.search(token_j) and last != "opening":
                        boundary = j + 1
                        last = "closing"
                    else:
                        break
        return [tokenized_paragraph[i:j] for i, j in zip([0] + sentence_boundaries, sentence_boundaries + [paragraph_length])]
