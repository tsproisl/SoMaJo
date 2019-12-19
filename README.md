# SoMaJo #

  * [Introduction](#introduction)
  * [Installation](#installation)
  * [Usage](#usage)
      * [Using the somajo-tokenizer executable](#using-the-somajo-tokenizer-executable)
      * [Using the module](#using-the-module)
  * [Evaluation](#evaluation)
  * [Tokenizing English text](#tokenizing-english-text)
  * [References](#references)


## Introduction ##

SoMaJo is a state-of-the-art tokenizer and sentence splitter for
German and English web and social media texts. It won the [EmpiriST
2015 shared task](https://sites.google.com/site/empirist2015/) on
automatic linguistic annotation of computer-mediated communication /
social media. As such, it is particularly well-suited to perform
tokenization on all kinds of written discourse, for example chats,
forums, wiki talk pages, tweets, blog comments, social networks, SMS
and WhatsApp dialogues.

In addition to tokenizing the input text, SoMaJo can also output token
class information for each token, i.e. if it is a number, an emoticon,
an abbreviation, etc.:

    echo 'Wow, superTool!;)' | somajo-tokenizer -c -t -
    Wow	regular
    ,	symbol
    super	regular
    Tool	regular
    !	symbol
    ;)	emoticon

SoMaJo can also output additional information for each token that can
help to reconstruct the original untokenized text (to a certain
extent):

    echo 'der beste Betreuer? - >ProfSmith! : )' | somajo-tokenizer -c -e -
    der	
    beste	
    Betreuer	SpaceAfter=No
    ?	
    ->	SpaceAfter=No, OriginalSpelling="- >"
    Prof	SpaceAfter=No
    Smith	SpaceAfter=No
    !	
    :)	OriginalSpelling=": )"

The `-t` and `-e` options can also be used in combination, of course.

SoMaJo can split the input text into sentences using the
`--split_sentences` option.

SoMaJo has full XML support, i.e. it can perform sensible tokenization
and sentence splitting on well-formed XML files using the `--xml` and
`--tag` options.

The system is described in greater detail in [Proisl and Uhrig
(2016)](http://aclweb.org/anthology/W16-2607).

For part-of-speech tagging, we recommend
[SoMeWeTa](https://github.com/tsproisl/SoMeWeTa), a part-of-speech
tagger with state-of-the-art performance on German web and social
media texts:

    somajo-tokenizer --split_sentences <file> | somewe-tagger --tag <model> -


## Installation ##

SoMaJo can be easily installed using pip (pip3 in some distributions):

    pip install SoMaJo

Alternatively, you can download and decompress the [latest
release](https://github.com/tsproisl/SoMaJo/releases/latest) or clone
the git repository:

    git clone https://github.com/tsproisl/SoMaJo.git

In the new directory, run the following command:

    python3 setup.py install


## Usage ##

### Using the somajo-tokenizer executable

You can use the tokenizer as a standalone program from the command
line. General usage information is available via the `-h` option:

    somajo-tokenizer -h

To tokenize a text file according to the guidelines of the EmpiriST
2015 shared task, just call the tokenizer like this:

    somajo-tokenizer -c <file>

If you do not want to split camel-cased tokens, simply drop the `-c`
option:

    somajo-tokenizer <file>

The tokenizer can also output token class information for each token,
i.e. if it is a number, an emoticon, an abbreviation, etc.:

    somajo-tokenizer -t <file>

If you want to be able to reconstruct the untokenized input to a
certain extent, SoMaJo can also provide you with additional details
for each token, i.e. if the token was followed by whitespace or if it
contained internal whitespace (according to the EmpiriST tokenization
guidelines, things like “: )” get normalized to “:)”):

    somajo-tokenizer -e <file>

SoMaJo assumes that paragraphs are delimited by empty lines in the
input file. If your input file uses single newlines instead, you have
to tell that to the tokenizer via the `-s` or `--paragraph_separator`
option:

    somajo-tokenizer --paragraph_separator single_newlines <file>

To speed up tokenization, you can specify the number of worker
processes used via the `--parallel` option:

    somajo-tokenizer --parallel <number> <file>

SoMaJo can split the input paragraphs into sentences:

    somajo-tokenizer --split_sentences <file>

SoMaJo can also process XML files. Use the `-x` or `--xml` option to
tell the tokenizer that your input is an XML file:

    somajo-tokenizer --xml <xml-file>

If you also want to do sentence splitting, you can use (multiple
instances of) the `--tag` option to specify XML tags that are always
sentence breaks, i.e. that can never occur in the middle of a
sentence. Per default, the sentence splitter uses the following list
of tags: title, h1, h2, h3, h4, h5, h6, p, br, hr, div, ol, ul, dl and
table.

    somajo-tokenizer --xml --split_sentences --tag h1 --tag p --tag div <xml-file>


### Using the module ###

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
documentation](docs/build/markdown/somajo.md).

Here is an example for tokenizing and sentence splitting two paragraphs:

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

For processing XML data, use the `tokenize_xml` or `tokenize_xml_file` methods:

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

## Evaluation ##

SoMaJo was the system with the highest average F₁ score in the
EmpiriST 2015 shared task. The performance of the current version on
the two test sets is summarized in the following table (Training and
test sets are available from the [official
website](https://sites.google.com/site/empirist2015/home/gold)):

| Corpus | Precision | Recall | F₁    |
|--------|-----------|--------|-------|
| CMC    | 99.71     | 99.56  | 99.64 |
| Web    | 99.84     | 99.92  | 99.88 |


## Tokenizing English text ##

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
| English Web Treebank | 99.65     | 99.62  | 99.63 |


## References ##

  * Proisl, Thomas, Peter Uhrig (2016): “SoMaJo: State-of-the-art
    tokenization for German web and social media texts.” In:
    Proceedings of the 10th Web as Corpus Workshop (WAC-X) and the
    EmpiriST Shared Task. Berlin: Association for Computational
    Linguistics (ACL), 57–62.
    [PDF](http://aclweb.org/anthology/W16-2607).

	```bibtex
    @InProceedings{Proisl_Uhrig_EmpiriST:2016,
      author    = {Proisl, Thomas and Uhrig, Peter},
      title     = {{SoMaJo}: {S}tate-of-the-art tokenization for {G}erman web and social media texts},
      booktitle = {Proceedings of the 10th {W}eb as {C}orpus Workshop ({WAC-X}) and the {EmpiriST} Shared Task},
      year      = {2016},
      address   = {Berlin},
      publisher = {Association for Computational Linguistics ({ACL})},
      pages     = {57--62},
      url       = {http://aclweb.org/anthology/W16-2607},
    }
	```
