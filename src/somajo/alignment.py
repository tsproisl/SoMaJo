#!/usr/bin/env python3

import unicodedata

import regex as re


def align_nfc(nfc, orig):
    """Character alignment from NFC version to original string."""
    assert len(nfc) <= len(orig), f"len({nfc}) > len({orig})"
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
        # assert nfc[nfc_i:nfc_j] == unicodedata.normalize("NFC", orig[orig_i:orig_j])
        alignment[(nfc_i, nfc_j)] = (orig_i, orig_j)
        nfc_i = nfc_j
        orig_i = orig_j
    assert orig_j == len(orig), f"{orig_j} != {len(orig)}; nfc: '{nfc}', orig: '{orig}'"
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


def pretoken_offset_xml(token, raw):
    # resolve entities
    raw, align_to_raw = resolve_entities(raw)
    raw = re.sub(r"\s", " ", raw)
    text = token.text
    text = re.sub(r"\s", " ", text)
    if token.markup:
        text, align_to_text = resolve_entities(text)
        text = text.replace("'", '"')
        pattern = "(" + re.escape(text) + ")"
        pattern = pattern.replace(r"\ ", r"\s+")
        pattern = pattern.replace("=", r"\s*=\s*")
        if not text.startswith("</"):
            pattern = pattern[:-2] + r"\s*/?\s*" + pattern[-2:]
        local_raw = raw.replace("'", '"')
        m = re.match(pattern, local_raw)
        if text.startswith("</") and not m:
            start, end = 0, 0
        else:
            assert m, f"'{text}' not found in '{local_raw}'"
            start, end = m.span(1)
    else:
        assert raw.startswith(text), f"'{raw}' does not start with '{text}'"
        pattern = "(" + re.escape(text) + ")"
        m = re.search(pattern, raw)
        assert m, f"'{text}' not found in '{raw}'"
        start, end = m.span(1)
    if start == end:
        return (align_to_raw[start][0], align_to_raw[start][0])
    else:
        return (align_to_raw[start][0], align_to_raw[end - 1][1])


def token_offsets(tokens, raw, position):
    """Determine start and end positions of tokens in the original raw (NFC) input."""
    skipable_characters = r"[\s\u0000-\u001F\u007F-\u009F\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF\uFE0F]*?"
    # skipable_characters = r".*?"
    offsets = []
    raw_i = 0
    raw = re.sub(r"\s", " ", raw)
    for token in tokens:
        text = token.text
        if token.original_spelling is not None:
            text = token.original_spelling
        text = re.sub(r"\s", " ", text)
        if token.markup:
            start, end = token.character_offset
            start -= position
            end -= position
            # text, align_to_text = resolve_entities(text)
            # text = text.replace("'", '"')
            # pattern = skipable_characters + "(" + skipable_characters.join([re.escape(c) for c in text])
            # if not text.startswith("</"):
            #     pattern = pattern[:-1] + "/??" + skipable_characters + pattern[-1]
            # pattern += ")"
            # local_raw = raw.replace("'", '"')
            # m = re.search(pattern, local_raw, pos=raw_i)
            # if text.startswith("</") and not m:
            #     start, end = raw_i, raw_i
            # else:
            #     assert m, f"'{text}' not found in '{local_raw[raw_i:]}'"
            #     start, end = m.span(1)
        else:
            pattern = skipable_characters + "(" + skipable_characters.join([re.escape(c) for c in text]) + ")"
            m = re.search(pattern, raw, pos=raw_i)
            assert m, f"'{text}' not found in '{raw[raw_i:]}'\n{[ord(c) for c in text]} not found in {[ord(c) for c in raw[raw_i:]]}"
            start, end = m.span(1)
        offsets.append((start, end))
        raw_i = end
    return offsets


def token_offsets_xml(tokens, raw):
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
    offsets = token_offsets(tokens, raw_nfc)
    offsets = [(align_to_raw[align_starts[s]][0], align_to_raw[align_ends[e] - 1][1]) for s, e in offsets]
    return offsets
