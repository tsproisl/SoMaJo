#!/usr/bin/env python3

from typing import Literal, Tuple


class Token:
    """Token objects store a piece of text (in the end a single token) with additional information.

    Args:
        text: The text that makes up the token object.
        markup: Is the token a markup token? Defaults to False.
        markup_class: If `markup=True`, then `markup_class` must be either "start" or "end".
            Defaults to None.
        markup_eos: Is the markup token a sentence boundary? Defaults to None.
        locked: Mark the token as locked. Defaults to False.
        token_class: The class of the token, e.g. "regular", "emoticon", "URL", etc.
            Must be one of: 'URL', 'XML_entity', 'XML_tag', 'abbreviation', 'action_word',
            'amount', 'date', 'email_address', 'emoticon', 'hashtag', 'measurement',
            'mention', 'number', 'ordinal', 'regular', 'semester', 'symbol', 'time'.
            Defaults to None.
        space_after: Was there a space after the token in the original data?
            Defaults to True.
        original_spelling: The original spelling of the token, if it is different from
            the one in `text`. Defaults to None.
        first_in_sentence: Is it the first token of a sentence? Defaults to False.
        last_in_sentence: Is it the last token of a sentence? Defaults to False.
        character_offset: Character offset of the token in the input as tuple `(start, end)`
            such that `input[start:end] == text` (if there are no changes to the token text
            during tokenization). Defaults to None.

    """

    token_classes: set[str] = {
        "URL",
        "XML_entity",
        "XML_tag",
        "abbreviation",
        "action_word",
        "amount",
        "date",
        "email_address",
        "emoticon",
        "hashtag",
        "measurement",
        "mention",
        "number",
        "ordinal",
        "regular",
        "semester",
        "symbol",
        "time",
    }

    def __init__(
            self,
            text: str,
            *,
            markup: bool = False,
            markup_class: Literal["start", "end"] | None = None,
            markup_eos: bool | None = None,
            locked: bool = False,
            token_class: str | None = None,
            space_after: bool = True,
            original_spelling: str | None = None,
            first_in_sentence: bool = False,
            last_in_sentence: bool = False,
            character_offset: Tuple[int, int] | None = None
    ) -> None:
        self.text = text
        if markup:
            assert markup_class is not None, "You need to specify a `markup_class` for markup tokens."
            assert markup_eos is not None, "You need to provide a value for `markup_eos` for markup tokens."
        if markup_class is not None:
            assert markup, "You can only specify a `markup_class` for markup tokens."
            assert markup_class == "start" or markup_class == "end", f"'{markup_class}' is not a recognized markup class."
        if markup_eos is not None:
            assert markup, "You can only use `markup_eos` for markup tokens."
            assert isinstance(markup_eos, bool), f"'{markup_eos}' is not a Boolean value."
        if token_class is not None:
            assert token_class in self.token_classes, f"'{token_class}' is not a recognized token class."
        self.markup = markup
        self.markup_class = markup_class
        self.markup_eos = markup_eos
        self._locked = locked
        self.token_class = token_class
        self.space_after = space_after
        self.original_spelling = original_spelling
        self.first_in_sentence = first_in_sentence
        self.last_in_sentence = last_in_sentence
        self.character_offset = character_offset

    def __str__(self) -> str:
        return self.text

    @property
    def extra_info(self) -> str:
        """String representation of extra information.

        Returns:
            str: A string representation of the `space_after` and `original_spelling` attributes.

        Examples:
            >>> tok = Token(":)", token_class="regular", space_after=False, original_spelling=": )")
            >>> print(tok.text)
            :)
            >>> print(tok.extra_info)
            SpaceAfter=No, OriginalSpelling=": )"

        """
        info: list[str] = []
        if not self.space_after:
            info.append("SpaceAfter=No")
        if self.original_spelling is not None:
            info.append("OriginalSpelling=\"%s\"" % self.original_spelling)
        return ", ".join(info)
