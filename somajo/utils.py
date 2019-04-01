#!/usr/bin/env python3

import collections
import logging
import os
import xml.etree.ElementTree as ET


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
