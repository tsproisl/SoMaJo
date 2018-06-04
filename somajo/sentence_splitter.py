#!/usr/bin/env python3

import regex as re

from somajo import utils


class SentenceSplitter(object):
    def __init__(self, is_tuple=False, language="de"):
        """Create a SentenceSplitter object. If the tokenized paragraphs
        contain token classes or extra info, set is_tuple=True.

        """
        self.is_tuple = is_tuple
        # full stop, ellipsis, exclamation and question marks
        self.sentence_ending_punct = re.compile(r"^(?:\.+|…+\.*|[!?]+)$")
        self.opening_punct = re.compile(r"^(?:['\"¿¡\p{Pi}\p{Ps}–—]|-{2,})$")
        if language == "de":
            self.closing_punct = re.compile(r"^(?:['\"“\p{Pf}\p{Pe}])$")
        else:
            self.closing_punct = re.compile(r"^(?:['\"\p{Pf}\p{Pe}])$")
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

    def split_xml(self, tokenized_xml, eos_tags):
        """Split tokenized XML into sentences."""
        tag_to_word = {}
        word_to_token = {}
        word_index = 0
        words = []
        paragraph_boundaries = set()
        opening_tag = re.compile(r"""<(?:[^\s:]+:)?([_A-Z][-.\w]*)(?:\s+[_:A-Z][-.:\w]*\s*=\s*(?:"[^"]*"|'[^']*'))*\s*/?>""", re.IGNORECASE)
        closing_tag = re.compile(r"^</([_:A-Z][-.:\w]*)\s*>$", re.IGNORECASE)
        after_word_or_closing = False
        for i, token in enumerate(tokenized_xml):
            tok = token
            if self.is_tuple:
                tok = token[0]
            opening = opening_tag.search(tok)
            closing = closing_tag.search(tok)
            if closing:
                tagname = closing.group(1)
                if after_word_or_closing:
                    tag_to_word[i] = word_index - 1
                    if tagname in eos_tags:
                        paragraph_boundaries.add(word_index)
                else:
                    tag_to_word[i] = word_index
            elif opening:
                tagname = opening.group(1)
                tag_to_word[i] = word_index
                if tagname in eos_tags:
                    paragraph_boundaries.add(word_index)
                after_word_or_closing = False
            else:
                words.append(token)
                word_to_token[word_index] = i
                after_word_or_closing = True
                word_index += 1
        tag_to_word = {t: w - 1 if w == word_index else w for t, w in tag_to_word.items()}
        tags = sorted(tag_to_word.keys(), reverse=True)
        paragraph_boundaries = sorted(paragraph_boundaries)
        paragraphs = [words[i:j] for i, j in zip([0] + paragraph_boundaries, paragraph_boundaries + [word_index]) if i != j]
        word_idx = 0
        for paragraph in paragraphs:
            for sentence in self.split(paragraph):
                out_sentence = []
                for word in sentence:
                    tok = word
                    if self.is_tuple:
                        tok = word[0]
                    token_index = word_to_token[word_idx]
                    while len(tags) > 0 and tag_to_word[tags[-1]] == word_idx and tags[-1] < token_index:
                        tag = tags.pop()
                        out_sentence.append(tokenized_xml[tag])
                    out_sentence.append(tokenized_xml[token_index])
                    while len(tags) > 0 and tag_to_word[tags[-1]] == word_idx and tags[-1] > token_index:
                        tag = tags.pop()
                        out_sentence.append(tokenized_xml[tag])
                    word_idx += 1
                yield out_sentence
