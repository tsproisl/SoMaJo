#!/usr/bin/env python3

import itertools
import unicodedata
import unittest

import somajo.alignment
from somajo.doubly_linked_list import DLL
from somajo.token import Token
from somajo.somajo import Tokenizer
from somajo import utils


class TestNfcAlignment(unittest.TestCase):
    def test_nfc_01(self):
        """Singleton: Angstrom sign"""
        orig = "xÅx"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 1): (0, 1), (1, 2): (1, 2), (2, 3): (2, 3)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_02(self):
        """Single combining mark"""
        orig = "xA\u0308x"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 1): (0, 1), (1, 2): (1, 3), (2, 3): (3, 4)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_03(self):
        """Multiple combining marks"""
        orig = "xs\u0323\u0307x"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 1): (0, 1), (1, 2): (1, 4), (2, 3): (4, 5)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_04(self):
        """Multiple combining marks"""
        orig = "xs\u0307\u0323x"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 1): (0, 1), (1, 2): (1, 4), (2, 3): (4, 5)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_05(self):
        """Multiple combining marks"""
        orig = "x\u1e0b\u0323x"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 1): (0, 1), (1, 3): (1, 3), (3, 4): (3, 4)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_06(self):
        """Multiple combining marks"""
        orig = "q\u0307\u0323x"
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {(0, 3): (0, 3), (3, 4): (3, 4)}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)

    def test_nfc_07(self):
        """Empty string"""
        orig = ""
        nfc = unicodedata.normalize("NFC", orig)
        alignment = {}
        self.assertEqual(somajo.alignment.align_nfc(nfc, orig), alignment)


class TestTokenAlignment(unittest.TestCase):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(split_camel_case=True, language="de_CMC")

    def _equal(self, raw, tokenized):
        raw = unicodedata.normalize("NFC", raw)
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        dll = DLL([Token(raw, first_in_sentence=True, last_in_sentence=True)])
        tokens = self.tokenizer._tokenize(dll)
        offsets = somajo.alignment.token_offsets(tokens, raw)
        self.assertEqual([raw[s:e] for s, e in offsets], tokenized)

    def _equal_xml(self, raw, tokenized):
        raw = unicodedata.normalize("NFC", raw)
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        token_lists = utils.xml_chunk_generator(raw, is_file=False, eos_tags=eos_tags)
        token_dlls = map(DLL, token_lists)
        chunks = map(self.tokenizer._tokenize, token_dlls)
        complete = list(itertools.chain.from_iterable(chunks))
        complete = utils.escape_xml_tokens(complete)
        offsets = somajo.alignment.token_offsets_xml(complete, raw, self.tokenizer)
        self.assertEqual([raw[s:e] for s, e in offsets], tokenized)

    def test_token_alignment_01(self):
        self._equal("Ein simpler Test.", "Ein simpler Test .")

    def test_token_alignment_02(self):
        self._equal("bla \u1e0d\u0307amit.", "bla \u1e0d\u0307amit .")

    def test_token_alignment_03(self):
        self._equal("foo (bar) baz?", "foo ( bar ) baz ?")

    def test_token_alignment_04(self):
        self._equal("foo​bar foo­bar foo\ufeffbar foobarbazquxalphabetagamma foo‌bar‍baz foo‏bar‎baz foo\u202bbar\u202abaz\u202cqux\u202ealpha\u202dbeta", ["foo​bar", "foo­bar", "foo\ufeffbar", "foobarbazquxalphabetagamma", "foo‌bar‍baz", "foo‏bar‎baz", "foo\u202bbar\u202abaz\u202cqux\u202ealpha\u202dbeta"])

    @unittest.expectedFailure
    def test_token_alignment_05(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! : )</foo>", ["<foo>", "der", "beste", "Betreuer", "?", "- &gt;", "Prof", "Smith", "!", ": )", "</foo>"])

    @unittest.expectedFailure
    def test_token_alignment_06(self):
        self._equal_xml("<foo>das steht auf S.&#x00ad;5</foo>", "<foo> das steht auf S. 5 </foo>")

    @unittest.expectedFailure
    def test_token_alignment_07(self):
        self._equal_xml("<foo><bar>na so was -&#x200B;</bar><bar>&gt; bla</bar></foo>", "<foo> <bar> na so was - </bar> <bar> &gt; bla </bar> </foo>")

    def test_token_alignment_08(self):
        self._equal_xml("<foo>T&#x0065;st</foo>", "<foo> T&#x0065;st </foo>")

    @unittest.expectedFailure
    def test_token_alignment_09(self):
        self._equal_xml("<foo>3 &#x003c; 5</foo>", "<foo> 3 &#x003c; 5 </foo>")

    @unittest.expectedFailure
    def test_token_alignment_10(self):
        self._equal_xml("<foo>Test&#x00ad;fall</foo>", "<foo> Test&#x00ad;fall </foo>")

    def test_token_alignment_11(self):
        self._equal_xml("<foo>Test­fall</foo>", "<foo> Test­fall </foo>")

    @unittest.expectedFailure
    def test_token_alignment_12(self):
        """Single combining mark"""
        self._equal_xml("<foo>foo xA&#x0308;x foo</foo>", "<foo> foo xA&#x0308;x foo </foo>")

    @unittest.expectedFailure
    def test_token_alignment_13(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x0323;&#x0307;x foo</foo>", "<foo> foo xs&#x0323;&#x0307;x foo </foo>")

    @unittest.expectedFailure
    def test_token_alignment_14(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x0307;&#x0323;x foo</foo>", "<foo> foo xs&#x0307;&#x0323;x foo </foo>")

    def test_token_alignment_15(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x1e0b;&#x0323;x foo</foo>", "<foo> foo xs&#x1e0b;&#x0323;x foo </foo>")

    def test_token_alignment_16(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xq&#x0307;&#x0323;x foo</foo>", "<foo> foo xq&#x0307;&#x0323;x foo </foo>")

    @unittest.expectedFailure
    def test_xml_07(self):
        self._equal_xml("<foo><text><p>blendend. 👱‍</p></text><text ><blockquote><p>Foo bar baz</p></blockquote></text></foo>", ["<foo>", "<text>", "<p>", "blendend", ".", "👱‍", "</p>", "</text>", "<text >", "<blockquote>", "<p>", "Foo", "bar", "baz", "</p>", "</blockquote>", "</text>", "</foo>"])

    @unittest.expectedFailure
    def test_xml_08(self):
        self._equal_xml("<text><p>Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt.</p><p>So 🙇🙇 manchen Unionspolitikern gestehe ich schon …</p></text>", "<text> <p> Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt . </p> <p> So 🙇 🙇 manchen Unionspolitikern gestehe ich schon … </p> </text>")

    @unittest.expectedFailure
    def test_xml_09(self):
        self._equal_xml("""<text>
<p>Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt.</p>

<p>So 🙇🙇 manchen Unionspolitikern gestehe ich schon noch irgendwie zu, dass sie durchaus das Bedürfnis haben, ihren Bürgern ein gutes Leben zu ermöglichen. Zwar halte ich ihre Vorstellung von einem "guten Leben" und/oder die ☠☣ Wege, auf denen dieses erreicht werden soll, für grundsätzlich falsch - aber da stecken zumindest teilweise durchaus legitim gute Absichten dahinter.</p>

<p>Jens Spahn allerdings mangelt es 🚎 schmerzhaft offensichtlich an 📯🏻 diesem oben genannten Mindestmaß an 👹👹 Anstand. Die Dinge, die er ⤵⤵ erkennbar überzeugt von sich gibt, triefen vor Arroganz und Empathielosigkeit (Hartz IV? Mehr als genug; Gefährlich niedrige Versorgung mit Geburtshilfe? Sollen die 💯🚦 Weiber halt nen Kilometer weiter fahren); die andere Hälfte seiner verbalen Absonderungen ist ♂ schmerzhaft durchsichtiges taktisches Anbiedern an 💕👹 konservative Interessengruppen (jüngst beispielsweise Abtreibungsgegner) mittels plumpmöglichster Populismen.</p>
        </text>""", """<text> <p> Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt . </p> <p> So 🙇 🙇 manchen Unionspolitikern gestehe ich schon noch irgendwie zu , dass sie durchaus das Bedürfnis haben , ihren Bürgern ein gutes Leben zu ermöglichen . Zwar halte ich ihre Vorstellung von einem " guten Leben " und / oder die ☠ ☣ Wege , auf denen dieses erreicht werden soll , für grundsätzlich falsch - aber da stecken zumindest teilweise durchaus legitim gute Absichten dahinter . </p> <p> Jens Spahn allerdings mangelt es 🚎 schmerzhaft offensichtlich an 📯🏻 diesem oben genannten Mindestmaß an 👹 👹 Anstand . Die Dinge , die er ⤵ ⤵ erkennbar überzeugt von sich gibt , triefen vor Arroganz und Empathielosigkeit ( Hartz IV ? Mehr als genug ; Gefährlich niedrige Versorgung mit Geburtshilfe ? Sollen die 💯 🚦 Weiber halt nen Kilometer weiter fahren ) ; die andere Hälfte seiner verbalen Absonderungen ist ♂ schmerzhaft durchsichtiges taktisches Anbiedern an 💕 👹 konservative Interessengruppen ( jüngst beispielsweise Abtreibungsgegner ) mittels plumpmöglichster Populismen . </p> </text>""")

    def test_xml_10(self):
        self._equal_xml("<foo><p>foo bar</p>\n\n<p>foo bar</p></foo>", "<foo> <p> foo bar </p> <p> foo bar </p> </foo>")

    def test_xml_11(self):
        self._equal_xml("<foo bar='baz'>Foo</foo>", ["<foo bar='baz'>", 'Foo', '</foo>'])

    @unittest.expectedFailure
    def test_xml_12(self):
        self._equal_xml("<foo bar='ba\"z'>Foo</foo>", ["<foo bar='ba\"z'>", 'Foo', '</foo>'])
