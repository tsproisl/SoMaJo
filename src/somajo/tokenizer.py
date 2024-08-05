#!/usr/bin/env python3

import itertools
import logging
import operator
import unicodedata

import regex as re

from . import (
    doubly_linked_list,
    utils
)
from .token import Token


class Tokenizer():

    _supported_languages = {"de", "de_CMC", "en", "en_PTB"}
    _default_language = "de_CMC"

    def __init__(self, split_camel_case=False, token_classes=False, extra_info=False, language="de_CMC"):
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
        self.language = language if language in self._supported_languages else self.default_language

        self.spaces = re.compile(r"\s+")
        self.spaces_or_empty = re.compile(r"^\s*$")
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
        # no square brackets and spaces in URL: [^][ ]
        self.markdown_links = re.compile(r"""
                                             (?P<lsb>\[)                                             # [
                                             [^]]+                                                   # link description
                                             (?P<rsb>\])                                             # ]
                                             (?P<lrb>\()                                             # (
                                             (?:(?:(?:https?|ftp|svn)://|(?:https?://)?www\.)[^)]+)  # URL
                                             (?P<rrb>\))                                             # )
        """, re.VERBOSE | re.IGNORECASE)
        self.simple_url_with_brackets = re.compile(r"""
                                                       \b
                                                       (?:
                                                         (?:https?|ftp|svn)://
                                                         |
                                                         (?:https?://)?www\.
                                                       )
                                                       [^][<> ]+?
                                                       \(
                                                       \S*?
                                                       \)
                                                       [^][<> ]*
                                                       (?=$|[\'. "!?,;])
        """, re.VERBOSE | re.IGNORECASE)
        self.simple_url = re.compile(r"""
                                         \b
                                         (?:
                                           (?:https?|ftp|svn)://
                                           |
                                           (?:https?://)?www\.
                                         )
                                         [^][<> ]+                # no square or angle brackets
                                         [^][<>\'. "!?,;:()]      # last character
        """, re.VERBOSE | re.IGNORECASE)
        self.doi = re.compile(r'\bdoi:10\.\d+/\S+', re.IGNORECASE)
        self.doi_with_space = re.compile(r'(?<=\bdoi: )10\.\d+/\S+', re.IGNORECASE)
        # regex for ISBNs adapted from:
        # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s13.html
        self.isbn = re.compile(r"""\b
                                   (?:
                                     (?<=ISBN(?:-1[03])?:?[ ]?)  # Either preceded by ISBN identifier
                                     |                           # or,
                                     (?<![0-9][ -])              # if there is no ISBN identifier, not preceded by [0-9][ -].
                                   )
                                   (?:
                                     (?:[0-9]{9}[0-9X])          # ISBN-10 without separators.
                                     |
                                     (?:(?=[0-9X -]{13}\b)       # ISBN-10 with separators.
                                       [0-9]{1,5}([ -])          # 1-5 digit group identifier.
                                       [0-9]{1,7}\1              # Publisher identifier.
                                       [0-9]{1,7}\1              # Title identifier.
                                       [0-9X])                   # Check digit.
                                     |
                                     (?:97[89][0-9]{10})         # ISBN-13 without separators.
                                     |
                                     (?:(?=[0-9X -]{17}\b)       # ISBN-13 with separators
                                       97[89]([ -])              # ISBN-13 prefix.
                                       [0-9]{1,5}\2              # 1-5 digit group identifier.
                                       [0-9]{1,7}\2              # Publisher identifier.
                                       [0-9]{1,7}\2              # Title identifier.
                                       [0-9])                    # Check digit.
                                   )
                                   (?!\w|[ -][0-9])""", re.VERBOSE | re.IGNORECASE)
        # we also allow things like tagesschau.de-App
        self.url_without_protocol = re.compile(r'\b[\w./-]+\.(?:de|com|tv|me|net|us|org|at|cc|ly|be|ch|info|live|eu|edu|gov|jpg|png|gif|log|txt|xlsx?|docx?|pptx?|pdf)(?:-\w+)?\b', re.IGNORECASE)
        self.reddit_links = re.compile(r'(?<!\w)/?[rlu](?:/\w+)+/?(?!\w)', re.IGNORECASE)

        # XML entities
        self.entity = re.compile(r"""&(?:
                                         quot|amp|apos|lt|gt  # named entities
                                         |
                                         \#\d+                # decimal entities
                                         |
                                         \#x[0-9a-f]+         # hexadecimal entities
                                      );""", re.VERBOSE | re.IGNORECASE)

        # high priority single tokens
        single_token_list = utils.read_abbreviation_file(f"single_tokens_{self.language[:2]}.txt")
        self.single_tokens = re.compile(r"(?<![\w.])(?:" + r'|'.join([re.escape(_) for _ in single_token_list]) + r')(?!\p{L})', re.IGNORECASE)

        # EMOTICONS
        emoticon_set = {"(-.-)", "(T_T)", "(♥_♥)", ")':", ")-:",
                        "(-:", ")=", ")o:", ")x", ":'C", ":/", ":<",
                        ":C", ":[", "=(", "=)", "=D", "=P", ">:",
                        "\\:", "]:", "x(", "^^", "o.O", "\\O/",
                        "\\m/", ":;))", "_))", "*_*", "._.", ">_<",
                        "*<:-)", ":!:", ":;-))", "x'D", ":^)",
                        "(>_<)", ":->", "\\o/", "B-)", ":-$", "O:-)",
                        "=-O", ":O", ":-!", ":-x", ":-|", ":-\\",
                        ":-[", ">:-(", "^.^"}
        # From https://textfac.es/
        textfaces_space = {'⚆ _ ⚆', '˙ ͜ʟ˙', '◔ ⌣ ◔', '( ﾟヮﾟ)', '(• ε •)',
                           '(づ￣ ³￣)づ', '♪~ ᕕ(ᐛ)ᕗ', '\\ (•◡•) /', '( ಠ ͜ʖರೃ)',
                           '( ⚆ _ ⚆ )', '(▀̿Ĺ̯▀̿ ̿)', '༼ つ ◕_◕ ༽つ', '༼ つ ಥ_ಥ ༽つ',
                           '( ͡° ͜ʖ ͡°)', '( ͡°╭͜ʖ╮͡° )', '(╯°□°）╯︵ ┻━┻',
                           '( ͡ᵔ ͜ʖ ͡ᵔ )', '┬──┬ ノ( ゜-゜ノ)', '┬─┬ノ( º _ ºノ)',
                           '(ง ͠° ͟ل͜ ͡°)ง', '(͡ ͡° ͜ つ ͡͡°)', "﴾͡๏̯͡๏﴿ O'RLY?",
                           '（╯°□°）╯︵( .o.)', '(° ͡ ͜ ͡ʖ ͡ °)', '┬─┬ ︵ /(.□. ）',
                           '(/) (°,,°) (/)', '| (• ◡•)| (❍ᴥ❍ʋ)',
                           '༼ つ ͡° ͜ʖ ͡° ༽つ', '(╯°□°)╯︵ ʞooqǝɔɐɟ', '┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻',
                           '┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴', '(ó ì_í)=óò=(ì_í ò)',
                           '(•_•) ( •_•)>⌐■-■ (⌐■_■)', '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)',
                           '[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]', '/╲/\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\╱\\',
                           '( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)', '(._.) ( l: ) ( .-. ) ( :l ) (._.)',
                           "̿ ̿ ̿'̿'\\̵͇̿̿\\з=(•_•)=ε/̵͇̿̿/'̿'̿ ̿", '༼ ºل͟º ༼ ºل͟º ༼ ºل͟º ༽ ºل͟º ༽ ºل͟º ༽',
                           "̿'̿'\\̵͇̿̿\\з=( ͠° ͟ʖ ͡°)=ε/̵͇̿̿/'̿̿ ̿ ̿ ̿ ̿ ̿",
                           "̿̿ ̿̿ ̿̿ ̿'̿'\\̵͇̿̿\\з= ( ▀ ͜͞ʖ▀) =ε/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿",
                           # From Signal:
                           "ヽ(°◇° )ノ", "■-■¬ <(•_•)"}
        textfaces_emoji = {'♥‿♥', '☼.☼', '≧☉_☉≦', '(°ロ°)☝', '(☞ﾟ∀ﾟ)☞', '☜(˚▽˚)☞', '☜(⌒▽⌒)☞',
                           '(☞ຈل͜ຈ)☞', 'ヾ(⌐■_■)ノ♪', '(☞ﾟヮﾟ)☞', '☜(ﾟヮﾟ☜)'}
        textfaces_wo_emoji = {'=U', 'ಠ_ಠ', '◉_◉', 'ಥ_ಥ', ":')", 'ಠ⌣ಠ', 'ಠ~ಠ', 'ಠ_ಥ', 'ಠ‿↼',
                              'ʘ‿ʘ', 'ಠoಠ', 'ರ_ರ', '◔̯◔', '¬_¬', 'ب_ب', '°Д°', '^̮^', '^̮^', '^̮^',
                              '>_>', '^̮^', '^̮^', 'ಠ╭╮ಠ', '(>ლ)', 'ʕ•ᴥ•ʔ', '(ಥ﹏ಥ)', '(ᵔᴥᵔ)',
                              '(¬‿¬)', '⌐╦╦═─', '(•ω•)', '(¬_¬)', '｡◕‿◕｡', '(ʘ‿ʘ)', '٩◔̯◔۶',
                              '(>人<)', '(~_^)', '(^̮^)', '(･.◤)', '(◕‿◕✿)', '｡◕‿‿◕｡', '(─‿‿─)',
                              '(；一_一)', "(ʘᗩʘ')", '(✿´‿`)', 'ლ(ಠ益ಠლ)', '~(˘▾˘~)', '(~˘▾˘)~',
                              '(｡◕‿◕｡)', '(っ˘ڡ˘ς)', 'ლ(´ڡ`ლ)', 'ƪ(˘⌣˘)ʃ', '(´・ω・`)',
                              '(ღ˘⌣˘ღ)', '(▰˘◡˘▰)', '〆(・∀・＠)', '༼ʘ̚ل͜ʘ̚༽', 'ᕙ(⇀‸↼‶)ᕗ',
                              'ᕦ(ò_óˇ)ᕤ', '(｡◕‿‿◕｡)', 'ヽ༼ຈل͜ຈ༽ﾉ', '(ง°ل͜°)ง', '╚(ಠ_ಠ)=┐',
                              '(´・ω・)っ由', 'Ƹ̵̡Ӝ̵̨̄Ʒ', '¯\\_(ツ)_/¯', '▄︻̷̿┻̿═━一', "(ง'̀-'́)ง",
                              '¯\\(°_o)/¯', '｡゜(｀Д´)゜｡', '(づ｡◕‿‿◕｡)づ', '(;´༎ຶД༎ຶ`)',
                              '(ノಠ益ಠ)ノ彡┻━┻', 'ლ,ᔑ•ﺪ͟͠•ᔐ.ლ', '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧', '┬┴┬┴┤(･_├┬┴┬┴',
                              '[̲̅$̲̅(̲̅5̲̅)̲̅$̲̅]'}
        self.textfaces_space = re.compile(r"|".join([re.escape(_) for _ in sorted(textfaces_space, key=len, reverse=True)]))
        self.textfaces_emoji = re.compile(r"|".join([re.escape(_) for _ in sorted(textfaces_emoji, key=len, reverse=True)]))
        textfaces_signal = {"\\(ˆ˚ˆ)/", "(╥﹏╥)", "(╯°□°)╯︵", "┻━┻", "┬─┬", "ノ(°–°ノ)", "(^._.^)ﾉ", "ฅ^•ﻌ•^ฅ", "(•_•)", "(■_■¬)", "ƪ(ړײ)ƪ"}
        emoticon_list = sorted(emoticon_set | textfaces_wo_emoji | textfaces_signal, key=len, reverse=True)
        self.emoticon = re.compile(r"""(?:(?:[:;]|(?<!\d)8)           # a variety of eyes, alt.: [:;8]
                                        [-'oO]?                       # optional nose or tear
                                        (?: \)+ | \(+ | [*] | ([DPp])\1*(?!\w)))   # a variety of mouths
                                    """ +
                                   r"|" +
                                   r"(?:\b[Xx]D+\b)" +
                                   r"|" +
                                   r"(?:\b(?:D'?:|oO)\b)" +
                                   r"|" +
                                   r"(?:(?<!\b\d{1,2}):\w+:(?!\d{2}\b))" +   # Textual representations of emojis: :smile:, etc. We don't want to match times: 08:30:00
                                   r"|" +
                                   r"|".join([re.escape(_) for _ in emoticon_list]), re.VERBOSE)
        # Avoid matching phone numbers like "Tel: ( 0049)" or "Tel: (+49)"
        self.space_emoticon = re.compile(r"""([:;])                # eyes
                                             [ ]                   # space between eyes and mouth
                                             ([()])                # mouths
                                             (?![ ]?(?:00|[+])\d)  # not followed by, e.g., 0049 or +49 (issue #12)
                                          """, re.VERBOSE)
        # ^3 is an emoticon, unless it is preceded by a number (with
        # optional whitespace between number and ^3)
        # ^\^3               # beginning of line, no leading characters
        # ^\D\^3             # beginning of line, one leading character
        # (?<=\D[ ])\^3      # two leading characters, non-number + space
        # (?<=.[^\d ])\^3    # two leading characters, x + non-space-non-number
        # (?<=[<^]3[ ]?)\^3  # leading heart with optional space
        self.heart_emoticon = re.compile(r"(?:^|^\D|(?<=\D[ ])|(?<=.[^\d ])|(?<=[<^]3[ ]?))[<^]3(?!\d)")
        # U+2600..U+26FF	Miscellaneous Symbols
        # U+2700..U+27BF	Dingbats
        # U+FE0E..U+FE0F        text and emoji variation selectors
        # U+1F300..U+1F5FF	Miscellaneous Symbols and Pictographs
        # -> U+1F3FB..U+1F3FF   Emoji modifiers (skin tones)
        # U+1F600..U+1F64F	Emoticons
        # U+1F680..U+1F6FF	Transport and Map Symbols
        # U+1F900..U+1F9FF	Supplemental Symbols and Pictographs
        # self.unicode_symbols = re.compile(r"[\u2600-\u27BF\uFE0E\uFE0F\U0001F300-\U0001f64f\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]")
        self.symbols_and_dingbats = re.compile(r"[\u2600-\u27BF]")
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

        # GENDER MARKER
        self.gender_marker = re.compile(r'\b\p{L}+[*:/]in(?:nen)?\p{Ll}*\b', re.IGNORECASE)

        # ABBREVIATIONS
        self.single_letter_ellipsis = re.compile(r"(?<![\w.])(?P<a_letter>\p{L})(?P<b_ellipsis>\.{3})(?!\.)")
        self.and_cetera = re.compile(r"(?<![\w.&])&c\.(?!\p{L}{1,3}\.)")
        self.str_abbreviations = re.compile(r'(?<![\w.])([\p{L}-]+str\.)(?!\p{L})', re.IGNORECASE)
        self.nr_abbreviations = re.compile(r"(?<![\w.])(\w+\.-?Nr\.)(?!\p{L}{1,3}\.)", re.IGNORECASE)
        self.single_letter_abbreviation = re.compile(r"(?<![\w.])\p{L}\.(?!\p{L}{1,3}\.)")
        # abbreviations with multiple dots that constitute tokens
        single_token_abbreviation_list = utils.read_abbreviation_file(f"single_token_abbreviations_{self.language[:2]}.txt")
        self.single_token_abbreviation = re.compile(r"(?<![\w.])(?:" + r'|'.join([re.escape(_) for _ in single_token_abbreviation_list]) + r')(?!\p{L})', re.IGNORECASE)
        self.ps = re.compile(r"(?<!\d[ ])\bps\.", re.IGNORECASE)
        self.multipart_abbreviation = re.compile(r'(?:\p{L}+\.){2,}')
        # only abbreviations that are not matched by (?:\p{L}\.)+
        abbreviation_list = utils.read_abbreviation_file(f"abbreviations_{self.language[:2]}.txt", to_lower=True)
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
        self.artikel = re.compile(r"\bArt.(?=\s?\d)", re.IGNORECASE)

        # MENTIONS, HASHTAGS, ACTION WORDS, UNDERLINE
        self.mention = re.compile(r'[@]\w+(?!\w)')
        self.hashtag_sequence = re.compile(r'(?<!\w)(?:[#]\w(?:[\w-]*\w)?)+(?!\w)')
        self.single_hashtag = re.compile(r'[#]\w(?:[\w-]*\w)?(?!\w)')
        self.action_word = re.compile(r'(?<!\w)(?P<a_open>[*+])(?P<b_middle>[^\s*]+)(?P<c_close>[*])(?!\w)')
        # a pair of underscores can be used to "underline" some text
        self.underline = re.compile(r"(?<!\w)(?P<left>_)(?:\w[^_]+\w)(?P<right>_)(?!\w)")

        # DATE, TIME, NUMBERS
        self.three_part_date_year_first = re.compile(r'(?<![\d.]) (?P<a_year>\d{4}) (?P<b_month_or_day>([/-])\d{1,2}) (?P<c_day_or_month>\3\d{1,2}) (?!\d)', re.VERBOSE)
        self.three_part_date_dmy = re.compile(r'(?<![\d.]) (?P<a_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])([./-])) (?P<b_month>(?:0?[1-9]|1[0-2])\2) (?P<c_year>(?:\d\d){1,2}) (?!\d)', re.VERBOSE)
        self.three_part_date_mdy = re.compile(r'(?<![\d.]) (?P<a_month>(?:0?[1-9]|1[0-2])([./-])) (?P<b_day>(?:0?[1-9]|1[0-9]|2[0-9]|3[01])\2) (?P<c_year>(?:\d\d){1,2}) (?!\d)', re.VERBOSE)
        self.two_part_date = re.compile(r'(?<![\d.]) (?P<a_day_or_month>\d{1,2}([./-])) (?P<b_day_or_month>\d{1,2}\2) (?!\d)', re.VERBOSE)
        self.time = re.compile(r'(?<!\w)\d{1,2}(?:(?::\d{2}){1,2}){1,2}(?![\d:])')
        self.en_time = re.compile(r'(?<![\w])(?P<a_time>\d{1,2}(?:(?:[.:]\d{2})){0,2}) ?(?P<b_am_pm>(?:[ap]m\b|[ap]\.m\.(?!\w)))', re.IGNORECASE)
        self.en_us_phone_number = re.compile(r"(?<![\d-])(?:[2-9]\d{2}[/-])?\d{3}-\d{4}(?![\d-])")
        self.en_numerical_identifiers = re.compile(r"(?<![\d-])\d+-(?:\d+-)+\d+(?![\d-])|(?<![\d/])\d+/(?:\d+/)+\d+(?![\d/])")
        self.en_us_zip_code = re.compile(r"(?<![\d-])\d{5}-\d{4}(?![\d-])")
        self.ordinal = re.compile(r'(?<![\w.])(?:\d{1,3}|\d{5,}|[3-9]\d{3})\.(?!\d)')
        self.english_ordinal = re.compile(r'\b(?:\d+(?:,\d+)*)?(?:1st|2nd|3rd|\dth)\b')
        self.roman_ordinal = re.compile(r"\b(?=[MDCLXVI])M{0,4}(?:C[MD]|D?C{0,3})(?:X[CL]|L?X{0,3})(?:I[XV]|V?I{0,3})\.")
        self.english_decades = re.compile(r"\b(?:[12]\d)?\d0['’]?s\b")
        self.fraction = re.compile(r'(?<!\w)\d+/\d+(?![\d/])')
        fraction = r"""(?:
                         \d{1,2}/
                         (?:
                           (?:[1-9]|10)          # denominators 1–10
                           |
                           (?:\d{1,2}|100)/100           # denominator 100
                           |
                           (?:\d{1,3}|1000)/1000         # denominator 1000
                         )
                       )"""
        scientific_number = r"""(?:
                                  [−+-]?               # optional sign
                                  (?:\d*               # optional digits before decimal point
                                  [.,])?               # optional decimal point
                                  \d+                  # digits
                                  (?:[eE][−+-]?\d+)?   # optional exponent
                                )"""
        grouped_number = r"""(?:
                               \d{1,3}(?:[.]\d{3})+(?:,\d+)?  # dot for thousands, comma for decimals: 1.999,95
                               |
                               \d{1,3}(?:,\d{3})+(?:[.]\d+)?  # comma for thousands, dot for decimals: 1,999.95
                             )"""
        number = f"(?P<number>{fraction}|{scientific_number}|{grouped_number})"
        number_range = f"""(?:
                             (?P<frfrom>{fraction})(?P<frdash>[-–])(?P<frto>{fraction})
                             |
                             (?P<snfrom>{scientific_number})(?P<sndash>[-–])(?P<snto>{scientific_number})
                             |
                             (?P<gnfrom>{grouped_number})(?P<gndash>[-–])(?P<gnto>{grouped_number})
                           )"""
        self.number_range = re.compile(r"(?<!\w|\d[.,]?)" + number_range + r"(?![.,]?\d)", re.VERBOSE)
        self.calculation = re.compile(r"(?P<arg1>\d+(?:[,.]\d+)?)(?P<op>[+*x×÷−])(?P<arg2>\d+(?:[,.]\d+)?)")
        self.amount = re.compile(r'(?<!\w)(?:\d+[\d,.]*[,.]-)(?!\w)')
        self.semester = re.compile(r'(?<!\w)(?P<a_semester>[WS]S|SoSe|WiSe)(?P<b_jahr>\d\d(?:/\d\d)?)(?!\w)', re.IGNORECASE)
        units = utils.read_abbreviation_file("units.txt")
        self.measurement = re.compile(r"(?<!\w|\d[.,]?)" + f"(?:{number}|{number_range})[ ]?" + r"(?P<unit>" + r"|".join([re.escape(_) for _ in units]) + ")" + r"(?!\w)", re.IGNORECASE | re.VERBOSE)
        self.number_compound = re.compile(r'(?<!\w-?) (?:\d+-?[\p{L}@][\p{L}@-]*) (?!\w)', re.VERBOSE)
        self.number = re.compile(r"(?<!\w-?|\d[.,]?)" + number + r"(?![.,]?\d)", re.VERBOSE)
        self.ipv4 = re.compile(r"(?<!\w|\d[.,]?)(?:\d{1,3}[.]){3}\d{1,3}(?![.,]?\d)")
        self.section_number = re.compile(r"(?<!\w|\d[.,]?)(?:\d+[.])+\d+[.]?(?![.,]?\d)")

        # PUNCTUATION
        self.quest_exclam = re.compile(r"([!?]+)")
        # arrows
        self.arrow = re.compile(r'(-+[ ]?>|<[ ]?-+|[\u2190-\u21ff])')
        # parens
        self.all_parens = re.compile(r"""(
                                      (?:(?<=\w)        # alphanumeric character
                                        [(]             # opening paren
                                        (?!inn?[)])) |  # not followed by "in)" or "inn)"
                                      (?:(?<!\w)        # no alphanumeric character
                                        [(]) |          # opening paren
                                      (?:(?<!.[(]in|[(]inn)  # not preceded by "(in" or "(inn"
                                        [)]) |          # closing paren
                                        [][{}]           # curly and square brackets
                                      # (?:(?<!\w)        # no alphanumeric character
                                      #   [[{(]           # opening paren
                                      #   (?=\w)) |       # alphanumeric character
                                      # (?:(?<=\w)        # alphanumeric character
                                      #   []})]           # closing paren
                                      #   (?!\w)) |       # no alphanumeric character
                                      # (?:(?:(?<=\s)|^)  # space or start of string
                                      #   []})]           # closing paren
                                      #   (?=\w)) |       # alphanumeric character
                                      # (?:(?<=\w-)       # hyphen
                                      #   [)]             # closing paren
                                      #   (?=\w))         # alphanumeric character
                                    )""", re.VERBOSE | re.IGNORECASE)
        self.de_slash = re.compile(r'(/+)(?!in(?:nen)?|en)')
        # English possessive and contracted forms
        self.en_trailing_apos = re.compile(r"(?<=[sx])(['’])(?![\w'])")
        self.en_dms = re.compile(r"(?<=\w)(['’][dms])\b", re.IGNORECASE)
        self.en_llreve = re.compile(r"(?<=\w)(['’](?:ll|re|ve))\b", re.IGNORECASE)
        self.en_not = re.compile(r"(?<=\w)(n['’]t)\b", re.IGNORECASE)
        en_twopart_contractions = [r"\b(?P<p1>a)(?P<p2>lot)\b", r"\b(?P<p1>gon)(?P<p2>na)\b", r"\b(?P<p1>got)(?P<p2>ta)\b", r"\b(?P<p1>lem)(?P<p2>me)\b",
                                   r"\b(?P<p1>out)(?P<p2>ta)\b", r"\b(?P<p1>wan)(?P<p2>na)\b", r"\b(?P<p1>c'm)(?P<p2>on)\b",
                                   r"\b(?P<p1>more)(?P<p2>['’]n)\b", r"\b(?P<p1>d['’])(?P<p2>ye)\b", r"(?<!\w)(?P<p1>['’]t)(?P<p2>is)\b",
                                   r"(?<!\w)(?P<p1>['’]t)(?P<p2>was)\b", r"\b(?P<p1>there)(?P<p2>s)\b", r"\b(?P<p1>i)(?P<p2>m)\b",
                                   r"\b(?P<p1>you)(?P<p2>re)\b", r"\b(?P<p1>he)(?P<p2>s)\b", r"\b(?P<p1>she)(?P<p2>s)\b",
                                   r"\b(?P<p1>ai)(?P<p2>nt)\b", r"\b(?P<p1>are)(?P<p2>nt)\b", r"\b(?P<p1>is)(?P<p2>nt)\b",
                                   r"\b(?P<p1>do)(?P<p2>nt)\b", r"\b(?P<p1>does)(?P<p2>nt)\b", r"\b(?P<p1>did)(?P<p2>nt)\b",
                                   r"\b(?P<p1>i)(?P<p2>ve)\b", r"\b(?P<p1>you)(?P<p2>ve)\b", r"\b(?P<p1>they)(?P<p2>ve)\b",
                                   r"\b(?P<p1>have)(?P<p2>nt)\b", r"\b(?P<p1>has)(?P<p2>nt)\b", r"\b(?P<p1>can)(?P<p2>not)\b",
                                   r"\b(?P<p1>ca)(?P<p2>nt)\b", r"\b(?P<p1>could)(?P<p2>nt)\b", r"\b(?P<p1>wo)(?P<p2>nt)\b",
                                   r"\b(?P<p1>would)(?P<p2>nt)\b", r"\b(?P<p1>you)(?P<p2>ll)\b", r"\b(?P<p1>let)(?P<p2>s)\b"]
        en_threepart_contractions = [r"\b(?P<p1>du)(?P<p2>n)(?P<p3>no)\b", r"\b(?P<p1>wha)(?P<p2>dd)(?P<p3>ya)\b", r"\b(?P<p1>wha)(?P<p2>t)(?P<p3>cha)\b", r"\b(?P<p1>i)(?P<p2>'m)(?P<p3>a)\b"]
        # w/o, w/out, b/c, b/t, l/c, w/, d/c, u/s
        self.en_slash_words = re.compile(r"\b(?:w/o|w/out|b/t|l/c|b/c|d/c|u/s)\b|\bw/(?!\w)", re.IGNORECASE)
        # word--word
        self.en_twopart_contractions = [re.compile(contr, re.IGNORECASE) for contr in en_twopart_contractions]
        self.en_threepart_contractions = [re.compile(contr, re.IGNORECASE) for contr in en_threepart_contractions]
        # English hyphenated words
        if self.language == "en" or self.language == "en_PTB":
            nonbreaking_prefixes = utils.read_abbreviation_file(f"non-breaking_prefixes_{self.language[:2]}.txt")
            nonbreaking_suffixes = utils.read_abbreviation_file(f"non-breaking_suffixes_{self.language[:2]}.txt")
            nonbreaking_words = utils.read_abbreviation_file(f"non-breaking_hyphenated_words_{self.language[:2]}.txt")
            self.en_nonbreaking_prefixes = re.compile(r"(?<![\w-])(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_prefixes]) + r")-[\w-]+", re.IGNORECASE)
            self.en_nonbreaking_suffixes = re.compile(r"\b[\w-]+-(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_suffixes]) + r")(?![\w-])", re.IGNORECASE)
            self.en_nonbreaking_words = re.compile(r"\b(?:" + r'|'.join([re.escape(_) for _ in nonbreaking_words]) + r")\b", re.IGNORECASE)
        self.en_hyphen = re.compile(r"(?<=\w)-+(?=\w)")
        self.en_no = re.compile(r"\b(no\.)\s*(?=\d)", re.IGNORECASE)
        self.en_degree = re.compile(r"(?<=\d ?)°(?:F|C|Oe)\b", re.IGNORECASE)
        # quotation marks
        # L'Enfer, d'accord, O'Connor
        self.letter_apostrophe_word = re.compile(r"\b([dlo]['’]\p{L}+)\b", re.IGNORECASE)
        self.double_latex_quote = re.compile(r"(?:(?<!`)``(?!`))|(?:(?<!')''(?!'))")
        self.paired_single_latex_quote = re.compile(r"(?<!`)(?P<left>`)(?:[^`']+)(?P<right>')(?!')")
        self.paired_single_quot_mark = re.compile(r"(?<!\p{L})(?P<left>['])(?:[^']+)(?P<right>['])(?!\p{L})")
        # Musical notes, two programming languages
        self.letter_sharp = re.compile(r"\b[acdfg]#(?:-\p{L}+)?(?!\w)", re.IGNORECASE)
        self.other_punctuation = re.compile(r'([#<>%‰€$£₤¥°@~*„“”‚‘"»«›‹,;:+×÷±≤≥=&–—])')
        self.en_quotation_marks = re.compile(r'([„“”‚‘’"»«›‹])')
        self.en_other_punctuation = re.compile(r'([#<>%‰€$£₤¥°@~*,;:+×÷±≤≥=&/–—-]+)')
        self.ellipsis = re.compile(r'\.{2,}|…+(?:\.{2,})?')
        self.dot_without_space = re.compile(r'(?<=\p{Ll}{2})(\.)(?=\p{Lu}\p{Ll}{2})')
        # self.dot = re.compile(r'(?<=[\w)])(\.)(?![\w])')
        self.dot = re.compile(r'(\.)')
        # Soft hyphen ­ „“

    def _split_on_boundaries(self, node, boundaries, token_class, *, lock_match=True, delete_whitespace=False):
        """"""
        n = len(boundaries)
        if n == 0:
            return
        token_dll = node.list
        prev_end = 0
        for i, (start, end, replacement) in enumerate(boundaries):
            original_spelling = None
            left_space_after, match_space_after = False, False
            left = node.value.text[prev_end:start]
            match = node.value.text[start:end]
            if replacement is not None:
                if match != replacement:
                    original_spelling = match
                    match = replacement
            right = node.value.text[end:]
            prev_end = end
            if left.endswith(" ") or match.startswith(" "):
                left_space_after = True
            if match.endswith(" ") or right.startswith(" "):
                match_space_after = True
            elif right == "":
                match_space_after = node.value.space_after
            left = left.strip()
            match = match.strip()
            right = right.strip()
            if delete_whitespace:
                match_wo_spaces = match.replace(" ", "")
                if match_wo_spaces != match:
                    if original_spelling is None:
                        original_spelling = match
                    match = match_wo_spaces
            first_in_sentence, match_last_in_sentence, right_last_in_sentence = False, False, False
            if i == 0:
                first_in_sentence = node.value.first_in_sentence
            if i == n - 1:
                match_last_in_sentence = node.value.last_in_sentence
                if right != "":
                    match_last_in_sentence = False
                    right_last_in_sentence = node.value.last_in_sentence
            if left != "":
                token_dll.insert_left(Token(left, token_class="regular", space_after=left_space_after, first_in_sentence=first_in_sentence), node)
                first_in_sentence = False
            token_dll.insert_left(Token(match, locked=lock_match,
                                        token_class=token_class,
                                        space_after=match_space_after,
                                        original_spelling=original_spelling,
                                        first_in_sentence=first_in_sentence,
                                        last_in_sentence=match_last_in_sentence),
                                  node)
            if i == n - 1 and right != "":
                token_dll.insert_left(Token(right, token_class="regular", space_after=node.value.space_after, last_in_sentence=right_last_in_sentence), node)
        token_dll.remove(node)

    def _split_matches(self, regex, node, token_class="regular", repl=None, split_named_subgroups=True, delete_whitespace=False):
        boundaries = []
        split_groups = split_named_subgroups and len(regex.groupindex) > 0
        group_numbers = sorted(regex.groupindex.values())
        for m in regex.finditer(node.value.text):
            if split_groups:
                for g in group_numbers:
                    if m.span(g) != (-1, -1):
                        boundaries.append((m.start(g), m.end(g), None))
            else:
                if repl is None:
                    boundaries.append((m.start(), m.end(), None))
                else:
                    boundaries.append((m.start(), m.end(), m.expand(repl)))
        self._split_on_boundaries(node, boundaries, token_class, delete_whitespace=delete_whitespace)

    def _split_emojis(self, node, token_class="emoticon"):
        boundaries = []
        for m in re.finditer(r"\X", node.value.text):
            if m.end() - m.start() > 1:
                if re.search(r"[\p{Extended_Pictographic}\p{Emoji_Presentation}\uFE0F]", m.group()):
                    boundaries.append((m.start(), m.end(), None))
            else:
                if re.search(r"[\p{Extended_Pictographic}\p{Emoji_Presentation}]", m.group()):
                    boundaries.append((m.start(), m.end(), None))
        self._split_on_boundaries(node, boundaries, token_class)

    def _split_set(self, regex, node, items, token_class="regular", to_lower=False):
        boundaries = []
        for m in regex.finditer(node.value.text):
            instance = m.group(0)
            if to_lower:
                instance = instance.lower()
            if instance in items:
                boundaries.append((m.start(), m.end(), None))
        self._split_on_boundaries(node, boundaries, token_class)

    def _split_left(self, regex, node):
        boundaries = []
        prev_end = 0
        for m in regex.finditer(node.value.text):
            boundaries.append((prev_end, m.start(), None))
            prev_end = m.start()
        self._split_on_boundaries(node, boundaries, token_class=None, lock_match=False)

    def _split_all_matches(self, regex, token_dll, token_class="regular", *, repl=None, split_named_subgroups=True, delete_whitespace=False):
        """Turn matches for the regex into tokens."""
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            self._split_matches(regex, t, token_class, repl, split_named_subgroups, delete_whitespace)

    def _split_all_matches_in_match(self, regex1, regex2, token_dll, token_class="regular", *, delete_whitespace=False):
        """Find all matches for regex1 and turn all matches for regex2 within
        the matches for regex1 into tokens.

        """
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            boundaries = []
            for m1 in regex1.finditer(t.value.text):
                for m2 in regex2.finditer(m1.group(0)):
                    boundaries.append((m2.start() + m1.start(), m2.end() + m1.start(), None))
            self._split_on_boundaries(t, boundaries, token_class, delete_whitespace=delete_whitespace)

    def _split_all_emojis(self, token_dll, token_class="emoticon"):
        """Replace all emoji sequences"""
        self._split_all_matches(self.textfaces_emoji, token_dll, "emoticon")
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            self._split_emojis(t, token_class)

    def _split_all_set(self, token_dll, regex, items, token_class="regular", to_lower=False):
        """Turn all elements from items into separate tokens. Note: All
        elements need to be matched by regex. Optionally lowercase the
        matches before the comparison. Note: to_lower does not modify
        the elements of items, i.e. setting to_lower=True only makes
        sense if the elements of items are already in lowercase.

        """
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            self._split_set(regex, t, items, token_class, to_lower)

    def _split_all_left(self, regex, token_dll):
        """Split to the left of the match."""
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            self._split_left(regex, t)

    def _split_abbreviations(self, token_dll, split_multipart_abbrevs=True):
        """Turn instances of abbreviations into tokens."""
        self._split_all_matches(self.single_letter_ellipsis, token_dll, "abbreviation")
        self._split_all_matches(self.and_cetera, token_dll, "abbreviation")
        self._split_all_matches(self.str_abbreviations, token_dll, "abbreviation")
        self._split_all_matches(self.nr_abbreviations, token_dll, "abbreviation")
        self._split_all_matches(self.single_token_abbreviation, token_dll, "abbreviation")
        self._split_all_matches(self.single_letter_abbreviation, token_dll, "abbreviation")
        self._split_all_matches(self.ps, token_dll, "abbreviation")

        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            boundaries = []
            for m in self.abbreviation.finditer(t.value.text):
                instance = m.group(0)
                if split_multipart_abbrevs and self.multipart_abbreviation.fullmatch(instance):
                    start, end = m.span(0)
                    s = start
                    for i, c in enumerate(instance, start=1):
                        if c == ".":
                            boundaries.append((s, start + i, None))
                            s = start + i
                else:
                    boundaries.append((m.start(), m.end(), None))
            self._split_on_boundaries(t, boundaries, "abbreviation")

    def _remove_empty_tokens(self, token_dll):
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            if self.spaces_or_empty.search(t.value.text):
                if t.value.first_in_sentence:
                    next_non_markup = token_dll.next_matching(t, operator.attrgetter("value.markup"), False)
                    if next_non_markup is not None:
                        next_non_markup.value.first_in_sentence = True
                if t.value.last_in_sentence:
                    previous_non_markup = token_dll.previous_matching(t, operator.attrgetter("value.markup"), False)
                    if previous_non_markup is not None:
                        previous_non_markup.value.last_in_sentence = True
                token_dll.remove(t)

    def _tokenize(self, token_dll):
        """Tokenize paragraph (may contain newlines) according to the
        guidelines of the EmpiriST 2015 shared task on automatic
        linguistic annotation of computer-mediated communication /
        social media.

        """
        for t in token_dll:
            # convert to Unicode normal form C (NFC)
            t.value.text = unicodedata.normalize("NFC", t.value.text)
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
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

        # Emoji sequences can contain zero-width joiners. Get them out
        # of the way next
        # First textfaces that contain whitespace:
        self._split_all_matches(self.textfaces_space, token_dll, "emoticon")
        # Then flags:
        self._split_all_matches(self.unicode_flags, token_dll, "emoticon")
        # Then all other emojis
        self._split_all_emojis(token_dll, "emoticon")

        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            # get rid of other junk characters
            t.value.text = self.other_nasties.sub("", t.value.text)
            # normalize whitespace
            t.value.text = self.spaces.sub(" ", t.value.text)

        # Remove empty tokens
        self._remove_empty_tokens(token_dll)

        # Some emoticons contain erroneous spaces. We fix this.
        self._split_all_matches(self.space_emoticon, token_dll, "emoticon", repl=r'\1\2')
        # obfuscated email addresses can contain spaces
        self._split_all_matches(self.email, token_dll, "email_address", delete_whitespace=True)

        # urls
        self._split_all_matches(self.markdown_links, token_dll, "symbol")
        self._split_all_matches(self.simple_url_with_brackets, token_dll, "URL")
        self._split_all_matches(self.simple_url, token_dll, "URL")
        self._split_all_matches(self.doi, token_dll, "URL")
        self._split_all_matches(self.doi_with_space, token_dll, "URL")
        self._split_all_matches(self.url_without_protocol, token_dll, "URL")
        self._split_all_matches(self.reddit_links, token_dll, "URL")

        # XML entities
        self._split_all_matches(self.entity, token_dll, "XML_entity")

        # high priority single tokens
        self._split_all_matches(self.single_tokens, token_dll)

        # emoticons
        self._split_all_matches(self.heart_emoticon, token_dll, "emoticon")
        self._split_all_matches(self.emoticon, token_dll, "emoticon")
        self._split_all_matches(self.symbols_and_dingbats, token_dll, "emoticon")

        # mentions, hashtags
        self._split_all_matches(self.mention, token_dll, "mention")
        self._split_all_matches_in_match(self.hashtag_sequence, self.single_hashtag, token_dll, "hashtag")
        # action words
        self._split_all_matches(self.action_word, token_dll, "action_word")
        # underline
        self._split_all_matches(self.underline, token_dll)
        # textual representations of emoji
        self._split_all_matches(self.emoji, token_dll, "emoticon")

        # tokens with + or &
        self._split_all_matches(self.token_with_plus_ampersand, token_dll)
        self._split_all_set(token_dll, self.simple_plus_ampersand_candidates, self.simple_plus_ampersand, to_lower=True)

        # camelCase
        if self.split_camel_case:
            self._split_all_matches(self.camel_case_token, token_dll)
            self._split_all_set(token_dll, self.simple_camel_case_candidates, self.simple_camel_case_tokens)
            self._split_all_matches(self.in_and_innen, token_dll)
            self._split_all_left(self.camel_case, token_dll)

        # gender marker
        self._split_all_matches(self.gender_marker, token_dll)

        # English possessive and contracted forms
        if self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.english_decades, token_dll, "regular")
            self._split_all_matches(self.en_dms, token_dll)
            self._split_all_matches(self.en_llreve, token_dll)
            self._split_all_matches(self.en_not, token_dll)
            self._split_all_left(self.en_trailing_apos, token_dll)
            for contraction in self.en_twopart_contractions:
                self._split_all_matches(contraction, token_dll)
            for contraction in self.en_threepart_contractions:
                self._split_all_matches(contraction, token_dll)
            self._split_all_matches(self.en_no, token_dll)
            self._split_all_matches(self.en_degree, token_dll)
            self._split_all_matches(self.en_nonbreaking_words, token_dll)
            self._split_all_matches(self.en_nonbreaking_prefixes, token_dll)
            self._split_all_matches(self.en_nonbreaking_suffixes, token_dll)

        # measurements
        self._split_all_matches(self.measurement, token_dll, "measurement")
        # remove known abbreviations
        split_abbreviations = False if self.language == "en" or self.language == "en_PTB" else True
        self._split_abbreviations(token_dll, split_multipart_abbrevs=split_abbreviations)
        self._split_all_matches(self.artikel, token_dll, "abbreviation")

        # DATES AND NUMBERS
        self._split_all_matches(self.isbn, token_dll, "number", delete_whitespace=True)
        # dates
        split_dates = False if self.language == "en" or self.language == "en_PTB" else True
        self._split_all_matches(self.three_part_date_year_first, token_dll, "date", split_named_subgroups=split_dates)
        self._split_all_matches(self.three_part_date_dmy, token_dll, "date", split_named_subgroups=split_dates)
        self._split_all_matches(self.three_part_date_mdy, token_dll, "date", split_named_subgroups=split_dates)
        self._split_all_matches(self.two_part_date, token_dll, "date", split_named_subgroups=split_dates)
        # time
        if self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.en_time, token_dll, "time")
        self._split_all_matches(self.time, token_dll, "time")
        # US phone numbers and ZIP codes
        if self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.en_us_phone_number, token_dll, "number")
            self._split_all_matches(self.en_us_zip_code, token_dll, "number")
            self._split_all_matches(self.en_numerical_identifiers, token_dll, "number")
        # ordinals
        if self.language == "de" or self.language == "de_CMC":
            self._split_all_matches(self.ordinal, token_dll, "ordinal")
        elif self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.english_ordinal, token_dll, "ordinal")
        self._split_all_matches(self.roman_ordinal, token_dll, "ordinal")
        # number ranges
        self._split_all_matches(self.number_range, token_dll, "number", split_named_subgroups=True)
        # fractions
        self._split_all_matches(self.fraction, token_dll, "number")
        # calculations
        self._split_all_matches(self.calculation, token_dll, "number")
        # amounts (1.000,-)
        self._split_all_matches(self.amount, token_dll, "amount")
        # semesters
        self._split_all_matches(self.semester, token_dll, "semester")
        # measurements
        # self._split_all_matches(self.measurement, token_dll, "measurement")
        # number compounds
        self._split_all_matches(self.number_compound, token_dll, "regular")
        # numbers
        self._split_all_matches(self.number, token_dll, "number")
        self._split_all_matches(self.ipv4, token_dll, "number")
        self._split_all_matches(self.section_number, token_dll, "number")

        # (clusters of) question marks and exclamation marks
        self._split_all_matches(self.quest_exclam, token_dll, "symbol")
        # arrows
        self._split_all_matches(self.arrow, token_dll, "symbol", delete_whitespace=True)
        # parens
        self._split_all_matches(self.all_parens, token_dll, "symbol")
        # slash
        if self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.en_slash_words, token_dll, "regular")
        if self.language == "de" or self.language == "de_CMC":
            self._split_all_matches(self.de_slash, token_dll, "symbol")
        # O'Connor and French omitted vocals: L'Enfer, d'accord
        self._split_all_matches(self.letter_apostrophe_word, token_dll)
        # LaTeX-style quotation marks
        self._split_all_matches(self.double_latex_quote, token_dll, "symbol")
        self._split_all_matches(self.paired_single_latex_quote, token_dll, "symbol")
        # single quotation marks, apostrophes
        self._split_all_matches(self.paired_single_quot_mark, token_dll, "symbol")
        # other punctuation symbols
        # paragraph = self._replace_regex(paragraph, self.dividing_line, "symbol")
        self._split_all_matches(self.letter_sharp, token_dll, "regular")
        if self.language == "en" or self.language == "en_PTB":
            self._split_all_matches(self.en_hyphen, token_dll, "symbol")
            self._split_all_matches(self.en_quotation_marks, token_dll, "symbol")
            self._split_all_matches(self.en_other_punctuation, token_dll, "symbol")
        else:
            self._split_all_matches(self.other_punctuation, token_dll, "symbol")
        # ellipsis
        self._split_all_matches(self.ellipsis, token_dll, "symbol")
        # dots
        self._split_all_matches(self.dot_without_space, token_dll, "symbol")
        self._split_all_matches(self.dot, token_dll, "symbol")

        # Split on whitespace
        for t in token_dll:
            if t.value.markup or t.value._locked:
                continue
            wt = t.value.text.split()
            n_wt = len(wt)
            for i, tok in enumerate(wt):
                if i == n_wt - 1:
                    token_dll.insert_left(Token(tok, token_class="regular", space_after=t.value.space_after), t)
                else:
                    token_dll.insert_left(Token(tok, token_class="regular", space_after=True), t)
                token_dll.remove(t)

        return token_dll.to_list()

    def _convert_to_legacy(self, tokens):
        if self.token_classes and self.extra_info:
            tokens = [(t.text, t.token_class, t.extra_info) for t in tokens]
        elif self.token_classes:
            tokens = [(t.text, t.token_class) for t in tokens]
        elif self.extra_info:
            tokens = [(t.text, t.extra_info) for t in tokens]
        else:
            tokens = [t.text for t in tokens]
        return tokens

    def tokenize(self, paragraph):
        """An alias for tokenize_paragraph"""
        logging.warning("Since version 2.0.0, somajo.Tokenizer.tokenize() is deprecated. Please use somajo.SoMaJo.tokenize_text() instead. For more details see https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md")
        return self.tokenize_paragraph(paragraph)

    def tokenize_file(self, filename, parsep_empty_lines=True):
        """Tokenize utf-8-encoded text file and yield tokenized paragraphs."""
        logging.warning("Since version 2.0.0, somajo.Tokenizer.tokenize_file() is deprecated. Please use somajo.SoMaJo.tokenize_text_file() instead. For more details see https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md")
        with open(filename, encoding="utf-8") as f:
            parsep = "single_newlines"
            if parsep_empty_lines:
                parsep = "empty_lines"
            paragraph_info = utils.get_paragraphs_str(f, paragraph_separator=parsep)
            paragraphs = (pi[0] for pi in paragraph_info)
            paragraphs = (paragraph for paragraph, position in paragraphs)
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
        logging.warning("Since version 2.0.0, somajo.Tokenizer.tokenize_paragraph() is deprecated. Please use somajo.SoMaJo.tokenize_text() instead. For more details see https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md")
        token_dll = doubly_linked_list.DLL([Token(paragraph, first_in_sentence=True, last_in_sentence=True)])
        tokens = self._tokenize(token_dll)
        return self._convert_to_legacy(tokens)

    def tokenize_xml(self, xml, is_file=True, eos_tags=None):
        """Tokenize XML file or XML string according to the guidelines of the
        EmpiriST 2015 shared task on automatic linguistic annotation
        of computer-mediated communication / social media.

        """
        logging.warning("Since version 2.0.0, somajo.Tokenizer.tokenize_xml() is deprecated. Please use somajo.SoMaJo.tokenize_xml() instead. For more details see https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md")
        chunk_info = utils.xml_chunk_generator(xml, is_file, eos_tags)
        chunk_lists = (ci[0] for ci in chunk_info)
        token_dlls = map(doubly_linked_list.DLL, chunk_lists)
        tokens = map(self._tokenize, token_dlls)
        tokens = map(utils.escape_xml_tokens, tokens)
        tokens = map(self._convert_to_legacy, tokens)
        return list(itertools.chain.from_iterable(tokens))
