#!/usr/bin/env python3

import argparse
import collections
import logging
import multiprocessing
import time
import xml.etree.ElementTree as ET

from somajo import Tokenizer
from somajo import SentenceSplitter


def arguments():
    """"""
    parser = argparse.ArgumentParser(description="Tokenize an input file according to the guidelines of the EmpiriST 2015 shared task on automatic linguistic annotation of computer-mediated communication / social media.")
    parser.add_argument("-s", "--paragraph_separator", choices=["empty_lines", "single_newlines"], default="empty_lines", help="How are paragraphs separated in the input text? Will be ignored if option -x/--xml is used. (Default: empty_lines)")
    parser.add_argument("-x", "--xml", action="store_true", help="The input is an XML file. You can specify tags that always constitute a sentence break (e.g. HTML p tags) via the --tag option.")
    parser.add_argument("--tag", action="append", help="Start and end tags of this type constitute sentence breaks, i.e. we do not expect a sentence to cross these tags. Can be used multiple times to specify multiple tags, e.g. --tag p --tag br. Implies option -x/--xml. (Default: --tag title --tag h1 --tag h2 --tag h3 --tag h4 --tag h5 --tag h6 --tag p --tag br --tag div --tag ol --tag ul --tag dl --tag table)")
    parser.add_argument("-c", "--split_camel_case", action="store_true", help="Split items in written in camelCase (excluding several exceptions).")
    parser.add_argument("-t", "--token_classes", action="store_true", help="Output the token classes (number, XML tag, abbreviation, etc.) in addition to the tokens.")
    parser.add_argument("-e", "--extra_info", action="store_true", help='Output additional information for each token: SpaceAfter=No if the token was not followed by a space and OriginalSpelling="…" if the token contained whitespace.')
    parser.add_argument("--parallel", type=int, default=1, metavar="N", help="Run N worker processes (up to the number of CPUs) to speed up tokenization.")
    parser.add_argument("--split_sentences", action="store_true", help="Do also split the paragraphs into sentences.")
    parser.add_argument("FILE", type=argparse.FileType("r"), help="The input file")
    args = parser.parse_args()
    return args


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


def parse_xml(fh):
    """Return a list of XML elements and their text/tail as well as the
    whole text of the document.

    """
    Element = collections.namedtuple("Element", ["element", "type", "text"])

    def text_getter(elem):
        text = elem.text
        tail = elem.tail
        if text is not None:
            yield Element(elem, "text", text)
        for child in elem:
            for t in text_getter(child):
                yield t
        if tail is not None:
            yield Element(elem, "tail", tail)
    tree = ET.parse(fh)
    root = tree.getroot()
    elements = list(text_getter(root))
    return root, elements


def main():
    args = arguments()
    n_tokens = 0
    t0 = time.perf_counter()
    if args.xml or args.tag is not None:
        is_xml = True
    tokenizer = Tokenizer(args.split_camel_case, args.token_classes, args.extra_info, is_xml)
    sentence_splitter = SentenceSplitter(args.token_classes or args.extra_info)
    if is_xml:
        if args.parallel > 1:
            logging.warning("Parallel tokenization of XML files is currently not supported.")
            args.parallel = 1
        eos_tags = args.tag
        if eos_tags is None:
            eos_tags = ["title h1 h2 h3 h4 h5 h6 p br div ol ul dl table".split()]
        root, elements = parse_xml(args.FILE)
        paragraphs = [elements]
        for element in elements:
            element.element.text = "\nfoo\n"
            element.element.tail = "\nbar\n"
        print(ET.tostring(root).decode("utf8"))
    elif args.paragraph_separator == "empty_lines":
        paragraphs = get_paragraphs(args.FILE)
    elif args.paragraph_separator == "single_newlines":
        paragraphs = (line for line in args.FILE if line.strip() != "")
    if args.parallel > 1:
        pool = multiprocessing.Pool(min(args.parallel, multiprocessing.cpu_count()))
        tokenized_paragraphs = pool.imap(tokenizer.tokenize, paragraphs, 250)
    else:
        tokenized_paragraphs = map(tokenizer.tokenize, paragraphs)
    tokenized_paragraphs = (tp for tp in tokenized_paragraphs if tp)
    if args.split_sentences:
        tokenized_paragraphs = map(sentence_splitter.split, tokenized_paragraphs)
        tokenized_paragraphs = (s for tp in tokenized_paragraphs for s in tp)
    if args.token_classes or args.extra_info:
        tokenized_paragraphs = (["\t".join(t) for t in tp] for tp in tokenized_paragraphs)
    for tp in tokenized_paragraphs:
        n_tokens += len(tp)
        print("\n".join(tp), "\n", sep="")
    t1 = time.perf_counter()
    logging.info("Tokenized %d tokens in %d seconds (%d tokens/s)" % (n_tokens, t1 - t0, n_tokens / (t1 - t0)))
