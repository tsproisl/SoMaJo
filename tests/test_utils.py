#!/usr/bin/env python3

import unittest

from somajo import utils


class TestXmlChunkGenerator(unittest.TestCase):
    def _equal(self, raw, chunks, prune_tags=None):
        eos_tags = set(["p"])
        if prune_tags is not None:
            prune_tags = set(prune_tags)
        chunk_info = list(utils.xml_chunk_generator(raw, is_file=False, eos_tags=eos_tags, prune_tags=prune_tags))
        chunk_lists = (ci[0] for ci in chunk_info)
        chunk_lists = [[t.text for t in gc] for gc in chunk_lists]
        self.assertEqual(chunk_lists, chunks)

    def _equal_offsets(self, raw, chunks, prune_tags=None):
        eos_tags = set(["p"])
        if prune_tags is not None:
            prune_tags = set(prune_tags)
        chunk_info = list(utils.xml_chunk_generator(raw, is_file=False, eos_tags=eos_tags, prune_tags=prune_tags, character_offsets=True))
        chunk_lists, raws, positions = zip(*chunk_info)
        offsets = [[t.character_offset for t in cl] for cl in chunk_lists]
        extracted_chunks = [[raw[s:e] for s, e in o] for o in offsets]
        self.assertEqual(extracted_chunks, chunks)

    def test_xml_chunk_generator_01(self):
        self._equal("<x>foo bar</x>", [["<x>", "foo bar", "</x>"]])

    def test_xml_chunk_generator_02(self):
        self._equal("<x><p>foo</p><p>bar</p></x>", [["<x>", "<p>", "foo", "</p>"], ["<p>", "bar", "</p>", "</x>"]])

    def test_xml_chunk_generator_03(self):
        self._equal("<x>\n<p>\nfoo\n</p>\n<p>\nbar\n</p>\n</x>", [["<x>", "\n", "<p>", "\nfoo\n", "</p>"], ["\n", "<p>", "\nbar\n", "</p>", "\n", "</x>"]])

    def test_xml_chunk_generator_04(self):
        self._equal(
            "<x>\n  <p>\n    foo\n  </p>\n  <p>\n    bar\n  </p>\n</x>",
            [["<x>", "\n  ", "<p>", "\n    foo\n  ", "</p>"], ["\n  ", "<p>", "\n    bar\n  ", "</p>", "\n", "</x>"]]
        )

    def test_xml_chunk_generator_05(self):
        self._equal(
            "<x><p>foo</p><i>baz</i><p>bar</p><i>baz</i></x>",
            [["<x>", "<p>", "foo", "</p>"], ["<i>", "baz", "</i>"], ["<p>", "bar", "</p>"], ["<i>", "baz", "</i>", "</x>"]]
        )

    def test_xml_chunk_generator_06(self):
        self._equal(
            "<x><p>foo</p><br/><p>bar</p><br/></x>",
            [["<x>", "<p>", "foo", "</p>"], ["<br>", "</br>", "<p>", "bar", "</p>"], ["<br>", "</br>", "</x>"]]
        )

    def test_xml_chunk_generator_07(self):
        self._equal("<x><del>foo</del><i>bar</i></x>", [["<x>", "<i>", "bar", "</i>", "</x>"]], prune_tags=["del"])

    def test_xml_chunk_generator_08(self):
        self._equal("<x><del>foo</del><p>bar</p></x>", [["<x>", "<p>", "bar", "</p>", "</x>"]], prune_tags=["del"])

    def test_xml_chunk_generator_09(self):
        self._equal("<x>bar\n  <del>foo</del>\nbaz</x>", [["<x>", "bar\n  \nbaz", "</x>"]], prune_tags=["del"])

    def test_xml_chunk_offsets_01(self):
        self._equal_offsets("<foo>T&#x0065;st</foo>", [["<foo>", "T&#x0065;st", "</foo>"]])

    def test_xml_chunk_offsets_02(self):
        self._equal_offsets("<foo>3 &#x003c; 5</foo>", [["<foo>", "3 &#x003c; 5",  "</foo>"]])

    def test_xml_chunk_offsets_03(self):
        self._equal_offsets("<foo>Test&#x00ad;fall</foo>", [["<foo>", "Test&#x00ad;fall", "</foo>"]])

    def test_xml_chunk_offsets_04(self):
        self._equal_offsets("<foo>Test­fall</foo>", [["<foo>", "Test­fall", "</foo>"]])

    def test_xml_chunk_offsets_05(self):
        """Single combining mark"""
        self._equal_offsets("<foo>foo xA&#x0308;x foo</foo>", [["<foo>", "foo xA&#x0308;x foo", "</foo>"]])

    def test_xml_chunk_offsets_06(self):
        """Multiple combining marks"""
        self._equal_offsets("<foo>foo xs&#x0323;&#x0307;x foo</foo>", [["<foo>", "foo xs&#x0323;&#x0307;x foo", "</foo>"]])

    def test_xml_chunk_offsets_07(self):
        """Multiple combining marks"""
        self._equal_offsets("<foo>foo xs&#x0307;&#x0323;x foo</foo>", [["<foo>", "foo xs&#x0307;&#x0323;x foo", "</foo>"]])

    def test_xml_chunk_offsets_08(self):
        """Multiple combining marks"""
        self._equal_offsets("<foo>foo xs&#x1e0b;&#x0323;x foo</foo>", [["<foo>", "foo xs&#x1e0b;&#x0323;x foo", "</foo>"]])

    def test_xml_chunk_offsets_09(self):
        """Multiple combining marks"""
        self._equal_offsets("<foo>foo xq&#x0307;&#x0323;x foo</foo>", [["<foo>", "foo xq&#x0307;&#x0323;x foo", "</foo>"]])

    def test_xml_chunk_offsets_10(self):
        self._equal_offsets("<foo bar='baz'>Foo</foo>", [["<foo bar='baz'>", "Foo", "</foo>"]])

    def test_xml_chunk_offsets_11(self):
        self._equal_offsets("<foo bar='ba\"z'>Foo</foo>", [["<foo bar='ba\"z'>", "Foo", "</foo>"]])

    def test_xml_chunk_offsets_12(self):
        self._equal_offsets("<foo   bar   =   'baz'>   Foo   </foo>", [["<foo   bar   =   'baz'>", "   Foo   ", "</foo>"]])

    def test_xml_chunk_offsets_13(self):
        self._equal_offsets("<foo bar='ba\"z'>Foo \"Bar\" 'Baz'</foo>", [["<foo bar='ba\"z'>", "Foo \"Bar\" 'Baz'", "</foo>"]])

    def test_xml_chunk_offsets_14(self):
        self._equal_offsets('<foo bar="baz"\n  spam="eggs">\n    Foo\n</foo>', [['<foo bar="baz"\n  spam="eggs">', "\n    Foo\n", "</foo>"]])

    def test_xml_chunk_offsets_15(self):
        self._equal_offsets("<foo>Hallo<br/>Tschüß</foo>", [["<foo>", "Hallo", "<br/>", "", "Tschüß", "</foo>"]])

    def test_xml_chunk_offsets_16(self):
        self._equal_offsets("<foo>Hallo<br />Tschüß</foo>", [["<foo>", "Hallo", "<br />", "", "Tschüß", "</foo>"]])

    def test_xml_chunk_offsets_17(self):
        self._equal_offsets("<foo>\u0303foo</foo>", [["<foo>", "\u0303foo", "</foo>"]])

    def test_xml_chunk_offsets_18(self):
        self._equal_offsets("<foo>foo<p>bar</p></foo>", [["<foo>", "foo"], ["<p>", "bar", "</p>", "</foo>"]])

    @unittest.expectedFailure
    def test_xml_chunk_offsets_19(self):
        self._equal_offsets("<foo>bar <del>futsch</del> baz</foo>", [["<foo>", "bar  baz", "</foo>"]], prune_tags=["del"])
