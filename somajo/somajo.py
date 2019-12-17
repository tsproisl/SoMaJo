#!/usr/bin/env python3

import functools
import itertools

from somajo.tokenizer import Tokenizer
from somajo.sentence_splitter import SentenceSplitter
from somajo import utils


class SoMaJo:
    """Tokenization and sentence splitting.

    Parameters
    ----------
    language : {'de_CMC', 'en_PTB'}
        Language-specific tokenization rules.
    split_camel_case : bool, (default=False)
        Split words written in camelCase (excluding established names and terms).
    split_sentences : bool, (default=True)
        Perform sentence splitting in addition to tokenization.

    """

    supported_languages = set(["de_CMC", "en_PTB"])
    _default_language = "de_CMC"
    paragraph_separators = set(["empty_lines", "single_newlines"])
    _default_parsep = "empty_lines"

    def __init__(self, language, *, split_camel_case=False, split_sentences=True):
        assert language in self.supported_languages
        self.language = language
        self.split_camel_case = split_camel_case
        self.split_sentences = split_sentences
        self._tokenizer = Tokenizer(split_camel_case=self.split_camel_case, language=self.language)
        if self.split_sentences:
            self._sentence_splitter = SentenceSplitter(language=self.language)

    def tokenize_text_file(self, text_file, paragraph_separator, *, parallel=1):
        """Split the contents of a text file into sequences of tokens.

        Parameters
        ----------
        text_file : str or file-like object
            A file containing text. Either a filename or a file-like
            object.
        paragraph_separator : {'single_newlines', 'empty_lines'}
            How are paragraphs separated in the input? Is there one
            paragraph per line ('single_newlines') or do paragraphs
            span several lines and are separated by 'empty_lines'?

        Yields
        -------
        list
            The ``Token`` objects in a single sentence or paragraph
            (depending on the value of ``split_sentences``).

        """
        assert paragraph_separator in self.paragraph_separators
        if isinstance(text_file, str):
            with open(text_file, encoding="utf-8") as fh:
                paragraphs = utils.get_paragraphs(fh, paragraph_separator)
        else:
            paragraphs = utils.get_paragraphs(text_file, paragraph_separator)
        tokenize_paragraph = functools.partial(self._tokenizer.tokenize_paragraph, legacy=False)
        tokenized = map(tokenize_paragraph, paragraphs)
        if self.split_sentences:
            tokenized = map(self._sentence_splitter._split, tokenized)
            tokenized = itertools.chain.from_iterable(tokenized)
        return tokenized

    def tokenize_xml_file(self, xml_file, eos_tags, *, strip_tags=False, parallel=1):
        """Split the contents of an xml file into sequences of tokens.

        Parameters
        ----------
        xml_file : str or file-like object
            A file containing XML data. Either a filename or a
            file-like object.
        eos_tags : iterable
            XML tags that constitute sentence breaks, i.e. tags that
            do not occur in the middle of a sentence. For HTML input,
            you might use the following list of tags: ``['title',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
            'div', 'ol', 'ul', 'dl', 'table']``
        strip_tags : bool, (default=False)
            Remove the XML tags from the output.

        Yields
        -------
        list
            The ``Token`` objects in a single sentence or stretch of
            XML delimited by ``eos_tags`` (depending on the value of
            ``split_sentences``).

        """
        eos_tags = set(eos_tags)
        tokenized = self._tokenizer.tokenize_xml(xml_file, is_file=True, eos_tags=eos_tags, legacy=False)
        if strip_tags:
            tokenized = ([t for t in par if not t.markup] for par in tokenized)
        if self.split_sentences:
            sentence_splitter = functools.partial(self._sentence_splitter.split_xml, legacy=False)
            tokenized = map(sentence_splitter, tokenized)
            tokenized = itertools.chain.from_iterable(tokenized)
        return tokenized

    def tokenize_text(self, paragraph, *, parallel=1):
        """Split a paragraph of text into (sequences of) tokens.

        Parameters
        ----------
        paragraph : str
            A single paragraph of text.

        Returns
        -------
        list

            Depending on the value of ``split_sentences`` either
            sentences (where each sentence is a list of ``Token``
            objects) or ``Token`` objects.

        """
        tokenized = self._tokenizer.tokenize_paragraph(paragraph, legacy=False)
        if self.split_sentences:
            tokenized = self._sentence_splitter._split(tokenized)
            tokenized = itertools.chain.from_iterable(tokenized)
        return tokenized

    def tokenize_xml(self, xml_data, eos_tags, *, strip_tags=False, parallel=1):
        """Split a string of XML data into sequences of tokens.

        Parameters
        ----------
        xml_data : str
            A string containing XML data.
        eos_tags : iterable
            XML tags that constitute sentence breaks, i.e. tags that
            do not occur in the middle of a sentence. For HTML input,
            you might use the following list of tags: ``['title',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
            'div', 'ol', 'ul', 'dl', 'table']``
        strip_tags : bool, (default=False)
            Remove the XML tags from the output.

        Returns
        -------
        list
            Depending on the value of ``split_sentences`` either
            sentences or stretches of XML delimited by ``eos_tags``.
            Each element of the list is a list of ``Token`` objects.

        """
        if eos_tags is not None:
            eos_tags = set(eos_tags)
        tokenized = self._tokenizer.tokenize_xml(xml_data, is_file=False, eos_tags=eos_tags, legacy=False)
        if strip_tags:
            tokenized = ([t for t in par if not t.markup] for par in tokenized)
        if self.split_sentences:
            sentence_splitter = functools.partial(self._sentence_splitter.split_xml, legacy=False)
            tokenized = map(sentence_splitter, tokenized)
            tokenized = itertools.chain.from_iterable(tokenized)
        return tokenized
