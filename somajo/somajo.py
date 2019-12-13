#!/usr/bin/env python3

from somajo.tokenizer import Tokenizer
from somajo.sentence_splitter import SentenceSplitter


class SoMaJo:
    """Tokenization and sentence splitting.

    Parameters
    ----------
    language : {'de_CMC' or 'en_PTB'}
        Language-specific tokenization rules.
    split_camel_case : bool, (default=False)
        Split words written in camelCase (excluding established names and terms).
    split_sentences : bool, (default=True)
        Perform sentence splitting in addition to tokenization.

    """

    _supported_languages = set(["de_CMC", "en_PTB"])
    _paragraph_separators = set(["single_newline", "empty_line"])

    def __init__(self, language, *, split_camel_case=False, split_sentences=True):
        assert language in self._supported_languages
        self.language = language
        self.split_camel_case = split_camel_case
        self.split_sentences = split_sentences
        self._tokenizer = Tokenizer(split_camel_case=self.split_camel_case, language=self.language)
        if self.split_sentences:
            self._sentence_splitter = SentenceSplitter(language=self.language)

    def tokenize_text_file(self, text_file, paragraph_separator):
        """Split the contents of a text file into sequences of tokens.

        Parameters
        ----------
        text_file : {str, file-like object}
            A file containing text. Either a filename or a file-like
            object.
        paragraph_separator : {'single_newline', 'empty_line'}, (default='empty_line')
            How are paragraphs separated in the input? Is there one
            paragraph per line ('single_newline') or do paragraphs
            span several lines and are separated by an 'empty_line'?

        Yields
        -------
        list
            The ``Token`` objects in a single sentence or paragraph
            (depending on the value of ``split_sentences``).

        """
        assert paragraph_separator in self._paragraph_separators

    def tokenize_xml_file(self, xml_file, eos_tags, strip_tags=False):
        """Split the contents of an xml file into sequences of tokens.

        Parameters
        ----------
        xml_file : {str, file-like object}
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
            sentences or the whole paragraph as a single element. Each
            element of the list is a list of ``Token`` objects.

        """
        pass

    def tokenize_xml(self, xml_data, eos_tags, *, strip_tags=False):
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
        pass
