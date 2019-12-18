#!/usr/bin/env python3

import io
import unittest

from somajo.somajo import SoMaJo


class TestSoMaJo(unittest.TestCase):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC")

    def _equal_text(self, paragraphs, tokenized_sentences):
        sentences = self.tokenizer.tokenize_text(paragraphs)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_text_file_single_newlines(self, paragraphs, tokenized_sentences):
        pseudofile = io.StringIO("\n".join(paragraphs))
        sentences = self.tokenizer.tokenize_text_file(pseudofile, paragraph_separator="single_newlines")
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_text_file_empty_lines(self, paragraphs, tokenized_sentences):
        pseudofile = io.StringIO("\n\n".join(paragraphs))
        sentences = self.tokenizer.tokenize_text_file(pseudofile, paragraph_separator="empty_lines")
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_xml(self, xml, tokenized_sentences):
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        sentences = self.tokenizer.tokenize_xml(xml, eos_tags)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_xml_file(self, xml, tokenized_sentences):
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        pseudofile = io.StringIO(xml)
        sentences = self.tokenizer.tokenize_xml_file(pseudofile, eos_tags)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])


class TestSoMaJoNoSent(TestSoMaJo):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC", split_sentences=False)


class TestText(TestSoMaJo):
    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"])

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"])

    def test_text_03(self):
        self._equal_text_file_single_newlines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"])


class TestTextNoSent(TestSoMaJoNoSent):
    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])

    def test_text_03(self):
        self._equal_text_file_single_newlines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])


class TestXML(TestSoMaJo):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"])

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"])


class TestXMLNoSent(TestSoMaJoNoSent):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"])

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"])
