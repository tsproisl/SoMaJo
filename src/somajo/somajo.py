#!/usr/bin/env python3

import functools
import itertools
import multiprocessing
import unicodedata

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

    Parameters
    ----------
    language : {'de_CMC', 'en_PTB'}
        Language-specific tokenization rules.
    split_camel_case : bool, (default=False)
        Split words written in camelCase (excluding established names
        and terms).
    split_sentences : bool, (default=True)
        Perform sentence splitting in addition to tokenization.
    xml_sentences : str, (default=None)
        Delimit sentences by XML tags of this name
        (``xml_sentences='s'`` → <s>…</s>). When used with XML input,
        this might lead to minor changes to the original tags to
        guarantee well-formed output (tags might need to be closed and
        re-opened at sentence boundaries).
    character_offsets : bool, (default=False)
        Compute for each token the character offsets in the input.
        This allows for stand-off tokenization.

    """

    supported_languages = {"de_CMC", "en_PTB"}
    _default_language = "de_CMC"
    paragraph_separators = {"empty_lines", "single_newlines"}
    _default_parsep = "empty_lines"

    def __init__(self, language, *, split_camel_case=False, split_sentences=True, xml_sentences=None, character_offsets=False):
        assert language in self.supported_languages
        self.language = language
        self.split_camel_case = split_camel_case
        self.split_sentences = split_sentences
        self.xml_sentences = xml_sentences
        self.character_offsets = character_offsets
        self._tokenizer = Tokenizer(split_camel_case=self.split_camel_case, language=self.language)
        if self.split_sentences:
            self._sentence_splitter = SentenceSplitter(language=self.language)

    def _tokenize(self, token_info, xml_input):
        """Tokenize and sentence split a single token_dll."""
        # unpack token_info
        # resolve entities in xml
        # convert raw to nfc
        # align nfc
        # tokenize
        # find character offsets
        token_list, raw, position = token_info
        token_dll = doubly_linked_list.DLL(token_list)
        tokens = self._tokenizer._tokenize(token_dll)
        if self.character_offsets:
            if xml_input:
                chunk_offsets = [(t.markup, t.character_offset[0] - position, t.character_offset[1] - position) for t in token_list]
                raw, align_to_entities = alignment.resolve_entities(raw)
                align_from_entities = {i: char_i for char_i, (start, end) in enumerate(align_to_entities) for i in range(start, end)}
                chunks = [raw[align_from_entities[start]:align_from_entities[end - 1] + 1] for markup, start, end in chunk_offsets]
                chunks_nfc = [unicodedata.normalize("NFC", c) for c in chunks]
                alignments = [alignment.align_nfc(chunk_nfc, chunk) for chunk, chunk_nfc in zip(chunks, chunks_nfc)]
                align_to_raw = alignments[0]
                for i in range(1, len(alignments)):
                    o1 = sum(len(c) for c in chunks_nfc[:i])
                    o2 = sum(len(c) for c in chunks[:i])
                    align_to_raw.update({(k[0] + o1, k[1] + o1): (v[0] + o2, v[1] + o2) for k, v in alignments[i].items()})
                raw_nfc = "".join(chunks_nfc)
            else:
                raw_nfc = unicodedata.normalize("NFC", raw)
                align_to_raw = alignment.align_nfc(raw_nfc, raw)
            align_from_raw = {i: k for k, v in align_to_raw.items() for i in range(v[0], v[1])}
            # align_starts = {k[0]: v[0] for k, v in align_to_raw.items()}
            # align_ends = {k[1]: v[1] for k, v in align_to_raw.items()}
            align_to_starts = {i: v[0] for k, v in align_to_raw.items() for i in range(k[0], k[1])}
            align_to_ends = {i: v[1] for k, v in align_to_raw.items() for i in range(k[0], k[1])}
            for i in range(len(tokens)):
                if tokens[i].markup:
                    s, e = tokens[i].character_offset
                    s -= position
                    e -= position
                    tokens[i].character_offset = (align_from_raw[align_from_entities[s]][0] + position, align_from_raw[align_from_entities[e - 1]][1] + position)
            offsets = alignment.token_offsets(tokens, raw_nfc, position)
            assert len(tokens) == len(offsets)
            offsets = [(align_to_starts[s], align_to_ends[e - 1]) for s, e in offsets]
            if xml_input:
                offsets = [(align_to_entities[s][0], align_to_entities[e - 1][1]) for s, e in offsets]
            for i in range(len(tokens)):
                tokens[i].character_offset = offsets[i]
        if self.split_sentences:
            tokens = self._sentence_splitter._split_sentences(tokens)
        return tokens

    def _parallel_tokenize(self, token_info, *, parallel=1, strip_tags=False, xml_input=False):
        """Tokenize and sentence split an iterable of token_dlls; optional
        parallelization.

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
        if self.split_sentences:
            tokens = itertools.chain.from_iterable(tokens)
            tokens = self._sentence_splitter._merge_empty_sentences(tokens)
        if strip_tags:
            tokens = ([t for t in par if not t.markup] for par in tokens)
        if self.split_sentences and (self.xml_sentences is not None):
            tokens = self._sentence_splitter._add_xml_tags(tokens, s_tag=self.xml_sentences)
        return tokens

    def _tokenize_text(self, token_info, parallel):
        tokens = self._parallel_tokenize(token_info, parallel=parallel)
        if self.xml_sentences:
            tokens = map(utils.escape_xml_tokens, tokens)
        return tokens

    def _tokenize_xml(self, xml_data, is_file, eos_tags, strip_tags, parallel, prune_tags):
        if eos_tags is not None:
            eos_tags = set(eos_tags)
        if prune_tags is not None:
            prune_tags = set(prune_tags)
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

    def tokenize_text_file(self, text_file, paragraph_separator, *, parallel=1):
        """Split the contents of a text file into sequences of tokens.

        Parameters
        ----------
        text_file : str or file-like object
            Either a filename or a file-like object containing text.
        paragraph_separator : {'single_newlines', 'empty_lines'}
            How are paragraphs separated in the input? Is there one
            paragraph per line ('single_newlines') or do paragraphs
            span several lines and are separated by 'empty_lines'?
        parallel : int, (default=1)
            Number of processes to use.

        Yields
        -------
        list
            The ``Token`` objects in a single sentence or paragraph
            (depending on the value of ``split_sentences``).

        Examples
        --------

        Tokenization and sentence splitting; input file with
        paragraphs separated by empty lines; print one token per line
        with token classes and extra information; print an empty line
        after each sentence:

        >>> with open("example_empty_lines.txt") as f:
        ...     print(f.read())
        ... 
        Heyi:)
        ​
        Was machst du morgen Abend?! Lust auf Film?;-)
        >>> sentences = tokenizer.tokenize_text_file("example_empty_lines.txt", paragraph_separator="single_newlines")
        >>> for sentence in sentences:
        ...     for token in sentence:
        ...         print("{}\t{}\t{}".format(token.text, token.token_class, token.extra_info))
        ...     print()
        ... 
        Heyi	regular	SpaceAfter=No
        :)	emoticon	
        ​
        Was	regular	
        machst	regular	
        du	regular	
        morgen	regular	
        Abend	regular	SpaceAfter=No
        ?!	symbol	
        ​
        Lust	regular	
        auf	regular	
        Film	regular	SpaceAfter=No
        ?	symbol	SpaceAfter=No
        ;-)	emoticon	
        ​

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

    def tokenize_xml_file(self, xml_file, eos_tags, *, strip_tags=False, parallel=1, prune_tags=None):
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
            Remove all XML tags from the output.
        parallel : int, (default=1)
            Number of processes to use.
        prune_tags : iterable
            These XML tags and their contents will be removed from the
            input before tokenization. For HTML input, you might use
            ``['script', 'style']`` or, depending on your use case,
            ``['head']``.

        Yields
        -------
        list
            The ``Token`` objects in a single sentence or stretch of
            XML delimited by ``eos_tags`` (depending on the value of
            ``split_sentences``).

        Examples
        --------

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
        ​
        <p>
        Was
        machst
        du
        morgen
        Abend
        ?!
        ​
        Lust
        auf
        Film
        ?
        ;-)
        </p>
        </body>
        </html>
        ​

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

    def tokenize_text(self, paragraphs, *, parallel=1):
        """Split paragraphs of text into sequences of tokens.

        Parameters
        ----------
        paragraphs : iterable
            An iterable of single paragraphs of text.
        parallel : int, (default=1)
            Number of processes to use.

        Yields
        ------
        list
            The ``Token`` objects in a single sentence or paragraph
            (depending on the value of ``split_sentences``).

        Examples
        --------

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
        ...         print("{}\t{}\t{}".format(token.text, token.token_class, token.extra_info))
        ...     print()
        ... 
        Heyi	regular	SpaceAfter=No
        :)	emoticon	
        ​
        Was	regular	
        machst	regular	
        du	regular	
        morgen	regular	
        Abend	regular	SpaceAfter=No
        ?!	symbol	
        ​
        Lust	regular	
        auf	regular	
        Film	regular	SpaceAfter=No
        ?	symbol	SpaceAfter=No
        ;-)	emoticon
        ​

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

    def tokenize_xml(self, xml_data, eos_tags, *, strip_tags=False, parallel=1, prune_tags=None):
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
        parallel : int, (default=1)
            Number of processes to use.
        prune_tags : iterable
            These XML tags and their contents will be removed from the
            input before tokenization. For HTML input, you might use
            ``['script', 'style']`` or, depending on your use case,
            ``['head']``.

        Yields
        ------
        list
            The ``Token`` objects in a single sentence or stretch of
            XML delimited by ``eos_tags`` (depending on the value of
            ``split_sentences``).

        Examples
        --------

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
        ​
        <p>
        Was
        machst
        du
        morgen
        Abend
        ?!
        ​
        Lust
        auf
        Film
        ?
        ;-)
        </p>
        </body>
        </html>
        ​

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
