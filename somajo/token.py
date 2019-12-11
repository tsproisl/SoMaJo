#!/usr/bin/env python3


class Token:
    """Token objects store a piece of text (in the end a single token) with additional information.

    Parameters
    ----------
    text : str
        The text that makes up the token object
    markup : bool
        Is the token a markup token? (Default: False)
    markup_class : {None, 'start', 'end'}
        If `markup=True`, then `markup_class` must be either "start" or "end". (Default: None)
    locked : bool
        Mark the token as locked. (Default: False)
    token_class : str
        The class of the token, e.g. "regular", "emoticon", "url", etc. (Default: None)
    space_after : bool
        Was there a space after the token in the original data? (Default: True)
    original_spelling : str
        The original spelling of the token, if it is different from the one in `text`. (Default: None)
    first_in_sentence : bool
        Is it the first token of a sentence? (Default: False)
    last_in_sentence : bool
        Is it the last token of a sentence? (Default: False)

    """
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
        """String representation of extra information.

        Returns
        -------
        str
            A string representation of the `space_after` and `original_spelling` attributes.
        """
        info = []
        if not self.space_after:
            info.append("SpaceAfter=No")
        if self.original_spelling is not None:
            info.append("OriginalSpelling=\"%s\"" % self.original_spelling)
        return ", ".join(info)
