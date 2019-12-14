#!/usr/bin/env python3

import regex as re

from somajo import token
from somajo import utils


class SentenceSplitter():
    def __init__(self, is_tuple=False, language="de_CMC"):
        """Create a SentenceSplitter object. If the tokenized paragraphs
        contain token classes or extra info, set is_tuple=True.

        """
        self.is_tuple = is_tuple
        # full stop, ellipsis, exclamation and question marks
        self.sentence_ending_punct = re.compile(r"^(?:\.+|…+\.*|[!?]+)$")
        self.opening_punct = re.compile(r"^(?:['\"¿¡\p{Pi}\p{Ps}–—]|-{2,})$")
        if language == "de" or language == "de_CMC":
            self.closing_punct = re.compile(r"^(?:['\"“\p{Pf}\p{Pe}])$")
        else:
            self.closing_punct = re.compile(r"^(?:['\"\p{Pf}\p{Pe}])$")
        self.eos_abbreviations = utils.read_abbreviation_file("eos_abbreviations.txt")

    def split(self, tokenized_paragraph, legacy=True):
        """Split tokenized_paragraph into sentences."""
        if legacy:
            if self.is_tuple:
                tokens = [token.Token(t[0]) for t in tokenized_paragraph]
            else:
                tokens = [token.Token(t) for t in tokenized_paragraph]
        tokens = self._split(tokens)
        sentence_boundaries = [i for i, t in enumerate(tokens, start=1) if t.last_in_sentence]
        return [tokenized_paragraph[i:j] for i, j in zip([0] + sentence_boundaries[:-1], sentence_boundaries)]

    def split_xml(self, tokenized_xml, eos_tags=set(), legacy=True):
        """Split tokenized XML into sentences."""
        n = len(tokenized_xml)
        if legacy:
            opening_tag = re.compile(r"""<(?:[^\s:]+:)?([_A-Z][-.\w]*)(?:\s+[_:A-Z][-.:\w]*\s*=\s*(?:"[^"]*"|'[^']*'))*\s*/?>""", re.IGNORECASE)
            closing_tag = re.compile(r"^</([_:A-Z][-.:\w]*)\s*>$", re.IGNORECASE)
            if self.is_tuple:
                tokens = [token.Token(t[0]) for t in tokenized_xml]
            else:
                tokens = [token.Token(t) for t in tokenized_xml]
            first_token_in_sentence = True
            for i, t in enumerate(tokens):
                opening = opening_tag.search(t.text)
                closing = closing_tag.search(t.text)
                if opening:
                    t.markup = True
                    t.markup_class = "start"
                    tagname = opening.group(1)
                if closing:
                    t.markup = True
                    t.markup_class = "end"
                    tagname = closing.group(1)
                if t.markup:
                    if tagname in eos_tags:
                        # previous non-markup is last_in_sentence
                        for j in range(i - 1, -1, -1):
                            if not tokens[j].markup:
                                tokens[j].last_in_sentence = True
                                break
                        # next non-markup is first_in_sentence
                        first_token_in_sentence = True
                    continue
                if first_token_in_sentence:
                    t.first_in_sentence = True
                    first_token_in_sentence = False
        else:
            tokens = tokenized_xml
        tokens = self._split(tokens)
        sentence_boundaries = []
        for i, t in enumerate(tokens):
            if t.last_in_sentence:
                boundary = i
                for j in range(i + 1, n):
                    if tokens[j].markup_class == "end":
                        boundary += 1
                    else:
                        break
                sentence_boundaries.append(boundary + 1)
        if len(sentence_boundaries) == 0:
            sentence_boundaries.append(n)
        if sentence_boundaries[-1] != n:
            sentence_boundaries[-1] = n
        return [tokenized_xml[i:j] for i, j in zip([0] + sentence_boundaries[:-1], sentence_boundaries)]

    def _split(self, tokens):
        """Split tokens into sentences."""
        n = len(tokens)
        # the last non-markup token is last_in_sentence
        for tok in reversed(tokens):
            if not tok.markup:
                tok.last_in_sentence = True
                break
        for i, tok in enumerate(tokens):
            if tok.markup:
                continue
            if tok.last_in_sentence:
                continue
            if self.sentence_ending_punct.search(tok.text) or tok.text.lower() in self.eos_abbreviations:
                last = None
                last_token_in_sentence = tok
                first_token_in_sentence = None
                for j in range(i + 1, n):
                    tok_j = tokens[j]
                    if tok_j.markup:
                        continue
                    if first_token_in_sentence is None:
                        first_token_in_sentence = tok_j
                    if tok_j.text[0].isupper():
                        last_token_in_sentence.last_in_sentence = True
                        first_token_in_sentence.first_in_sentence = True
                        break
                    elif self.opening_punct.search(tok_j.text) and tok_j.text != "“":
                        last = "opening"
                    elif self.closing_punct.search(tok_j.text) and last != "opening":
                        last_token_in_sentence = tok_j
                        first_token_in_sentence = None
                        last = "closing"
                    else:
                        break
        return tokens
