import importlib.metadata

from somajo import tokenizer
from somajo import sentence_splitter
from somajo import somajo

__version__ = importlib.metadata.version(__package__ or __name__)

Tokenizer = tokenizer.Tokenizer
SentenceSplitter = sentence_splitter.SentenceSplitter
SoMaJo = somajo.SoMaJo
