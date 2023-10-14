#!/usr/bin/env python3

import unicodedata

import regex as re


def align_nfc(nfc, orig):
    """Character alignment from NFC version to original string."""
    assert len(nfc) <= len(orig)
    alignment = {}
    if nfc == "":
        assert orig == ""
        return alignment
    nfc_i, nfc_j = 0, 0
    orig_i, orig_j = 0, 0
    assert unicodedata.combining(nfc[0]) == 0
    assert unicodedata.combining(orig[0]) == 0
    while nfc_j < len(nfc):
        nfc_j = nfc_i + 1
        while (nfc_j < len(nfc)) and (unicodedata.combining(nfc[nfc_j]) > 0):
            nfc_j += 1
        orig_j = orig_i + 1
        while (orig_j < len(orig)) and (unicodedata.combining(orig[orig_j]) > 0):
            orig_j += 1
        assert nfc[nfc_i:nfc_j] == unicodedata.normalize("NFC", orig[orig_i:orig_j])
        alignment[(nfc_i, nfc_j)] = (orig_i, orig_j)
        nfc_i = nfc_j
        orig_i = orig_j
    assert orig_j == len(orig)
    return alignment


def token_offsets(tokens, raw):
    """Determine start and end positions of tokens in the original raw (NFC) input."""
    offsets = []
    raw_i = 0
    for token in tokens:
        text = token.text
        if token.original_spelling is not None:
            text = token.original_spelling
        pattern = ".*?(" + ".*?".join([re.escape(c) for c in text]) + ")"
        m = re.search(pattern, raw, pos=raw_i)
        assert m
        start, end = m.span(1)
        offsets.append((start, end))
        raw_i = end
    return offsets


def token_offsets_xml(tokens, raw, tokenizer):
    """Determine start and end positions of tokens in the original raw
    (NFC) input. Account for XML entities.
    """
    offsets = []
    raw_i = 0
    skip_pattern = "|".join([r"\s", "\uFE0F", tokenizer.controls.pattern, tokenizer.other_nasties.pattern])
    skip = re.compile(skip_pattern)
    for token in tokens:
        text = token.text
        if token.original_spelling is not None:
            text = token.original_spelling
        # print(text)
        start, end = None, None
        for i, char in enumerate(text):
            while True:
                # print(char, raw_i, raw[raw_i])
                if char == raw[raw_i]:
                    s = raw_i
                    raw_i += 1
                    e = raw_i
                    break
                elif ((char == "'") or (char == '"')) and ((raw[raw_i] == "'") or (raw[raw_i] == '"')):
                    s = raw_i
                    raw_i += 1
                    e = raw_i
                    break
                elif raw[raw_i] == "&":
                    # TODO: process_entities(text, i, raw, raw_i)
                    s = raw_i
                    while raw[raw_i] != ";":
                        raw_i += 1
                    raw_i += 1
                    e = raw_i
                    entity = raw[s:e]
                    break
                elif skip.match(raw[raw_i]):
                    raw_i += 1
                    continue
                else:
                    raise ValueError(f"Cannot find char {char} from {text} in {raw[raw_i:raw_i + 20]}...")
            if i == 0:
                start = s
            elif i == len(text) - 1:
                end = e
        offsets.append((start, end))
    return offsets
