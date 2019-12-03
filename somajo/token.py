#!/usr/bin/env python3

class Token:
    def __init__(self, text, markup=False, locked=False, first_in_sentence=False, last_in_sentence=False):
        self.text = text
        self.markup = markup
        self.locked = locked
        self.first_in_sentence = first_in_sentence
        self.last_in_sentence = last_in_sentence
        self.token_class = None

    def __str__(self):
        return self.text
