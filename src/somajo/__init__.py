import importlib.metadata

from . import (
    sentence_splitter,
    somajo,
    tokenizer
)

__version__ = importlib.metadata.version(__package__ or __name__)

Tokenizer = tokenizer.Tokenizer
SentenceSplitter = sentence_splitter.SentenceSplitter
SoMaJo = somajo.SoMaJo
