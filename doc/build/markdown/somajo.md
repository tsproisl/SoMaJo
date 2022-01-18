# somajo package

* [class somajo.somajo.SoMaJo](#class-somajosomajosomajolanguage--split_camel_casefalse-split_sentencestrue)
    * [tokenize_text](#tokenize_textparagraphs--parallel1)
    * [tokenize_text_file](#tokenize_text_filetext_file-paragraph_separator--parallel1)
    * [tokenize_xml](#tokenize_xmlxml_data-eos_tags--strip_tagsfalse-parallel1)
    * [tokenize_xml_file](#tokenize_xml_filexml_file-eos_tags--strip_tagsfalse-parallel1)
* [class somajo.token.Token](#class-somajotokentokentext--markupfalse-markup_classnone-markup_eosnone-lockedfalse-token_classnone-space_aftertrue-original_spellingnone-first_in_sentencefalse-last_in_sentencefalse)
    * [property extra_info()](#property-extra_info)


## somajo.somajo module


### class somajo.somajo.SoMaJo(language, \*, split_camel_case=False, split_sentences=True, xml_sentences=None)
Bases: `object`

Tokenization and sentence splitting.


* **Parameters**

    
    * **language** (*{'de_CMC', 'en_PTB'}*) – Language-specific tokenization rules.


    * **split_camel_case** (*bool, (default=False)*) – Split words written in camelCase (excluding established names
    and terms).


    * **split_sentences** (*bool, (default=True)*) – Perform sentence splitting in addition to tokenization.


    * **xml_sentences** (*str, (default=None)*) – Delimit sentences by XML tags of this name
    (`xml_sentences='s'` → <s>…</s>). When used with XML input,
    this might lead to minor changes to the original tags to
    guarantee well-formed output (tags might need to be closed and
    re-opened at sentence boundaries).


#### tokenize_text(paragraphs, \*, parallel=1)
Split paragraphs of text into sequences of tokens.


* **Parameters**

    * **paragraphs** (*iterable*) – An iterable of single paragraphs of text.


    * **parallel** (*int, (default=1)*) – Number of processes to use.



* **Yields**

    *list* – The `Token` objects in a single sentence or paragraph
    (depending on the value of `split_sentences`).


##### Examples

Tokenization and sentence splitting; print one sentence per
line:

```python
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

```python
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

```python
>>> sentences = tokenizer.tokenize_text(paragraphs)
>>> for sentence in sentences:
...     for token in sentence:
...         print("{}\t{}\t{}".format(token.text, token.token_class, token.extra_info))
...     print()
...
Heyi    regular SpaceAfter=No
:)      emoticon
​
Was     regular
machst  regular
du      regular
morgen  regular
Abend   regular SpaceAfter=No
?!      symbol
​
Lust    regular
auf     regular
Film    regular SpaceAfter=No
?       symbol  SpaceAfter=No
;-)     emoticon
​
```

Tokenization and sentence splitting; print one token per line
and delimit sentences with XML tags:

```python
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


#### tokenize_text_file(text_file, paragraph_separator, \*, parallel=1)
Split the contents of a text file into sequences of tokens.


* **Parameters**

    
    * **text_file** (*str or file-like object*) – Either a filename or a file-like object containing text.


    * **paragraph_separator** (*{'single_newlines', 'empty_lines'}*) – How are paragraphs separated in the input? Is there one
    paragraph per line (‘single_newlines’) or do paragraphs
    span several lines and are separated by ‘empty_lines’?


    * **parallel** (*int, (default=1)*) – Number of processes to use.



* **Yields**

    *list* – The `Token` objects in a single sentence or paragraph
    (depending on the value of `split_sentences`).


##### Examples

Tokenization and sentence splitting; input file with
paragraphs separated by empty lines; print one token per line
with token classes and extra information; print an empty line
after each sentence:

```python
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
Heyi    regular SpaceAfter=No
:)      emoticon
​
Was     regular
machst  regular
du      regular
morgen  regular
Abend   regular SpaceAfter=No
?!      symbol
​
Lust    regular
auf     regular
Film    regular SpaceAfter=No
?       symbol  SpaceAfter=No
;-)     emoticon
​
```

Tokenization and sentence splitting; input file with
paragraphs separated by single newlines; print one sentence
per line:

```python
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


#### tokenize_xml(xml_data, eos_tags, \*, strip_tags=False, parallel=1, prune_tags=None)
Split a string of XML data into sequences of tokens.


* **Parameters**

    
    * **xml_data** (*str*) – A string containing XML data.


    * **eos_tags** (*iterable*) – XML tags that constitute sentence breaks, i.e. tags that
    do not occur in the middle of a sentence. For HTML input,
    you might use the following list of tags: `['title',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
    'div', 'ol', 'ul', 'dl', 'table']`


    * **strip_tags** (*bool, (default=False)*) – Remove the XML tags from the output.


    * **parallel** (*int, (default=1)*) – Number of processes to use.


    * **prune_tags** (*iterable*) – These XML tags and their contents will be removed from the
    input before tokenization. For HTML input, you might use
    `['script', 'style']` or, depending on your use case,
    `['head']`.



* **Yields**

    *list* – The `Token` objects in a single sentence or stretch of
    XML delimited by `eos_tags` (depending on the value of
    `split_sentences`).


##### Examples

Tokenization and sentence splitting; print one token per line
and an empty line after each sentence:

```python
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

```python
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

```python
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

```python
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


#### tokenize_xml_file(xml_file, eos_tags, \*, strip_tags=False, parallel=1, prune_tags=None)
Split the contents of an xml file into sequences of tokens.


* **Parameters**

    
    * **xml_file** (*str or file-like object*) – A file containing XML data. Either a filename or a
    file-like object.


    * **eos_tags** (*iterable*) – XML tags that constitute sentence breaks, i.e. tags that
    do not occur in the middle of a sentence. For HTML input,
    you might use the following list of tags: `['title',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
    'div', 'ol', 'ul', 'dl', 'table']`


    * **strip_tags** (*bool, (default=False)*) – Remove all XML tags from the output.


    * **parallel** (*int, (default=1)*) – Number of processes to use.


    * **prune_tags** (*iterable*) – These XML tags and their contents will be removed from the
    input before tokenization. For HTML input, you might use
    `['script', 'style']` or, depending on your use case,
    `['head']`.



* **Yields**

    *list* – The `Token` objects in a single sentence or stretch of
    XML delimited by `eos_tags` (depending on the value of
    `split_sentences`).


##### Examples

Tokenization and sentence splitting; print one token per line
and an empty line after each sentence:

```python
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

```python
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

```python
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


### class somajo.token.Token(text, \*, markup=False, markup_class=None, markup_eos=None, locked=False, token_class=None, space_after=True, original_spelling=None, first_in_sentence=False, last_in_sentence=False)
Bases: `object`

Token objects store a piece of text (in the end a single token) with additional information.


* **Parameters**

    
    * **text** (*str*) – The text that makes up the token object


    * **markup** (*bool, (default=False)*) – Is the token a markup token?


    * **markup_class** (*{'start', 'end'}, optional (default=None)*) – If markup=True, then markup_class must be either “start” or “end”.


    * **markup_eos** (*bool, optional (default=None)*) – Is the markup token a sentence boundary?


    * **locked** (*bool, (default=False)*) – Mark the token as locked.


    * **token_class** (*str, optional (default=None)*) – The class of the token, e.g. “regular”, “emoticon”, “url”, etc.


    * **space_after** (*bool, (default=True)*) – Was there a space after the token in the original data?


    * **original_spelling** (*str, optional (default=None)*) – The original spelling of the token, if it is different from the one in text.


    * **first_in_sentence** (*bool, (default=False)*) – Is it the first token of a sentence?


    * **last_in_sentence** (*bool, (default=False)*) – Is it the last token of a sentence?



#### property extra_info()
String representation of extra information.


* **Returns**

    A string representation of the space_after and original_spelling attributes.



* **Return type**

    str


##### Examples

```python
>>> tok = Token(":)", token_class="regular", space_after=False, original_spelling=": )")
>>> print(tok.text)
:)
>>> print(tok.extra_info)
SpaceAfter=No, OriginalSpelling=": )"
```
