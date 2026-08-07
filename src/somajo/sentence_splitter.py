#!/usr/bin/env python3

from __future__ import annotations

import collections
from typing import Iterable, Iterator, cast

import regex as re

from . import doubly_linked_list, token, utils


class SentenceSplitter:
    """Sentence splitter for tokenized text.

    Args:
        is_tuple: If the tokenized paragraphs contain token classes or extra info,
            set is_tuple=True. Defaults to False.
        language: Language for sentence splitting. Defaults to "de_CMC".

    """

    def __init__(self, is_tuple: bool = False, language: str = "de_CMC") -> None:
        self.is_tuple = is_tuple
        # full stop, ellipsis, exclamation and question marks
        self.sentence_ending_punct = re.compile(r"^(?:\.+|…+\.*|[!?]+)$")
        self.opening_punct = re.compile(r"^(?:['\"¿¡\p{Pi}\p{Ps}–—]|-{2,})$")
        self.closing_punct = re.compile(r"^(?:['\"\p{Pf}\p{Pe}])$")
        # International quotes: «» “” ‹› ‘’
        # German quotes: »« „“ ›‹ ‚‘
        self.problematic_quotes = {'"'}
        if language == "de" or language == "de_CMC":
            # German opening quotes [»›] have category Pf
            # German closing quotes [“‘«‹] have category Pi
            self.problematic_quotes = {'"', "»", "«", "›", "‹", "“", "‘"}
        self.eos_abbreviations = utils.read_abbreviation_file("eos_abbreviations.txt")
        # We match these via regular expressions because users could
        # call the split or split_xml methods with pretokenized input
        # that does not have SoMaJo token classes
        self.mention = re.compile(r'^[@]\w+$')
        self.hashtag = re.compile(r'^[#]\w(?:[\w-]*\w)?$')

    def _get_sentence_boundaries(self, tokens: list[token.Token]) -> list[int]:
        """Get sentence boundary positions from tokens.

        Args:
            tokens: List of Token objects.

        Returns:
            list: List of boundary indices.

        """
        sentence_boundaries = []
        n = len(tokens)
        for i, t in enumerate(tokens, start=1):
            if t.last_in_sentence:
                boundary = i
                for j in range(i, n):
                    if tokens[j].markup_class == "end":
                        boundary += 1
                    else:
                        break
                sentence_boundaries.append(boundary)
        if len(sentence_boundaries) == 0:
            sentence_boundaries.append(n)
        if sentence_boundaries[-1] != n:
            sentence_boundaries[-1] = n
        return sentence_boundaries

    def _add_xml_tags(self, tokens: Iterable[list[token.Token]], s_tag: str = "s") -> Iterator[list[token.Token]]:
        """Mark sentence boundaries with XML tags.

        Args:
            tokens: Iterable of token lists (sentences).
            s_tag: Tag name for sentence markers. Defaults to "s".

        Yields:
            list: Token lists with XML sentence tags added.

        """
        # Positions of XML tags w.r.t. the actual sentence:
        start, inside, end, na = 1, 2, 3, 4
        open_tags: collections.deque[dict[str, str | int | doubly_linked_list.DLLElement | None]] = collections.deque()
        reopen_after_start: collections.deque[dict[str, str | int | doubly_linked_list.DLLElement | None]] = collections.deque()
        reopen_after_end: collections.deque[dict[str, str | int | doubly_linked_list.DLLElement | None]] = collections.deque()
        start_tag = re.compile(r"^<([^ ]+)[ ]?[^>]*>$")
        end_tag = re.compile(r"^</(.+)>$")
        for sentence in tokens:
            # print([(t.text, t.first_in_sentence, t.last_in_sentence) for t in sentence])
            sentence_dll = doubly_linked_list.DLL(sentence)
            position = start
            tags: collections.deque[dict[str, str | int | doubly_linked_list.DLLElement | None]] = collections.deque()
            first_token: doubly_linked_list.DLLElement | None = None
            last_token: doubly_linked_list.DLLElement | None = None
            for tag in reversed(reopen_after_end):
                top = open_tags.pop()
                assert top is tag
            while len(reopen_after_end) > 0:
                tag = reopen_after_end.pop()
                assert isinstance(sentence_dll.first, doubly_linked_list.DLLElement)  # for mypy
                sentence_dll.insert_left(tag["start_token"], sentence_dll.first)
            for tok in sentence_dll:
                if tok.value.markup:
                    # better store tag name in Token object
                    if tok.value.markup_class == "start":
                        m = start_tag.search(tok.value.text)
                        assert m
                        tag_name = m.group(1)
                        tag = {"tag_name": tag_name, "start_token": tok, "end_token": None, "start": position, "end": na}
                        open_tags.append(tag)
                        tags.append(tag)
                    elif tok.value.markup_class == "end":
                        m = end_tag.search(tok.value.text)
                        assert m
                        tag_name = m.group(1)
                        top = open_tags.pop()
                        assert tag_name == top["tag_name"]
                        top["end_token"] = tok
                        top["end"] = position
                        if top["start"] == na:
                            tags.appendleft(top)
                if tok.value.first_in_sentence:
                    position = inside
                    first_token = tok
                if tok.value.last_in_sentence:
                    position = end
                    last_token = tok
            if first_token is None:
                yield sentence_dll.to_list()
                continue
            s_start = first_token  # left of first token
            s_end = last_token     # right of last token
            lot = sentence_dll.last
            for tag in tags:
                # print(tag)
                if tag["start"] == na:
                    if tag["end"] == inside:
                        ft = sentence_dll.first
                        assert isinstance(ft, doubly_linked_list.DLLElement)  # for mypy
                        # close tag
                        closing_tag = token.Token("</%s>" % tag["tag_name"], markup=True, markup_class="end", markup_eos=False, locked=True)
                        sentence_dll.insert_left(closing_tag, ft)
                        # put starting s-tag to the right
                        assert isinstance(ft.prev, doubly_linked_list.DLLElement)  # for mypy
                        assert sentence_dll.is_right_of(s_start, ft.prev)
                        # re-open tag
                        reopen_after_start.append(tag)
                elif tag["start"] == start:
                    if tag["end"] == inside:
                        # put starting s-tag to the left
                        assert isinstance(tag["start_token"], doubly_linked_list.DLLElement)  # for mypy
                        if not sentence_dll.is_left_of(s_start, tag["start_token"]):
                            s_start = tag["start_token"]
                elif tag["start"] == inside:
                    if tag["end"] == end:
                        # put ending s-tag to the right
                        assert isinstance(s_end, doubly_linked_list.DLLElement)  # for mypy
                        assert isinstance(tag["end_token"], doubly_linked_list.DLLElement)  # for mypy
                        if not sentence_dll.is_right_of(s_end, tag["end_token"]):
                            s_end = tag["end_token"]
                    elif tag["end"] == na:
                        # close tag
                        closing_tag = token.Token("</%s>" % tag["tag_name"], markup=True, markup_class="end", markup_eos=False, locked=True)
                        assert isinstance(lot, doubly_linked_list.DLLElement)  # for mypy
                        sentence_dll.insert_right(closing_tag, lot)
                        # put ending s-tag
                        assert isinstance(s_end, doubly_linked_list.DLLElement)  # for mypy
                        assert isinstance(lot.next, doubly_linked_list.DLLElement)  # for mypy
                        if not sentence_dll.is_right_of(s_end, lot.next):
                            # s_end = sentence_dll.last
                            s_end = lot.next
                        # re-open tag
                        reopen_after_end.append(tag)
            # starting s-tag
            sentence_dll.insert_left(token.Token("<%s>" % s_tag, markup=True, markup_class="start", markup_eos=True, locked=True), s_start)
            while len(reopen_after_start) > 0:
                tag = reopen_after_start.popleft()
                sentence_dll.insert_left(tag["start_token"], s_start)
            # ending s-tag
            assert isinstance(s_end, doubly_linked_list.DLLElement)  # for mypy
            sentence_dll.insert_right(token.Token("</%s>" % s_tag, markup=True, markup_class="end", markup_eos=True, locked=True), s_end)
            # for all tags on the stack, change start to na
            for tag in open_tags:
                tag["start"] = na
            yield sentence_dll.to_list()
        assert len(open_tags) == 0

    def _merge_empty_sentences(self, tokens: Iterable[list[token.Token]]) -> Iterator[list[token.Token]]:
        """Merge empty sentences with preceding sentence.

        Args:
            tokens: Iterable of token lists (sentences).

        Yields:
            list: Merged token lists.

        """
        empty_first = True
        previous: list[token.Token] = []
        for sentence in tokens:
            empty_sentence = not any([tok.first_in_sentence for tok in sentence])
            if empty_first:
                previous.extend(sentence)
                empty_first = empty_sentence
            else:
                if empty_sentence:
                    previous.extend(sentence)
                else:
                    yield previous
                    previous = sentence
        yield previous

    def _split_sentences(self, tokens: list[token.Token]) -> list[list[token.Token]]:
        """Split list of Token objects into sentences.

        Args:
            tokens: List of Token objects.

        Returns:
            list: List of token lists, one per sentence.

        """
        tokens, sentence_boundaries = self._split_token_objects(tokens)
        return [tokens[i:j] for i, j in zip([0] + sentence_boundaries[:-1], sentence_boundaries)]

    def split(self, tokenized_paragraph: list[str | tuple[str]]) -> list[list[str | tuple[str]]]:
        """Split tokenized_paragraph into sentences.

        Args:
            tokenized_paragraph: List of token strings or tuples.

        Returns:
            list: List of sentences, where each sentence is a list of tokens.

        """
        if self.is_tuple:
            tokens = [token.Token(t[0]) for t in tokenized_paragraph]
        else:
            tp = cast(list[str], tokenized_paragraph)  # for mypy
            tokens = [token.Token(t) for t in tp]
        tokens, sentence_boundaries = self._split_token_objects(tokens)
        return [tokenized_paragraph[i:j] for i, j in zip([0] + sentence_boundaries[:-1], sentence_boundaries)]

    def split_xml(self, tokenized_xml: list[str | tuple[str]], eos_tags: set[str] = set()) -> list[list[str | tuple[str]]]:
        """Split tokenized XML into sentences.

        Args:
            tokenized_xml: List of token strings or tuples.
            eos_tags: Set of XML tags that constitute sentence breaks.

        Returns:
            list: List of XML chunks, one per sentence.

        """
        opening_tag = re.compile(r"""<(?:[^\s:]+:)?([_A-Z][-.\w]*)(?:\s+[_:A-Z][-.:\w]*\s*=\s*(?:"[^"]*"|'[^']*'))*\s*/?>""", re.IGNORECASE)
        closing_tag = re.compile(r"^</([_:A-Z][-.:\w]*)\s*>$", re.IGNORECASE)
        if self.is_tuple:
            tokens = [token.Token(t[0]) for t in tokenized_xml]
        else:
            tx = cast(list[str], tokenized_xml)  # for mypy
            tokens = [token.Token(t) for t in tx]
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
        tokens, sentence_boundaries = self._split_token_objects(tokens)
        return [tokenized_xml[i:j] for i, j in zip([0] + sentence_boundaries[:-1], sentence_boundaries)]

    def _split_token_objects(self, tokens: list[token.Token]) -> tuple[list[token.Token], list[int]]:
        """Split token objects into sentences.

        Args:
            tokens: List of Token objects.

        Returns:
            tuple: (tokens, sentence_boundaries) where tokens may have been modified
                and sentence_boundaries is a list of boundary indices.

        """
        n = len(tokens)
        # the first non-markup token is first_in_sentence
        for tok in tokens:
            if not tok.markup:
                tok.first_in_sentence = True
                break
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
                    opening, closing = False, False
                    if first_token_in_sentence is None:
                        first_token_in_sentence = tok_j
                    # Heuristically disambiguate problematic quotes:
                    if tok_j.text in self.problematic_quotes:
                        # opening: preceded by space or opening
                        if tokens[j - 1].space_after or self.opening_punct.search(tokens[j - 1].text):
                            opening = True
                        # closing: last token or followed by space or closing
                        elif j == n - 1 or tok_j.space_after or self.closing_punct.search(tokens[j + 1].text):
                            closing = True
                    if tok_j.text[0].isupper() or tok_j.text.isnumeric() or self.mention.search(tok_j.text) or self.hashtag.search(tok_j.text):
                        last_token_in_sentence.last_in_sentence = True
                        first_token_in_sentence.first_in_sentence = True
                        break
                    # “Emoticons are treated as non-verbal comments to
                    # the text and are thus integrated in the
                    # utterance.” (Rehbein et al. 2018: 20)
                    #
                    # This does not work with pretokenized text fed
                    # into the split and split_xml methods since their
                    # input does not have SoMaJo token classes.
                    elif tok_j.token_class == "emoticon" and last != "opening":
                        last_token_in_sentence = tok_j
                        first_token_in_sentence = None
                    elif opening or (self.opening_punct.search(tok_j.text) and not closing):
                        last = "opening"
                    elif (closing or (self.closing_punct.search(tok_j.text) and not opening)) and last != "opening":
                        last_token_in_sentence = tok_j
                        first_token_in_sentence = None
                        last = "closing"
                    else:
                        break
        sentence_boundaries = self._get_sentence_boundaries(tokens)
        return tokens, sentence_boundaries
