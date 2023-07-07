#!/usr/bin/env python3

import operator
import unittest

from somajo.doubly_linked_list import DLL


class TestDLL(unittest.TestCase):
    def test_dll_01(self):
        lst = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(lst)
        self.assertEqual(dll.to_list(), lst)

    def test_dll_02(self):
        lst = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(lst)
        self.assertEqual(DLL(reversed(dll)).to_list(), list(reversed(lst)))

    def test_dll_03(self):
        lst = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(lst)
        self.assertEqual(len(dll), len(lst))

    def test_dll_04(self):
        lst = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(["Foo", "", 0, -1, False, True, None])
        self.assertEqual(str(dll), str(lst))

    def test_dll_05(self):
        dll = DLL([4, 5, 6])
        dll.append_left(3)
        self.assertEqual(dll.to_list(), [3, 4, 5, 6])

    def test_dll_06(self):
        dll = DLL([4, 5, 6])
        dll.append(7)
        self.assertEqual(dll.to_list(), [4, 5, 6, 7])

    def test_dll_07(self):
        dll = DLL([4, 5, 6])
        dll.extend([7, 8, 9])
        self.assertEqual(dll.to_list(), [4, 5, 6, 7, 8, 9])

    def test_dll_08(self):
        dll = DLL([4, 5, 6, 7])
        last = dll.pop()
        self.assertEqual(last, 7)
        self.assertEqual(len(dll), 3)
        self.assertEqual(dll.to_list(), [4, 5, 6])

    def test_dll_09(self):
        dll = DLL([])
        self.assertEqual(len(dll), 0)
        self.assertEqual(dll.to_list(), [])

    def test_dll_10(self):
        dll = DLL([4])
        last = dll.pop()
        self.assertEqual(last, 4)
        self.assertEqual(len(dll), 0)
        self.assertEqual(dll.to_list(), [])

    def test_dll_11(self):
        dll = DLL([4])
        last = dll.pop()
        self.assertEqual(last, 4)
        self.assertRaises(IndexError, dll.pop)

    def test_dll_12(self):
        dll = DLL([])
        dll.append_left(1)
        self.assertEqual(dll.to_list(), [1])

    def test_dll_13(self):
        dll = DLL([1, 2, 3, 4])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 2)
        self.assertEqual(x.value, 2)
        self.assertEqual([e.value for e in dll.__iter__(start=x)], [2, 3, 4])

    def test_dll_14(self):
        dll = DLL([1, 2, 3, 4])
        x = dll.previous_matching(dll.last, operator.attrgetter("value"), 3)
        self.assertEqual(x.value, 3)
        self.assertEqual([e.value for e in dll.__reversed__(start=x)], [3, 2, 1])

    def test_dll_15(self):
        dll = DLL([1, 2, 3, 4])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 4, operator.attrgetter("value"), 3)
        self.assertEqual(x.value, 4)

    def test_dll_16(self):
        dll = DLL([1, 2, 3, 4])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 7)
        self.assertIs(x, None)

    def test_dll_17(self):
        dll = DLL([1, 2, 3])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 2)
        dll.insert_left(7, x)
        self.assertEqual(dll.to_list(), [1, 7, 2, 3])

    def test_dll_18(self):
        dll = DLL([1, 2, 3])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 2)
        dll.insert_right(7, x)
        self.assertEqual(dll.to_list(), [1, 2, 7, 3])

    def test_dll_19(self):
        dll = DLL([1, 2, 3])
        self.assertTrue(dll.is_left_of(dll.first, dll.last))

    def test_dll_20(self):
        dll = DLL([1, 2, 3])
        self.assertTrue(dll.is_right_of(dll.last, dll.first))

    def test_dll_21(self):
        dll = DLL([1, 2, 3])
        x = dll.next_matching(dll.first, operator.attrgetter("value"), 2)
        dll.remove(x)
        self.assertEqual(dll.to_list(), [1, 3])

    def test_dll_22(self):
        dll = DLL([1, 2, 3])
        dll.remove(dll.first)
        self.assertEqual(dll.to_list(), [2, 3])

    def test_dll_23(self):
        dll = DLL([1, 2, 3])
        dll.remove(dll.last)
        self.assertEqual(dll.to_list(), [1, 2])

    def test_dll_24(self):
        dll = DLL([1, 2, 3])
        dll.insert_left(0, dll.first)
        self.assertEqual(dll.to_list(), [0, 1, 2, 3])

    def test_dll_25(self):
        dll = DLL([1, 2, 3])
        dll.insert_right(4, dll.last)
        self.assertEqual(dll.to_list(), [1, 2, 3, 4])

    def test_dll_26(self):
        dll = DLL([1, 2, 3])
        self.assertFalse(dll.is_left_of(dll.last, dll.first))

    def test_dll_27(self):
        dll = DLL([1])
        dll.remove(dll.last)
        self.assertEqual(dll.to_list(), [])

    def test_dll_28(self):
        dll = DLL([1])
        dll.remove(dll.first)
        self.assertEqual(dll.to_list(), [])
