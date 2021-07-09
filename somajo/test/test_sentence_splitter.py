#!/usr/bin/env python3

import io
import unittest

from somajo import SentenceSplitter
from somajo import SoMaJo
from somajo import Tokenizer


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

    def _equal_xml_strip(self, raw, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        sentences = self.tokenizer.tokenize_xml(raw, eos_tags, strip_tags=True)
        sentences = [" ".join([t.text for t in s]) for s in sentences]
        self.assertEqual(sentences, tokenized_sentences)


class TestSentenceSplitterXMLBoundaries(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = SoMaJo("de_CMC", split_camel_case=True, split_sentences=True, xml_sentences="s")

    def _equal(self, raw, tokenized_sentences):
        """"""
        sentences = self.tokenizer.tokenize_text([raw])
        sentences = " ".join([" ".join([t.text for t in s]) for s in sentences])
        self.assertEqual(sentences, tokenized_sentences)

    def _equal_text_file_single_newlines(self, raw, tokenized_sentences):
        pseudofile = io.StringIO(raw)
        sentences = self.tokenizer.tokenize_text_file(pseudofile, paragraph_separator="single_newlines")
        sentences = " ".join([" ".join([t.text for t in s]) for s in sentences])
        self.assertEqual(sentences, tokenized_sentences)

    def _equal_xml(self, raw, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        sentences = self.tokenizer.tokenize_xml(raw, eos_tags)
        sentences = " ".join([" ".join([t.text for t in s]) for s in sentences])
        self.assertEqual(sentences, tokenized_sentences)

    def _equal_xml_strip(self, raw, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        sentences = self.tokenizer.tokenize_xml(raw, eos_tags, strip_tags=True)
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


class TestSentenceSplitterTuple(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", token_classes=True, extra_info=True)
        self.sentence_splitter = SentenceSplitter(language="de_CMC", is_tuple=True)

    def _equal(self, raw, tokenized_sentences):
        """"""
        tokens = self.tokenizer.tokenize_paragraph(raw)
        sentences = self.sentence_splitter.split(tokens)
        self.assertEqual(sentences, tokenized_sentences)

    def _equal_xml(self, raw, tokenized_sentences):
        """"""
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        tokens = self.tokenizer.tokenize_xml(raw, is_file=False)
        sentences = self.sentence_splitter.split_xml(tokens, eos_tags)
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

    def test_misc_18(self):
        self._equal("Großartig! 👍 Weiter so!", ["Großartig ! 👍", "Weiter so !"])

    def test_misc_19(self):
        self._equal("Großartig! 👍🥰 Weiter so!", ["Großartig ! 👍 🥰", "Weiter so !"])

    def test_misc_20(self):
        self._equal('"In welchen Modi werden wir in einigen Jahren kommunizieren?" @berlinothar #ibk #cmc #dtaclarin14', ['" In welchen Modi werden wir in einigen Jahren kommunizieren ? "', "@berlinothar #ibk #cmc #dtaclarin14"])

    def test_misc_21(self):
        self._equal("Oder gibt es Unterschiede? #semibk", ["Oder gibt es Unterschiede ?", "#semibk"])


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

    def test_xml_07(self):
        self._equal_xml("<foo>Hallo Susi. <br/>Hallo Peter.</foo>", ["<foo> Hallo Susi .", "<br> </br> Hallo Peter . </foo>"])

    def test_xml_08(self):
        self._equal_xml("<foo>Hallo Susi. Hallo Peter.<br/></foo>", ["<foo> Hallo Susi .", "Hallo Peter . <br> </br> </foo>"])

    def test_xml_09(self):
        self._equal_xml_strip("<foo><p>hallo</p>du</foo>", ["hallo", "du"])


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


class TestMiscTuple(TestSentenceSplitterTuple):
    """"""
    def test_misc_pretok_01(self):
        self._equal("Hallo Susi. Hallo Peter.", [[('Hallo', 'regular', ''), ('Susi', 'regular', 'SpaceAfter=No'), ('.', 'symbol', '')], [('Hallo', 'regular', ''), ('Peter', 'regular', 'SpaceAfter=No'), ('.', 'symbol', '')]])

    def test_misc_pretok_02(self):
        self._equal_xml("<foo><p>Hallo</p> Susi. Hallo Peter.</foo>", [[('<foo>', None, ''), ('<p>', None, ''), ('Hallo', 'regular', ''), ('</p>', None, '')], [('Susi', 'regular', 'SpaceAfter=No'), ('.', 'symbol', '')], [('Hallo', 'regular', ''), ('Peter', 'regular', 'SpaceAfter=No'), ('.', 'symbol', ''), ('</foo>', None, '')]])


class TestXMLBoundaries(TestSentenceSplitterXMLBoundaries):
    """"""
    def test_xml_boundaries_01(self):
        self._equal_xml("<foo>Hallo Susi. Hallo Peter.</foo>", "<foo> <s> Hallo Susi . </s> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_02(self):
        self._equal_xml("<foo><i></i>Hallo Susi. Hallo Peter.</foo>", "<foo> <i> </i> <s> Hallo Susi . </s> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_03(self):
        self._equal_xml("<foo><i>Hallo Susi</i>. Hallo Peter.</foo>", "<foo> <s> <i> Hallo Susi </i> . </s> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_04(self):
        self._equal_xml("<foo><i>Hallo Susi.</i> Hallo Peter.</foo>", "<foo> <i> <s> Hallo Susi . </s> </i> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_05(self):
        self._equal_xml("<foo><i>Hallo Susi. Hallo</i> Peter.</foo>", "<foo> <i> <s> Hallo Susi . </s> </i> <s> <i> Hallo </i> Peter . </s> </foo>")

    def test_xml_boundaries_06(self):
        self._equal_xml("<foo><i>Hallo Susi. Hallo Peter.</i></foo>", "<foo> <i> <s> Hallo Susi . </s> <s> Hallo Peter . </s> </i> </foo>")

    def test_xml_boundaries_07(self):
        self._equal_xml("<foo><i>Hallo Susi. Hallo Peter. Hallo</i> Thomas.</foo>", "<foo> <i> <s> Hallo Susi . </s> <s> Hallo Peter . </s> </i> <s> <i> Hallo </i> Thomas . </s> </foo>")

    def test_xml_boundaries_08(self):
        self._equal_xml("<foo>Hallo <i>Susi</i>. Hallo Peter.</foo>", "<foo> <s> Hallo <i> Susi </i> . </s> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_09(self):
        self._equal_xml("<foo>Hallo <i>Susi.</i> Hallo Peter.</foo>", "<foo> <s> Hallo <i> Susi . </i> </s> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_10(self):
        self._equal_xml("<foo>Hallo <i>Susi. Hallo Peter. Hallo</i> Thomas.</foo>", "<foo> <s> Hallo <i> Susi . </i> </s> <i> <s> Hallo Peter . </s> </i> <s> <i> Hallo </i> Thomas . </s> </foo>")

    def test_xml_boundaries_11(self):
        self._equal_xml("<foo>Hallo <i>Susi. Hallo Peter. Hallo Thomas.</i></foo>", "<foo> <s> Hallo <i> Susi . </i> </s> <i> <s> Hallo Peter . </s> <s> Hallo Thomas . </s> </i> </foo>")

    def test_xml_boundaries_12(self):
        self._equal_xml("<foo>Hallo Susi.<i> Hallo</i> Peter.</foo>", "<foo> <s> Hallo Susi . </s> <s> <i> Hallo </i> Peter . </s> </foo>")

    def test_xml_boundaries_13(self):
        self._equal_xml("<foo><a><b>Hallo <c>Susi. <d>Hallo Peter. Hallo</d></c></b> Thomas.</a></foo>", "<foo> <a> <b> <s> Hallo <c> Susi . </c> </s> <c> <d> <s> Hallo Peter . </s> </d> </c> </b> <s> <b> <c> <d> Hallo </d> </c> </b> Thomas . </s> </a> </foo>")

    def test_xml_boundaries_14(self):
        self._equal_xml("<foo><i>Hallo</i> Susi<i>. Hallo</i> Peter<i>.</i></foo>", "<foo> <s> <i> Hallo </i> Susi <i> . </i> </s> <s> <i> Hallo </i> Peter <i> . </i> </s> </foo>")

    def test_xml_boundaries_15(self):
        self._equal_xml("<foo>Hallo <i><b>Susi. Hallo Peter. Hallo</b></i> Thomas.</foo>", "<foo> <s> Hallo <i> <b> Susi . </b> </i> </s> <i> <b> <s> Hallo Peter . </s> </b> </i> <s> <i> <b> Hallo </b> </i> Thomas . </s> </foo>")

    def test_xml_boundaries_16(self):
        self._equal_xml("<a>Hallo <b><d>Susi.</d> Hallo</b> Peter.</a>", "<a> <s> Hallo <b> <d> Susi . </d> </b> </s> <s> <b> Hallo </b> Peter . </s> </a>")

    def test_xml_boundaries_17(self):
        self._equal_xml("<a>Hallo <b><c><d>Susi.</d> Hallo</c></b> Peter.</a>", "<a> <s> Hallo <b> <c> <d> Susi . </d> </c> </b> </s> <s> <b> <c> Hallo </c> </b> Peter . </s> </a>")

    def test_xml_boundaries_18(self):
        self._equal_xml("<a>Hallo Susi.<x/> Hallo Peter.<x/></a>", "<a> <s> Hallo Susi . </s> <x> </x> <s> Hallo Peter . </s> <x> </x> </a>")

    def test_xml_boundaries_19(self):
        self._equal_xml("<foo><i>Hallo Susi.<x/></i> <i>Hallo Peter.</i></foo>", "<foo> <i> <s> Hallo Susi . </s> <x> </x> </i> <i> <s> Hallo Peter . </s> </i> </foo>")

    # This one could also be done differently
    def test_xml_boundaries_20(self):
        self._equal_xml("<foo>Hallo <i>Susi.<x/> Hallo</i> Peter.</foo>", "<foo> <s> Hallo <i> Susi . </i> </s> <s> <i> <x> </x> Hallo </i> Peter . </s> </foo>")

    def test_xml_boundaries_21(self):
        self._equal_xml("<foo><p><b>Hallo</b> <i>Susi.<x/></i></p> Hallo Peter.</foo>", "<foo> <p> <s> <b> Hallo </b> <i> Susi . <x> </x> </i> </s> </p> <s> Hallo Peter . </s> </foo>")

    def test_xml_boundaries_22(self):
        self._equal("Hallo Susi. Hallo Peter & Thomas.", "<s> Hallo Susi . </s> <s> Hallo Peter &amp; Thomas . </s>")

    def test_xml_boundaries_23(self):
        self._equal_xml_strip("<foo><p>hallo</p>du</foo>", ["<s> hallo </s>", "<s> du </s>"])

    def test_xml_boundaries_24(self):
        self._equal_text_file_single_newlines("Hallo Susi. Hallo Peter & Thomas.", "<s> Hallo Susi . </s> <s> Hallo Peter &amp; Thomas . </s>")

    def test_xml_boundaries_25(self):
        self._equal_xml("<foo><p>Hallo Susi.</p> <p></p> <p>Hallo Peter.</p></foo>", "<foo> <p> <s> Hallo Susi . </s> </p> <p> </p> <p> <s> Hallo Peter . </s> </p> </foo>")
