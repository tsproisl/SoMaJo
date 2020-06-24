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
