#!/usr/bin/env python3

import collections
import random
import unicodedata
import warnings
import xml.etree.ElementTree as ET

import regex as re

from somajo import utils

Token = collections.namedtuple("Token", ["token", "token_class"])


class Tokenizer(object):
    def __init__(self, split_camel_case=False, token_classes=False, extra_info=False):
        """Create a Tokenizer object. If split_camel_case is set to True,
        tokens written in CamelCase will be split. If token_classes is
        set to true, the tokenizer will output the token class for
        each token (if it is a number, an XML tag, an abbreviation,
        etc.). If extra_info is set to True, the tokenizer will output
        information about the original spelling of the tokens.

        """
        self.split_camel_case = split_camel_case
        self.token_classes = token_classes
        self.extra_info = extra_info
        self.unique_string_length = 7
        self.mapping = {}
        self.unique_prefix = None
        self.replacement_counter = 0

        self.spaces = re.compile(r"\s+")
        self.controls = re.compile(r"[\u0000-\u001F\u007F-\u009F]")
        # soft hyphen (00AD), zero-width space (200B), zero-width
        # non-joiner (200C), zero-width joiner (200D), left-to-right
        # mark (200E), right-to-left mark (200F)
        self.other_nasties = re.compile(r"[\u00AD\u200B-\u200F]")
        # combination
        self.starts_with_junk = re.compile(r"^[\u0000-\u001F\u007F-\u009F\u00AD\u200B-\u200F]+")
        self.junk_between_spaces = re.compile(r"(?:^|\s+)[\s\u0000-\u001F\u007F-\u009F\u00AD\u200B-\u200F]+(?:\s+|$)")

        # TAGS, EMAILS, URLs
        self.xml_declaration = re.compile(r"""<\?xml
                                              (?:                #   This group permits zero or more attributes
                                                \s+              #   Whitespace to separate attributes
                                                [_:A-Z][-.:\w]*  #   Attribute name
                                                \s*=\s*          #   Attribute name-value delimiter
                                                (?: "[^"]*"      #   Double-quoted attribute value
                                                  | '[^']*'      #   Single-quoted attribute value
                                                )
                                              )*
                                              \s*                #   Permit trailing whitespace
                                              \?>""", re.VERBOSE | re.IGNORECASE)
        # self.tag = re.compile(r'<(?!-)(?:/[^> ]+|[^>]+/?)(?<!-)>')
        # taken from Regular Expressions Cookbook
        self.tag = re.compile(r"""
                                  <
                                  (?:                  # Branch for opening tags:
                                    ([_:A-Z][-.:\w]*)  #   Capture the opening tag name to backreference 1
                                    (?:                #   This group permits zero or more attributes
                                      \s+              #   Whitespace to separate attributes
                                      [_:A-Z][-.:\w]*  #   Attribute name
                                      \s*=\s*          #   Attribute name-value delimiter
                                      (?: "[^"]*"      #   Double-quoted attribute value
                                        | '[^']*'      #   Single-quoted attribute value
                                      )
                                    )*
                                    \s*                #   Permit trailing whitespace
                                    /?                 #   Permit self-closed tags
                                  |                    # Branch for closing tags:
                                    /
                                    ([_:A-Z][-.:\w]*)  #   Capture the closing tag name to backreference 2
                                    \s*                #   Permit trailing whitespace
                                  )
                                  >
        """, re.VERBOSE | re.IGNORECASE)
        # regex for email addresses taken from:
        # http://www.regular-expressions.info/email.html
        # self.email = re.compile(r"\b[[:alnum:].%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}\b")
        self.email = re.compile(r"\b[[:alnum:].%+-]+(?:@| \[?at\]? )[[:alnum:].-]+(?:\.| \[?dot\]? )[[:alpha:]]{2,}\b")
        # simple regex for urls that start with http or www
        # TODO: schließende Klammer am Ende erlauben, wenn nach http etc. eine öffnende kam
        self.simple_url_with_brackets = re.compile(r'\b(?:(?:https?|ftp|svn)://|(?:https?://)?www\.)\S+?\(\S*?\)\S*(?=$|[\'. "!?,;\n\t])', re.IGNORECASE)
        self.simple_url = re.compile(r'\b(?:(?:https?|ftp|svn)://|(?:https?://)?www\.)\S+[^\'. "!?,;:\n\t]', re.IGNORECASE)
        self.doi = re.compile(r'\bdoi:10\.\d+/\S+', re.IGNORECASE)
        self.doi_with_space = re.compile(r'(?<=\bdoi: )10\.\d+/\S+', re.IGNORECASE)
        # we also allow things like tagesschau.de-App
        self.url_without_protocol = re.compile(r'\b[\w./-]+\.(?:de|com|org|net|edu|info|jpg|png|gif|log|txt)(?:-\w+)?\b', re.IGNORECASE)

        # XML entities
        self.entity_name = re.compile(r'&(?:quot|amp|apos|lt|gt);', re.IGNORECASE)
        self.entity_decimal = re.compile(r'&#\d+;')
        self.entity_hex = re.compile(r'&#x[0-9a-f]+;', re.IGNORECASE)

        # EMOTICONS
        # TODO: Peter, SMS von gestern Nacht -> hauptsächlich entities -> hilft nicht so wahnsinnig.
        emoticon_set = set(["(-.-)", "(T_T)", "(♥_♥)", ")':", ")-:",
                            "(-:", ")=", ")o:", ")x", ":'C", ":/",
                            ":<", ":C", ":[", "=(", "=)", "=D", "=P",
                            ">:", "D':", "D:", "\:", "]:", "x(", "^^",
                            "o.O", "oO", "\O/", "\m/", ":;))", "_))",
                            "*_*", "._.", ":wink:", ">_<", "*<:-)",
                            ":!:", ":;-))"])
        emoticon_list = sorted(emoticon_set, key=len, reverse=True)
        self.emoticon = re.compile(r"""(?:(?:[:;]|(?<!\d)8)           # a variety of eyes, alt.: [:;8]
                                        [-'oO]?                       # optional nose or tear
                                        (?: \)+ | \(+ | [*] | ([DPp])\1*(?!\w)))   # a variety of mouths
                                    """ +
                                   r"|" +
                                   r"(?:xD+|XD+)" +
                                   r"|" +
                                   r"|".join([re.escape(_) for _ in emoticon_list]), re.VERBOSE)
        self.space_emoticon = re.compile(r'([:;])[ ]+([()])')
        # ^3 is an emoticon, unless it is preceded by a number (with
        # optional whitespace between number and ^3)
        # ^\^3    # beginning of line, no leading characters
        # ^\D^3   # beginning of line, one leading character
        # (?<=\D[ ])^3   # two leading characters, non-number + space
        # (?<=.[^\d ])^3   # two leading characters, x + non-space-non-number
        self.heart_emoticon = re.compile(r"(?:^|^\D|(?<=\D[ ])|(?<=.[^\d ]))\^3")
        # U+2600..U+26FF	Miscellaneous Symbols
        # U+2700..U+27BF	Dingbats
        # U+1F300..U+1F5FF	Miscellaneous Symbols and Pictographs
        # U+1F600..U+1F64F	Emoticons
        # U+1F680..U+1F6FF	Transport and Map Symbols
        # U+1F900..U+1F9FF	Supplemental Symbols and Pictographs
        # self.unicode_symbols = re.compile(r"[\u2600-\u27BF]|[\u1F300-\u1F64F]|[\u1F680-\u1F6FF]|[\u1F900-\u1F9FF]")
        self.unicode_symbols = re.compile(r"[\u2600-\u27BF\U0001F300-\U0001f64f\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]")

        # special tokens containing + or &
        tokens_with_plus_or_ampersand = utils.read_abbreviation_file("tokens_with_plus_or_ampersand.txt")
        plus_amp_simple = [(pa, re.search(r"^\w+[&+]\w+$", pa)) for pa in tokens_with_plus_or_ampersand]
        self.simple_plus_ampersand = set([pa[0].lower() for pa in plus_amp_simple if pa[1]])
        self.simple_plus_ampersand_candidates = re.compile(r"\b\w+[&+]\w+\b")
        tokens_with_plus_or_ampersand = [pa[0] for pa in plus_amp_simple if not pa[1]]
        # self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:\L<patokens>)(?!\w)", re.IGNORECASE, patokens=tokens_with_plus_or_ampersand)
        self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:" + r"|".join([re.escape(_) for _ in tokens_with_plus_or_ampersand]) + r")(?!\w)", re.IGNORECASE)

        # camelCase
        self.emoji = re.compile(r'\bemojiQ[[:alpha:]]{3,}\b')
        camel_case_token_list = utils.read_abbreviation_file("camel_case_tokens.txt")
        cc_alnum = [(cc, re.search(r"^\w+$", cc)) for cc in camel_case_token_list]
        self.simple_camel_case_tokens = set([cc[0] for cc in cc_alnum if cc[1]])
        self.simple_camel_case_candidates = re.compile(r"\b\w*[[:lower:]][[:upper:]]\w*\b")
        camel_case_token_list = [cc[0] for cc in cc_alnum if not cc[1]]
        # things like ImmobilienScout24.de are already covered by URL detection
        # self.camel_case_url = re.compile(r'\b(?:[[:upper:]][[:lower:][:digit:]]+){2,}\.(?:de|com|org|net|edu)\b')
        self.camel_case_token = re.compile(r"\b(?:" + r"|".join([re.escape(_) for _ in camel_case_token_list]) + r"|:Mac[[:upper:]][[:lower:]]*)\b")
        # self.camel_case_token = re.compile(r"\b(?:\L<cctokens>|Mac[[:upper:]][[:lower:]]*)\b", cctokens=camel_case_token_set)
        self.in_and_innen = re.compile(r'\b[[:alpha:]]+[[:lower:]]In(?:nen)?[[:lower:]]*\b')
        self.camel_case = re.compile(r'(?<=[[:lower:]]{2})([[:upper:]])(?![[:upper:]]|\b)')

        # ABBREVIATIONS
        self.single_letter_ellipsis = re.compile(r"(?<![\w.])(?P<a_letter>[[:alpha:]])(?P<b_ellipsis>\.{3})(?!\.)")
        self.and_cetera = re.compile(r"(?<![\w.&])&c\.(?![[:alpha:]]{1,3}\.)")
        self.str_abbreviations = re.compile(r'(?<![\w.])([[:alpha:]-]+-Str\.)(?![[:alpha:]])', re.IGNORECASE)
        self.nr_abbreviations = re.compile(r"(?<![\w.])(\w+\.-?Nr\.)(?![[:alpha:]]{1,3}\.)", re.IGNORECASE)
        self.single_letter_abbreviation = re.compile(r"(?<![\w.])[[:alpha:]]\.(?![[:alpha:]]{1,3}\.)")
        # abbreviations with multiple dots that constitute tokens
        single_token_abbreviation_list = utils.read_abbreviation_file("single_token_abbreviations.txt")
        self.single_token_abbreviation = re.compile(r"(?<![\w.])(?:" + r'|'.join([re.escape(_) for _ in single_token_abbreviation_list]) + r')(?![[:alpha:]]{1,3}\.)')
        self.ps = re.compile(r"(?<!\d[ ])\bps\.", re.IGNORECASE)
        self.multipart_abbreviation = re.compile(r'(?:[[:alpha:]]+\.){2,}')
        # only abbreviations that are not matched by (?:[[:alpha:]]\.)+
        abbreviation_list = utils.read_abbreviation_file("abbreviations.txt")
        # abbrev_simple = [(a, re.search(r"^[[:alpha:]]{2,}\.$", a)) for a in abbreviation_list]
        # self.simple_abbreviations = set([a[0].lower() for a in abbrev_simple if a[1]])
        # self.simple_abbreviation_candidates = re.compile(r"(?<![\w.])[[:alpha:]]{2,}\.(?![[:alpha:]]{1,3}\.)")
        # abbreviation_list = [a[0] for a in abbrev_simple if not a[1]]
        self.abbreviation = re.compile(r"(?<![\w.])(?:" +
                                       r"(?:(?:[[:alpha:]]\.){2,})" +
                                       r"|" +
                                       # r"(?i:" +    # this part should be case insensitive
                                       r'|'.join([re.escape(_) for _ in abbreviation_list]) +
                                       # r"))+(?![[:alpha:]]{1,3}\.)", re.V1)
                                       r")+(?![[:alpha:]]{1,3}\.)", re.IGNORECASE)

        # MENTIONS, HASHTAGS, ACTION WORDS
        self.mention = re.compile(r'[@]\w+(?!\w)')
        self.hashtag = re.compile(r'(?<!\w)[#]\w+(?!\w)')
        # action words without spaces are to be treated as units
        self.action_word = re.compile(r'(?<!\w)(?P<a_open>[*+])(?P<b_middle>[^\s*]+)(?P<c_close>[*])(?!\w)')

        # DATE, TIME, NUMBERS
        self.three_part_date_year_first = re.compile(r'(?<![\d.]) (?P<a_year>\d{4}) (?P<b_month_or_day>([/-])\d{1,2}) (?P<c_day_or_month>\3\d{1,2}) (?![\d.])', re.VERBOSE)
        self.three_part_date_dmy = re.compile(r'(?<![\d.]) (?P<a_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])([./-])) (?P<b_month>(?:0?[1-9]|1[0-2])\2) (?P<c_year>(?:\d\d){1,2}) (?![\d.])', re.VERBOSE)
        self.three_part_date_mdy = re.compile(r'(?<![\d.]) (?P<a_month>(?:0?[1-9]|1[0-2])([./-])) (?P<b_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])\2) (?P<c_year>(?:\d\d){1,2}) (?![\d.])', re.VERBOSE)
        self.two_part_date = re.compile(r'(?<![\d.]) (?P<a_day_or_month>\d{1,2}([./-])) (?P<b_day_or_month>\d{1,2}\2) (?![\d.])', re.VERBOSE)
        self.time = re.compile(r'(?<!\w)\d{1,2}(?::\d{2}){1,2}(?![\d:])')
        self.ordinal = re.compile(r'(?<![\w.])(?:\d{1,3}|\d{5,}|[3-9]\d{3})\.(?!\d)')
        self.fraction = re.compile(r'(?<!\w)\d+/\d+(?![\d/])')
        self.amount = re.compile(r'(?<!\w)(?:\d+[\d,.]*-)(?!\w)')
        self.semester = re.compile(r'(?<!\w)(?P<a_semester>[WS]S|SoSe|WiSe)(?P<b_jahr>\d\d(?:/\d\d)?)(?!\w)', re.IGNORECASE)
        self.measurement = re.compile(r'(?<!\w)(?P<a_amount>[−+-]?\d*[,.]?\d+)(?P<b_unit>(?:mm|cm|dm|m|km)(?:\^?[23])?|qm|g|kg|min|h|s|sek|cent|eur)(?!\w)', re.IGNORECASE)
        # auch Web2.0
        self.number_compound = re.compile(r'(?<!\w) (?:\d+-?[[:alpha:]@]+ | [[:alpha:]@]+-?\d+(?:\.\d)?) (?!\w)', re.VERBOSE)
        self.number = re.compile(r"""(?<!\w)
                                     (?:[−+-]?              # optional sign
                                       \d*                  # optional digits before decimal point
                                       [.,]?                # optional decimal point
                                       \d+                  # digits
                                       (?:[eE][−+-]?\d+)?   # optional exponent
                                       |
                                       \d+[\d.,]*\d+)
                                     (?![.,]?\d)""", re.VERBOSE)

        # PUNCTUATION
        self.quest_exclam = re.compile(r"([!?]+)")
        # arrows
        self.space_right_arrow = re.compile(r'(-+)\s+(>)')
        self.space_left_arrow = re.compile(r'(<)\s+(-+)')
        self.arrow = re.compile(r'(-+>|<-+|[\u2190-\u21ff])')
        # parens
        self.paired_paren = re.compile(r'([(])(?!inn)([^()]*)([)])')
        self.paired_bracket = re.compile(r'(\[)([^][]*)(\])')
        self.paren = re.compile(r"""((?:(?<!\w)   # no alphanumeric character
                                       [[{(]      # opening paren
                                       (?=\w)) |  # alphanumeric character
                                     (?:(?<=\w)   # alphanumeric character
                                       []})]      # closing paren
                                       (?!\w)) |  # no alphanumeric character
                                     (?:(?<=\s)   # space
                                       []})]      # closing paren
                                       (?=\w)) |  # alphanumeric character
                                     (?:(?<=\w-)  # hyphen
                                       [)]        # closing paren
                                       (?=\w)))   # alphanumeric character
                                 """, re.VERBOSE)
        self.all_paren = re.compile(r"(?<=\s)[][(){}](?=\s)")
        self.slash = re.compile(r'(/+)(?!in(?:nen)?|en)')
        self.paired_double_latex_quote = re.compile(r"(?<!`)(``)([^`']+)('')(?!')")
        self.paired_single_latex_quote = re.compile(r"(?<!`)(`)([^`']+)(')(?!')")
        self.paired_single_quot_mark = re.compile(r"(['‚‘’])([^']+)(['‘’])")
        self.all_quote = re.compile(r"(?<=\s)(?:``|''|`|['‚‘’])(?=\s)")
        self.other_punctuation = re.compile(r'([<>%‰€$£₤¥°@~*„“”‚‘"»«›‹,;:+=&–])')
        self.ellipsis = re.compile(r'\.{2,}|…+(?:\.{2,})?')
        self.dot_without_space = re.compile(r'(?<=[[:lower:]]{2})(\.)(?=[[:upper:]][[:lower:]]{2})')
        # self.dot = re.compile(r'(?<=[\w)])(\.)(?![\w])')
        self.dot = re.compile(r'(\.)')
        # Soft hyphen ­ „“

    def _get_unique_prefix(self, text):
        """Return a string that is not a substring of text."""
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        # create random string of length self.unique_string_length
        unique_string = ""
        while unique_string in text:
            unique_string = "".join(random.choice(alphabet) for _ in range(self.unique_string_length))
        return unique_string

    def _get_unique_suffix(self):
        """Obtain a unique suffix for combination with self.unique_prefix.

        """
        digits = "abcdefghijklmnopqrstuvwxyz"
        n = self.replacement_counter
        b26 = ""
        while n > 0:
            quotient, remainder = divmod(n, 26)
            b26 = digits[remainder] + b26
            n = quotient
        self.replacement_counter += 1
        return b26.rjust(self.unique_string_length, "a")

    def _get_unique_string(self):
        """Return a string that is not a substring of text."""
        return self.unique_prefix + self._get_unique_suffix()

    def _replace_regex(self, text, regex, token_class="regular"):
        """Replace instances of regex with unique strings and store
        replacements in mapping.

        """
        replacements = {}

        def repl(match):
            instance = match.group(0)
            if instance not in replacements:
                # check if there are named subgroups
                if len(match.groupdict()) > 0:
                    parts = [v for k, v in sorted(match.groupdict().items())]
                    replacements[instance] = self._multipart_replace(instance, parts, token_class)
                else:
                    replacement = replacements.setdefault(instance, self._get_unique_string())
                    self.mapping[replacement] = Token(instance, token_class)
            return " %s " % replacements[instance]
        return regex.sub(repl, text)

    def _multipart_replace(self, instance, parts, token_class):
        """"""
        replacements = []
        for part in parts:
            replacement = self._get_unique_string()
            self.mapping[replacement] = Token(part, token_class)
            replacements.append(replacement)
        multipart = " ".join(replacements)
        return multipart

    def _reintroduce_instances(self, tokens):
        """Replace the unique strings with the original text."""
        tokens = [self.mapping.get(t, Token(t, "regular")) for t in tokens]
        return tokens

    def _replace_abbreviations(self, text):
        """Replace instances of abbreviations with unique strings and store
        replacements in self.mapping.

        """
        replacements = {}
        text = self._replace_regex(text, self.single_letter_ellipsis, "abbreviation")
        text = self._replace_regex(text, self.and_cetera, "abbreviation")
        text = self._replace_regex(text, self.str_abbreviations, "abbreviation")
        text = self._replace_regex(text, self.nr_abbreviations, "abbreviation")
        text = self._replace_regex(text, self.single_letter_abbreviation, "abbreviation")
        text = self._replace_regex(text, self.single_token_abbreviation, "abbreviation")
        text = self.spaces.sub(" ", text)
        text = self._replace_regex(text, self.ps, "abbreviation")

        def repl(match):
            instance = match.group(0)
            if instance not in replacements:
                # check if it is a multipart abbreviation
                if self.multipart_abbreviation.fullmatch(instance):
                    parts = [p.strip() + "." for p in instance.strip(".").split(".")]
                    replacements[instance] = self._multipart_replace(instance, parts, "abbreviation")
                else:
                    replacement = replacements.setdefault(instance, self._get_unique_string())
                    self.mapping[replacement] = Token(instance, "abbreviation")
            return " %s " % replacements[instance]
        text = self.abbreviation.sub(repl, text)
        # text = self._replace_set(text, self.simple_abbreviation_candidates, self.simple_abbreviations, "abbreviation", ignore_case=True)
        return text

    def _replace_set(self, text, regex, items, token_class="regular", ignore_case=False):
        """Replace all elements from items in text with unique strings."""
        replacements = {}

        def repl(match):
            instance = match.group(0)
            ic_instance = instance
            if ignore_case:
                ic_instance = instance.lower()
            if ic_instance in items:
                if instance not in replacements:
                    replacement = replacements.setdefault(instance, self._get_unique_string())
                    self.mapping[replacement] = Token(instance, token_class)
                return " %s " % replacements[instance]
            else:
                return instance
        return regex.sub(repl, text)

    def _check_spaces(self, tokens, original_text):
        """Compare the tokens with the original text to see which tokens had
        trailing whitespace (to be able to annotate SpaceAfter=No) and
        which tokens contained internal whitespace (to be able to
        annotate OriginalSpelling="...").

        """
        extra_info = ["" for _ in tokens]
        normalized = self.spaces.sub(" ", original_text)
        normalized = self.junk_between_spaces.sub(" ", normalized)
        normalized = normalized.strip()
        for token_index, t in enumerate(tokens):
            original_spelling = None
            token = t.token
            token_length = len(token)
            if normalized.startswith(token):
                normalized = normalized[token_length:]
            else:
                orig = []
                for char in token:
                    first_char = None
                    while first_char != char:
                        try:
                            first_char = normalized[0]
                            normalized = normalized[1:]
                            orig.append(first_char)
                        except IndexError:
                            warnings.warn("IndexError in this paragraph: '%s'\nTokens: %s" % (original_text, tokens))
                original_spelling = "".join(orig)
            m = self.starts_with_junk.search(normalized)
            if m:
                if original_spelling is None:
                    original_spelling = token
                original_spelling += normalized[:m.end()]
                normalized = normalized[m.end():]
            if original_spelling is not None:
                extra_info[token_index] = 'OriginalSpelling="%s"' % original_spelling
            if len(normalized) > 0:
                if normalized.startswith(" "):
                    normalized = normalized[1:]
                else:
                    if len(extra_info[token_index]) > 0:
                        extra_info[token_index] = ", " + extra_info[token_index]
                    extra_info[token_index] = "SpaceAfter=No" + extra_info[token_index]
        try:
            assert len(normalized) == 0
        except AssertionError:
            warnings.warn("AssertionError in this paragraph: '%s'\nTokens: %s\nRemaining normalized text: '%s'" % (original_text, tokens, normalized))
        return extra_info

    def _match_xml(self, tokens, elements):
        """"""
        agenda = list(reversed(tokens))
        for element in elements:
            original_text = unicodedata.normalize("NFC", element.text)
            normalized = self.spaces.sub(" ", original_text)
            normalized = self.junk_between_spaces.sub(" ", normalized)
            normalized = normalized.strip()
            output = []
            while len(normalized) > 0:
                t = agenda.pop()
                original_spelling = None
                extra_info = ""
                token = t.token
                if normalized.startswith(token):
                    normalized = normalized[len(token):]
                elif token.startswith(normalized):
                    agenda.append(Token(token[len(normalized):], t.token_class))
                    token = normalized
                    normalized = ""
                else:
                    orig = []
                    for char in token:
                        first_char = None
                        while first_char != char:
                            try:
                                first_char = normalized[0]
                                normalized = normalized[1:]
                                orig.append(first_char)
                            except IndexError:
                                warnings.warn("IndexError in this paragraph: '%s'\nTokens: %s" % (original_text, tokens))
                    original_spelling = "".join(orig)
                m = self.starts_with_junk.search(normalized)
                if m:
                    if original_spelling is None:
                        original_spelling = token
                    original_spelling += normalized[:m.end()]
                    normalized = normalized[m.end():]
                if original_spelling is not None:
                    extra_info = 'OriginalSpelling="%s"' % original_spelling
                if len(normalized) > 0:
                    if normalized.startswith(" "):
                        normalized = normalized[1:]
                    else:
                        if len(extra_info) > 0:
                            extra_info = ", " + extra_info
                        extra_info = "SpaceAfter=No" + extra_info
                output.append("\t".join((token, t.token_class, extra_info)))
            if len(output) > 0:
                tokenized_text = "\n" + "\n".join(output) + "\n"
            else:
                tokenized_text = "\n"
            if element.type == "text":
                element.element.text = tokenized_text
            elif element.type == "tail":
                element.element.tail = tokenized_text
        try:
            assert len(agenda) == 0
        except AssertionError:
            warnings.warn("AssertionError: %d tokens left over" % len(agenda))
        return elements

    def _tokenize(self, paragraph):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        # reset mappings for the current paragraph
        self.mapping = {}
        self.unique_prefix = self._get_unique_prefix(paragraph)

        # normalize whitespace
        paragraph = self.spaces.sub(" ", paragraph)

        # get rid of junk characters
        paragraph = self.controls.sub("", paragraph)
        paragraph = self.other_nasties.sub("", paragraph)

        # Some tokens are allowed to contain whitespace. Get those out
        # of the way first. We replace them with unique strings and
        # undo that later on.
        # - XML tags
        paragraph = self._replace_regex(paragraph, self.xml_declaration, "XML_tag")
        paragraph = self._replace_regex(paragraph, self.tag, "XML_tag")
        # - email address obfuscation may involve spaces
        paragraph = self._replace_regex(paragraph, self.email, "email_address")

        # Some emoticons contain erroneous spaces. We fix this.
        paragraph = self.space_emoticon.sub(r'\1\2', paragraph)

        # urls
        paragraph = self._replace_regex(paragraph, self.simple_url_with_brackets, "URL")
        paragraph = self._replace_regex(paragraph, self.simple_url, "URL")
        paragraph = self._replace_regex(paragraph, self.doi, "DOI")
        paragraph = self._replace_regex(paragraph, self.doi_with_space, "DOI")
        paragraph = self._replace_regex(paragraph, self.url_without_protocol, "URL")
        # paragraph = self._replace_regex(paragraph, self.url)

        # XML entities
        paragraph = self._replace_regex(paragraph, self.entity_name, "XML_entity")
        paragraph = self._replace_regex(paragraph, self.entity_decimal, "XML_entity")
        paragraph = self._replace_regex(paragraph, self.entity_hex, "XML_entity")

        # replace emoticons with unique strings so that they are out
        # of the way
        paragraph = self.spaces.sub(" ", paragraph)
        paragraph = self._replace_regex(paragraph, self.heart_emoticon, "emoticon")
        paragraph = self._replace_regex(paragraph, self.emoticon, "emoticon")
        paragraph = self._replace_regex(paragraph, self.unicode_symbols, "emoticon")

        # mentions, hashtags
        paragraph = self._replace_regex(paragraph, self.mention, "mention")
        paragraph = self._replace_regex(paragraph, self.hashtag, "hashtag")
        # action words
        paragraph = self._replace_regex(paragraph, self.action_word, "action_word")
        # textual representations of emoji
        paragraph = self._replace_regex(paragraph, self.emoji, "emoticon")

        paragraph = self._replace_regex(paragraph, self.token_with_plus_ampersand)
        paragraph = self._replace_set(paragraph, self.simple_plus_ampersand_candidates, self.simple_plus_ampersand, ignore_case=True)

        # camelCase
        if self.split_camel_case:
            paragraph = self._replace_regex(paragraph, self.camel_case_token)
            paragraph = self._replace_set(paragraph, self.simple_camel_case_candidates, self.simple_camel_case_tokens)
            paragraph = self._replace_regex(paragraph, self.in_and_innen)
            paragraph = self.camel_case.sub(r' \1', paragraph)

        # remove known abbreviations
        paragraph = self._replace_abbreviations(paragraph)

        # DATES AND NUMBERS
        # dates
        paragraph = self._replace_regex(paragraph, self.three_part_date_year_first, "date")
        paragraph = self._replace_regex(paragraph, self.three_part_date_dmy, "date")
        paragraph = self._replace_regex(paragraph, self.three_part_date_mdy, "date")
        paragraph = self._replace_regex(paragraph, self.two_part_date, "date")
        # time
        paragraph = self._replace_regex(paragraph, self.time, "time")
        # ordinals
        paragraph = self._replace_regex(paragraph, self.ordinal, "ordinal")
        # fractions
        paragraph = self._replace_regex(paragraph, self.fraction, "number")
        # amounts (1.000,-)
        paragraph = self._replace_regex(paragraph, self.amount, "amount")
        # semesters
        paragraph = self._replace_regex(paragraph, self.semester, "semester")
        # measurements
        paragraph = self._replace_regex(paragraph, self.measurement, "measurement")
        # number compounds
        paragraph = self._replace_regex(paragraph, self.number_compound, "number_compound")
        # numbers
        paragraph = self._replace_regex(paragraph, self.number, "number")

        # (clusters of) question marks and exclamation marks
        paragraph = self._replace_regex(paragraph, self.quest_exclam, "symbol")
        # arrows
        paragraph = self.space_right_arrow.sub(r'\1\2', paragraph)
        paragraph = self.space_left_arrow.sub(r'\1\2', paragraph)
        paragraph = self._replace_regex(paragraph, self.arrow, "symbol")
        # parens
        paragraph = self.paired_paren.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paired_bracket.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paren.sub(r' \1 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.all_paren, "symbol")
        # slash
        # paragraph = self.slash.sub(r' \1 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.slash, "symbol")
        # LaTeX-style quotation marks
        paragraph = self.paired_double_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paired_single_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        # single quotation marks, apostrophes
        paragraph = self.paired_single_quot_mark.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.all_quote, "symbol")
        # other punctuation symbols
        # paragraph = self.other_punctuation.sub(r' \1 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.other_punctuation, "symbol")
        # ellipsis
        paragraph = self._replace_regex(paragraph, self.ellipsis, "symbol")
        # dots
        # paragraph = self.dot_without_space.sub(r' \1 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.dot_without_space, "symbol")
        # paragraph = self.dot.sub(r' \1 ', paragraph)
        paragraph = self._replace_regex(paragraph, self.dot, "symbol")

        # tokenize
        tokens = paragraph.strip().split()

        # reintroduce mapped tokens
        tokens = self._reintroduce_instances(tokens)

        return tokens

    def tokenize(self, paragraph):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        # convert paragraph to Unicode normal form C (NFC)
        paragraph = unicodedata.normalize("NFC", paragraph)

        tokens = self._tokenize(paragraph)

        if len(tokens) == 0:
            return []

        if self.extra_info:
            extra_info = self._check_spaces(tokens, paragraph)

        tokens, token_classes = zip(*tokens)
        if self.token_classes:
            if self.extra_info:
                return list(zip(tokens, token_classes, extra_info))
            else:
                return list(zip(tokens, token_classes))
        else:
            if self.extra_info:
                return list(zip(tokens, extra_info))
            else:
                return list(tokens)

    def tokenize_xml(self, xml, is_file=True):
        """Tokenize XML file or XML string according to the guidelines of the
        EmpiriST 2015 shared task on automatic linguistic annotation
        of computer-mediated communication / social media.

        """
        elements = utils.parse_xml(xml, is_file)
        whole_text = " ".join((e.text for e in elements))

        # convert paragraph to Unicode normal form C (NFC)
        whole_text = unicodedata.normalize("NFC", whole_text)

        tokens = self._tokenize(whole_text)

        tokenized_elements = self._match_xml(tokens, elements)
        xml = ET.tostring(tokenized_elements[0].element, encoding="unicode").rstrip()

        tokens = [l.split("\t") for l in xml.split("\n")]
        if self.token_classes:
            if self.extra_info:
                return [t if len(t) == 3 else (t[0], None, None) for t in tokens]
            else:
                return [(t[0], t[1]) if len(t) == 3 else (t[0], None) for t in tokens]
        else:
            if self.extra_info:
                return [(t[0], t[2]) if len(t) == 3 else (t[0], None) for t in tokens]
            else:
                return [t[0] for t in tokens]
