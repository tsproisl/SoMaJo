#!/usr/bin/env python3

import unicodedata

import regex as re


_ranges = [
    (0x0000, 0x001F),
    (0x007F, 0x009F),
    (0x2000, 0x200A),           # whitespace
    (0x200B, 0x200F),
    (0x202A, 0x202E),
    (0x2066, 0x2069)
]
_single_characters = ["\u00AD", "\u061C", "\u2060", "\uFEFF", "\uFE0F"]
_whitespace = [" ", "\u00A0", "\u1680", "\u2028", "\u2029", "\u202F", "\u205F", "\u3000"]
_skipable_characters = set(_single_characters + _whitespace + [chr(i) for start, end in _ranges for i in range(start, end + 1)])


def _align_nfc(nfc, orig):
    """Character alignment from NFC version to original string."""
    alignment = {}
    if nfc == "":
        assert orig == "", "NFC string is empty - expected original string to be also empty; it is '{orig}' instead"
        return alignment
    nfc_i, nfc_j = 0, 0
    orig_i, orig_j = 0, 0
    while nfc_j < len(nfc):
        nfc_j = nfc_i + 1
        while (nfc_j < len(nfc)) and (unicodedata.combining(nfc[nfc_j]) > 0):
            nfc_j += 1
        orig_j = orig_i + 1
        while (orig_j < len(orig)) and (unicodedata.combining(orig[orig_j]) > 0):
            orig_j += 1
        assert nfc[nfc_i:nfc_j] == unicodedata.normalize("NFC", orig[orig_i:orig_j]), f"'{nfc[nfc_i:nfc_j]}' != unicodedata.normalize('NFC', '{orig[orig_i:orig_j]}')"
        alignment[(nfc_i, nfc_j)] = (orig_i, orig_j)
        nfc_i = nfc_j
        orig_i = orig_j
    assert orig_j == len(orig), f"{orig_j} != {len(orig)}; nfc: '{nfc}', orig: '{orig}'"
    return alignment


def _determine_offsets(tokens, raw, position):
    """Determine start and end positions of tokens in the original raw (NFC) input."""
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
        else:
            raw_start = raw_i
            for i, char in enumerate(text):
                for j in range(raw_start, len(raw)):
                    if raw[j] == char:
                        if i == 0:
                            start = j
                        if i == len(text) - 1:
                            end = j + 1
                        break
                    else:
                        assert raw[j] in _skipable_characters, f"'{raw[j]}' ({hex(ord(raw[j]))}) is not a skipable character; token: '{text}', raw: '{raw[raw_i:]}'"
                raw_start = j + 1
        offsets.append((start, end))
        raw_i = end
    return offsets


def _resolve_entities(xml):
    """Resolve XML entities and provide an alignment from output string to input string."""
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


def token_offsets(token_list, raw, position, xml_input, tokens):
    """Determine character offsets for tokens."""
    if xml_input:
        chunk_offsets = [(t.character_offset[0] - position, t.character_offset[1] - position) for t in token_list]
        raw, align_to_entities = _resolve_entities(raw)
        align_from_entities = {i: char_i for char_i, (start, end) in enumerate(align_to_entities) for i in range(start, end)}
        chunks = [raw[align_from_entities[start]:align_from_entities[end - 1] + 1] for start, end in chunk_offsets]
        chunks_nfc = [unicodedata.normalize("NFC", c) for c in chunks]
        alignments = [_align_nfc(chunk_nfc, chunk) for chunk, chunk_nfc in zip(chunks, chunks_nfc)]
        align_to_raw = alignments[0]
        for i in range(1, len(alignments)):
            o1 = sum(len(c) for c in chunks_nfc[:i])
            o2 = sum(len(c) for c in chunks[:i])
            align_to_raw.update({(k[0] + o1, k[1] + o1): (v[0] + o2, v[1] + o2) for k, v in alignments[i].items()})
        raw_nfc = "".join(chunks_nfc)
    else:
        raw_nfc = unicodedata.normalize("NFC", raw)
        align_to_raw = _align_nfc(raw_nfc, raw)
    align_from_raw = {i: k for k, v in align_to_raw.items() for i in range(v[0], v[1])}
    align_to_starts = {i: v[0] for k, v in align_to_raw.items() for i in range(k[0], k[1])}
    align_to_ends = {i: v[1] for k, v in align_to_raw.items() for i in range(k[0], k[1])}
    # adjust character offsets for markup tokens
    if xml_input:
        for i in range(len(tokens)):
            if tokens[i].markup:
                s, e = tokens[i].character_offset
                tokens[i].character_offset = (
                    align_from_raw[align_from_entities[s - position]][0] + position,
                    align_from_raw[align_from_entities[e - position - 1]][1] + position
                )
    offsets = _determine_offsets(tokens, raw_nfc, position)
    assert len(tokens) == len(offsets), f"Not as many tokens as offsets: {len(tokens)} != {len(offsets)}"
    offsets = [(align_to_starts[s], align_to_ends[e - 1]) for s, e in offsets]
    if xml_input:
        offsets = [(align_to_entities[s][0], align_to_entities[e - 1][1]) for s, e in offsets]
    return offsets


def xml_chunk_offset(token, raw):
    """Determine character offset for an XML chunk created by `utils._xml_chunk_generator`."""
    raw, align_to_raw = _resolve_entities(raw)
    raw = re.sub(r"\s", " ", raw)
    text = token.text
    text = re.sub(r"\s", " ", text)
    if token.markup:
        text, align_to_text = _resolve_entities(text)
        text = text.replace("'", '"')
        if raw.startswith(text):
            start = 0
            end = len(text)
        else:
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
        start = 0
        end = len(text)
    if start == end:
        return (align_to_raw[start][0], align_to_raw[start][0])
    else:
        return (align_to_raw[start][0], align_to_raw[end - 1][1])
