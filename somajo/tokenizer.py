#!/usr/bin/env python3

import unicodedata
import warnings

import regex as re

from somajo import doubly_linked_list
from somajo import utils
from somajo.token import Token


class Tokenizer(object):

    supported_languages = set(["de", "en"])
    default_language = "de"

    def __init__(self, split_camel_case=False, token_classes=False, extra_info=False, language="de"):
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
        self.language = language if language in self.supported_languages else self.default_language
        self.unique_string_length = 7
        self.mapping = {}
        self.unique_prefix = None
        self.replacement_counter = 0

        self.spaces = re.compile(r"\s+")
        self.controls = re.compile(r"[\u0000-\u001F\u007F-\u009F]")
        self.stranded_variation_selector = re.compile(r" \uFE0F")
        # soft hyphen (00AD), zero-width space (200B), zero-width
        # non-joiner (200C), zero-width joiner (200D), Arabic letter
        # mark (061C), left-to-right mark (200E), right-to-left mark
        # (200F), word joiner (2060), left-to-right isolate (2066),
        # right-to-left isolate (2067), first strong isolate (2068),
        # pop directional isolate (2069), l-t-r/r-t-l embedding (202A,
        # 202B), l-t-r/r-t-l override (202D, 202E), pop directional
        # formatting (202C), zero-width no-break space (FEFF)
        self.other_nasties = re.compile(r"[\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]")
        # combination
        self.starts_with_junk = re.compile(r"^[\u0000-\u001F\u007F-\u009F\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]+")
        self.junk_next_to_space = re.compile(r"(?:^|\s)[\u0000-\u001F\u007F-\u009F\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]+|[\u0000-\u001F\u007F-\u009F\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]+(?:\s|$)")
        self.junk_between_spaces = re.compile(r"(?:^|\s+)[\s\u0000-\u001F\u007F-\u009F\u00AD\u061C\u200B-\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]+(?:\s+|$)")

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
        # self.email = re.compile(r"\b[\w.%+-]+@[\w.-]+\.\p{L}{2,}\b")
        self.email = re.compile(r"\b[\w.%+-]+(?:@| \[at\] )[\w.-]+(?:\.| \[?dot\]? )\p{L}{2,}\b")
        # simple regex for urls that start with http or www
        # TODO: schließende Klammer am Ende erlauben, wenn nach http etc. eine öffnende kam
        self.simple_url_with_brackets = re.compile(r'\b(?:(?:https?|ftp|svn)://|(?:https?://)?www\.)\S+?\(\S*?\)\S*(?=$|[\'. "!?,;])', re.IGNORECASE)
        self.simple_url = re.compile(r'\b(?:(?:https?|ftp|svn)://|(?:https?://)?www\.)\S+[^\'. "!?,;:)]', re.IGNORECASE)
        self.doi = re.compile(r'\bdoi:10\.\d+/\S+', re.IGNORECASE)
        self.doi_with_space = re.compile(r'(?<=\bdoi: )10\.\d+/\S+', re.IGNORECASE)
        # we also allow things like tagesschau.de-App
        self.url_without_protocol = re.compile(r'\b[\w./-]+\.(?:de|com|org|net|edu|info|gov|jpg|png|gif|log|txt|xlsx?|docx?|pptx?|pdf)(?:-\w+)?\b', re.IGNORECASE)
        self.reddit_links = re.compile(r'(?<!\w)/?[rlu](?:/\w+)+/?(?!\w)', re.IGNORECASE)

        # XML entities
        self.entity = re.compile(r"""&(?:
                                         quot|amp|apos|lt|gt  # named entities
                                         |
                                         #\d+                 # decimal entities
                                         |
                                         #x[0-9a-f]+          # hexadecimal entities
                                      );""", re.VERBOSE | re.IGNORECASE)

        # EMOTICONS
        emoticon_set = set(["(-.-)", "(T_T)", "(♥_♥)", ")':", ")-:",
                            "(-:", ")=", ")o:", ")x", ":'C", ":/",
                            ":<", ":C", ":[", "=(", "=)", "=D", "=P",
                            ">:", "\\:", "]:", "x(", "^^", "o.O",
                            "\\O/", "\\m/", ":;))", "_))", "*_*", "._.",
                            ":wink:", ">_<", "*<:-)", ":!:", ":;-))"])
        emoticon_list = sorted(emoticon_set, key=len, reverse=True)
        self.emoticon = re.compile(r"""(?:(?:[:;]|(?<!\d)8)           # a variety of eyes, alt.: [:;8]
                                        [-'oO]?                       # optional nose or tear
                                        (?: \)+ | \(+ | [*] | ([DPp])\1*(?!\w)))   # a variety of mouths
                                    """ +
                                   r"|" +
                                   r"(?:\b[Xx]D+\b)" +
                                   r"|" +
                                   r"(?:\b(?:D'?:|oO)\b)" +
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
        # U+FE0E..U+FE0F        text and emoji variation selectors
        # U+1F300..U+1F5FF	Miscellaneous Symbols and Pictographs
        # -> U+1F3FB..U+1F3FF   Emoji modifiers (skin tones)
        # U+1F600..U+1F64F	Emoticons
        # U+1F680..U+1F6FF	Transport and Map Symbols
        # U+1F900..U+1F9FF	Supplemental Symbols and Pictographs
        # self.unicode_symbols = re.compile(r"[\u2600-\u27BF\uFE0E\uFE0F\U0001F300-\U0001f64f\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]")
        self.unicode_flags = re.compile(r"\p{Regional_Indicator}{2}\uFE0F?")

        # special tokens containing + or &
        tokens_with_plus_or_ampersand = utils.read_abbreviation_file("tokens_with_plus_or_ampersand.txt")
        plus_amp_simple = [(pa, re.search(r"^\w+[&+]\w+$", pa)) for pa in tokens_with_plus_or_ampersand]
        self.simple_plus_ampersand = set([pa[0].lower() for pa in plus_amp_simple if pa[1]])
        self.simple_plus_ampersand_candidates = re.compile(r"\b\w+[&+]\w+\b")
        tokens_with_plus_or_ampersand = [pa[0] for pa in plus_amp_simple if not pa[1]]
        # self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:\L<patokens>)(?!\w)", re.IGNORECASE, patokens=tokens_with_plus_or_ampersand)
        self.token_with_plus_ampersand = re.compile(r"(?<!\w)(?:" + r"|".join([re.escape(_) for _ in tokens_with_plus_or_ampersand]) + r")(?!\w)", re.IGNORECASE)

        # camelCase
        self.emoji = re.compile(r'\bemojiQ\p{L}{3,}\b')
        camel_case_token_list = utils.read_abbreviation_file("camel_case_tokens.txt")
        cc_alnum = [(cc, re.search(r"^\w+$", cc)) for cc in camel_case_token_list]
        self.simple_camel_case_tokens = set([cc[0] for cc in cc_alnum if cc[1]])
        self.simple_camel_case_candidates = re.compile(r"\b\w*\p{Ll}\p{Lu}\w*\b")
        camel_case_token_list = [cc[0] for cc in cc_alnum if not cc[1]]
        # things like ImmobilienScout24.de are already covered by URL detection
        # self.camel_case_url = re.compile(r'\b(?:\p{Lu}[\p{Ll}\d]+){2,}\.(?:de|com|org|net|edu)\b')
        self.camel_case_token = re.compile(r"\b(?:" + r"|".join([re.escape(_) for _ in camel_case_token_list]) + r"|:Mac\p{Lu}\p{Ll}*)\b")
        # self.camel_case_token = re.compile(r"\b(?:\L<cctokens>|Mac\p{Lu}\p{Ll}*)\b", cctokens=camel_case_token_set)
        self.in_and_innen = re.compile(r'\b\p{L}+\p{Ll}In(?:nen)?\p{Ll}*\b')
        self.camel_case = re.compile(r'(?<=\p{Ll}{2})(\p{Lu})(?!\p{Lu}|\b)')

        # GENDER STAR
        self.gender_star = re.compile(r'\b\p{L}+\*in(?:nen)?\p{Ll}*\b', re.IGNORECASE)

        # ABBREVIATIONS
        self.single_letter_ellipsis = re.compile(r"(?<![\w.])(?P<a_letter>\p{L})(?P<b_ellipsis>\.{3})(?!\.)")
        self.and_cetera = re.compile(r"(?<![\w.&])&c\.(?!\p{L}{1,3}\.)")
        self.str_abbreviations = re.compile(r'(?<![\w.])([\p{L}-]+-Str\.)(?!\p{L})', re.IGNORECASE)
        self.nr_abbreviations = re.compile(r"(?<![\w.])(\w+\.-?Nr\.)(?!\p{L}{1,3}\.)", re.IGNORECASE)
        self.single_letter_abbreviation = re.compile(r"(?<![\w.])\p{L}\.(?!\p{L}{1,3}\.)")
        # abbreviations with multiple dots that constitute tokens
        single_token_abbreviation_list = utils.read_abbreviation_file("single_token_abbreviations_%s.txt" % self.language)
        self.single_token_abbreviation = re.compile(r"(?<![\w.])(?:" + r'|'.join([re.escape(_) for _ in single_token_abbreviation_list]) + r')(?!\p{L}{1,3}\.)', re.IGNORECASE)
        self.ps = re.compile(r"(?<!\d[ ])\bps\.", re.IGNORECASE)
        self.multipart_abbreviation = re.compile(r'(?:\p{L}+\.){2,}')
        # only abbreviations that are not matched by (?:\p{L}\.)+
        abbreviation_list = utils.read_abbreviation_file("abbreviations_%s.txt" % self.language)
        # abbrev_simple = [(a, re.search(r"^\p{L}{2,}\.$", a)) for a in abbreviation_list]
        # self.simple_abbreviations = set([a[0].lower() for a in abbrev_simple if a[1]])
        # self.simple_abbreviation_candidates = re.compile(r"(?<![\w.])\p{L}{2,}\.(?!\p{L}{1,3}\.)")
        # abbreviation_list = [a[0] for a in abbrev_simple if not a[1]]
        self.abbreviation = re.compile(r"(?<![\p{L}.])(?:" +
                                       r"(?:(?:\p{L}\.){2,})" +
                                       r"|" +
                                       # r"(?i:" +    # this part should be case insensitive
                                       r'|'.join([re.escape(_) for _ in abbreviation_list]) +
                                       # r"))+(?!\p{L}{1,3}\.)", re.V1)
                                       r")+(?!\p{L}{1,3}\.)", re.IGNORECASE)

        # MENTIONS, HASHTAGS, ACTION WORDS, UNDERLINE
        self.mention = re.compile(r'[@]\w+(?!\w)')
        self.hashtag = re.compile(r'(?<!\w)[#]\w+(?!\w)')
        self.action_word = re.compile(r'(?<!\w)(?P<a_open>[*+])(?P<b_middle>[^\s*]+)(?P<c_close>[*])(?!\w)')
        # a pair of underscores can be used to "underline" some text
        self.underline = re.compile(r"(?<!\w)(_)(\w[^_]+\w)(_)(?!\w)")

        # DATE, TIME, NUMBERS
        self.three_part_date_year_first = re.compile(r'(?<![\d.]) (?P<a_year>\d{4}) (?P<b_month_or_day>([/-])\d{1,2}) (?P<c_day_or_month>\3\d{1,2}) (?![\d.])', re.VERBOSE)
        self.three_part_date_dmy = re.compile(r'(?<![\d.]) (?P<a_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])([./-])) (?P<b_month>(?:0?[1-9]|1[0-2])\2) (?P<c_year>(?:\d\d){1,2}) (?![\d.])', re.VERBOSE)
        self.three_part_date_mdy = re.compile(r'(?<![\d.]) (?P<a_month>(?:0?[1-9]|1[0-2])([./-])) (?P<b_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])\2) (?P<c_year>(?:\d\d){1,2}) (?![\d.])', re.VERBOSE)
        self.two_part_date = re.compile(r'(?<![\d.]) (?P<a_day_or_month>\d{1,2}([./-])) (?P<b_day_or_month>\d{1,2}\2) (?![\d.])', re.VERBOSE)
        self.time = re.compile(r'(?<!\w)\d{1,2}(?:(?::\d{2}){1,2}){1,2}(?![\d:])')
        self.en_time = re.compile(r'(?<![\w])(?P<a_time>\d{1,2}(?:(?:[.:]\d{2})){0,2}) ?(?P<b_am_pm>(?:[ap]m\b|[ap]\.m\.(?!\w)))', re.IGNORECASE)
        self.en_us_phone_number = re.compile(r"(?<![\d-])(?:[2-9]\d{2}[/-])?\d{3}-\d{4}(?![\d-])")
        self.en_numerical_identifiers = re.compile(r"(?<![\d-])\d+-(?:\d+-)+\d+(?![\d-])|(?<![\d/])\d+/(?:\d+/)+\d+(?![\d/])")
        self.en_us_zip_code = re.compile(r"(?<![\d-])\d{5}-\d{4}(?![\d-])")
        self.ordinal = re.compile(r'(?<![\w.])(?:\d{1,3}|\d{5,}|[3-9]\d{3})\.(?!\d)')
        self.english_ordinal = re.compile(r'\b(?:\d+(?:,\d+)*)?(?:1st|2nd|3rd|\dth)\b')
        self.english_decades = re.compile(r"\b(?:[12]\d)?\d0['’]?s\b")
        self.fraction = re.compile(r'(?<!\w)\d+/\d+(?![\d/])')
        self.amount = re.compile(r'(?<!\w)(?:\d+[\d,.]*-)(?!\w)')
        self.semester = re.compile(r'(?<!\w)(?P<a_semester>[WS]S|SoSe|WiSe)(?P<b_jahr>\d\d(?:/\d\d)?)(?!\w)', re.IGNORECASE)
        self.measurement = re.compile(r'(?<!\w)(?P<a_amount>[−+-]?\d*[,.]?\d+) ?(?P<b_unit>(?:mm|cm|dm|m|km)(?:\^?[23])?|bit|cent|eur|f|ft|g|ghz|h|hz|kg|l|lb|min|ml|qm|s|sek)(?!\w)', re.IGNORECASE)
        # auch Web2.0
        self.number_compound = re.compile(r'(?<!\w) (?:\d+-?[\p{L}@][\p{L}@-]* | [\p{L}@][\p{L}@-]*-?\d+(?:\.\d)?) (?!\w)', re.VERBOSE)
        self.number = re.compile(r"""(?<!\w|\d[.,]?)
                                     (?:[−+-]?              # optional sign
                                       (?:\d*               # optional digits before decimal point
                                       [.,])?               # optional decimal point
                                       \d+                  # digits
                                       (?:[eE][−+-]?\d+)?   # optional exponent
                                       |
                                       \d{1,3}(?:[.]\d{3})+(?:,\d+)?  # dot for thousands, comma for decimals: 1.999,95
                                       |
                                       \d{1,3}(?:,\d{3})+(?:[.]\d+)?  # comma for thousands, dot for decimals: 1,999.95
                                       )
                                     (?![.,]?\d)""", re.VERBOSE)
        self.ipv4 = re.compile(r"(?<!\w|\d[.,]?)(?:\d{1,3}[.]){3}\d{1,3}(?![.,]?\d)")
        self.section_number = re.compile(r"(?<!\w|\d[.,]?)(?:\d+[.])+\d+[.]?(?![.,]?\d)")

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
        self.de_slash = re.compile(r'(/+)(?!in(?:nen)?|en)')
        # English possessive and contracted forms
        self.en_trailing_apos = re.compile(r"(?<!..in|')(['’])(?!\w)")
        self.en_dms = re.compile(r"(?<=\w)(['’][dms])\b", re.IGNORECASE)
        self.en_llreve = re.compile(r"(?<=\w)(['’](?:ll|re|ve))\b", re.IGNORECASE)
        self.en_not = re.compile(r"(?<=\w)(n['’]t)\b", re.IGNORECASE)
        en_twopart_contractions = [r"\b(a)(lot)\b", r"\b(gon)(na)\b", r"\b(got)(ta)\b", r"\b(lem)(me)\b",
                                   r"\b(out)(ta)\b", r"\b(wan)(na)\b", r"\b(c'm)(on)\b",
                                   r"\b(more)(['’]n)\b", r"\b(d['’])(ye)\b", r"(?<!\w)(['’]t)(is)\b",
                                   r"(?<!\w)(['’]t)(was)\b", r"\b(there)(s)\b", r"\b(i)(m)\b",
                                   r"\b(you)(re)\b", r"\b(he)(s)\b", r"\b(she)(s)\b",
                                   r"\b(ai)(nt)\b", r"\b(are)(nt)\b", r"\b(is)(nt)\b",
                                   r"\b(do)(nt)\b", r"\b(does)(nt)\b", r"\b(did)(nt)\b",
                                   r"\b(i)(ve)\b", r"\b(you)(ve)\b", r"\b(they)(ve)\b",
                                   r"\b(have)(nt)\b", r"\b(has)(nt)\b", r"\b(can)(not)\b",
                                   r"\b(ca)(nt)\b", r"\b(could)(nt)\b", r"\b(wo)(nt)\b",
                                   r"\b(would)(nt)\b", r"\b(you)(ll)\b", r"\b(let)(s)\b"]
        en_threepart_contractions = [r"\b(du)(n)(no)\b", r"\b(wha)(dd)(ya)\b", r"\b(wha)(t)(cha)\b", r"\b(i)('m)(a)\b"]
        # w/o, w/out, b/c, b/t, l/c, w/, d/c, u/s
        self.en_slash_words = re.compile(r"\b(?:w/o|w/out|b/t|l/c|b/c|d/c|u/s)\b|\bw/(?!\w)", re.IGNORECASE)
        # word--word
        self.en_double_hyphen = re.compile(r"(?<=\w)--+(?=\w)")
        self.en_twopart_contractions = [re.compile(contr, re.IGNORECASE) for contr in en_twopart_contractions]
        self.en_threepart_contractions = [re.compile(contr, re.IGNORECASE) for contr in en_threepart_contractions]
        # English hyphenated words
        if self.language == "en":
            nonbreaking_prefixes = utils.read_abbreviation_file("non-breaking_prefixes_%s.txt" % self.language)
            nonbreaking_suffixes = utils.read_abbreviation_file("non-breaking_suffixes_%s.txt" % self.language)
            nonbreaking_words = utils.read_abbreviation_file("non-breaking_hyphenated_words_%s.txt" % self.language)
            self.en_nonbreaking_prefixes = re.compile(r"(?<![\w-])(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_prefixes]) + r")-[\w-]+", re.IGNORECASE)
            self.en_nonbreaking_suffixes = re.compile(r"\b[\w-]+-(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_suffixes]) + r")(?![\w-])", re.IGNORECASE)
            self.en_nonbreaking_words = re.compile(r"\b(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_words]) + r")\b", re.IGNORECASE)
        self.en_hyphen = re.compile(r"(?<=\w)(-)(?=\w)")
        self.en_no = re.compile(r"\b(no\.)\s*(?=\d)", re.IGNORECASE)
        self.en_degree = re.compile(r"(?<=\d ?)°(?:F|C|Oe)\b", re.IGNORECASE)
        # quotation marks
        # L'Enfer, d'accord, O'Connor
        self.letter_apostrophe_word = re.compile(r"\b([dlo]['’]\p{L}+)\b", re.IGNORECASE)
        self.paired_double_latex_quote = re.compile(r"(?<!`)(``)([^`']+)('')(?!')")
        self.paired_single_latex_quote = re.compile(r"(?<!`)(`)([^`']+)(')(?!')")
        self.paired_single_quot_mark = re.compile(r"(['‚‘’])([^']+)(['‘’])")
        self.all_quote = re.compile(r"(?<=\s)(?:``|''|`|['‚‘’])(?=\s)")
        self.other_punctuation = re.compile(r'([#<>%‰€$£₤¥°@~*„“”‚‘"»«›‹,;:+×÷±≤≥=&–—])')
        self.en_quotation_marks = re.compile(r'([„“”‚‘’"»«›‹])')
        self.en_other_punctuation = re.compile(r'([#<>%‰€$£₤¥°@~*,;:+×÷±≤≥=&/–—-]+)')
        self.ellipsis = re.compile(r'\.{2,}|…+(?:\.{2,})?')
        self.dot_without_space = re.compile(r'(?<=\p{Ll}{2})(\.)(?=\p{Lu}\p{Ll}{2})')
        # self.dot = re.compile(r'(?<=[\w)])(\.)(?![\w])')
        self.dot = re.compile(r'(\.)')
        # Soft hyphen ­ „“

    def _split_on_boundaries(self, node, boundaries, token_class):
        """"""
        token_dll = node.list
        n = len(boundaries)
        prev_end = 0
        for i, (start, end) in enumerate(boundaries):
            lsa, msa = False, False
            left = node.value.text[prev_end:start]
            match = node.value.text[start:end]
            right = node.value.text[end:]
            if left.endswith(" "):
                lsa = True
            if right.startswith(" "):
                msa = True
            elif right == "":
                msa = node.value.space_after
            left = left.strip()
            right = right.strip()
            if left != "":
                token_dll.insert_left(Token(left, space_after=lsa), node)
            token_dll.insert_left(Token(match, locked=True, token_class=token_class, space_after=msa), node)
            if i == n - 1:
                if right != "":
                    token_dll.insert_left(Token(right, space_after=node.value.space_after), node)
            prev_end = end
        if n > 0:
            token_dll.remove(node)

    def _split_matches(self, regex, node, token_class="regular", split_named_subgroups=True):
        boundaries = []
        split_groups = split_named_subgroups and len(regex.groupindex) > 0
        group_numbers = sorted(regex.groupindex.values())
        for m in regex.finditer(node.value.text):
            if split_groups:
                for g in group_numbers:
                    start, end = m.span(g)
                    boundaries.append((start, end))
            else:
                start, end = m.span(0)
                boundaries.append((start, end))
        self._split_on_boundaries(node, boundaries, token_class)

    def _split_emojis(self, node, token_class="emoticon"):
        boundaries = []
        for m in re.finditer(r"\X", node.value.text):
            if m.end() - m.start() > 1:
                if re.search(r"[\p{Extended_Pictographic}\p{Emoji_Presentation}\uFE0F]", m.group()):
                    boundaries.append(m.span())
            else:
                if re.search(r"[\p{Extended_Pictographic}\p{Emoji_Presentation}]", m.group()):
                    boundaries.append(m.span())
        self._split_on_boundaries(node, boundaries, token_class)

    def _split_all_matches(self, regex, token_dll, token_class="regular", split_named_subgroups=True):
        """Turn matches for the regex into tokens."""
        for t in token_dll:
            if t.value.markup or t.value.locked:
                continue
            self._split_matches(regex, t, token_class, split_named_subgroups)

    def _split_all_emojis(self, token_dll, token_class="emoticon"):
        """Replace all emoji sequences"""
        for t in token_dll:
            if t.value.markup or t.value.locked:
                continue
            self._split_emojis(t, token_class)

    def _replace_abbreviations(self, text, split_multipart_abbrevs=True):
        """Replace instances of abbreviations with unique strings and store
        replacements in self.mapping.

        """
        replacements = {}
        text = self._replace_regex(text, self.single_letter_ellipsis, "abbreviation")
        text = self._replace_regex(text, self.and_cetera, "abbreviation")
        text = self._replace_regex(text, self.str_abbreviations, "abbreviation")
        text = self._replace_regex(text, self.nr_abbreviations, "abbreviation")
        text = self._replace_regex(text, self.single_token_abbreviation, "abbreviation")
        text = self._replace_regex(text, self.single_letter_abbreviation, "abbreviation")
        text = self.spaces.sub(" ", text)
        text = self._replace_regex(text, self.ps, "abbreviation")

        def repl(match):
            instance = match.group(0)
            if instance not in replacements:
                # check if it is a multipart abbreviation
                if split_multipart_abbrevs and self.multipart_abbreviation.fullmatch(instance):
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
        normalized = self.junk_between_spaces.sub(" ", original_text)
        normalized = self.spaces.sub(" ", normalized)
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
                            warnings.warn("Error aligning tokens with original text!\nOriginal text: '%s'\nToken: '%s'\nRemaining normalized text: '%s'\nValue of orig: '%s'" % (original_text, token, normalized, "".join(orig)))
                            break
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
            normalized = self.junk_between_spaces.sub(" ", original_text)
            normalized = self.spaces.sub(" ", normalized)
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
                    agenda.append(Token(token[len(normalized):].lstrip(), t.token_class))
                    token = normalized
                    normalized = ""
                else:
                    orig = []
                    processed = []
                    for char in token:
                        first_char = None
                        while first_char != char:
                            try:
                                first_char = normalized[0]
                                normalized = normalized[1:]
                                orig.append(first_char)
                            except IndexError:
                                warnings.warn("Error aligning tokens with original text!\nOriginal text: '%s'\nToken: '%s'\nRemaining normalized text: '%s'\nValue of orig: '%s'" % (original_text, token, normalized, "".join(orig)))
                                break
                        else:
                            processed.append(char)
                    if len(processed) != len(token):
                        agenda.append(Token(token[len(processed):].lstrip(), t.token_class))
                        token = token[:len(processed)]
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

    def _tokenize(self, token_dll):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        for t in token_dll:
            if t.value.markup or t.value.locked:
                continue
            # convert to Unicode normal form C (NFC)
            t.value.text = unicodedata.normalize("NFC", t.value.text)
            # normalize whitespace
            t.value.text = self.spaces.sub(" ", t.value.text)
            # get rid of control characters
            t.value.text = self.controls.sub("", t.value.text)
            # get rid of isolated variation selectors
            t.value.text = self.stranded_variation_selector.sub("", t.value.text)
            # normalize whitespace
            t.value.text = self.spaces.sub(" ", t.value.text)

        # Some tokens are allowed to contain whitespace. Get those out
        # of the way first.
        # - XML tags
        self._split_all_matches(self.xml_declaration, token_dll, "XML_tag")
        self._split_all_matches(self.tag, token_dll, "XML_tag")
        # - email address obfuscation may involve spaces
        self._split_all_matches(self.email, token_dll, "email_address")

        # Emoji sequences can contain zero-width joiners. Get them out
        # of the way next
        self._split_all_matches(self.unicode_flags, token_dll, "emoticon")
        self._split_all_emojis(token_dll, "emoticon")

        for t in token_dll:
            if t.value.markup or t.value.locked:
                continue
            # get rid of other junk characters
            t.value.text = self.other_nasties.sub("", t.value.text)
            # normalize whitespace
            t.value.text = self.spaces.sub(" ", t.value.text)
            # Some emoticons contain erroneous spaces. We fix this.
            t.value.text = self.space_emoticon.sub(r'\1\2', t.value.text)
            # Split on whitespace
            wt = t.value.text.split()
            n_wt = len(wt)
            for i, tok in enumerate(wt):
                if i == n_wt - 1:
                    token_dll.insert_left(Token(tok, space_after=t.value.space_after), t)
                else:
                    token_dll.insert_left(Token(tok, space_after=True), t)
            token_dll.remove(t)

        return token_dll

        # # urls
        # paragraph = self._replace_regex(paragraph, self.simple_url_with_brackets, "URL")
        # paragraph = self._replace_regex(paragraph, self.simple_url, "URL")
        # paragraph = self._replace_regex(paragraph, self.doi, "DOI")
        # paragraph = self._replace_regex(paragraph, self.doi_with_space, "DOI")
        # paragraph = self._replace_regex(paragraph, self.url_without_protocol, "URL")
        # paragraph = self._replace_regex(paragraph, self.reddit_links, "URL")
        # # paragraph = self._replace_regex(paragraph, self.url)

        # # XML entities
        # paragraph = self._replace_regex(paragraph, self.entity_name, "XML_entity")
        # paragraph = self._replace_regex(paragraph, self.entity_decimal, "XML_entity")
        # paragraph = self._replace_regex(paragraph, self.entity_hex, "XML_entity")

        # # replace emoticons with unique strings so that they are out
        # # of the way
        # paragraph = self.spaces.sub(" ", paragraph)
        # paragraph = self._replace_regex(paragraph, self.heart_emoticon, "emoticon")
        # paragraph = self._replace_regex(paragraph, self.emoticon, "emoticon")
        # # paragraph = self._replace_regex(paragraph, self.unicode_symbols, "emoticon")

        # # mentions, hashtags
        # paragraph = self._replace_regex(paragraph, self.mention, "mention")
        # paragraph = self._replace_regex(paragraph, self.hashtag, "hashtag")
        # # action words
        # paragraph = self._replace_regex(paragraph, self.action_word, "action_word")
        # # underline
        # paragraph = self.underline.sub(r' \1 \2 \3 ', paragraph)
        # # textual representations of emoji
        # paragraph = self._replace_regex(paragraph, self.emoji, "emoticon")

        # paragraph = self._replace_regex(paragraph, self.token_with_plus_ampersand)
        # paragraph = self._replace_set(paragraph, self.simple_plus_ampersand_candidates, self.simple_plus_ampersand, ignore_case=True)

        # # camelCase
        # if self.split_camel_case:
        #     paragraph = self._replace_regex(paragraph, self.camel_case_token)
        #     paragraph = self._replace_set(paragraph, self.simple_camel_case_candidates, self.simple_camel_case_tokens)
        #     paragraph = self._replace_regex(paragraph, self.in_and_innen)
        #     paragraph = self.camel_case.sub(r' \1', paragraph)

        # # gender star
        # paragraph = self._replace_regex(paragraph, self.gender_star)

        # # English possessive and contracted forms
        # if self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.english_decades, "number_compound")
        #     paragraph = self._replace_regex(paragraph, self.en_dms, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_llreve, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_not, "regular")
        #     paragraph = self.en_trailing_apos.sub(r' \1', paragraph)
        #     for contraction in self.en_twopart_contractions:
        #         paragraph = contraction.sub(r' \1 \2 ', paragraph)
        #     for contraction in self.en_threepart_contractions:
        #         paragraph = contraction.sub(r' \1 \2 \3 ', paragraph)
        #     paragraph = self._replace_regex(paragraph, self.en_no, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_degree, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_nonbreaking_words, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_nonbreaking_prefixes, "regular")
        #     paragraph = self._replace_regex(paragraph, self.en_nonbreaking_suffixes, "regular")

        # # remove known abbreviations
        # split_abbreviations = False if self.language == "en" else True
        # paragraph = self._replace_abbreviations(paragraph, split_multipart_abbrevs=split_abbreviations)

        # # DATES AND NUMBERS
        # # dates
        # split_dates = False if self.language == "en" else True
        # paragraph = self._replace_regex(paragraph, self.three_part_date_year_first, "date", split_named_subgroups=split_dates)
        # paragraph = self._replace_regex(paragraph, self.three_part_date_dmy, "date", split_named_subgroups=split_dates)
        # paragraph = self._replace_regex(paragraph, self.three_part_date_mdy, "date", split_named_subgroups=split_dates)
        # paragraph = self._replace_regex(paragraph, self.two_part_date, "date", split_named_subgroups=split_dates)
        # # time
        # if self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.en_time, "time")
        # paragraph = self._replace_regex(paragraph, self.time, "time")
        # # US phone numbers and ZIP codes
        # if self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.en_us_phone_number, "number")
        #     paragraph = self._replace_regex(paragraph, self.en_us_zip_code, "number")
        #     paragraph = self._replace_regex(paragraph, self.en_numerical_identifiers, "number")
        # # ordinals
        # if self.language == "de":
        #     paragraph = self._replace_regex(paragraph, self.ordinal, "ordinal")
        # elif self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.english_ordinal, "ordinal")
        # # fractions
        # paragraph = self._replace_regex(paragraph, self.fraction, "number")
        # # amounts (1.000,-)
        # paragraph = self._replace_regex(paragraph, self.amount, "amount")
        # # semesters
        # paragraph = self._replace_regex(paragraph, self.semester, "semester")
        # # measurements
        # paragraph = self._replace_regex(paragraph, self.measurement, "measurement")
        # # number compounds
        # paragraph = self._replace_regex(paragraph, self.number_compound, "number_compound")
        # # numbers
        # paragraph = self._replace_regex(paragraph, self.number, "number")
        # paragraph = self._replace_regex(paragraph, self.ipv4, "number")
        # paragraph = self._replace_regex(paragraph, self.section_number, "number")

        # # (clusters of) question marks and exclamation marks
        # paragraph = self._replace_regex(paragraph, self.quest_exclam, "symbol")
        # # arrows
        # paragraph = self.space_right_arrow.sub(r'\1\2', paragraph)
        # paragraph = self.space_left_arrow.sub(r'\1\2', paragraph)
        # paragraph = self._replace_regex(paragraph, self.arrow, "symbol")
        # # parens
        # paragraph = self.paired_paren.sub(r' \1 \2 \3 ', paragraph)
        # paragraph = self.paired_bracket.sub(r' \1 \2 \3 ', paragraph)
        # paragraph = self.paren.sub(r' \1 ', paragraph)
        # paragraph = self._replace_regex(paragraph, self.all_paren, "symbol")
        # # slash
        # if self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.en_slash_words, "regular")
        # if self.language == "de":
        #     paragraph = self._replace_regex(paragraph, self.de_slash, "symbol")
        # # O'Connor and French omitted vocals: L'Enfer, d'accord
        # paragraph = self._replace_regex(paragraph, self.letter_apostrophe_word, "regular")
        # # LaTeX-style quotation marks
        # paragraph = self.paired_double_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        # paragraph = self.paired_single_latex_quote.sub(r' \1 \2 \3 ', paragraph)
        # # single quotation marks, apostrophes
        # paragraph = self.paired_single_quot_mark.sub(r' \1 \2 \3 ', paragraph)
        # paragraph = self._replace_regex(paragraph, self.all_quote, "symbol")
        # # other punctuation symbols
        # # paragraph = self._replace_regex(paragraph, self.dividing_line, "symbol")
        # if self.language == "en":
        #     paragraph = self._replace_regex(paragraph, self.en_hyphen, "symbol")
        #     paragraph = self._replace_regex(paragraph, self.en_double_hyphen, "symbol")
        #     paragraph = self._replace_regex(paragraph, self.en_quotation_marks, "symbol")
        #     paragraph = self._replace_regex(paragraph, self.en_other_punctuation, "symbol")
        # else:
        #     paragraph = self._replace_regex(paragraph, self.other_punctuation, "symbol")
        # # ellipsis
        # paragraph = self._replace_regex(paragraph, self.ellipsis, "symbol")
        # # dots
        # # paragraph = self.dot_without_space.sub(r' \1 ', paragraph)
        # paragraph = self._replace_regex(paragraph, self.dot_without_space, "symbol")
        # # paragraph = self.dot.sub(r' \1 ', paragraph)
        # paragraph = self._replace_regex(paragraph, self.dot, "symbol")

        # # tokenize
        # tokens = paragraph.strip().split()

        # # reintroduce mapped tokens
        # tokens = self._reintroduce_instances(tokens)

        # return tokens

    def tokenize(self, paragraph):
        """An alias for tokenize_paragraph"""
        return self.tokenize_paragraph(paragraph)

    def tokenize_file(self, filename, parsep_empty_lines=True):
        """Tokenize file and yield tokenized paragraphs."""
        with open(filename) as f:
            if parsep_empty_lines:
                paragraphs = utils.get_paragraphs(f)
            else:
                paragraphs = (line for line in f if line.strip() != "")
            tokenized_paragraphs = map(self.tokenize_paragraph, paragraphs)
            for tp in tokenized_paragraphs:
                if tp:
                    yield tp

    def tokenize_paragraph(self, paragraph):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        token_dll = doubly_linked_list.DLL([Token(paragraph, first_in_sentence=True, last_in_sentence=True)])
        token_dll = self._tokenize(token_dll)
        return token_dll.to_list()
        # # convert paragraph to Unicode normal form C (NFC)
        # paragraph = unicodedata.normalize("NFC", paragraph)

        # tokens = self._tokenize(paragraph)

        # if len(tokens) == 0:
        #     return []

        # if self.extra_info:
        #     extra_info = self._check_spaces(tokens, paragraph)

        # tokens, token_classes = zip(*tokens)
        # if self.token_classes:
        #     if self.extra_info:
        #         return list(zip(tokens, token_classes, extra_info))
        #     else:
        #         return list(zip(tokens, token_classes))
        # else:
        #     if self.extra_info:
        #         return list(zip(tokens, extra_info))
        #     else:
        #         return list(tokens)

    def tokenize_xml(self, xml, is_file=True):
        """Tokenize XML file or XML string according to the guidelines of the
        EmpiriST 2015 shared task on automatic linguistic annotation
        of computer-mediated communication / social media.

        """
        token_dll = utils.parse_xml_to_token_dll(xml, is_file)
        self._tokenize(token_dll)
        return token_dll.to_list()
        # whole_text = " ".join((e.text for e in elements))

        # # convert paragraph to Unicode normal form C (NFC)
        # whole_text = unicodedata.normalize("NFC", whole_text)

        # tokens = self._tokenize(whole_text)

        # tokenized_elements = self._match_xml(tokens, elements)
        # xml = ET.tostring(tokenized_elements[0].element, encoding="unicode").rstrip()

        # tokens = [l.split("\t") for l in xml.split("\n")]
        # if self.token_classes:
        #     if self.extra_info:
        #         return [t if len(t) == 3 else (t[0], None, None) for t in tokens]
        #     else:
        #         return [(t[0], t[1]) if len(t) == 3 else (t[0], None) for t in tokens]
        # else:
        #     if self.extra_info:
        #         return [(t[0], t[2]) if len(t) == 3 else (t[0], None) for t in tokens]
        #     else:
        #         return [t[0] for t in tokens]
