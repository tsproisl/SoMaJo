#!/usr/bin/env python3

import argparse
import logging
import time

from somajo import SoMaJo
from somajo.version import __version__


# New options?
# - extract text from XML, i.e. strip XML tags


def arguments():
    """"""
    parser = argparse.ArgumentParser(description="Tokenize an input file according to the guidelines of the EmpiriST 2015 shared task on automatic linguistic annotation of computer-mediated communication / social media.")
    parser.add_argument("-s", "--paragraph_separator", choices=SoMaJo.paragraph_separators, default=SoMaJo._default_parsep, help="How are paragraphs separated in the input text? Will be ignored if option -x/--xml is used. (Default: empty_lines)")
    parser.add_argument("-x", "--xml", action="store_true", help="The input is an XML file. You can specify tags that always constitute a sentence break (e.g. HTML p tags) via the --tag option.")
    parser.add_argument("--tag", action="append", help="Start and end tags of this type constitute sentence breaks, i.e. they do not occur in the middle of a sentence. Can be used multiple times to specify multiple tags, e.g. --tag p --tag br. Implies option -x/--xml. (Default: --tag title --tag h1 --tag h2 --tag h3 --tag h4 --tag h5 --tag h6 --tag p --tag br --tag hr --tag div --tag ol --tag ul --tag dl --tag table)")
    parser.add_argument("--strip-tags", action="store_true", help="Suppresses output of XML tags (implies option -x/--xml).")
    parser.add_argument("-c", "--split_camel_case", action="store_true", help="Split items in written in camelCase (excluding several exceptions).")
    parser.add_argument("-t", "--token_classes", action="store_true", help="Output the token classes (number, XML tag, abbreviation, etc.) in addition to the tokens.")
    parser.add_argument("-e", "--extra_info", action="store_true", help='Output additional information for each token: SpaceAfter=No if the token was not followed by a space and OriginalSpelling="…" if the token contained whitespace.')
    parser.add_argument("-l", "--language", choices=SoMaJo.supported_languages, default=SoMaJo._default_language, help="Choose a language. Currently supported are German EmpiriST-style tokenization (de_CMC) and English Penn-Treebank-style tokenization(en_PTB). (Default: de_CMC)")
    parser.add_argument("--parallel", type=int, default=1, metavar="N", help="Run N worker processes (up to the number of CPUs) to speed up tokenization.")
    parser.add_argument("--split_sentences", "--split-sentences", action="store_true", help="Do also split the paragraphs into sentences.")
    parser.add_argument("-v", "--version", action="version", version="SoMaJo %s" % __version__, help="Output version information and exit.")
    parser.add_argument("FILE", type=argparse.FileType("r", encoding="utf-8"), help="The input file (UTF-8-encoded)")
    args = parser.parse_args()
    return args


def main():
    args = arguments()
    n_tokens = 0
    n_sentences = 0
    t0 = time.perf_counter()
    is_xml = False
    if args.xml or args.tag is not None:
        is_xml = True
    tokenizer = SoMaJo(args.language, split_camel_case=args.split_camel_case, split_sentences=args.split_sentences)
    if is_xml:
        eos_tags = args.tag
        if eos_tags is None:
            eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        chunks = tokenizer.tokenize_xml_file(args.FILE, eos_tags, strip_tags=args.strip_tags, parallel=args.parallel)
    else:
        chunks = tokenizer.tokenize_text_file(args.FILE, args.paragraph_separator, parallel=args.parallel)
    for chunk in chunks:
        n_sentences += 1
        for token in chunk:
            if not token.markup:
                n_tokens += 1
            output = token.text
            if args.token_classes and token.token_class is not None:
                output += "\t" + token.token_class
            if args.extra_info:
                output += "\t" + token.extra_info()
            print(output)
        if args.split_sentences:
            print()
    t1 = time.perf_counter()
    if args.split_sentences:
        logging.info("Tokenized %d tokens (%d sentences) in %d seconds (%d tokens/s)" % (n_tokens, n_sentences, t1 - t0, n_tokens / (t1 - t0)))
    else:
        logging.info("Tokenized %d tokens in %d seconds (%d tokens/s)" % (n_tokens, t1 - t0, n_tokens / (t1 - t0)))
