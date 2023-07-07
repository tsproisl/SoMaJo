#!/usr/bin/env python3

import unittest

from somajo.token import Token


class TestToken(unittest.TestCase):
    def test_token_01(self):
        text = "FooBar"
        t = Token(text)
        self.assertEqual(str(t), text)

    def test_token_02(self):
        t = Token("FooBar", space_after=False, original_spelling="Foo Bar")
        self.assertEqual(t.extra_info, 'SpaceAfter=No, OriginalSpelling="Foo Bar"')

    def test_token_03(self):
        t = Token("<p foo='bar'>", markup=True, markup_class="start", markup_eos=True)
        self.assertEqual(t.markup_class, "start")
        self.assertTrue(t.markup_eos)
