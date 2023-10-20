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


class TestResolveEntities(unittest.TestCase):
    def test_entitites_01(self):
        xml = '<foo attr="bar &quot;baz&quot; qux">foo &lt;bar&gt; baz</foo>'
        resolved = '<foo attr="bar "baz" qux">foo <bar> baz</foo>'
        alignment = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
                     (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12),
                     (12, 13), (13, 14), (14, 15), (15, 21), (21, 22),
                     (22, 23), (23, 24), (24, 30), (30, 31), (31, 32),
                     (32, 33), (33, 34), (34, 35), (35, 36), (36, 37),
                     (37, 38), (38, 39), (39, 40), (40, 44), (44, 45),
                     (45, 46), (46, 47), (47, 51), (51, 52), (52, 53),
                     (53, 54), (54, 55), (55, 56), (56, 57), (57, 58),
                     (58, 59), (59, 60), (60, 61)]
        res, al = somajo.alignment.resolve_entities(xml)
        self.assertEqual(res, resolved)
        self.assertEqual(al, alignment)

    def test_entities_02(self):
        xml = "<foo>T&#x0065;st</foo>"
        resolved = "<foo>Test</foo>"
        alignment = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22)]
        res, al = somajo.alignment.resolve_entities(xml)
        self.assertEqual(res, resolved)
        self.assertEqual(al, alignment)


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
        offsets = somajo.alignment.token_offsets_xml(complete, raw)
        self.assertEqual([raw[s:e] for s, e in offsets], tokenized)

    def test_token_alignment_01(self):
        self._equal("Ein simpler Test.", "Ein simpler Test .")

    def test_token_alignment_02(self):
        self._equal("bla \u1e0d\u0307amit.", "bla \u1e0d\u0307amit .")

    def test_token_alignment_03(self):
        self._equal("foo (bar) baz?", "foo ( bar ) baz ?")

    def test_token_alignment_04(self):
        self._equal("foo​bar foo­bar foo\ufeffbar foobarbazquxalphabetagamma foo‌bar‍baz foo‏bar‎baz foo\u202bbar\u202abaz\u202cqux\u202ealpha\u202dbeta", ["foo​bar", "foo­bar", "foo\ufeffbar", "foobarbazquxalphabetagamma", "foo‌bar‍baz", "foo‏bar‎baz", "foo\u202bbar\u202abaz\u202cqux\u202ealpha\u202dbeta"])

    def test_token_alignment_05(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! : )</foo>", ["<foo>", "der", "beste", "Betreuer", "?", "- &gt;", "Prof", "Smith", "!", ": )", "</foo>"])

    def test_token_alignment_06(self):
        self._equal_xml("<foo>das steht auf S.&#x00ad;5</foo>", "<foo> das steht auf S. 5 </foo>")

    def test_token_alignment_07(self):
        self._equal_xml("<foo><bar>na so was -&#x200B;</bar><bar>&gt; bla</bar></foo>", "<foo> <bar> na so was - </bar> <bar> &gt; bla </bar> </foo>")

    def test_token_alignment_08(self):
        self._equal_xml("<foo>T&#x0065;st</foo>", "<foo> T&#x0065;st </foo>")

    def test_token_alignment_09(self):
        self._equal_xml("<foo>3 &#x003c; 5</foo>", "<foo> 3 &#x003c; 5 </foo>")

    def test_token_alignment_10(self):
        self._equal_xml("<foo>Test&#x00ad;fall</foo>", "<foo> Test&#x00ad;fall </foo>")

    def test_token_alignment_11(self):
        self._equal_xml("<foo>Test­fall</foo>", "<foo> Test­fall </foo>")

    def test_token_alignment_12(self):
        """Single combining mark"""
        self._equal_xml("<foo>foo xA&#x0308;x foo</foo>", "<foo> foo xA&#x0308;x foo </foo>")

    def test_token_alignment_13(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x0323;&#x0307;x foo</foo>", "<foo> foo xs&#x0323;&#x0307;x foo </foo>")

    def test_token_alignment_14(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x0307;&#x0323;x foo</foo>", "<foo> foo xs&#x0307;&#x0323;x foo </foo>")

    def test_token_alignment_15(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xs&#x1e0b;&#x0323;x foo</foo>", "<foo> foo xs&#x1e0b;&#x0323;x foo </foo>")

    def test_token_alignment_16(self):
        """Multiple combining marks"""
        self._equal_xml("<foo>foo xq&#x0307;&#x0323;x foo</foo>", "<foo> foo xq&#x0307;&#x0323;x foo </foo>")

    def test_token_alignment_17(self):
        self._equal_xml("<foo bar='baz'>Foo</foo>", ["<foo bar='baz'>", "Foo", "</foo>"])

    def test_token_alignment_18(self):
        self._equal_xml("<foo bar='ba\"z'>Foo</foo>", ["<foo bar='ba\"z'>", "Foo", "</foo>"])

    def test_token_alignment_19(self):
        self._equal_xml("<foo   bar   =   'baz'>   Foo   </foo>", ["<foo   bar   =   'baz'>", "Foo", "</foo>"])

    def test_token_alignment_20(self):
        self._equal_xml("<foo bar='ba\"z'>Foo \"Bar\" 'Baz'</foo>", ["<foo bar='ba\"z'>", "Foo", '"', "Bar", '"', "'", "Baz", "'", "</foo>"])
