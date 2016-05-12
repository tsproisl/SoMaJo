#!/usr/bin/env python3

import os
import random

import regex as re


class Tokenizer(object):
    def __init__(self, split_camel_case=False):
        """"""
        self.split_camel_case = split_camel_case
        self.unique_string_length = 7
        self.mapping = {}

        # TAGS, EMAILS, URLs
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

        # EMOTICONS
        # TODO: Peter, SMS von gestern Nacht -> hauptsächlich entities -> hilft nicht so wahnsinnig.
        emoticon_set = set(["(-.-)", "(T_T)", "(♥_♥)", ")':", ")-:",
                            "(-:", ")=", ")o:", ")x", ":'C", ":/",
                            ":<", ":C", ":[", "=(", "=)", "=D", "=P",
                            ">:", "D':", "D:", "\:", "]:", "x(", "^^",
                            "o.O", "oO", "\O/", "\m/", ":;))", "_))",
                            "*_*", "._.", ":wink:", ">_<", "*<:-)",
                            ":!:", ":;-))"])
        self.emoticon = re.compile(r"""(?:(?:[:;]|(?<!\d)8)           # a variery of eyes, alt.: [:;8]
                                        [-'oO]?                       # optional nose or tear
                                        (?: \)+ | \(+ | [*] | ([DPp])\1*(?!\w)))   # a variety of mouths
                                    """ +
                                   r"|" +
                                   r"(?:xD+|XD+)" +
                                   r"|" +
                                   r"(?<!\d[ ]|\d)\^3" +
                                   r"|" +
                                   r"|".join([re.escape(_) for _ in emoticon_set]), re.VERBOSE)
        self.space_emoticon = re.compile(r'([:;])[ ]([()])')

        # special tokens containing + or &
        tokens_with_plus_or_ampersand = self._read_abbreviation_file("tokens_with_plus_or_ampersand.txt")
        self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:\L<patokens>)(?!\w)", re.IGNORECASE, patokens=tokens_with_plus_or_ampersand)
        # self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:" + r"|".join([re.escape(_) for _ in tokens_with_plus_or_ampersand]) + r")(?!\w)")

        #camelCase
        self.emoji = re.compile(r'\bemoji[[:alpha:]]+\b')
        camel_case_token_set = self._read_abbreviation_file("camel_case_tokens.txt")
        # things like ImmobilienScout24.de are already covered by URL detection
        # self.camel_case_url = re.compile(r'\b(?:[[:upper:]][[:lower:][:digit:]]+){2,}\.(?:de|com|org|net|edu)\b')
        # self.camel_case_token = re.compile(r"\b(?:" + r"|".join([re.escape(_) for _ in camel_case_token_set]) + r"|Mac[[:upper:]][[:lower:]]*)\b")
        self.camel_case_token = re.compile(r"\b(?:\L<cctokens>|Mac[[:upper:]][[:lower:]]*)\b", cctokens=camel_case_token_set)
        self.in_and_innen = re.compile(r'\b[[:alpha:]]+[[:lower:]]In(?:nen)?[[:lower:]]*\b')
        self.camel_case = re.compile(r'(?<=[[:lower:]]{2,})([[:upper:]])(?![[:upper:]]|\b)')

        # ABBREVIATIONS
        self.single_letter_ellipsis = re.compile(r"(?<![\w.])(?P<a_letter>[[:alpha:]])(?P<b_ellipsis>\.{3})(?!\.)")
        self.and_cetera = re.compile(r"(?<![\w.&])&c\.(?![[:alpha:]]{1,3}\.)")
        self.str_abbreviations = re.compile(r'(?<![\w.])([[:alpha:]-]+-Str\.)(?![[:alpha:]])', re.IGNORECASE)
        self.nr_abbreviations = re.compile(r"(?<![\w.])(\w+\.-?Nr\.)(?![[:alpha:]]{1,3}\.)", re.IGNORECASE)
        self.single_letter_abbreviation = re.compile(r"(?<![\w.])[[:alpha:]]\.(?![[:alpha:]]{1,3}\.)")
        # abbreviations with multiple dots that constitute tokens
        single_token_abbreviation_set = self._read_abbreviation_file("single_token_abbreviations.txt")
        self.single_token_abbreviation = re.compile(r"(?<![\w.])(?:" + r'|'.join([re.escape(_) for _ in single_token_abbreviation_set]) + r')(?![[:alpha:]]{1,3}\.)')
        self.ps = re.compile(r"(?<!\d[ ]+)\bps\.", re.IGNORECASE)
        self.multipart_abbreviation = re.compile(r'(?:[[:alpha:]]+\.){2,}')
        # only abbreviations that are not matched by (?:[[:alpha:]]\.)+
        abbreviation_set = self._read_abbreviation_file("abbreviations.txt")
        self.abbreviation = re.compile(r"(?<![\w.])(?:" +
                                       r"(?:(?:[[:alpha:]]\.){2,})" +
                                       r"|" +
                                       r"(?i:" +    # this part should be case insensitive
                                       r'|'.join([re.escape(_) for _ in abbreviation_set]) +
                                       r"))+(?![[:alpha:]]{1,3}\.)", re.V1)

        # MENTIONS, HASHTAGS, ACTION WORDS
        self.mention_hashtag = re.compile(r'(?<!\w)[@#]\w+(?!\w)')
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
        self.measurement = re.compile(r'(?<!\w)(?P<a_amount>[−+-]?\d*[,.]?\d+)(?P<b_unit>(?:mm|cm|dm|m|km)(?:^?[23])?|qm|g|kg|min|h|s|sek|cent|eur)(?!\w)', re.IGNORECASE)
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
        self.slash = re.compile(r'(/+)(?!in(?:nen)?|en)')
        self.paired_double_latex_quote = re.compile(r"(?<!`)(``)([^`']+)('')(?!')")
        self.paired_single_latex_quote = re.compile(r"(?<!`)(`)([^`']+)(')(?!')")
        self.paired_single_quot_mark = re.compile(r"(['‚‘’])([^']+)(['‘’])")
        self.other_punctuation = re.compile(r'([<>%‰€$£₤¥°~*„“”‚‘"»«›‹,;:+=&–])')
        self.ellipsis = re.compile(r'\.{2,}|…+(?:\.{2,})?')
        self.dot_without_space = re.compile(r'(?<=[[:lower:]]{2})(\.)(?=[[:upper:]][[:lower:]]{2})')
        # self.dot = re.compile(r'(?<=[\w)])(\.)(?![\w])')
        self.dot = re.compile(r'(\.)')
        # Soft hyphen ­ „“

    def _read_abbreviation_file(self, filename):
        """Return the abbreviations from the given filename."""
        abbreviations = set()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line == "":
                    continue
                abbreviations.add(line)
        return abbreviations

    def _get_unique_string(self, text):
        """Return a string that is not a substring of text."""
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        # create random string of length self.unique_string_length
        unique_string = ""
        while unique_string in self.mapping or unique_string in text:
            unique_string = "".join(random.choice(alphabet) for _ in range(self.unique_string_length))
        return unique_string

    def _replace_regex(self, text, regex):
        """Replace instances of regex with unique strings and store
        replacements in mapping.

        """
        replacements = {}
        spans = set()
        for match in regex.finditer(text):
            instance = match.group(0)
            spans.add(match.span())
            # check if there are named subgroups
            if len(match.groupdict()) > 0:
                parts = [v for k, v in sorted(match.groupdict().items())]
                multipart = self._multipart_replace(text, instance, parts)
                replacements[instance] = multipart
            else:
                replacement = self._get_unique_string(text)
                self.mapping[replacement] = instance
                replacements[instance] = replacement
        for beginning, end in reversed(sorted(spans)):
            text = text[:beginning] + " " + replacements[text[beginning:end]] + " " + text[end:]
        return text

    def _reintroduce_instances(self, tokens):
        """Replace the unique strings with the original text."""
        tokens = [self.mapping.get(t, t) for t in tokens]
        return tokens

    def _replace_abbreviations(self, text):
        """Replace instances of abbreviations with unique strings and store
        replacements in self.mapping.

        """
        replacements = {}
        spans = set()
        text = self._replace_regex(text, self.single_letter_ellipsis)
        text = self._replace_regex(text, self.and_cetera)
        text = self._replace_regex(text, self.str_abbreviations)
        text = self._replace_regex(text, self.nr_abbreviations)
        text = self._replace_regex(text, self.single_letter_abbreviation)
        text = self._replace_regex(text, self.single_token_abbreviation)
        text = self._replace_regex(text, self.ps)
        for match in self.abbreviation.finditer(text):
            instance = match.group(0)
            spans.add(match.span())
            # check if it is a multipart abbreviation
            if self.multipart_abbreviation.fullmatch(instance):
                parts = [p.strip() + "." for p in instance.strip(".").split(".")]
                multipart = self._multipart_replace(text, instance, parts)
                replacements[instance] = multipart
            else:
                replacement = self._get_unique_string(text)
                self.mapping[replacement] = instance
                replacements[instance] = replacement
        for beginning, end in reversed(sorted(spans)):
            text = text[:beginning] + " " + replacements[text[beginning:end]] + " " + text[end:]
        return text

    def _multipart_replace(self, text, instance, parts):
        """"""
        replacements = []
        for part in parts:
            replacement = self._get_unique_string(text)
            self.mapping[replacement] = part
            replacements.append(replacement)
        multipart = " ".join(replacements)
        return multipart

    def tokenize(self, paragraph):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        # reset mappings for the current paragraph
        self.mapping = {}

        # XML tags are the only tokens that may contain spaces. We
        # first replace them with unique strings and undo that after
        # tokenizing the text.
        paragraph = self._replace_regex(paragraph, self.tag)

        # remove email addresses and urls
        paragraph = self._replace_regex(paragraph, self.email)
        paragraph = self._replace_regex(paragraph, self.simple_url_with_brackets)
        paragraph = self._replace_regex(paragraph, self.simple_url)
        paragraph = self._replace_regex(paragraph, self.doi)
        paragraph = self._replace_regex(paragraph, self.doi_with_space)
        paragraph = self._replace_regex(paragraph, self.url_without_protocol)
        # paragraph = self._replace_regex(paragraph, self.url)

        # remove spaces from certain emoticons
        paragraph = self.space_emoticon.sub(r'\1\2', paragraph)
        # replace emoticons with unique strings so that they are out
        # of the way
        paragraph = self._replace_regex(paragraph, self.emoticon)

        # mentions, hashtags
        paragraph = self._replace_regex(paragraph, self.mention_hashtag)
        # action words
        paragraph = self._replace_regex(paragraph, self.action_word)

        paragraph = self._replace_regex(paragraph, self.token_with_plus_ampersand)

        # camelCase
        if self.split_camel_case:
            paragraph = self._replace_regex(paragraph, self.emoji)
            # paragraph = self._replace_regex(paragraph, self.camel_case_url)
            paragraph = self._replace_regex(paragraph, self.camel_case_token)
            paragraph = self._replace_regex(paragraph, self.in_and_innen)
            paragraph = self.camel_case.sub(r' \1', paragraph)

        # remove known abbreviations
        paragraph = self._replace_abbreviations(paragraph)

        # DATES AND NUMBERS
        # dates
        paragraph = self._replace_regex(paragraph, self.three_part_date_year_first)
        paragraph = self._replace_regex(paragraph, self.three_part_date_dmy)
        paragraph = self._replace_regex(paragraph, self.three_part_date_mdy)
        paragraph = self._replace_regex(paragraph, self.two_part_date)
        # time
        paragraph = self._replace_regex(paragraph, self.time)
        # ordinals
        paragraph = self._replace_regex(paragraph, self.ordinal)
        # fractions
        paragraph = self._replace_regex(paragraph, self.fraction)
        # amounts (1.000,-)
        paragraph = self._replace_regex(paragraph, self.amount)
        # semesters
        paragraph = self._replace_regex(paragraph, self.semester)
        # measurements
        paragraph = self._replace_regex(paragraph, self.measurement)
        # number compunds
        paragraph = self._replace_regex(paragraph, self.number_compound)
        # numbers
        paragraph = self._replace_regex(paragraph, self.number)

        # (clusters of) question marks and exclamation marks
        paragraph = self.quest_exclam.sub(r' \1 ', paragraph)
        # arrows
        paragraph = self.space_right_arrow.sub(r'\1\2', paragraph)
        paragraph = self.space_left_arrow.sub(r'\1\2', paragraph)
        paragraph = self._replace_regex(paragraph, self.arrow)
        # @ symbol
        paragraph = paragraph.replace("@", " @")
        # parens
        paragraph = self.paired_paren.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paired_bracket.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paren.sub(r' \1 ', paragraph)
        # slash
        paragraph = self.slash.sub(r' \1 ', paragraph)
        # LaTeX-style quotation marks
        paragraph = self.paired_double_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        paragraph = self.paired_single_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        # single quotation marks, apostrophes
        paragraph = self.paired_single_quot_mark.sub(r' \1 \2 \3 ', paragraph)
        # other punctuation symbols
        paragraph = self.other_punctuation.sub(r' \1 ', paragraph)
        # ellipsis
        paragraph = self._replace_regex(paragraph, self.ellipsis)
        # dots
        paragraph = self.dot_without_space.sub(r' \1 ', paragraph)
        paragraph = self.dot.sub(r' \1 ', paragraph)

        # tokenize
        tokens = paragraph.strip().split()

        # reintroduce mapped tokens
        tokens = self._reintroduce_instances(tokens)

        return tokens
