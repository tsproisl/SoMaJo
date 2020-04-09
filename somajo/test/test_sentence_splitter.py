#!/usr/bin/env python3

import unittest

from somajo import SentenceSplitter
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


class TestSentenceSplitterEnglish(TestSentenceSplitter):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("en_PTB", split_camel_case=True, split_sentences=True)


class TestSentenceSplitterPretokenized(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.sentence_splitter = SentenceSplitter(language="de_CMC")

    def _equal(self, tokens, tokenized_sentences):
        """"""
        sentences = self.sentence_splitter.split(tokens.split())
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])

    def _equal_xml(self, tokens, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        sentences = self.sentence_splitter.split_xml(tokens.split(), eos_tags)
        self.assertEqual(sentences, [ts.split() for ts in tokenized_sentences])


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

    def test_misc_05(self):
        self._equal("Er sagte: \"Das ist schlimm.\" Und damit hatte er recht.", ["Er sagte : \" Das ist schlimm . \"", "Und damit hatte er recht ."])

    def test_misc_06(self):
        self._equal("Er sagte: „Das ist schlimm.“ Und damit hatte er recht.", ["Er sagte : „ Das ist schlimm . “", "Und damit hatte er recht ."])

    def test_misc_07(self):
        self._equal("Foo \"Bar.\" Baz.", ["Foo \" Bar . \"", "Baz ."])

    def test_misc_08(self):
        self._equal("Foo „Bar.“ Baz.", ["Foo „ Bar . “", "Baz ."])

    def test_misc_09(self):
        self._equal("Foo “Bar.” Baz.", ["Foo “ Bar . ”", "Baz ."])

    def test_misc_10(self):
        self._equal("Foo »Bar.« Baz.", ["Foo » Bar . «", "Baz ."])

    def test_misc_11(self):
        self._equal("Foo «Bar.» Baz.", ["Foo « Bar . »", "Baz ."])

    def test_misc_12(self):
        self._equal("Foo (bar, baz, usw.) quux", ["Foo ( bar , baz , usw. ) quux"])

    def test_misc_13(self):
        self._equal("(Bar, baz, usw.) Quux", ["( Bar , baz , usw. )", "Quux"])

    def test_misc_14(self):
        self._equal("Foo, bar, baz, usw. quux", ["Foo , bar , baz , usw. quux"])

    def test_misc_15(self):
        self._equal("Foo, bar, baz, usw. Quux", ["Foo , bar , baz , usw.", "Quux"])

    def test_misc_16(self):
        self._equal("„Hi!“ „Hi!“", ["„ Hi ! “", "„ Hi ! “"])

    def test_misc_17(self):
        self._equal("blafasel bla. 700 Jahre später…", ["blafasel bla .", "700 Jahre später …"])


class TestMiscEnglish(TestSentenceSplitterEnglish):
    """"""
    def test_misc_en_01(self):
        self._equal("Foo \"Bar.\" Baz.", ["Foo \" Bar . \"", "Baz ."])

    def test_misc_en_02(self):
        self._equal("Foo “Bar.” Baz.", ["Foo “ Bar . ”", "Baz ."])

    def test_misc_en_03(self):
        self._equal("Foo «Bar.» Baz.", ["Foo « Bar . »", "Baz ."])


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


class TestMiscPretokenized(TestSentenceSplitterPretokenized):
    """"""
    # Successful disambiguation of “ requires full, i.e. not
    # pre-tokenized, input text
    @unittest.expectedFailure
    def test_misc_01(self):
        self._equal("„ Ich habe heute keine Zeit “ , sagte die Frau und flüsterte leise : „ Und auch keine Lust . “ Wir haben 1.000.000 Euro .", ["„ Ich habe heute keine Zeit “ , sagte die Frau und flüsterte leise : „ Und auch keine Lust . “", "Wir haben 1.000.000 Euro ."])

    def test_misc_02(self):
        self._equal("Es gibt jedoch einige Vorsichtsmaßnahmen , die Du ergreifen kannst , z. B. ist es sehr empfehlenswert , dass Du Dein Zuhause von allem Junkfood befreist .", ["Es gibt jedoch einige Vorsichtsmaßnahmen , die Du ergreifen kannst , z. B. ist es sehr empfehlenswert , dass Du Dein Zuhause von allem Junkfood befreist ."])

    def test_misc_03(self):
        self._equal("Was sind die Konsequenzen der Abstimmung vom 12. Juni ?", ["Was sind die Konsequenzen der Abstimmung vom 12. Juni ?"])

    def test_misc_04(self):
        self._equal("Wir könnten wandern , schwimmen , Fahrrad fahren , usw. Worauf hättest du denn Lust ?", ["Wir könnten wandern , schwimmen , Fahrrad fahren , usw.", "Worauf hättest du denn Lust ?"])


class TestXMLPretokenized(TestSentenceSplitterPretokenized):
    """"""
    def test_xml_01(self):
        self._equal_xml("<foo> <p> hallo </p> du </foo>", ["<foo> <p> hallo </p>", "du </foo>"])

    def test_xml_02(self):
        self._equal_xml("<foo> <p> </p> <p> hallo </p> du </foo>", ["<foo> <p> </p> <p> hallo </p>", "du </foo>"])

    def test_xml_03(self):
        self._equal_xml("<bar> <foo> Foo bar . </foo> <foo> </foo> </bar>", ["<bar> <foo> Foo bar . </foo> <foo> </foo> </bar>"])

    def test_xml_04(self):
        self._equal_xml("<foo> Foo <br> </br> bar </foo>", ["<foo> Foo", "<br> </br> bar </foo>"])

    def test_xml_05(self):
        self._equal_xml("<foo> Foo <br/> bar </foo>", ["<foo> Foo", "<br/> bar </foo>"])

    def test_xml_06(self):
        self._equal_xml("<foo> <p> foo bar </p> <p> foo bar </p> </foo>", ["<foo> <p> foo bar </p>", "<p> foo bar </p> </foo>"])


class TestXMLBoundaries(TestSentenceSplitter):
    """"""
    @unittest.skip("Not implemented, yet")
    def test_xml_boundaries_01(self):
        self._equal_xml("<foo>Foo bar. Foo bar.</foo>", ["<foo> <s> Foo bar . </s>", "<s> Foo bar . </s> </foo>"])

    @unittest.skip("Not implemented, yet")
    def test_xml_boundaries_02(self):
        self._equal_xml("<foo><i>Foo bar</i>. Foo <i>bar.</i></foo>", ["<foo> <s> <i> Foo bar </i> . </s>", "<s> Foo <i> bar . </i> </s> </foo>"])

    @unittest.skip("Not implemented, yet")
    def test_xml_boundaries_03(self):
        self._equal_xml("<foo><i>Foo bar.</i> Foo bar.</foo>", ["<foo> <i> <s> Foo bar . </s> </i>", "<s> Foo bar . </s> </foo>"])

    @unittest.skip("Not implemented, yet")
    def test_xml_boundaries_04(self):
        self._equal_xml("<foo>Foo <i>bar. Foo</i> bar.</foo>", ["<foo> <s> Foo <i> bar . </i> </s>", "<s> <i> Foo </i> bar . </s> </foo>"])
