# somajo package

* [class somajo.somajo.SoMaJo](#class-somajosomajosomajolanguage-literalde_cmc-en_ptb--split_camel_case-bool--false-split_sentences-bool--true-xml_sentences-str--none--none-character_offsets-bool--false)
    * [tokenize_text](#tokenize_textparagraphs-iterablestr--parallel-int--1--iteratorlisttoken)
    * [tokenize_text_file](#tokenize_text_filetext_file-str--textio-paragraph_separator-literalempty_lines-single_newlines--parallel-int--1--iteratorlisttoken)
    * [tokenize_xml](#tokenize_xmlxml_data-str-eos_tags-iterablestr--strip_tags-bool--false-parallel-int--1-prune_tags-iterablestr--none--none--iteratorlisttoken)
    * [tokenize_xml_file](#tokenize_xml_filexml_file-str--textio-eos_tags-iterablestr--strip_tags-bool--false-parallel-int--1-prune_tags-iterablestr--none--none--iteratorlisttoken)
* [class somajo.token.Token](#class-somajotokentokentext-str--markup-bool--false-markup_class-literalstart-end--none--none-markup_eos-bool--none--none-locked-bool--false-token_class-str--none--none-space_after-bool--true-original_spelling-str--none--none-first_in_sentence-bool--false-last_in_sentence-bool--false-character_offset-tupleint-int--none--none)
    * [property extra_info()](#property-extra_info--str)

## somajo.somajo module

### *class* somajo.somajo.SoMaJo(language: Literal['de_CMC', 'en_PTB'], \*, split_camel_case: bool = False, split_sentences: bool = True, xml_sentences: str | None = None, character_offsets: bool = False)

Bases: `object`

Tokenization and sentence splitting.

* **Parameters:**
  * **language** – Language-specific tokenization rules. ‘de_CMC’ for
    German, ‘en_PTB’ for English.
  * **split_camel_case** – Split words written in camelCase (excluding established names
    and terms). Defaults to False.
  * **split_sentences** – Perform sentence splitting in addition to tokenization.
    Defaults to True.
  * **xml_sentences** – Delimit sentences by XML tags of this name
    (e.g., `xml_sentences='s'` produces `<s>...</s>` tags). When used with XML input,
    this might lead to minor changes to the original tags to guarantee well-formed
    output (tags might need to be closed and re-opened at sentence boundaries).
    Defaults to None.
  * **character_offsets** – Compute the character offsets in the input for each token.
    This allows for stand-off tokenization. Defaults to False.

#### tokenize_text(paragraphs: Iterable[str], \*, parallel: int = 1) → Iterator[list[[Token](#class-somajotokentokentext-str--markup-bool--false-markup_class-literalstart-end--none--none-markup_eos-bool--none--none-locked-bool--false-token_class-str--none--none-space_after-bool--true-original_spelling-str--none--none-first_in_sentence-bool--false-last_in_sentence-bool--false-character_offset-tupleint-int--none--none)]]

Split paragraphs of text into sequences of tokens.

* **Parameters:**
  * **paragraphs** – An iterable of single paragraphs of text.
  * **parallel** – Number of processes to use. Defaults to 1.
* **Yields:**
  *list* –

  The Token objects in a single sentence or paragraph
  : (depending on the value of `split_sentences`).

##### Examples

Tokenization and sentence splitting; print one sentence per
line:

```pycon
>>> paragraphs = ["Heyi:)", "Was machst du morgen Abend?! Lust auf Film?;-)"]
>>> tokenizer = SoMaJo("de_CMC")
>>> sentences = tokenizer.tokenize_text(paragraphs)
>>> for sentence in sentences:
...     print(" ".join([token.text for token in sentence]))
...
Heyi :)
Was machst du morgen Abend ?!
Lust auf Film ? ;-)
```

Only tokenization; print one paragraph per line:

```pycon
>>> tokenizer = SoMaJo("de_CMC", split_sentences=False)
>>> tokenized_paragraphs = tokenizer.tokenize_text(paragraphs)
>>> for paragraph in tokenized_paragraphs:
...     print(" ".join([token.text for token in paragraph]))
...
Heyi :)
Was machst du morgen Abend ?! Lust auf Film ? ;-)
```

Tokenization and sentence splitting; print one token per line
with token classes and extra information; print an empty line
after each sentence:

```pycon
>>> sentences = tokenizer.tokenize_text(paragraphs)
>>> for sentence in sentences:
...     for token in sentence:
...         print("{token.text}     {token.token_class}     {token.extra_info}")
...     print()
...
Heyi        regular SpaceAfter=No
:)  emoticon
​
Was regular
machst      regular
du  regular
morgen      regular
Abend       regular SpaceAfter=No
?!  symbol
​
Lust        regular
auf regular
Film        regular SpaceAfter=No
?   symbol  SpaceAfter=No
;-) emoticon
​
```

Tokenization and sentence splitting; print one token per line
and delimit sentences with XML tags:

```pycon
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
```

#### tokenize_text_file(text_file: str | TextIO, paragraph_separator: Literal['empty_lines', 'single_newlines'], \*, parallel: int = 1) → Iterator[list[[Token](#class-somajotokentokentext-str--markup-bool--false-markup_class-literalstart-end--none--none-markup_eos-bool--none--none-locked-bool--false-token_class-str--none--none-space_after-bool--true-original_spelling-str--none--none-first_in_sentence-bool--false-last_in_sentence-bool--false-character_offset-tupleint-int--none--none)]]

Split the contents of a text file into sequences of tokens.

* **Parameters:**
  * **text_file** – Either a filename or a file-like object containing text.
  * **paragraph_separator** – How are paragraphs separated in the input?
    ‘single_newlines’ means one paragraph per line.
    ‘empty_lines’ means paragraphs span several lines and are
    separated by empty lines.
  * **parallel** – Number of processes to use. Defaults to 1.
* **Yields:**
  *list* –

  The Token objects in a single sentence or paragraph
  : (depending on the value of `split_sentences`).

##### Examples

Tokenization and sentence splitting; input file with
paragraphs separated by empty lines; print one token per line
with token classes and extra information; print an empty line
after each sentence:

```pycon
>>> with open("example_empty_lines.txt") as f:
...     print(f.read())
...
Heyi:)
​
Was machst du morgen Abend?! Lust auf Film?;-)
>>> sentences = tokenizer.tokenize_text_file("example_empty_lines.txt", paragraph_separator="single_newlines")
>>> for sentence in sentences:
...     for token in sentence:
...         print("{token.text}     {token.token_class}     {token.extra_info}")
...     print()
...
Heyi        regular SpaceAfter=No
:)  emoticon
​
Was regular
machst      regular
du  regular
morgen      regular
Abend       regular SpaceAfter=No
?!  symbol
​
Lust        regular
auf regular
Film        regular SpaceAfter=No
?   symbol  SpaceAfter=No
;-) emoticon
​
```

Tokenization and sentence splitting; input file with
paragraphs separated by single newlines; print one sentence
per line:

```pycon
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
```

#### tokenize_xml(xml_data: str, eos_tags: Iterable[str], \*, strip_tags: bool = False, parallel: int = 1, prune_tags: Iterable[str] | None = None) → Iterator[list[[Token](#class-somajotokentokentext-str--markup-bool--false-markup_class-literalstart-end--none--none-markup_eos-bool--none--none-locked-bool--false-token_class-str--none--none-space_after-bool--true-original_spelling-str--none--none-first_in_sentence-bool--false-last_in_sentence-bool--false-character_offset-tupleint-int--none--none)]]

Split a string of XML data into sequences of tokens.

* **Parameters:**
  * **xml_data** – A string containing XML data.
  * **eos_tags** – XML tags that constitute sentence breaks, i.e. tags that
    do not occur in the middle of a sentence. For HTML input,
    you might use the following list of tags: [‘title’,
    ‘h1’, ‘h2’, ‘h3’, ‘h4’, ‘h5’, ‘h6’, ‘p’, ‘br’, ‘hr’,
    ‘div’, ‘ol’, ‘ul’, ‘dl’, ‘table’]
  * **strip_tags** – Remove the XML tags from the output. Defaults to False.
  * **parallel** – Number of processes to use. Defaults to 1.
  * **prune_tags** – These XML tags and their contents will be removed from the
    input before tokenization. For HTML input, you might use
    [‘script’, ‘style’] or, depending on your use case,
    [‘head’]. Defaults to None.
* **Yields:**
  *list* –

  The Token objects in a single sentence or stretch of
  : XML delimited by `eos_tags` (depending on the value of
    `split_sentences`).

##### Examples

Tokenization and sentence splitting; print one token per line
and an empty line after each sentence:

```pycon
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
```

Tokenization and sentence splitting; strip XML tags from the
output and print one sentence per line

```pycon
>>> sentences = tokenizer.tokenize_xml(xml, eos_tags, strip_tags=True)
>>> for sentence in sentences:
...     print(" ".join([token.text for token in sentence]))
...
Heyi :)
Was machst du morgen Abend ?!
Lust auf Film ? ;-)
```

Only tokenization; print one chunk of XML (delimited by
`eos_tags`) per line:

```pycon
>>> tokenizer = SoMaJo("de_CMC", split_sentences=False)
>>> chunks = tokenizer.tokenize_xml(xml, eos_tags)
>>> for chunk in chunks:
...     print(" ".join([token.text for token in chunk]))
...
<html> <body> <p> Heyi :) </p>
<p> Was machst du morgen Abend ?! Lust auf Film ? ;-) </p> </body> </html>
```

Tokenization and sentence splitting; print one token per line
and delimit sentences with XML tags:

```pycon
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
```

#### tokenize_xml_file(xml_file: str | TextIO, eos_tags: Iterable[str], \*, strip_tags: bool = False, parallel: int = 1, prune_tags: Iterable[str] | None = None) → Iterator[list[[Token](#class-somajotokentokentext-str--markup-bool--false-markup_class-literalstart-end--none--none-markup_eos-bool--none--none-locked-bool--false-token_class-str--none--none-space_after-bool--true-original_spelling-str--none--none-first_in_sentence-bool--false-last_in_sentence-bool--false-character_offset-tupleint-int--none--none)]]

Split the contents of an xml file into sequences of tokens.

* **Parameters:**
  * **xml_file** – A file containing XML data. Either a filename or a file-like object.
  * **eos_tags** – XML tags that constitute sentence breaks, i.e. tags that
    do not occur in the middle of a sentence. For HTML input,
    you might use the following list of tags: [‘title’,
    ‘h1’, ‘h2’, ‘h3’, ‘h4’, ‘h5’, ‘h6’, ‘p’, ‘br’, ‘hr’,
    ‘div’, ‘ol’, ‘ul’, ‘dl’, ‘table’]
  * **strip_tags** – Remove all XML tags from the output. Defaults to False.
  * **parallel** – Number of processes to use. Defaults to 1.
  * **prune_tags** – These XML tags and their contents will be removed from the
    input before tokenization. For HTML input, you might use
    [‘script’, ‘style’] or, depending on your use case,
    [‘head’]. Defaults to None.
* **Yields:**
  *list* –

  The Token objects in a single sentence or stretch of
  : XML delimited by `eos_tags` (depending on the value of
    `split_sentences`).

##### Examples

Tokenization and sentence splitting; print one token per line
and an empty line after each sentence:

```pycon
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
```

Tokenization and sentence splitting; strip XML tags from the
output and print one sentence per line:

```pycon
>>> with open("example.xml") as f:
...     sentences = tokenizer.tokenize_xml_file(f, eos_tags, strip_tags=True)
...     for sentence in sentences:
...         print(" ".join(token.text for token in sentence))
...
Heyi :)
Was machst du morgen Abend ?!
Lust auf Film ? ;-)
```

Only tokenization; print one token per line

```pycon
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
```

## somajo.token module

### *class* somajo.token.Token(text: str, \*, markup: bool = False, markup_class: Literal['start', 'end'] | None = None, markup_eos: bool | None = None, locked: bool = False, token_class: str | None = None, space_after: bool = True, original_spelling: str | None = None, first_in_sentence: bool = False, last_in_sentence: bool = False, character_offset: Tuple[int, int] | None = None)

Bases: `object`

Token objects store a piece of text (in the end a single token) with additional information.

* **Parameters:**
  * **text** – The text that makes up the token object.
  * **markup** – Is the token a markup token? Defaults to False.
  * **markup_class** – If markup=True, then markup_class must be either “start” or “end”.
    Defaults to None.
  * **markup_eos** – Is the markup token a sentence boundary? Defaults to None.
  * **locked** – Mark the token as locked. Defaults to False.
  * **token_class** – The class of the token, e.g. “regular”, “emoticon”, “URL”, etc.
    Must be one of: ‘URL’, ‘XML_entity’, ‘XML_tag’, ‘abbreviation’, ‘action_word’,
    ‘amount’, ‘date’, ‘email_address’, ‘emoticon’, ‘hashtag’, ‘measurement’,
    ‘mention’, ‘number’, ‘ordinal’, ‘regular’, ‘semester’, ‘symbol’, ‘time’.
    Defaults to None.
  * **space_after** – Was there a space after the token in the original data?
    Defaults to True.
  * **original_spelling** – The original spelling of the token, if it is different from
    the one in text. Defaults to None.
  * **first_in_sentence** – Is it the first token of a sentence? Defaults to False.
  * **last_in_sentence** – Is it the last token of a sentence? Defaults to False.
  * **character_offset** – Character offset of the token in the input as tuple (start, end)
    such that input[start:end] == text (if there are no changes to the token text
    during tokenization). Defaults to None.

#### *property* extra_info *: str*

String representation of extra information.

* **Returns:**
  A string representation of the space_after and original_spelling attributes.
* **Return type:**
  str

##### Examples

```pycon
>>> tok = Token(":)", token_class="regular", space_after=False, original_spelling=": )")
>>> print(tok.text)
:)
>>> print(tok.extra_info)
SpaceAfter=No, OriginalSpelling=": )"
```

#### token_classes *: set[str]* *= {'URL', 'XML_entity', 'XML_tag', 'abbreviation', 'action_word', 'amount', 'date', 'email_address', 'emoticon', 'hashtag', 'measurement', 'mention', 'number', 'ordinal', 'regular', 'semester', 'symbol', 'time'}*
