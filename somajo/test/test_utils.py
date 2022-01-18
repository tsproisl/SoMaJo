#!/usr/bin/env python3

import unittest

from somajo import utils


class TestXmlChunkGenerator(unittest.TestCase):
    def _equal(self, raw, chunks):
        eos_tags = ["p"]
        gen_chunks = list(utils.xml_chunk_generator(raw, is_file=False, eos_tags=eos_tags))
        gen_chunks = [[t.text for t in gc] for gc in gen_chunks]
        self.assertEqual(gen_chunks, chunks)

    def test_xml_chunk_generator_01(self):
        self._equal("<x>foo bar</x>", [["<x>", "foo bar", "</x>"]])

    def test_xml_chunk_generator_02(self):
        self._equal("<x><p>foo</p><p>bar</p></x>", [["<x>", "<p>", "foo", "</p>"], ["<p>", "bar", "</p>", "</x>"]])

    def test_xml_chunk_generator_03(self):
        self._equal("<x>\n<p>\nfoo\n</p>\n<p>\nbar\n</p>\n</x>", [["<x>", "<p>", "foo", "</p>"], ["<p>", "bar", "</p>", "</x>"]])

    def test_xml_chunk_generator_04(self):
        self._equal("<x>\n  <p>\n    foo\n  </p>\n  <p>\n    bar\n  </p>\n</x>", [["<x>", "  ", "<p>", "    foo  ", "</p>"], ["  ", "<p>", "    bar  ", "</p>", "</x>"]])

    def test_xml_chunk_generator_05(self):
        self._equal("<x><p>foo</p><i>baz</i><p>bar</p><i>baz</i></x>", [["<x>", "<p>", "foo", "</p>"], ["<i>", "baz", "</i>"], ["<p>", "bar", "</p>"], ["<i>", "baz", "</i>", "</x>"]])

    def test_xml_chunk_generator_06(self):
        self._equal("<x><p>foo</p><br/><p>bar</p><br/></x>", [["<x>", "<p>", "foo", "</p>"], ["<br>", "</br>", "<p>", "bar", "</p>"], ["<br>", "</br>", "</x>"]])
