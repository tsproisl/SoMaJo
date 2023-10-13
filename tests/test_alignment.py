#!/usr/bin/env python3

import unicodedata
import unittest

import somajo.alignment


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
