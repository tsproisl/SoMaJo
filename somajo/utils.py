#!/usr/bin/env python3

import collections
import logging
import os
import xml.etree.ElementTree as ET
import xml.sax

from somajo import doubly_linked_list
from somajo.token import Token


def get_paragraphs(fh):
    """Generator for the paragraphs in the file."""
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


def parse_xml(xml, is_file=True):
    """Return a list of XML elements and their text/tail as well as the
    whole text of the document.

    """
    Element = collections.namedtuple("Element", ["element", "type", "text"])

    def text_getter(elem):
        text = elem.text
        tail = elem.tail
        if text is None:
            text = ""
        if tail is None:
            tail = ""
        yield Element(elem, "text", text)
        for child in elem:
            for t in text_getter(child):
                yield t
        yield Element(elem, "tail", tail)
    try:
        if is_file:
            tree = ET.parse(xml)
            root = tree.getroot()
        else:
            root = ET.fromstring(xml)
    except ET.ParseError as err:
        logging.error("Error parsing the XML file:\n%s" % err)
        return []
    elements = list(text_getter(root))
    return elements


class SaxTokenHandler(xml.sax.handler.ContentHandler):
    def __init__(self, eos_tags=None):
        super().__init__()
        self.eos_tags = eos_tags
        self.token_dll = doubly_linked_list.DLL()
        self.content = ""
        self.sentence_start = True

    def _insert_element(self, name, text, markup_class):
        sentence_boundary = False
        if self.eos_tags is not None and name in self.eos_tags:
            sentence_boundary = True
        if self.content != "":
            content_token = Token(self.content, token_class="regular", first_in_sentence=self.sentence_start, last_in_sentence=sentence_boundary)
            self.token_dll.append(content_token)
            self.content = ""
            self.sentence_start = False
        token = Token(text, markup=True, markup_class=markup_class, markup_eos=sentence_boundary, locked=True)
        self.token_dll.append(token)
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


def parse_xml_to_token_dll(data, is_file=True, eos_tags=None):
    """Parse the XML data to a doubly linked list of Token objects"""
    handler = SaxTokenHandler(eos_tags)
    if is_file:
        xml.sax.parse(data, handler)
    else:
        xml.sax.parseString(data, handler)
    return handler.token_dll


def escape_xml(string):
    """Escape "&", "<" and ">" in string."""
    return xml.sax.saxutils.escape(string)
