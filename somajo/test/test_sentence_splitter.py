#!/usr/bin/env python3

import unittest

from somajo import SoMaJo


class TestSentenceSplitter(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC", split_camel_case=True, split_sentences=True)

    def _equal(self, raw, tokenized_sentences):
        """"""
        sentences = self.tokenizer.tokenize_text([raw])
        sentences = [" ".join([t.text for t in s]) for s in sentences]
        self.assertEqual(sentences, tokenized_sentences)

    def _equal_xml(self, raw, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        sentences = self.tokenizer.tokenize_xml(raw, eos_tags)
        sentences = [" ".join([t.text for t in s]) for s in sentences]
        self.assertEqual(sentences, tokenized_sentences)


class TestMisc(TestSentenceSplitter):
    """"""
    def test_misc_01(self):
        self._equal("„Ich habe heute keine Zeit“, sagte die Frau und flüsterte leise: „Und auch keine Lust.“ Wir haben 1.000.000 Euro.", ["„ Ich habe heute keine Zeit “ , sagte die Frau und flüsterte leise : „ Und auch keine Lust . “", "Wir haben 1.000.000 Euro ."])

    def test_misc_02(self):
        self._equal("Es gibt jedoch einige Vorsichtsmaßnahmen, die Du ergreifen kannst, z. B. ist es sehr empfehlenswert, dass Du Dein Zuhause von allem Junkfood befreist.", ["Es gibt jedoch einige Vorsichtsmaßnahmen , die Du ergreifen kannst , z. B. ist es sehr empfehlenswert , dass Du Dein Zuhause von allem Junkfood befreist ."])

    def test_misc_03(self):
        self._equal("Was sind die Konsequenzen der Abstimmung vom 12. Juni?", ["Was sind die Konsequenzen der Abstimmung vom 12. Juni ?"])

    def test_misc_04(self):
        self._equal("Wir könnten wandern, schwimmen, Fahrrad fahren, usw. Worauf hättest du denn Lust?", ["Wir könnten wandern , schwimmen , Fahrrad fahren , usw.", "Worauf hättest du denn Lust ?"])


class TestXML(TestSentenceSplitter):
    """"""
    def test_xml_01(self):
        self._equal_xml("<foo><p>hallo</p>du</foo>", ["<foo> <p> hallo </p>", "du </foo>"])

    def test_xml_02(self):
        self._equal_xml("<foo><p></p><p>hallo</p>du</foo>", ["<foo> <p> </p> <p> hallo </p>", "du </foo>"])

    def test_xml_03(self):
        self._equal_xml("<bar><foo>Foo bar.</foo><foo></foo></bar>", ["<bar> <foo> Foo bar . </foo> <foo> </foo> </bar>"])

    def test_xml_04(self):
        self._equal_xml("<foo>Foo<br></br>bar</foo>", ["<foo> Foo", "<br> </br> bar </foo>"])

    def test_xml_05(self):
        # self._equal_xml("<foo>Foo<br/>bar</foo>", ["<foo> Foo", "<br/> bar </foo>"])
        self._equal_xml("<foo>Foo<br/>bar</foo>", ["<foo> Foo", "<br> </br> bar </foo>"])

    def test_xml_06(self):
        self._equal_xml("<foo><p>foo bar</p>\n\n<p>foo bar</p></foo>", ["<foo> <p> foo bar </p>", "<p> foo bar </p> </foo>"])
