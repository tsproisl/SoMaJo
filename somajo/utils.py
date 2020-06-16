#!/usr/bin/env python3

import os
import regex as re
import xml.sax
import xml.sax.saxutils

from somajo.token import Token


def get_paragraphs_str(fh, paragraph_separator="empty_lines"):
    """Generator for the paragraphs in the file."""
    if paragraph_separator == "single_newlines":
        for line in fh:
            if line.strip() != "":
                yield line
    elif paragraph_separator == "empty_lines":
        paragraph = []
        for line in fh:
            if line.strip() == "":
                if len(paragraph) > 0:
                    yield "".join(paragraph)
                    paragraph = []
            else:
                paragraph.append(line)
        if len(paragraph) > 0:
            yield "".join(paragraph)


def get_paragraphs_list(text_file, paragraph_separator="empty_lines"):
    """Generator for the paragraphs in the file."""
    if isinstance(text_file, str):
        with open(text_file, encoding="utf-8") as fh:
            for paragraph in get_paragraphs_str(fh, paragraph_separator):
                yield [Token(paragraph, first_in_sentence=True, last_in_sentence=True)]
    else:
        for paragraph in get_paragraphs_str(text_file, paragraph_separator):
            yield [Token(paragraph, first_in_sentence=True, last_in_sentence=True)]


def read_abbreviation_file(filename):
    """Return the abbreviations from the given filename."""
    abbreviations = set()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#"):
                continue
            if line == "":
                continue
            abbreviations.add(line)
    return sorted(abbreviations, key=len, reverse=True)


class SaxTokenHandler(xml.sax.handler.ContentHandler):
    def __init__(self, eos_tags=None):
        super().__init__()
        self.eos_tags = eos_tags
        self.token_list = []
        self.content = ""
        self.sentence_start = True

    def _insert_element(self, name, text, markup_class):
        sentence_boundary = False
        if self.eos_tags is not None and name in self.eos_tags:
            sentence_boundary = True
        if self.content != "":
            content_token = Token(self.content, token_class="regular", first_in_sentence=self.sentence_start, last_in_sentence=sentence_boundary)
            self.token_list.append(content_token)
            self.content = ""
            self.sentence_start = False
        token = Token(text, markup=True, markup_class=markup_class, markup_eos=sentence_boundary, locked=True)
        self.token_list.append(token)
        if sentence_boundary:
            self.sentence_start = True

    def characters(self, data):
        self.content += data

    def startElement(self, name, attrs):
        if len(attrs) > 0:
            text = "<%s %s>" % (name, " ".join(["%s=\"%s\"" % (k, xml.sax.saxutils.escape(v, {'"': "&quot;"})) for k, v in attrs.items()]))
        else:
            text = "<%s>" % name
        self._insert_element(name, text, "start")

    def endElement(self, name):
        text = "</%s>" % name
        self._insert_element(name, text, "end")


def incremental_xml_parser(f, eos_tags=None):
    parser = xml.sax.make_parser(["xml.sax.xmlreader.IncrementalParser"])
    handler = SaxTokenHandler(eos_tags)
    parser.setContentHandler(handler)
    for line in f:
        parser.feed(line)
        if len(handler.token_list) > 0:
            yield handler.token_list
            handler.token_list = []
    parser.close()


def _xml_chunk_generator(f, eos_tags=None):
    """Parse the XML data and yield doubly linked lists of Token objects
    that are delimited by eos_tags.

    """
    non_whitespace = re.compile(r"\S")
    token_lists = incremental_xml_parser(f, eos_tags)
    current = []
    bos, eos = True, False
    lexical_tokens = 0
    # yield chunks delimited by eos_tags
    algo_dot = """digraph {
    is_tag [label="tag?"]
    tok_is_eos [label="eos?"]
    tag_is_eos [label="eos?"]
    is_bos [label="bos?"]
    is_eos_tag [label="eos_tag?"]
    eos_markup_class [label="markup_class"]
    non_eos_markup_class [label="markup_class"]
    yield_token [label="eos = False\nyield\nreset"];
    yield_non_eos [label="eos = False\nyield\nreset"];
    fis [label = "first_in_sentence = True\nbos = False"];
    eos_start [label="eos = False\nbos = True\nset last_in_sentence\nyield\nreset"];
    eos_end [label="eos = True\nbos = True\nset last_in_sentence"];

    start -> is_tag [label = "read"];
        is_tag -> tok_is_eos [label = "no"];
            tok_is_eos -> yield_token [label = "yes"];
                yield_token -> is_bos;
            tok_is_eos -> is_bos [label = "no"];
                is_bos -> fis [label = "yes"];
                    fis -> append;
                is_bos -> append [label = "no"];
        is_tag -> is_eos_tag [label = "yes"];
            is_eos_tag -> tag_is_eos [label = "no"];
                tag_is_eos -> non_eos_markup_class [label = "yes"];
                    non_eos_markup_class -> yield_non_eos [label = "start"];
                        yield_non_eos -> append;
                    non_eos_markup_class -> append [label = "end"];
                tag_is_eos -> append [label = "no"];
            is_eos_tag -> eos_markup_class [label = "yes"];
                eos_markup_class -> eos_start [label = "start"];
                    eos_start -> append;
                eos_markup_class -> eos_end [label = "end"];
                    eos_end -> append;
    append -> start;
}"""
    # created using https://dot-to-ascii.ggerganov.com/
    algo_sketch = """
              read    +----------------------+
  +-----------------> |         tag?         | -+
  |                   +----------------------+  |
  |                     |                       |
  |                     | no                    |
  |                     v                       |
  |                   +----------------------+  |
  |            +----- |         eos?         |  |
  |            |      +----------------------+  |
  |            |        |                       |
  |            |        | yes                   |
  |            |        v                       |
  |            |      +----------------------+  |
  |            |      |     eos = False      |  |
  |            | no   |        yield         |  |
  |            |      |        reset         |  |
  |            |      +----------------------+  |
  |            |        |                       |
  |            |        |                       |
  |            |        v                       |
  |            |      +----------------------+  |                                +--------------------------+
  |            |      |         bos?         |  |                       yes      | first_in_sentence = True |
  |            +----> |                      | -+------------------------------> |       bos = False        |
  |                   +----------------------+  |                                +--------------------------+
  |                     |                       |                                  |
  |            +--------+                       | yes                              |
  |            |                                |                                  |
  |            |      +----------------------+  |                                  |
  |    +-------+----- |       eos_tag?       | <+                                  |
  |    |       |      +----------------------+                                     |
  |    |       |        |                                                          |
  |    |       |        | no                                                       |
  |    |       |        v                                                          |
  |    |       |      +----------------------+                                     |
  |    |       |      |         eos?         | -+                                  |
  |    |       |      +----------------------+  |                                  |
  |    |       |        |                       |                                  |
  |    | yes   |        | yes                   |                                  |
  |    |       |        v                       |                                  |
  |    |       |      +----------------------+  |                                  |
  |    |       |      |     markup_class     | -+------------------------+         |
  |    |       |      +----------------------+  |                        |         |
  |    |       |        |                       |                        |         |
  |    |       |        +-----------------------+---------+              |         |
  |    |       |                                |         |              |         |
  |    |       |      +----------------------+  |         |              |         |
  |    +-------+----> |     markup_class     | -+---------+--------------+---------+--------------------------------+
  |            |      +----------------------+  |         |              |         |                                |
  |            |        |                       |         |              |         |                                |
  |            |        | end                   |         |              |         |                                |
  |            |        v                       |         |              |         |                                |
  |            |      +----------------------+  |         |              |         |                                |
  |            |      |      eos = True      |  |         |              |         |                                |
  |            | no   |      bos = True      |  |         |              |         |                                |
  |            |      | set last_in_sentence |  |         |              |         |                                |
  |            |      +----------------------+  |         |              |         |                                |
  |            |        |                       |         |              |         |                                |
  |            |        |                       | no      | end          +---------+---------------------------+    |
  |            |        v                       v         v                        |                           |    |
  |            |      +-----------------------------------------------+            |                           |    |
  |            +----> |                    append                     | <----------+                           |    |
  |                   +-----------------------------------------------+                                        |    |
  |                     |                       ^         ^                                                    |    |
  |                     |                       |         |                                                    |    |
  |                     v                       |         |                                                    |    |
  |                   +----------------------+  |       +-------------+                                        |    |
  |                   |>>>>>>+-------+<<<<<<<|  |       | eos = False |                                        |    |
  |                   |>>>>>>| START |<<<<<<<|  |       |    yield    |  start                                 |    |
  +------------------ |>>>>>>+-------+<<<<<<<|  |       |    reset    | <--------------------------------------+    |
                      +----------------------+  |       +-------------+                                             |
                                                |                                                                   |
                        +-----------------------+                                                                   |
                        |                                                                                           |
                      +----------------------+                                                                      |
                      |     eos = False      |                                                                      |
                      |      bos = True      |                                                                      |
                      | set last_in_sentence |                                                                      |
                      |        yield         |  start                                                               |
                      |        reset         | <--------------------------------------------------------------------+
                      +----------------------+
"""
    del algo_dot, algo_sketch
    for token_list in token_lists:
        for token in token_list:
            if token.markup:
                # markup
                if token.markup_eos:
                    bos = True
                    for t in reversed(current):
                        if not t.markup:
                            t.last_in_sentence = True
                            break
                    if token.markup_class == "start":
                        eos = False
                        if lexical_tokens > 0:
                            # remove trailing opening tags from current
                            temp_list = []
                            while current[-1].markup_class == "start" or (not non_whitespace.search(current[-1].text)):
                                temp_list.append(current.pop())
                            yield current
                            current = temp_list[::-1]
                            lexical_tokens = 0
                    elif token.markup_class == "end":
                        eos = True
                else:
                    if eos and token.markup_class == "start":
                        eos = False
                        if lexical_tokens > 0:
                            yield current
                            current = []
                            lexical_tokens = 0
            else:
                # non-markup
                whitespace = True
                if non_whitespace.search(token.text):
                    whitespace = False
                if not whitespace:
                    if eos:
                        eos = False
                        if lexical_tokens > 0:
                            yield current
                            current = []
                            lexical_tokens = 0
                    if bos:
                        bos = False
                        token.first_in_sentence = True
                        lexical_tokens += 1
            current.append(token)
    if len(current) > 0:
        yield current


def xml_chunk_generator(data, is_file=True, eos_tags=None):
    """Parse the XML data and yield doubly linked lists of Token objects
    that are delimited by eos_tags.

    """
    if is_file:
        if isinstance(data, str):
            with open(data, encoding="utf-8") as f:
                for chunk in _xml_chunk_generator(f, eos_tags):
                    yield chunk
        else:
            for chunk in _xml_chunk_generator(data, eos_tags):
                yield chunk
    else:
        for chunk in _xml_chunk_generator(data.split("\n"), eos_tags):
            yield chunk


def escape_xml(string):
    """Escape "&", "<" and ">" in string."""
    return xml.sax.saxutils.escape(string)


def escape_xml_tokens(tokens):
    for t in tokens:
        if not t.markup:
            t.text = escape_xml(t.text)
            if t.original_spelling is not None:
                t.original_spelling = escape_xml(t.original_spelling)
    return tokens
