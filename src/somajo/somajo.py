#!/usr/bin/env python3

import functools
import itertools
import multiprocessing
from typing import Iterable, Iterator, Literal, TextIO

from . import (
    alignment,
    doubly_linked_list,
    utils
)
from .sentence_splitter import SentenceSplitter
from .token import Token
from .tokenizer import Tokenizer


class SoMaJo:
    """Tokenization and sentence splitting.

    Args:
        language: Language-specific tokenization rules. Must be one of 'de_CMC' or 'en_PTB'.
        split_camel_case: Split words written in camelCase (excluding established names
            and terms). Defaults to False.
        split_sentences: Perform sentence splitting in addition to tokenization.
            Defaults to True.
        xml_sentences: Delimit sentences by XML tags of this name
            (e.g., ``xml_sentences='s'`` produces <s>...</s> tags). When used with XML input,
            this might lead to minor changes to the original tags to guarantee well-formed
            output (tags might need to be closed and re-opened at sentence boundaries).
            Defaults to None.
        character_offsets: Compute the character offsets in the input for each token.
            This allows for stand-off tokenization. Defaults to False.

    """

    supported_languages: set[str] = {"de_CMC", "en_PTB"}
    _default_language: str = "de_CMC"
    paragraph_separators: set[str] = {"empty_lines", "single_newlines"}
    _default_parsep: str = "empty_lines"

    def __init__(
        self,
        language: str,
        *,
        split_camel_case: bool = False,
        split_sentences: bool = True,
        xml_sentences: str | None = None,
        character_offsets: bool = False
    ) -> None:
        assert language in self.supported_languages
        self.language = language
        self.split_camel_case = split_camel_case
        self.split_sentences = split_sentences
        self.xml_sentences = xml_sentences
        self.character_offsets = character_offsets
        self._tokenizer = Tokenizer(split_camel_case=self.split_camel_case, language=self.language)
        if self.split_sentences:
            self._sentence_splitter = SentenceSplitter(language=self.language)

    def _tokenize(self, token_info: tuple[list[Token], str, int], xml_input: bool) -> list[list[Token]]:
        """Tokenize and sentence split a single token_dll.

        Args:
            token_info: Tuple containing token list, raw text, and position.
            xml_input: Whether the input is XML.

        Returns:
            List of lists of Token objects after tokenization and
            optional sentence splitting.

        """
        token_list, raw, position = token_info
        token_dll = doubly_linked_list.DLL(token_list)
        tokens = self._tokenizer._tokenize(token_dll)
        if self.character_offsets:
            offsets = alignment.token_offsets(token_list, raw, position, xml_input, tokens)
            for i in range(len(tokens)):
                tokens[i].character_offset = offsets[i]
        if self.split_sentences:
            return self._sentence_splitter._split_sentences(tokens)
        else:
            return [tokens]

    def _parallel_tokenize(
        self,
        token_info: Iterable[tuple[list[Token], str, int]],
        *,
        parallel: int = 1,
        strip_tags: bool = False,
        xml_input: bool = False
    ) -> Iterator[list[Token]]:
        """Tokenize and sentence split an iterable of token_dlls; optional parallelization.

        Args:
            token_info: Iterable of token info tuples (token list, raw text, position).
            parallel: Number of processes to use for parallelization. Defaults to 1.
            strip_tags: Whether to strip XML tags from output. Defaults to False.
            xml_input: Whether the input is XML. Defaults to False.

        Returns:
            Iterator of lists of Token objects.

        """
        def partok():
            with multiprocessing.Pool(min(parallel, multiprocessing.cpu_count())) as pool:
                tokens = pool.imap(
                    functools.partial(self._tokenize, xml_input=xml_input),
                    token_info,
                    250
                )
                for par in tokens:
                    yield par

        if parallel > 1:
            tokens = partok()
        else:
            tokens = map(
                functools.partial(self._tokenize, xml_input=xml_input),
                token_info
            )
        tokens = itertools.chain.from_iterable(tokens)
        if self.split_sentences:
            tokens = self._sentence_splitter._merge_empty_sentences(tokens)
        if strip_tags:
            tokens = ([t for t in par if not t.markup] for par in tokens)
        if self.split_sentences and (self.xml_sentences is not None):
            tokens = self._sentence_splitter._add_xml_tags(tokens, s_tag=self.xml_sentences)
        return tokens

    def _tokenize_text(
        self, token_info: Iterable[tuple[list[Token], str, int]], parallel: int
    ) -> Iterator[list[Token]]:
        """Tokenize text paragraphs.

        Args:
            token_info: Iterable of token info tuples.
            parallel: Number of processes to use.

        Returns:
            Iterator of lists of Token objects.

        """
        tokens = self._parallel_tokenize(token_info, parallel=parallel)
        if self.xml_sentences:
            tokens = map(utils.escape_xml_tokens, tokens)
        return tokens

    def _tokenize_xml(
        self,
        xml_data: str | TextIO,
        is_file: bool,
        eos_tags: Iterable[str] | None,
        strip_tags: bool,
        parallel: int,
        prune_tags: Iterable[str] | None
    ) -> Iterator[list[Token]]:
        """Tokenize XML data.

        Args:
            xml_data: XML data as string or file-like object.
            is_file: Whether xml_data is a file path/object.
            eos_tags: XML tags that constitute sentence breaks.
            strip_tags: Whether to strip XML tags from output.
            parallel: Number of processes to use.
            prune_tags: XML tags to remove before tokenization.

        Returns:
            Iterator of lists of Token objects.

        """
        if eos_tags is not None:
            eos_tags = set(eos_tags)
        if prune_tags is not None:
            prune_tags = set(prune_tags)
            assert not self.character_offsets, "Cannot use `prune_tags` when SoMaJo is initialized with `character_offsets=True`."
        token_info = utils.xml_chunk_generator(
            xml_data,
            is_file,
            eos_tags=eos_tags,
            prune_tags=prune_tags,
            character_offsets=self.character_offsets
        )
        tokens = self._parallel_tokenize(token_info, parallel=parallel, strip_tags=strip_tags, xml_input=True)
        if not (strip_tags and self.xml_sentences is None):
            tokens = map(utils.escape_xml_tokens, tokens)
        return tokens

    def tokenize_text_file(
        self,
        text_file: str | TextIO,
        paragraph_separator: Literal["empty_lines", "single_newlines"],
        *,
        parallel: int = 1
    ) -> Iterator[list[Token]]:
        """Split the contents of a text file into sequences of tokens.

        Args:
            text_file: Either a filename or a file-like object containing text.
            paragraph_separator: How are paragraphs separated in the input?
                'single_newlines' means one paragraph per line.
                'empty_lines' means paragraphs span several lines and are
                separated by empty lines.
            parallel: Number of processes to use. Defaults to 1.

        Yields:
            list: The Token objects in a single sentence or paragraph
                (depending on the value of ``split_sentences``).

        Examples:
            Tokenization and sentence splitting; input file with
            paragraphs separated by empty lines; print one token per line
            with token classes and extra information; print an empty line
            after each sentence:

            >>> with open("example_empty_lines.txt") as f:
            ...     print(f.read())
            ... 
            Heyi:)
            \u200b
            Was machst du morgen Abend?! Lust auf Film?;-)
            >>> sentences = tokenizer.tokenize_text_file("example_empty_lines.txt", paragraph_separator="single_newlines")
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print("{token.text}\t{token.token_class}\t{token.extra_info}")
            ...     print()
            ... 
            Heyi\tregular\tSpaceAfter=No
            :)\temoticon\t
            \u200b
            Was\tregular\t
            machst\tregular\t
            du\tregular\t
            morgen\tregular\t
            Abend\tregular\tSpaceAfter=No
            ?!\tsymbol\t
            \u200b
            Lust\tregular\t
            auf\tregular\t
            Film\tregular\tSpaceAfter=No
            ?\tsymbol\tSpaceAfter=No
            ;-)\temoticon\t
            \u200b

            Tokenization and sentence splitting; input file with
            paragraphs separated by single newlines; print one sentence
            per line:

            >>> with open("example_single_newlines.txt", encoding="utf-8") as f:
            ...     print(f.read())
            ... 
            Heyi:)
            Was machst du morgen Abend?! Lust auf Film?;-)
            >>> tokenizer = SoMaJo("de_CMC")
            >>> with open("example_empty_lines.txt", encoding="utf-8") as f:
            ...     sentences = tokenizer.tokenize_text_file(f, paragraph_separator="empty_lines")
            ...     for sentence in sentences:
            ...         print(" ".join([token.text for token in sentence]))
            ... 
            Heyi :)
            Was machst du morgen Abend ?!
            Lust auf Film ? ;-)

        """
        assert paragraph_separator in self.paragraph_separators
        token_info = utils.get_paragraphs_list(text_file, paragraph_separator)
        return self._tokenize_text(token_info, parallel)

    def tokenize_xml_file(
        self,
        xml_file: str | TextIO,
        eos_tags: Iterable[str],
        *,
        strip_tags: bool = False,
        parallel: int = 1,
        prune_tags: Iterable[str] | None = None
    ) -> Iterator[list[Token]]:
        """Split the contents of an xml file into sequences of tokens.

        Args:
            xml_file: A file containing XML data. Either a filename or a file-like object.
            eos_tags: XML tags that constitute sentence breaks, i.e. tags that
                do not occur in the middle of a sentence. For HTML input,
                you might use the following list of tags: ['title',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
                'div', 'ol', 'ul', 'dl', 'table']
            strip_tags: Remove all XML tags from the output. Defaults to False.
            parallel: Number of processes to use. Defaults to 1.
            prune_tags: These XML tags and their contents will be removed from the
                input before tokenization. For HTML input, you might use
                ['script', 'style'] or, depending on your use case,
                ['head']. Defaults to None.

        Yields:
            list: The Token objects in a single sentence or stretch of
                XML delimited by ``eos_tags`` (depending on the value of
                ``split_sentences``).

        Examples:
            Tokenization and sentence splitting; print one token per line
            and an empty line after each sentence:

            >>> with open("example.xml") as f:
            ...     print(f.read())
            ... 
            <html>
              <body>
                <p>Heyi:)</p>
                <p>Was machst du morgen Abend?! Lust auf Film?;-)</p>
              </body>
            </html>
            >>> eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
            >>> tokenizer = SoMaJo("de_CMC")
            >>> sentences = tokenizer.tokenize_xml_file("example.xml", eos_tags)
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print(token)
            ...     print()
            ... 
            <html>
            <body>
            <p>
            Heyi
            :)
            </p>
            \u200b
            <p>
            Was
            machst
            du
            morgen
            Abend
            ?!
            \u200b
            Lust
            auf
            Film
            ?
            ;-)
            </p>
            </body>
            </html>
            \u200b

            Tokenization and sentence splitting; strip XML tags from the
            output and print one sentence per line:

            >>> with open("example.xml") as f:
            ...     sentences = tokenizer.tokenize_xml_file(f, eos_tags, strip_tags=True)
            ...     for sentence in sentences:
            ...         print(" ".join(token.text for token in sentence))
            ... 
            Heyi :)
            Was machst du morgen Abend ?!
            Lust auf Film ? ;-)

            Only tokenization; print one token per line

            >>> tokenizer = SoMaJo("de_CMC", split_sentences=False)
            >>> chunks = tokenizer.tokenize_xml_file("example.xml", eos_tags)
            >>> for chunk in chunks:
            ...     for token in chunk:
            ...         print(token.text)
            ... 
            <html>
            <body>
            <p>
            Heyi
            :)
            </p>
            <p>
            Was
            machst
            du
            morgen
            Abend
            ?!
            Lust
            auf
            Film
            ?
            ;-)
            </p>
            </body>
            </html>

        """
        return self._tokenize_xml(
            xml_file,
            is_file=True,
            eos_tags=eos_tags,
            strip_tags=strip_tags,
            parallel=parallel,
            prune_tags=prune_tags
        )

    def tokenize_text(self, paragraphs: Iterable[str], *, parallel: int = 1) -> Iterator[list[Token]]:
        """Split paragraphs of text into sequences of tokens.

        Args:
            paragraphs: An iterable of single paragraphs of text.
            parallel: Number of processes to use. Defaults to 1.

        Yields:
            list: The Token objects in a single sentence or paragraph
                (depending on the value of ``split_sentences``).

        Examples:
            Tokenization and sentence splitting; print one sentence per
            line:

            >>> paragraphs = ["Heyi:)", "Was machst du morgen Abend?! Lust auf Film?;-)"]
            >>> tokenizer = SoMaJo("de_CMC")
            >>> sentences = tokenizer.tokenize_text(paragraphs)
            >>> for sentence in sentences:
            ...     print(" ".join([token.text for token in sentence]))
            ... 
            Heyi :)
            Was machst du morgen Abend ?!
            Lust auf Film ? ;-)

            Only tokenization; print one paragraph per line:

            >>> tokenizer = SoMaJo("de_CMC", split_sentences=False)
            >>> tokenized_paragraphs = tokenizer.tokenize_text(paragraphs)
            >>> for paragraph in tokenized_paragraphs:
            ...     print(" ".join([token.text for token in paragraph]))
            ... 
            Heyi :)
            Was machst du morgen Abend ?! Lust auf Film ? ;-)

            Tokenization and sentence splitting; print one token per line
            with token classes and extra information; print an empty line
            after each sentence:

            >>> sentences = tokenizer.tokenize_text(paragraphs)
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print("{token.text}\t{token.token_class}\t{token.extra_info}")
            ...     print()
            ... 
            Heyi\tregular\tSpaceAfter=No
            :)\temoticon\t
            \u200b
            Was\tregular\t
            machst\tregular\t
            du\tregular\t
            morgen\tregular\t
            Abend\tregular\tSpaceAfter=No
            ?!\tsymbol\t
            \u200b
            Lust\tregular\t
            auf\tregular\t
            Film\tregular\tSpaceAfter=No
            ?\tsymbol\tSpaceAfter=No
            ;-)\temoticon
            \u200b

            Tokenization and sentence splitting; print one token per line
            and delimit sentences with XML tags:

            >>> tokenizer = SoMaJo("de_CMC", xml_sentences="s")
            >>> sentences = tokenizer.tokenize_text(paragraphs)
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print(token.text)
            ... 
            <s>
            Heyi
            :)
            </s>
            <s>
            Was
            machst
            du
            morgen
            Abend
            ?!
            </s>
            <s>
            Lust
            auf
            Film
            ?
            ;-)
            </s>

        """
        if isinstance(paragraphs, str):
            raise TypeError("``paragraphs`` must be an iterable of strings, not a string!")
        token_info = (([Token(p, first_in_sentence=True, last_in_sentence=True)], p, 0) for p in paragraphs)
        return self._tokenize_text(token_info, parallel)

    def tokenize_xml(
        self,
        xml_data: str,
        eos_tags: Iterable[str],
        *,
        strip_tags: bool = False,
        parallel: int = 1,
        prune_tags: Iterable[str] | None = None
    ) -> Iterator[list[Token]]:
        """Split a string of XML data into sequences of tokens.

        Args:
            xml_data: A string containing XML data.
            eos_tags: XML tags that constitute sentence breaks, i.e. tags that
                do not occur in the middle of a sentence. For HTML input,
                you might use the following list of tags: ['title',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
                'div', 'ol', 'ul', 'dl', 'table']
            strip_tags: Remove the XML tags from the output. Defaults to False.
            parallel: Number of processes to use. Defaults to 1.
            prune_tags: These XML tags and their contents will be removed from the
                input before tokenization. For HTML input, you might use
                ['script', 'style'] or, depending on your use case,
                ['head']. Defaults to None.

        Yields:
            list: The Token objects in a single sentence or stretch of
                XML delimited by ``eos_tags`` (depending on the value of
                ``split_sentences``).

        Examples:
            Tokenization and sentence splitting; print one token per line
            and an empty line after each sentence:

            >>> xml = "<html><body><p>Heyi:)</p><p>Was machst du morgen Abend?! Lust auf Film?;-)</p></body></html>"
            >>> eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
            >>> tokenizer = SoMaJo("de_CMC")
            >>> sentences = tokenizer.tokenize_xml(xml, eos_tags)
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print(token.text)
            ...     print()
            ... 
            <html>
            <body>
            <p>
            Heyi
            :)
            </p>
            \u200b
            <p>
            Was
            machst
            du
            morgen
            Abend
            ?!
            \u200b
            Lust
            auf
            Film
            ?
            ;-)
            </p>
            </body>
            </html>
            \u200b

            Tokenization and sentence splitting; strip XML tags from the
            output and print one sentence per line

            >>> sentences = tokenizer.tokenize_xml(xml, eos_tags, strip_tags=True)
            >>> for sentence in sentences:
            ...     print(" ".join([token.text for token in sentence]))
            ... 
            Heyi :)
            Was machst du morgen Abend ?!
            Lust auf Film ? ;-)

            Only tokenization; print one chunk of XML (delimited by
            ``eos_tags``) per line:

            >>> tokenizer = SoMaJo("de_CMC", split_sentences=False)
            >>> chunks = tokenizer.tokenize_xml(xml, eos_tags)
            >>> for chunk in chunks:
            ...     print(" ".join([token.text for token in chunk]))
            ... 
            <html> <body> <p> Heyi :) </p>
            <p> Was machst du morgen Abend ?! Lust auf Film ? ;-) </p> </body> </html>

            Tokenization and sentence splitting; print one token per line
            and delimit sentences with XML tags:

            >>> xml = "<html><body><p>Heyi:)</p><p>Was machst du morgen Abend?! Lust auf Film?;-)</p></body></html>"
            >>> eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
            >>> tokenizer = SoMaJo("de_CMC", xml_sentences="s")
            >>> sentences = tokenizer.tokenize_xml(xml, eos_tags)
            >>> for sentence in sentences:
            ...     for token in sentence:
            ...         print(token.text)
            ...     print()
            ...
            <html>
            <body>
            <p>
            <s>
            Heyi
            :)
            </s>
            </p>
            <p>
            <s>
            Was
            machst
            du
            morgen
            Abend
            ?!
            </s>
            <s>
            Lust
            auf
            Film
            ?
            ;-)
            </s>
            </p>
            </body>
            </html>

        """
        return self._tokenize_xml(
            xml_data,
            is_file=False,
            eos_tags=eos_tags,
            strip_tags=strip_tags,
            parallel=parallel,
            prune_tags=prune_tags
        )
