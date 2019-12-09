#!/usr/bin/env python3


class Token:
    def __init__(self, text, *, markup=False, markup_class=None, locked=False, token_class=None, space_after=True, original_spelling=None, first_in_sentence=False, last_in_sentence=False):
        self.text = text
        if markup:
            assert markup_class is not None
        if markup_class is not None:
            assert markup
            assert markup_class == "start" or markup_class == "end"
        self.markup = markup
        self.markup_class = markup_class
        self.locked = locked
        self.token_class = token_class
        self.space_after = space_after
        self.original_spelling = original_spelling
        self.first_in_sentence = first_in_sentence
        self.last_in_sentence = last_in_sentence

    def __str__(self):
        return self.text

    def extra_info(self):
        info = []
        if not self.space_after:
            info.append("SpaceAfter=No")
        if self.original_spelling is not None:
            info.append("OriginalSpelling=\"%s\"" % self.original_spelling)
        return ", ".join(info)
