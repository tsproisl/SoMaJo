#!/usr/bin/env python3


class Token:
    def __init__(self, text, markup=False, locked=False, token_class=None, space_after=True, original_spelling=None, first_in_sentence=False, last_in_sentence=False):
        self.text = text
        self.markup = markup
        self.locked = locked
        self.token_class = token_class
        self.space_after = space_after
        self.original_spelling = original_spelling
        self.first_in_sentence = first_in_sentence
        self.last_in_sentence = last_in_sentence

    def __str__(self):
        return self.text
