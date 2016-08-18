======
SoMaJo
======

Introduction
============

SoMaJo is a state-of-the-art tokenizer for German web and social media
texts that won the `EmpiriST 2015 shared task
<https://sites.google.com/site/empirist2015/>`_ on automatic
linguistic annotation of computer-mediated communication / social
media. As such, it is particularly well-suited to perform tokenization
on all kinds of written discourse, for example chats, forums, wiki
talk pages, tweets, blog comments, social networks, SMS and WhatsApp
dialogues.

In addition to tokenizing the input text, SoMaJo can also output token
class information for each token, i.e. if it is a number, an XML tag,
an abbreviation, etc.::

  echo 'Wow, superTool!;)' | tokenizer -c -t -
  Wow	regular
  ,	symbol
  super	regular
  Tool	regular
  !	symbol
  ;)	emoticon

*New in version 1.1.0*: SoMaJo can output additional information for
each token that can help to reconstruct the original untokenized text
(to a certain extent)::

  echo 'der beste Betreuer? - >ProfSmith! : )' | bin/tokenizer -c -e -
  der	
  beste	
  Betreuer	SpaceAfter=No
  ?	
  ->	SpaceAfter=No, OriginalSpelling="- >"
  Prof	SpaceAfter=No
  Smith	SpaceAfter=No
  !	
  :)	OriginalSpelling=": )"

The ``-t`` and ``-e`` options can also be used in combination, of course.

The system is described in greater detail in Proisl and Uhrig (2016).

Installation
============

SoMaJo can be easily installed using pip::

  pip install SoMaJo

Usage
=====

Using the tokenizer executable
------------------------------

You can use the tokenizer as a standalone program from the command
line. General usage information is available via the ``-h`` option::
  
  tokenizer -h

To tokenize a text file according to the guidelines of the EmpiriST
2015 shared task, just call the tokenizer like this::
  
  tokenizer -c <file>

If you do not want to split camel-cased tokens, simply drop the ``-c``
option::
  
  tokenizer <file>

The tokenizer can also output token class information for each token,
i.e. if it is a number, an XML tag, an abbreviation, etc.::
  
  tokenizer -t <file>

If you want to be able to reconstruct the untokenized input to a
certain extent, SoMaJo can also provide you with additional details
for each token, i.e. if the token was followed by whitespace or if it
contained internal whitespace (according to the tokenization
guidelines, things like “: )” get normalized to “:)”)::

  tokenizer -e <file>

Using the module
----------------

You can easily incorporate the tokenizer into your own Python
projects. All you have to do is import ``somajo.Tokenizer``, create a
``Tokenizer`` object and call its ``tokenize`` method::

  from somajo import Tokenizer
  
  tokenizer = Tokenizer(split_camel_case=True, token_classes=False, extra_info=False)
  tokens = tokenizer.tokenize(paragraph)

Evaluation
==========

SoMaJo was the system with the highest average F₁ score in the
EmpiriST 2015 shared task. The performance of the current version on
the two test sets is summarized in the following table\ [1]_:

====== ========= ====== =====
Corpus Precision Recall F₁
====== ========= ====== =====
CMC    99.62     99.56  99.59
Web    99.83     99.92  99.87
====== ========= ====== =====

.. [1] Training and test sets are available from the `official website
       <https://sites.google.com/site/empirist2015/home/shared-task-data>`_.

References
==========

- Proisl, Thomas, Peter Uhrig (2016): “SoMaJo: State-of-the-art
  tokenization for German web and social media texts.” In: Proceedings
  of the 10th Web as Corpus Workshop (WAC-X) and the EmpiriST Shared
  Task. Berlin: Association for Computational Linguistics (ACL),
  91–96. `PDF <http://aclweb.org/anthology/W16-2607>`_.
