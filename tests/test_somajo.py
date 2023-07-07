#!/usr/bin/env python3

import io
import unittest

from somajo.somajo import SoMaJo


class TestSoMaJo(unittest.TestCase):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC")

    def _equal_text(self, paragraphs, tokenized_sentences, parallel=1):
        sentences = self.tokenizer.tokenize_text(paragraphs, parallel=parallel)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_text_file_single_newlines(self, paragraphs, tokenized_sentences, parallel=1):
        pseudofile = io.StringIO("\n".join(paragraphs))
        sentences = self.tokenizer.tokenize_text_file(pseudofile, paragraph_separator="single_newlines", parallel=parallel)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_text_file_empty_lines(self, paragraphs, tokenized_sentences, parallel=1):
        pseudofile = io.StringIO("\n\n".join(paragraphs))
        sentences = self.tokenizer.tokenize_text_file(pseudofile, paragraph_separator="empty_lines", parallel=parallel)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_xml(self, xml, tokenized_sentences, strip_tags=False, parallel=1, prune_tags=None):
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        sentences = self.tokenizer.tokenize_xml(xml, eos_tags, strip_tags=strip_tags, parallel=parallel, prune_tags=prune_tags)
        sentences = [[t.text for t in s] for s in sentences]
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_xml_file(self, xml, tokenized_sentences, strip_tags=False, parallel=1, prune_tags=None):
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        pseudofile = io.StringIO(xml)
        sentences = self.tokenizer.tokenize_xml_file(pseudofile, eos_tags, strip_tags=strip_tags, parallel=parallel, prune_tags=prune_tags)
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

    def test_text_04(self):
        self.assertRaises(TypeError, self.tokenizer.tokenize_text, "Foo bar. Baz qux")


class TestTextXMLSent(TestSoMaJo):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC", xml_sentences="s")

    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["<s> Foo bar . </s>", "<s> Baz qux </s>", "<s> alpha . </s>", "<s> Beta gamma </s>"])

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["<s> Foo bar . </s>", "<s> Baz qux </s>", "<s> alpha . </s>", "<s> Beta gamma </s>"])


class TestTextParallel(TestSoMaJo):
    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"], parallel=2)

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"], parallel=2)

    def test_text_03(self):
        self._equal_text_file_single_newlines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"], parallel=2)


class TestTextNoSent(TestSoMaJoNoSent):
    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])

    def test_text_03(self):
        self._equal_text_file_single_newlines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"])


class TestTextNoSentParallel(TestSoMaJoNoSent):
    def test_text_01(self):
        self._equal_text(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"], parallel=2)

    def test_text_02(self):
        self._equal_text_file_empty_lines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"], parallel=2)

    def test_text_03(self):
        self._equal_text_file_single_newlines(["Foo bar. Baz qux", "alpha. Beta gamma"], ["Foo bar . Baz qux", "alpha . Beta gamma"], parallel=2)


class TestXML(TestSoMaJo):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"])

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"])


class TestXMLParallel(TestSoMaJo):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"], parallel=2)

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"], parallel=2)


class TestXMLNoSent(TestSoMaJoNoSent):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"])

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"])


class TestXMLNoSentParallel(TestSoMaJoNoSent):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"], parallel=2)

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar . Baz qux </p>", "<p> alpha . Beta gamma </p> </body> </html>"], parallel=2)


class TestXMLStripTags(TestSoMaJo):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"], strip_tags=True)

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["Foo bar .", "Baz qux", "alpha .", "Beta gamma"], strip_tags=True)


class TestXMLPruneTags(TestSoMaJo):
    def test_xml_01(self):
        self._equal_xml("<html>\n  <head>\n    Spam\n  </head>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"], prune_tags=["head"])

    def test_xml_02(self):
        self._equal_xml_file("<html>\n  <head>\n    Spam\n  </head>\n  <body>\n    <p>Foo bar. Baz qux</p>\n    <p>alpha. Beta gamma</p>\n  </body>\n</html>", ["<html> <body> <p> Foo bar .", "Baz qux </p>", "<p> alpha .", "Beta gamma </p> </body> </html>"], prune_tags=["head"])
