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

Using the module
----------------

You can easily incorporate the tokenizer into your own Python
projects. All you have to do is import ``somajo.Tokenizer``, create a
``Tokenizer`` object and call its ``tokenize`` method::

  from somajo import Tokenizer
  
  tokenizer = Tokenizer(split_camel_case=True, token_classes=False)
  tokens = tokenizer.tokenize(paragraph)

Evaluation
==========

SoMaJo was the system with the highest average F₁ score in the
EmpiriST 2015 shared task. The performance of the current version on
the two test sets is summarized in the following table\ [1]_:

====== ========= ====== ===========
Corpus Precision Recall F₁
====== ========= ====== ===========
CMC    99.62     99.56  99.59
Web    99.83     99.92  99.87
====== ========= ====== ===========

.. [1] Training and test sets are available from the `official website
       <https://sites.google.com/site/empirist2015/home/shared-task-data>`_.

References
==========

- Proisl, Thomas, Peter Uhrig (2016): “SoMaJo: State-of-the-art
  tokenization for German web and social media texts.” In: Proceedings
  of the 10th Web as Corpus Workshop (WAC-X). ACL.
