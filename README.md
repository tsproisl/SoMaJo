# SoMaJo

[![PyPI](https://img.shields.io/pypi/v/SoMaJo)](https://pypi.org/project/SoMaJo/)
[![Build](https://github.com/tsproisl/SoMaJo/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/tsproisl/SoMaJo/actions/workflows/test.yml?query=branch%3Amaster)

  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
      - [Using the somajo-tokenizer executable](#using-the-somajo-tokenizer-executable)
      - [Using the module](#using-the-module)
  - [Evaluation](#evaluation)
  - [Tokenizing English text](#tokenizing-english-text)
  - [Development](#development)
  - [References](#references)


## Introduction

```
echo 'Wow, superTool!;)' | somajo-tokenizer -c -
Wow
,
super
Tool
!
;)
```

SoMaJo is a rule-based tokenizer and sentence splitter that implements
tokenization guidelines for German and English. It has a strong focus
on web and social media texts (it was originally created as the
winning submission to the [EmpiriST 2015 shared
task](https://sites.google.com/site/empirist2015/) on automatic
linguistic annotation of computer-mediated communication / social
media) and is particularly well-suited to perform tokenization on all
kinds of written discourse, for example chats, forums, wiki talk
pages, tweets, blog comments, social networks, SMS and WhatsApp
dialogues. Of course it also works on more formal texts.

Version 1 of the tokenizer is described in greater detail in [Proisl
and Uhrig (2016)](https://aclanthology.org/W16-2607).

For part-of-speech tagging (in particular of German web and social
media texts), we recommend
[SoMeWeTa](https://github.com/tsproisl/SoMeWeTa):

```
somajo-tokenizer --split_sentences <file> | somewe-tagger --tag <model> -
```


## Features

  - Rule-based tokenization and sentence-splitting:
    - [EmpiriST 2015 tokenization
      guidelines](https://github.com/fau-klue/empirist-corpus/blob/9f00233951f7d1503ba4c3dd4af975d3c73cba80/doc/EmpiriST_Guideline-Tokenisierung.pdf)
      for German
    - “New” Penn Treebank conventions for English (described, for
      example, in the guidelines for ETTB 2.0 [(Mott et al.,
      2009)](https://web.archive.org/web/20110727133755/http://projects.ldc.upenn.edu/gale/task_specifications/ettb_guidelines.pdf)
      and CLEAR [(Warner et al.,
      2012)](https://clear.colorado.edu/compsem/documents/treebank_guidelines.pdf))
    - Optionally split camel-cased tokens
    - Optionally output token class information for each token, i.e.
      if it is a number, an emoticon, an abbreviation, etc.
    - Optionally output additional information for each token, e.g. if
      it was followed by whitespace or if it contained internal
      whitespace
    - Optionally split the tokenized text into sentences
    - Optionally determine the character offsets of the tokens in the
      input, allowing for stand-off tokenization
  - Text preprocessing/cleaning:
    - Normalize text to [Unicode Normalization Form C (NFC)](https://unicode.org/reports/tr15/)
    - Remove control characters and other usually unwanted characters,
      such as soft hyphens and zero-width spaces
  - XML support:
    - Transparent processing of XML: Tokenize the textual content of
      an XML file while preserving the XML structure
    - Optionally delimit sentence boundaries by XML tags
    - Optionally prune tags, i.e. subtrees, from the XML before
      tokenization (for example to remove `<script>` and `<style>`
      tags from HTML input)
    - Optionally strip all tags from the output, effectively turning
      the XML into plain text
  - Parallelization: Optionally run multiple worker processes to speed
    up tokenization


## Installation

SoMaJo can be easily installed using pip (pip3 in some distributions):

```sh
pip install -U SoMaJo
```

Alternatively, you can download and decompress the [latest
release](https://github.com/tsproisl/SoMaJo/releases/latest) or clone
the git repository:

```sh
git clone https://github.com/tsproisl/SoMaJo.git
```

In the new directory, run the following command:

```sh
pip install -U .
```


## Usage

### Using the somajo-tokenizer executable

You can use the tokenizer as a standalone program from the command
line. General usage information is available via the `-h` option:

```
somajo-tokenizer -h
usage: somajo-tokenizer [-h] [-l {en_PTB,de_CMC}]
                        [-s {single_newlines,empty_lines}] [-x] [--tag TAG]
                        [--prune PRUNE] [--strip-tags] [-c]
                        [--split_sentences] [--sentence_tag SENTENCE_TAG] [-t]
                        [-e] [--parallel N] [-v]
                        FILE

A tokenizer and sentence splitter for German and English texts. Currently, two
tokenization guidelines are implemented: The EmpiriST guidelines for German
web and social media texts (de_CMC) and the "new" Penn Treebank conventions
for English texts (en_PTB).

positional arguments:
  FILE                  The input file (UTF-8-encoded) or "-" to read from
                        STDIN.

options:
  -h, --help            show this help message and exit
  -l {en_PTB,de_CMC}, --language {en_PTB,de_CMC}
                        Choose a language. Currently supported are German
                        EmpiriST-style tokenization (de_CMC) and English Penn-
                        Treebank-style tokenization(en_PTB). (Default: de_CMC)
  -s {single_newlines,empty_lines}, --paragraph_separator {single_newlines,empty_lines}
                        How are paragraphs separated in the input text? Will
                        be ignored if option -x/--xml is used. (Default:
                        empty_lines)
  -x, --xml             The input is an XML file. You can specify tags that
                        always constitute a sentence break (e.g. HTML p tags)
                        via the --tag option.
  --tag TAG             Start and end tags of this type constitute sentence
                        breaks, i.e. they do not occur in the middle of a
                        sentence. Can be used multiple times to specify
                        multiple tags, e.g. --tag p --tag br. Implies option
                        -x/--xml. (Default: --tag title --tag h1 --tag h2
                        --tag h3 --tag h4 --tag h5 --tag h6 --tag p --tag br
                        --tag hr --tag div --tag ol --tag ul --tag dl --tag
                        table)
  --prune PRUNE         Tags of this type will be removed from the input
                        before tokenization. Can be used multiple times to
                        specify multiple tags, e.g. --tag script --tag style.
                        Implies option -x/--xml. By default, no tags are
                        pruned.
  --strip-tags          Suppresses output of XML tags. Implies option
                        -x/--xml.
  -c, --split_camel_case
                        Split items in written in camelCase (excluding
                        established names and terms).
  --split_sentences, --split-sentences
                        Also split the input into sentences.
  --sentence_tag SENTENCE_TAG, --sentence-tag SENTENCE_TAG
                        Tag name for sentence boundaries (e.g. --sentence_tag
                        s). If this option is specified, sentences will be
                        delimited by XML tags (e.g. <s>…</s>) instead of empty
                        lines. This option implies --split_sentences
  -t, --token_classes   Output the token classes (number, XML tag,
                        abbreviation, etc.) in addition to the tokens.
  -e, --extra_info      Output additional information for each token:
                        SpaceAfter=No if the token was not followed by a space
                        and OriginalSpelling="…" if the token contained
                        whitespace.
  --parallel N          Run N worker processes (up to the number of CPUs) to
                        speed up tokenization.
  -v, --version         Output version information and exit.
```

Here are some common use cases:

  - To tokenize a text file according to the guidelines of the
    EmpiriST 2015 shared task:
    
    ```
    somajo-tokenizer -c <file>
    ```
    
    <details><summary>Show example</summary>
    
    ```
    echo "der beste Betreuer? - >ProfSmith! : )" | somajo-tokenizer -c -
    der
    beste
    Betreuer
    ?
    ->
    Prof
    Smith
    !
    :)
    ```
    </details>
  - If you do not want to split camel-cased tokens, simply drop the
    `-c` option:
    
    ```
    somajo-tokenizer <file>
    ```
    
    <details><summary>Show example</summary>
    
    ```
    echo "der beste Betreuer? - >ProfSmith! : )" | somajo-tokenizer -
    der
    beste
    Betreuer
    ?
    ->
    ProfSmith
    !
    :)
    ```
    </details>
  - Your input delimits paragraphs by single newlines instead of empty
    lines? Tell the tokenizer via the `-s`/`--paragraph_separator`
    option:
    
    ```
    somajo-tokenizer --paragraph_separator single_newlines <file>
    ```
  - In addition to tokenizing the input, SoMaJo can also split it into
    sentences:
    
    ```
    somajo-tokenizer --split-sentences <file>
    ``` 
    
    <details><summary>Show example</summary>
    
    ```
    echo "Palim, Palim! Ich hätte gerne eine Flasche Pommes Frites." | somajo-tokenizer --split-sentences -
    Palim
    ,
    Palim
    !
    
    Ich
    hätte
    gerne
    eine
    Flasche
    Pommes
    Frites
    .
    
    ``` 
  - To tokenize English text according to the “new” Penn Treebank
    conventions, explicitly specify the tokenization guideline using
    the `-l`/`--language` option:
    
    ```
    somajo-tokenizer -l en_PTB <file>
    ```
    
    <details><summary>Show example</summary>
    
    ```
    echo "Dont you wanna come?" | somajo-tokenizer -l en_PTB -
    Do
    nt
    you
    wan
    na
    come
    ?
    ```
    </details>
  - SoMaJo can also process XML files. Use the `-x`/`--xml` option to
    tell the tokenizer that your input is an XML file:
    
    ```
    somajo-tokenizer --xml <xml-file>
    ```
    
    <details><summary>Show example</summary>
    
    ```
    echo '<html><head><title>Weihnachten</title></head><body><p>Fr&#x00fc;her war mehr Lametta!</p></body></html>' | somajo-tokenizer --xml -
    <html>
    <head>
    <title>
    Weihnachten
    </title>
    </head>
    <body>
    <p>
    Früher
    war
    mehr
    Lametta
    !
    </p>
    </body>
    </html>
    ```
    </details>
  - For XML input, you can use (multiple instances of) the `--tag`
    option to specify XML tags that are always sentence breaks, i.e.
    that can never occur in the middle of a sentence. See the help
    message for the default list of tags.
    
    ```
    somajo-tokenizer --xml --split_sentences --tag h1 --tag p --tag div <xml-file>
    ```
  - Via option `-t`/`--token_classes`, SoMaJo can output token class
    information for each token, i.e. if it is a number, an emoticon,
    an abbreviation, etc. Via option `-e`/`--extra_info`, additional
    information is available, e.g. if a token was followed by
    whitespace or if it contained internal whitespace.
    
    <details><summary>Show example</summary>
    
    ```
    echo "der beste Betreuer? - >ProfSmith! : )" | somajo-tokenizer -c -e -t -
    der      regular
    beste    regular
    Betreuer regular    SpaceAfter=No
    ?        symbol
    ->       symbol     SpaceAfter=No, OriginalSpelling="- >"
    Prof     regular    SpaceAfter=No
    Smith    regular    SpaceAfter=No
    !        symbol
    :)       emoticon   OriginalSpelling=": )"
    ```
    </details>
  - To speed up tokenization, you can specify the number of worker
    processes used via the `--parallel` option:
    
    ```
    somajo-tokenizer --parallel <number> <file>
    ```


### Using the module

You can easily incorporate SoMaJo into your own Python projects. All
you need to do is importing `somajo.SoMaJo`, creating a `SoMaJo`
object and calling one of its tokenizer functions: `tokenize_text`,
`tokenize_text_file`, `tokenize_xml` or `tokenize_xml_file`. These
functions return a generator that yields tokenized chunks of text. By
default, these chunks of text are sentences. If you set
`split_sentences=False`, then the chunks of text are either paragraphs
or chunks of XML. Every tokenized chunk of text is a list of `Token`
objects.

For more details, take a look at the [API
documentation](https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md).

Here is an example for tokenizing and sentence splitting two
paragraphs:

```python
from somajo import SoMaJo

tokenizer = SoMaJo("de_CMC", split_camel_case=True)

# note that paragraphs are allowed to contain newlines
paragraphs = ["der beste Betreuer?\n-- ProfSmith! : )",
              "Was machst du morgen Abend?! Lust auf Film?;-)"]

sentences = tokenizer.tokenize_text(paragraphs)
for sentence in sentences:
    for token in sentence:
        print("{}\t{}\t{}".format(token.text, token.token_class, token.extra_info))
    print()
```

And here is an example for tokenizing and sentence splitting a whole
file. The option `paragraph_separator="single_newlines"` states that
paragraphs are delimited by newlines instead of empty lines:

```python
sentences = tokenizer.tokenize_text_file("Beispieldatei.txt", paragraph_separator="single_newlines")
for sentence in sentences:
    for token in sentence:
        print(token.text)
    print()
```

For processing XML data, use the `tokenize_xml` or `tokenize_xml_file`
methods:

```python
eos_tags = ["title", "h1", "p"]

# you can read from an open file object
sentences = tokenizer.tokenize_xml_file(file_object, eos_tags)
# or you can specify a file name
sentences = tokenizer.tokenize_xml_file("Beispieldatei.xml", eos_tags)
# or you can pass a string with XML data
sentences = tokenizer.tokenize_xml(xml_string, eos_tags)

for sentence in sentences:
    for token in sentence:
        print(token.text)
    print()
```

## Evaluation

SoMaJo was the system with the highest average F₁ score in the
EmpiriST 2015 shared task. The performance of the current version on
the two test sets is summarized in the following table (Training and
test sets are available from the [official
website](https://sites.google.com/site/empirist2015/home/gold)):

| Corpus | Precision | Recall | F₁    |
|--------|-----------|--------|-------|
| CMC    | 99.71     | 99.56  | 99.64 |
| Web    | 99.91     | 99.92  | 99.91 |


## Tokenizing English text

Starting with version 1.8.0, SoMaJo can also tokenize English text. In
general, we follow the “new” Penn Treebank conventions described, for
example, in the guidelines for ETTB 2.0 [(Mott et al.,
2009)](https://web.archive.org/web/20110727133755/http://projects.ldc.upenn.edu/gale/task_specifications/ettb_guidelines.pdf)
and CLEAR [(Warner et al.,
2012)](https://clear.colorado.edu/compsem/documents/treebank_guidelines.pdf).

For tokenizing English text on the command line, specify the language
via the `-l` or `--language` option:

    somajo-tokenizer -l en_PTB <file>

From Python, you can pass `language="en_PTB"` to the `SoMaJo`
constructor, e.g.:

```python
paragraphs = ["That aint bad!:D"]
tokenizer = SoMaJo(language="en_PTB")
sentences = tokenizer.tokenize_text(paragraphs)
```

Performance of the English tokenizer:

| Corpus               | Precision | Recall | F₁    |
|----------------------|-----------|--------|-------|
| English Web Treebank | 99.66     | 99.64  | 99.65 |


## Development

Here are some brief notes to help you get started:

  - Preferably create a dedicated virtual environment.
  - Make sure you have pip ≥ 21.3.
  - Install the project in editable mode:
    
    ```sh
    pip install -U -e .
    ```
  - Install the development dependencies:
    
    ```sh
    pip install -r requirements_dev.txt
    ```
  - To run the tests:
    
    ```sh
    python3 -m unittest discover
    ```
  - To build the documentation:
    
    ```sh
    cd doc
    make markdown
    ```
    Note that the created markdown is not perfect and needs some
    manual postprocessing.
  - To build the distribution files:
    
    ```sh
    python3 -m build
    ```

## References

If you use SoMaJo for academic research, please consider citing the
following paper:

  - Proisl, Thomas, and Peter Uhrig. 2016. “SoMaJo: State-of-the-Art
    Tokenization for German Web and Social Media Texts.” In
    *Proceedings of the 10th Web as Corpus Workshop (WAC-X) and the
    EmpiriST Shared Task*, edited by Paul Cook, Stefan Evert, Roland
    Schäfer, and Egon Stemle, 57–62. Berlin: Association for
    Computational Linguistics. <https://doi.org/10.18653/v1/W16-2607>.
    
    ```bibtex
    @InProceedings{Proisl_Uhrig_EmpiriST:2016,
      author    = {Proisl, Thomas and Uhrig, Peter},
      title     = {{SoMaJo}: {S}tate-of-the-art tokenization for {G}erman web and social media texts},
      year      = {2016},
      booktitle = {Proceedings of the 10th {W}eb as {C}orpus Workshop ({WAC-X}) and the {EmpiriST} Shared Task},
      editor    = {Cook, Paul and Evert, Stefan and Schäfer, Roland and Stemle, Egon},
      address   = {Berlin},
      publisher = {Association for Computational Linguistics},
      pages     = {57--62},
      doi       = {10.18653/v1/W16-2607},
      url       = {https://aclanthology.org/W16-2607},
    }
    ```
