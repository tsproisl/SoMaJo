#!/usr/bin/env python3

import itertools
import multiprocessing

from somajo import doubly_linked_list
from somajo import utils
from somajo.sentence_splitter import SentenceSplitter
from somajo.token import Token
from somajo.tokenizer import Tokenizer


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

    def _tokenize(self, token_dlls, parallel=1):
        if parallel > 1:
            pool = multiprocessing.Pool(min(parallel, multiprocessing.cpu_count()))
            tokens = pool.imap(self.tokenizer._tokenize, token_dlls, 250)
            # tokenized = map(self._tokenize, paragraphs)
            if self.split_sentences:
                tokens = pool.imap(self._sentence_splitter._split_sentences, tokens, 250)
                tokens = itertools.chain.from_iterable(tokens)
        else:
            tokens = map(self._tokenizer._tokenize, token_dlls)
            if self.split_sentences:
                tokens = map(self._sentence_splitter._split_sentences, tokens)
                tokens = itertools.chain.from_iterable(tokens)
        return tokens

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
                token_dlls = utils.get_paragraphs_dll(fh, paragraph_separator)
        else:
            token_dlls = utils.get_paragraphs_dll(text_file, paragraph_separator)
        tokens = self._tokenize(token_dlls, parallel)
        return tokens

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
        if eos_tags is not None:
            eos_tags = set(eos_tags)
        token_dlls = utils.xml_chunk_generator(xml_file, is_file=True, eos_tags=eos_tags)
        tokens = self._tokenize(token_dlls, parallel)
        tokens = map(utils.escape_xml_tokens, tokens)
        if strip_tags:
            tokens = ([t for t in par if not t.markup] for par in tokens)
        return tokens

    def tokenize_text(self, paragraph):
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
        token_dll = doubly_linked_list.DLL([Token(paragraph, first_in_sentence=True, last_in_sentence=True)])
        tokens = self._tokenize([token_dll], parallel=1)
        if not self.split_sentences:
            tokens = itertools.chain.from_iterable(tokens)
        return tokens

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
        token_dlls = utils.xml_chunk_generator(xml_data, is_file=False, eos_tags=eos_tags)
        tokens = self._tokenize(token_dlls, parallel)
        tokens = list(tokens)
        tokens = map(utils.escape_xml_tokens, tokens)
        if strip_tags:
            tokens = ([t for t in par if not t.markup] for par in tokens)
        return tokens
