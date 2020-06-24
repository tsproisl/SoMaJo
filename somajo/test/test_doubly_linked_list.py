#!/usr/bin/env python3

import unittest

from somajo.doubly_linked_list import DLL


class TestDLL(unittest.TestCase):
    def test_dll_01(self):
        l = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(l)
        self.assertEqual(dll.to_list(), l)

    def test_dll_02(self):
        l = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(l)
        self.assertEqual(DLL(reversed(dll)).to_list(), list(reversed(l)))

    def test_dll_03(self):
        l = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(l)
        self.assertEqual(len(dll), len(l))

    def test_dll_04(self):
        l = ["Foo", "", 0, -1, False, True, None]
        dll = DLL(["Foo", "", 0, -1, False, True, None])
        self.assertEqual(str(dll), str(l))

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
        self.assertEqual(dll.to_list(), [4, 5, 6])
