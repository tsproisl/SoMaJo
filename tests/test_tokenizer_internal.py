#!/usr/bin/env python3

import unittest

import regex as re

from somajo import Tokenizer
from somajo.doubly_linked_list import DLL
from somajo.token import Token


class TestRemoveEmptyTokens(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True)

    def test_remove_empty_tokens_01(self):
        token_dll = DLL([Token(s) for s in (" ", "Foo", "bar", "baz", "qux")])
        token_dll.first.value.first_in_sentence = True
        token_dll.last.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "Foo bar baz qux".split())
        self.assertTrue(token_dll.first.value.first_in_sentence)
        self.assertTrue(token_dll.last.value.last_in_sentence)

    def test_remove_empty_tokens_02(self):
        token_dll = DLL([Token(s) for s in ("Foo", "bar", "baz", "qux", " ")])
        token_dll.first.value.first_in_sentence = True
        token_dll.last.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "Foo bar baz qux".split())
        self.assertTrue(token_dll.first.value.first_in_sentence)
        self.assertTrue(token_dll.last.value.last_in_sentence)

    def test_remove_empty_tokens_03(self):
        token_dll = DLL([Token(s) for s in ("<s>", " ", "Foo", "bar", "baz", "qux", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> Foo bar baz qux </s>".split())
        self.assertTrue(token_dll.first.next.value.first_in_sentence)
        self.assertTrue(token_dll.last.prev.value.last_in_sentence)

    def test_remove_empty_tokens_04(self):
        token_dll = DLL([Token(s) for s in ("<s>", "Foo", "bar", "baz", "qux", " ", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> Foo bar baz qux </s>".split())
        self.assertTrue(token_dll.first.next.value.first_in_sentence)
        self.assertTrue(token_dll.last.prev.value.last_in_sentence)

    def test_remove_empty_tokens_05(self):
        token_dll = DLL([Token(s) for s in ("<s>", " ", "<br/>", "Foo", "bar", "baz", "qux", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.first.next.next.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> <br/> Foo bar baz qux </s>".split())
        self.assertTrue(token_dll.first.next.next.value.first_in_sentence)
        self.assertTrue(token_dll.last.prev.value.last_in_sentence)

    def test_remove_empty_tokens_06(self):
        token_dll = DLL([Token(s) for s in ("<s>", "Foo", "bar", "baz", "qux", "<br/>", " ", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.last.prev.prev.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> Foo bar baz qux <br/> </s>".split())
        self.assertTrue(token_dll.first.next.value.first_in_sentence)
        self.assertTrue(token_dll.last.prev.prev.value.last_in_sentence)

    def test_remove_empty_tokens_07(self):
        token_dll = DLL([Token(s) for s in ("<s>", " ", "Foo", " ", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> Foo </s>".split())
        self.assertTrue(token_dll.first.next.value.first_in_sentence)
        self.assertTrue(token_dll.first.next.value.last_in_sentence)

    def test_remove_empty_tokens_08(self):
        token_dll = DLL([Token(s) for s in ("<s>", " ", " ", "</s>")])
        token_dll.first.value.markup = True
        token_dll.last.value.markup = True
        token_dll.first.next.value.first_in_sentence = True
        token_dll.last.prev.value.last_in_sentence = True
        self.tokenizer._remove_empty_tokens(token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "<s> </s>".split())
        self.assertFalse(any([t.value.first_in_sentence for t in token_dll]))
        self.assertFalse(any([t.value.last_in_sentence for t in token_dll]))


class TestSplitPaired(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True)
        self.regex = re.compile(r"(?P<left>a)[^a]+(?P<right>a)")

    def test_split_paired_01(self):
        token_dll = DLL([Token("babbbab")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "b a bbb a b".split())

    def test_split_paired_02(self):
        token_dll = DLL([Token("abbba")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "a bbb a".split())

    def test_split_paired_03(self):
        token_dll = DLL([Token("babbbababbab")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "b a bbb a b a bb a b".split())

    def test_split_paired_04(self):
        token_dll = DLL([Token("babbbababbb")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "b a bbb a babbb".split())

    def test_split_paired_05(self):
        token_dll = DLL([Token("bbb")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], "bbb".split())

    def test_split_paired_06(self):
        token_dll = DLL([Token("")])
        self.tokenizer._split_all_matches(self.regex, token_dll)
        self.assertEqual([t.text for t in token_dll.to_list()], [""])


class TestSplitOnBoundaries(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True)

    def test_split_on_boundaries_01(self):
        token_dll = DLL([Token("123456789")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, None), (5, 8, None)], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], "1 23 45 678 9".split())
        tokens = token_dll.to_list()
        self.assertEqual(tokens[1].token_class, "regular")
        self.assertEqual(tokens[3].token_class, "regular")
        self.assertEqual([t._locked for t in tokens], [False, True, False, True, False])

    def test_split_on_boundaries_02(self):
        token_dll = DLL([Token(" 2345678 ")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, None), (5, 8, None)], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], "23 45 678".split())
        tokens = token_dll.to_list()
        self.assertEqual(tokens[0].token_class, "regular")
        self.assertEqual(tokens[2].token_class, "regular")
        self.assertTrue(tokens[2].space_after)
        self.assertEqual([t._locked for t in tokens], [True, False, True])

    def test_split_on_boundaries_03(self):
        token_dll = DLL([Token("12 456 89")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, None), (5, 8, None)], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], ["1", "2", "45", "6 8", "9"])
        tokens = token_dll.to_list()
        self.assertEqual(tokens[1].token_class, "regular")
        self.assertEqual(tokens[3].token_class, "regular")
        self.assertTrue(tokens[1].space_after)
        self.assertEqual([t._locked for t in tokens], [False, True, False, True, False])

    def test_split_on_boundaries_04(self):
        token_dll = DLL([Token("1 3456 89")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, None), (5, 8, None)], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], ["1", "3", "45", "6 8", "9"])
        tokens = token_dll.to_list()
        self.assertEqual(tokens[1].token_class, "regular")
        self.assertEqual(tokens[3].token_class, "regular")
        self.assertTrue(tokens[0].space_after)
        self.assertEqual([t._locked for t in tokens], [False, True, False, True, False])

    def test_split_on_boundaries_05(self):
        token_dll = DLL([Token("12 456 89")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, None), (5, 8, None)], "regular", delete_whitespace=True)
        self.assertEqual([t.text for t in token_dll.to_list()], "1 2 45 68 9".split())
        tokens = token_dll.to_list()
        self.assertEqual(tokens[1].token_class, "regular")
        self.assertEqual(tokens[3].token_class, "regular")
        self.assertTrue(tokens[1].space_after)
        self.assertEqual(tokens[3].original_spelling, "6 8")
        self.assertEqual([t._locked for t in tokens], [False, True, False, True, False])

    def test_split_on_boundaries_06(self):
        token_dll = DLL([Token("123456789")])
        token_dll.first.value.first_in_sentence = True
        token_dll.first.value.last_in_sentence = True
        self.tokenizer._split_on_boundaries(token_dll.first, [(0, 2, None), (6, 9, None)], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], "12 3456 789".split())
        tokens = token_dll.to_list()
        self.assertEqual(tokens[0].token_class, "regular")
        self.assertEqual(tokens[2].token_class, "regular")
        self.assertTrue(tokens[0].first_in_sentence)
        self.assertTrue(tokens[2].last_in_sentence)
        self.assertFalse(tokens[0].last_in_sentence)
        self.assertFalse(tokens[2].first_in_sentence)
        self.assertFalse(tokens[1].first_in_sentence)
        self.assertFalse(tokens[1].last_in_sentence)
        self.assertEqual([t._locked for t in tokens], [True, False, True])

    def test_split_on_boundaries_07(self):
        token_dll = DLL([Token("123456789")])
        self.tokenizer._split_on_boundaries(token_dll.first, [(1, 3, "repl1"), (5, 8, "repl2")], "regular")
        self.assertEqual([t.text for t in token_dll.to_list()], "1 repl1 45 repl2 9".split())
        tokens = token_dll.to_list()
        self.assertEqual(tokens[1].token_class, "regular")
        self.assertEqual(tokens[3].token_class, "regular")
        self.assertEqual(tokens[1].original_spelling, "23")
        self.assertEqual(tokens[3].original_spelling, "678")
        self.assertEqual([t._locked for t in tokens], [False, True, False, True, False])


class TestSplitAllSet(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True)
        self.regex = re.compile(r"\p{L}{3}")
        self.set_ = set(["abc", "xYz"])

    def test_split_all_set_01(self):
        token_dll = DLL([Token(s) for s in "0abc0 0xyz0".split()])
        self.tokenizer._split_all_set(token_dll, self.regex, self.set_)
        tokens = token_dll.to_list()
        self.assertEqual([t.text for t in tokens], "0 abc 0 0xyz0".split())

    def test_split_all_set_02(self):
        token_dll = DLL([Token(s) for s in "0aBc0 0xYz0".split()])
        self.tokenizer._split_all_set(token_dll, self.regex, self.set_)
        tokens = token_dll.to_list()
        self.assertEqual([t.text for t in tokens], "0aBc0 0 xYz 0".split())

    def test_split_all_set_03(self):
        token_dll = DLL([Token(s) for s in "0abc0 0xyz0".split()])
        self.tokenizer._split_all_set(token_dll, self.regex, self.set_, to_lower=True)
        tokens = token_dll.to_list()
        self.assertEqual([t.text for t in tokens], "0 abc 0 0xyz0".split())

    def test_split_all_set_04(self):
        token_dll = DLL([Token(s) for s in "0aBc0 0xYz0".split()])
        self.tokenizer._split_all_set(token_dll, self.regex, self.set_, to_lower=True)
        tokens = token_dll.to_list()
        self.assertEqual([t.text for t in tokens], "0 aBc 0 0xYz0".split())
