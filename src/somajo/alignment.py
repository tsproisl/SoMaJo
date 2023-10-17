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


def resolve_entities(xml):
    entity = re.compile(r"&(?:#\d+|#x[0-9a-f]+|amp|apos|gt|lt|quot);", re.I)
    named = {"&amp;": "&", "&apos;": "'", "&gt;": ">", "&lt;": "<", "&quot;": '"'}
    outstring = ""
    alignment = []
    xml_lower = xml.lower()
    i = 0
    for m in entity.finditer(xml_lower):
        start, end = m.span()
        if xml_lower[start + 2] == "x":
            char = chr(int(xml[start + 3:end - 1], base=16))
        elif xml_lower[start + 1] == "#":
            char = chr(int(xml[start + 2:end - 1]))
        else:
            char = named[xml_lower[start:end]]
        outstring += xml[i:start] + char
        for j in range(i, start):
            alignment.append((j, j + 1))
        alignment.append((start, end))
        i = end
    outstring += xml[i:len(xml)]
    for j in range(i, len(xml)):
        alignment.append((j, j + 1))
    return outstring, alignment


def token_offsets(tokens, raw, xml_input=False):
    """Determine start and end positions of tokens in the original raw (NFC) input."""
    offsets = []
    raw_i = 0
    for token in tokens:
        text = token.text
        if token.original_spelling is not None:
            text = token.original_spelling
        if xml_input:
            text, align_to_text = resolve_entities(text)
            text = text.replace("'", '"')
            raw = raw.replace("'", '"')
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
    # resolve entities
    raw_entityless, align_to_raw = resolve_entities(raw)
    # convert to NFC
    raw_nfc = unicodedata.normalize("NFC", raw_entityless)
    # align NFC
    align_to_entityless = align_nfc(raw_nfc, raw_entityless)
    align_starts = {k[0]: v[0] for k, v in align_to_entityless.items()}
    align_ends = {k[1]: v[1] for k, v in align_to_entityless.items()}
    offsets = token_offsets(tokens, raw_nfc, xml_input=True)
    offsets = [(align_to_raw[align_starts[s]][0], align_to_raw[align_ends[e] - 1][1]) for s, e in offsets]
    return offsets
