#!/usr/bin/env python3

import itertools
import logging
import unittest

from somajo import Tokenizer
from somajo.doubly_linked_list import DLL
from somajo.token import Token
from somajo import utils


class TestTokenizer(unittest.TestCase):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True)

    def _equal(self, raw, tokenized):
        """"""
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        dll = DLL([Token(raw, first_in_sentence=True, last_in_sentence=True)])
        tokens = self.tokenizer._tokenize(dll)
        self.assertEqual([t.text for t in tokens], tokenized)

    def _equal_xml(self, raw, tokenized):
        """"""
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        eos_tags = "title h1 h2 h3 h4 h5 h6 p br hr div ol ul dl table".split()
        eos_tags = set(eos_tags)
        chunk_info = utils.xml_chunk_generator(raw, is_file=False, eos_tags=eos_tags)
        chunk_lists = (ci[0] for ci in chunk_info)
        token_dlls = map(DLL, chunk_lists)
        chunks = map(self.tokenizer._tokenize, token_dlls)
        complete = list(itertools.chain.from_iterable(chunks))
        complete = utils.escape_xml_tokens(complete)
        self.assertEqual([t.text for t in complete], tokenized)


class TestEnglishTokenizer(TestTokenizer):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="en_PTB", split_camel_case=True)
        
class TestCustomTokenizer(TestTokenizer):
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(language="de_CMC", split_camel_case=True,custom_abbreviations=['Brem.','GBl.'])


class TestTokenizerDeprecated(TestTokenizer):
    def _equal(self, raw, tokenized):
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        with self.assertLogs(level=logging.WARN):
            tokens = self.tokenizer.tokenize_paragraph(raw)
        self.assertEqual(tokens, tokenized)

    def _equal_xml(self, raw, tokenized):
        if isinstance(tokenized, str):
            tokenized = tokenized.split()
        with self.assertLogs(level=logging.WARN):
            tokens = self.tokenizer.tokenize_xml(raw, is_file=False)
        self.assertEqual(tokens, tokenized)


class TestGuidelines(TestTokenizer):
    """Test cases taken from the EmpiriST tokenization guidelines:
    https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxlbXBpcmlzdDIwMTV8Z3g6M2Y3MDlkYmQzMDk4NzFlZA

    Function names: test_<category>_<page><n>

    """

    def test_punctuation_0201(self):
        self._equal("Als ich ihn sah, war es bereits zu spät.", "Als ich ihn sah , war es bereits zu spät .")

    def test_punctuation_0601(self):
        self._equal("Das hab ich mich auch schon gefragt...", "Das hab ich mich auch schon gefragt ...")

    def test_punctuation_0602(self):
        self._equal("Das ist ein Test?!", "Das ist ein Test ?!")

    def test_punctuation_0603(self):
        self._equal("bh's", "bh's")

    def test_punctuation_0701(self):
        self._equal("mit'm Fahrrad", "mit'm Fahrrad")

    def test_punctuation_0702(self):
        self._equal("des Virus'", "des Virus'")

    @unittest.expectedFailure
    def test_punctuation_0703(self):
        self._equal("du bist echt ein a...", "du bist echt ein a...")

    @unittest.expectedFailure
    def test_punctuation_0704(self):
        self._equal("f*** you!", "f*** you !")

    def test_punctuation_0705(self):
        self._equal("Test.......", "Test .......")

    def test_punctuation_0706(self):
        self._equal("Test????????", "Test ????????")

    def test_punctuation_0707(self):
        self._equal("Test!!!", "Test !!!")

    def test_punctuation_0708(self):
        self._equal("Test?!?!?!", "Test ?!?!?!")

    def test_punctuation_0801(self):
        self._equal("In der 2....", "In der 2. ...")

    def test_punctuation_0802(self):
        self._equal("Test....????!!!!", "Test .... ????!!!!")

    def test_punctuation_0803(self):
        self._equal("Laub- und Nadelbäume", "Laub- und Nadelbäume")

    def test_punctuation_0804(self):
        self._equal("Hals-Nasen-Ohren-Arzt", "Hals-Nasen-Ohren-Arzt")

    def test_punctuation_0901(self):
        self._equal("10%", "10 %")

    def test_punctuation_0902(self):
        self._equal("200€", "200 €")

    def test_punctuation_0903(self):
        self._equal("§§48", "§§ 48")

    def test_punctuation_0904(self):
        self._equal("11+21=33", "11 + 21 = 33")

    def test_punctuation_0905(self):
        self._equal("Avril_Lavigne", "Avril_Lavigne")

    @unittest.expectedFailure
    def test_punctuation_0906(self):
        self._equal("+s", "+s")

    def test_punctuation_0907(self):
        self._equal("-v", "-v")

    def test_punctuation_1001(self):
        self._equal("f->d", "f -> d")

    def test_punctuation_1001a(self):
        self._equal("f→d", "f → d")

    def test_punctuation_1002(self):
        self._equal("f - > d", "f -> d")

    @unittest.expectedFailure
    def test_punctuation_1003(self):
        self._equal("/ig schdöbbs", "/ig schdöbbs")

    def test_punctuation_1004(self):
        self._equal("(Neu-)Veröffentlichung", "( Neu- ) Veröffentlichung")

    def test_punctuation_1005(self):
        self._equal("Student(inn)en", "Student(inn)en")

    def test_punctuation_1101(self):
        self._equal("StudentInnen", "StudentInnen")

    def test_punctuation_1102(self):
        self._equal("Student/innen", "Student/innen")

    def test_punctuation_1103(self):
        self._equal("Experten/Expertinnen", "Experten / Expertinnen")

    def test_punctuation_1104(self):
        self._equal("(“normale”/saisonale) Grippe", "( “ normale ” / saisonale ) Grippe")

    def test_punctuation_1105(self):
        self._equal("Vitamin C-Mangel", "Vitamin C-Mangel")

    def test_punctuation_1106(self):
        self._equal("Magen- Darm- Erkrankung", "Magen- Darm- Erkrankung")

    def test_punctuation_1201(self):
        self._equal("Oster-„Beckerei“", "Oster- „ Beckerei “")

    def test_punctuation_1202(self):
        self._equal("i-„Pott“", "i- „ Pott “")

    def test_sumtimedate_1301(self):
        self._equal("6.200", "6.200")

    def test_sumtimedate_1302(self):
        self._equal("6.200,-", "6.200,-")

    def test_sumtimedate_1303(self):
        self._equal("das dauert 2:40 std.", "das dauert 2:40 std.")

    def test_sumtimedate_1304(self):
        self._equal("-1,5", "-1,5")

    def test_sumtimedate_1304a(self):
        """Unicode minus sign"""
        self._equal("−1,5", "−1,5")

    def test_sumtimedate_1305(self):
        self._equal("1/2 h", "1/2 h")

    def test_sumtimedate_1306(self):
        self._equal("1 / 2 h", "1 / 2 h")

    def test_sumtimedate_1307(self):
        self._equal("14:00–18:00", "14:00 – 18:00")

    def test_sumtimedate_1401(self):
        self._equal("14–18 Uhr", "14 – 18 Uhr")

    def test_sumtimedate_1402(self):
        self._equal("1-3 Semester", "1 - 3 Semester")

    def test_sumtimedate_1403(self):
        self._equal("30-50kg", "30 - 50 kg")

    def test_sumtimedate_1404(self):
        self._equal("ca. 20°C", "ca. 20 ° C")

    def test_sumtimedate_1404a(self):
        self._equal("ca. 20 °C", "ca. 20 ° C")

    def test_sumtimedate_1405(self):
        self._equal("ca. 20 GHz", "ca. 20 GHz")

    @unittest.expectedFailure
    def test_sumtimedate_1406(self):
        self._equal("4-11mal", "4 - 11mal")

    def test_sumtimedate_1501(self):
        self._equal("16.07.2013", "16. 07. 2013")

    def test_sumtimedate_1502(self):
        self._equal("16. Juli 2013", "16. Juli 2013")

    def test_sumtimedate_1502a(self):
        self._equal("(am 20.06.2008)", "( am 20. 06. 2008 )")

    def test_sumtimedate_1503(self):
        self._equal("21/07/1980", "21/ 07/ 1980")

    def test_sumtimedate_1503a(self):
        self._equal("2016-01-27", "2016 -01 -27")

    def test_sumtimedate_1503b(self):
        self._equal("01-27-2016", "01- 27- 2016")

    def test_sumtimedate_1504(self):
        self._equal("Weimarer Klassik", "Weimarer Klassik")

    def test_sumtimedate_1505(self):
        self._equal("Hälfte des XIX Jh. = Anfang 1796", "Hälfte des XIX Jh. = Anfang 1796")

    def test_sumtimedate_1601(self):
        self._equal("WS04", "WS 04")

    def test_sumtimedate_1601a(self):
        self._equal("WS15/16", "WS 15/16")

    def test_sumtimedate_1602(self):
        self._equal("24-stündig", "24-stündig")

    def test_abbreviations_1603(self):
        self._equal("etc.", "etc.")

    def test_abbreviations_1604(self):
        self._equal("d.h.", "d. h.")

    def test_abbreviations_1605(self):
        self._equal("d. h.", "d. h.")

    def test_abbreviations_1606(self):
        self._equal("o.ä.", "o. ä.")

    def test_abbreviations_1607(self):
        self._equal("u.dgl.", "u. dgl.")

    def test_abbreviations_1608(self):
        self._equal("u. dgl.", "u. dgl.")

    def test_abbreviations_1609(self):
        self._equal("std.", "std.")

    def test_abbreviations_1610(self):
        self._equal("Mat.-Nr.", "Mat.-Nr.")

    def test_abbreviations_1611(self):
        self._equal("Wir kauften Socken, Hemden, Schuhe etc. Danach hatten wir alles.", "Wir kauften Socken , Hemden , Schuhe etc. Danach hatten wir alles .")

    def test_abbreviations_1701(self):
        self._equal("zB", "zB")

    def test_abbreviations_1702(self):
        self._equal("Zeitschr.titel", "Zeitschr.titel")

    def test_abbreviations_1703(self):
        self._equal("A9", "A9")

    def test_abbreviations_1704(self):
        self._equal("cu Peter", "cu Peter")

    def test_abbreviations_1705(self):
        self._equal("Bruce Springsteen aka The Boss", "Bruce Springsteen aka The Boss")

    def test_typos_1801(self):
        self._equal("die stehen da schona ber ohne preise", "die stehen da schona ber ohne preise")

    def test_typos_1802(self):
        self._equal("tag quaki : )", "tag quaki :)")

    def test_typos_1901(self):
        self._equal("Ich hab da noch maldrüber nachgedacht", "Ich hab da noch maldrüber nachgedacht")

    def test_typos_1902(self):
        self._equal("Anna,kannst du mal", "Anna , kannst du mal")

    @unittest.expectedFailure
    def test_typos_1903(self):
        self._equal("handfest un direkt- so sind se...die Pottler", "handfest un direkt - so sind se ... die Pottler")

    def test_typos_1904(self):
        self._equal("Warst du vom Zeugnis überraschtß", "Warst du vom Zeugnis überraschtß")

    def test_contractions_2001(self):
        self._equal("stimmt’s", "stimmt’s")

    def test_contractions_2002(self):
        self._equal("waren’s", "waren’s")

    def test_camel_case_2101(self):
        self._equal("Zu welchemHandlungsbereich gehört unsereKomm hier? Bildung?Freizeit?Mischung?", "Zu welchem Handlungsbereich gehört unsere Komm hier ? Bildung ? Freizeit ? Mischung ?")

    def test_camel_case_2102(self):
        self._equal("derText", "der Text")

    def test_camel_case_2103(self):
        self._equal("PepsiCo", "PepsiCo")

    def test_tags_2104(self):
        self._equal('eine <A target="_blank" href="https://en.wikipedia.org/w/index.php?tit-le=Talk:PRISM_(surveillance_program)&oldid=559238329#Known_Counter_Measures_deleted_.21">umfangreiche Diskussion</A> zu diesem Abschnitt', ['eine', '<A target="_blank" href="https://en.wikipedia.org/w/index.php?tit-le=Talk:PRISM_(surveillance_program)&oldid=559238329#Known_Counter_Measures_deleted_.21">', 'umfangreiche', 'Diskussion', '</A>', 'zu', 'diesem', 'Abschnitt'])

    def test_emails_urls_2201(self):
        self._equal("michael.beisswenger@tu-dortmund.de", "michael.beisswenger@tu-dortmund.de")

    def test_emails_urls_2202(self):
        self._equal("https://en.wikipedia.org/wiki/Main_Page", "https://en.wikipedia.org/wiki/Main_Page")

    def test_emails_urls_2203(self):
        self._equal("http://www.shortnews.de", "http://www.shortnews.de")

    def test_emails_urls_2203a(self):
        self._equal("Auf http://www.shortnews.de, der besten Seite.", "Auf http://www.shortnews.de , der besten Seite .")

    def test_emails_urls_2203b(self):
        self._equal("Auf www.shortnews.de, der besten Seite.", "Auf www.shortnews.de , der besten Seite .")

    def test_emails_urls_2204(self):
        self._equal("shortnews.de", "shortnews.de")

    def test_emails_urls_2204a(self):
        self._equal("Auf shortnews.de, der besten Seite.", "Auf shortnews.de , der besten Seite .")

    def test_emoticons_2205(self):
        self._equal(":-)", ":-)")

    def test_emoticons_2206(self):
        self._equal(":-)))))", ":-)))))")

    def test_emoticons_2207(self):
        self._equal(";-)", ";-)")

    def test_emoticons_2208(self):
        self._equal(":)", ":)")

    def test_emoticons_2209(self):
        self._equal(";)", ";)")

    def test_emoticons_2301(self):
        self._equal(":-(", ":-(")

    def test_emoticons_2302(self):
        self._equal("8)", "8)")

    def test_emoticons_2303(self):
        self._equal(":D", ":D")

    def test_emoticons_2304(self):
        self._equal("^^", "^^")

    def test_emoticons_2305(self):
        self._equal("o.O", "o.O")

    def test_emoticons_2306(self):
        self._equal("oO", "oO")

    def test_emoticons_2307(self):
        self._equal("\\O/", "\\O/")

    def test_emoticons_2308(self):
        self._equal("\\m/", "\\m/")

    def test_emoticons_2309(self):
        self._equal(":;))", ":;))")

    def test_emoticons_2310(self):
        self._equal("_))", "_))")

    def test_emoticons_2311(self):
        self._equal("tag quaki : )", "tag quaki :)")

    def test_emoticons_2311a(self):
        self._equal("hallo peter ; )", "hallo peter ;)")

    def test_emoticons_2312(self):
        self._equal("Das hab ich auch schon gehört (find ich super :-)", "Das hab ich auch schon gehört ( find ich super :-)")

    def test_actions_2401(self):
        self._equal("*grübel*", "* grübel *")

    def test_actions_2402(self):
        self._equal("*auf locher rumhüpf & konfetti mach*", "* auf locher rumhüpf & konfetti mach *")

    def test_actions_2501(self):
        self._equal("*dichmalganzdolleknuddelt*", "* dichmalganzdolleknuddelt *")

    def test_actions_2502(self):
        self._equal("immer noch nicht fassen kann", "immer noch nicht fassen kann")

    def test_actions_2503(self):
        self._equal("quakirenntdemflöppymitdeneiswürfelnnach*", "quakirenntdemflöppymitdeneiswürfelnnach *")

    def test_actions_2504(self):
        self._equal("+s*", "+ s *")

    def test_actions_2505(self):
        self._equal("*danachdenraminmeinenrechnereinbau*G*", "* danachdenraminmeinenrechnereinbau * G *")

    def test_actions_2601(self):
        self._equal("quaki knuddelt Thor", "quaki knuddelt Thor")

    def test_addressing_2602(self):
        self._equal("@bine23", "@bine23")

    def test_addressing_2603(self):
        self._equal("@alle", "@alle")

    def test_addressing_2604(self):
        self._equal("winke@bochum", "winke @bochum")

    def test_addressing_2605(self):
        self._equal("@bine23: hallöchen! :-)", "@bine23 : hallöchen ! :-)")

    def test_hashtags_2701(self):
        self._equal("#urlaub", "#urlaub")

    def test_hashtags_2702(self):
        self._equal("#SPD", "#SPD")


class TestWhitespace(TestTokenizer):
    def test_whitespace_01(self):
        # self.assertEqual(self.tokenizer.tokenize_text("Petra und Simone gehen ins Kino"), "Petra und Simone gehen ins Kino".split())
        self._equal("Petra und Simone gehen ins Kino", "Petra und Simone gehen ins Kino")

    def test_whitespace_02(self):
        # newline
        self._equal("foo\nbar", "foo bar")

    def test_whitespace_03(self):
        # Unicode line separator (2028)
        self._equal("foo\u2028bar", "foo bar")

    def test_whitespace_04(self):
        # Unicode paragraph separator (2029)
        self._equal("foo\u2029bar", "foo bar")


class TestJunk(TestTokenizer):
    def test_junk_01(self):
        # zero width space
        self._equal("foo​bar", "foobar")

    def test_junk_02(self):
        # soft hyphen
        self._equal("foo­bar", "foobar")

    def test_junk_03(self):
        # zero-width no-break space (FEFF)
        self._equal("foo\ufeffbar", "foobar")

    def test_junk_04(self):
        # control characters
        self._equal("foobarbazquxalphabetagamma", "foobarbazquxalphabetagamma")

    def test_junk_05(self):
        # zero width joiner and non-joiner
        self._equal("foo‌bar‍baz", "foobarbaz")

    def test_junk_06(self):
        # left-to-right and right-to-left mark
        self._equal("foo‏bar‎baz", "foobarbaz")

    def test_junk_07(self):
        # More left-to-right and right-to-left stuff
        self._equal("foo\u202bbar\u202abaz\u202cqux\u202ealpha\u202dbeta", "foobarbazquxalphabeta")

    def test_junk_08(self):
        # line separator and paragraph separator
        self._equal("foo bar baz", "foo bar baz")

    def test_junk_09(self):
        # word joiner
        self._equal("foo⁠bar", "foobar")

    def test_junk_10(self):
        self._equal("[Alt] + 240 =­\n", "[ Alt ] + 240 =")

    def test_junk_11(self):
        self._equal("[Alt] + 240 =\n", "[ Alt ] + 240 =")

    def test_junk_12(self):
        self._equal("foo­ bar", "foo bar")

    def test_junk_13(self):
        self._equal("foo­", "foo")

    def test_junk_14(self):
        self._equal("Vgl. Schott, E., Markt und Geschäftsbeziehung beim Outsourcing ­\n", "Vgl. Schott , E. , Markt und Geschäftsbeziehung beim Outsourcing")

    def test_junk_15(self):
        self._equal("foo ­ ​ bar", "foo bar")

    def test_junk_16(self):
        self._equal("­ \n­", [])


class TestXML(TestTokenizer):
    def test_tags_01(self):
        self._equal("<?xml version='1.0' encoding='US-ASCII' standalone='yes' ?>", ["<?xml version='1.0' encoding='US-ASCII' standalone='yes' ?>"])

    def test_tags_02(self):
        self._equal('<?xml version="1.0" encoding="UTF-8"?>', ['<?xml version="1.0" encoding="UTF-8"?>'])

    def test_entities_01(self):
        self._equal("&amp;", "&amp;")

    def test_entities_02(self):
        self._equal("&#x2fb1;", "&#x2fb1;")

    def test_entities_03(self):
        self._equal("&#75;", "&#75;")

    def test_entities_04(self):
        self._equal("foo&amp;bar", "foo &amp; bar")

    def test_entities_05(self):
        self._equal("&lt;", "&lt;")

    def test_xml_01(self):
        self._equal_xml("<foo><p>Most of myWork is in the areas of <a>language technology</a>, stylometry&amp;Digital Humanities. Recurring key aspects of my research are:</p>foobar</foo>", "<foo> <p> Most of my Work is in the areas of <a> language technology </a> , stylometry &amp; Digital Humanities . Recurring key aspects of my research are : </p> foobar </foo>")

    def test_xml_02(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! : )</foo>", "<foo> der beste Betreuer ? -&gt; Prof Smith ! :) </foo>")

    def test_xml_03(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! <x>:</x>)</foo>", "<foo> der beste Betreuer ? -&gt; Prof Smith ! <x> : </x> ) </foo>")

    @unittest.expectedFailure
    def test_xml_04(self):
        self._equal_xml("<foo>href in fett: &lt;a href='<b>href</b>'&gt;</foo>", ["<foo>", "href", "in", "fett", ":", "&lt;a href='", "<b>", "href", "</b>", "'&gt;", "</foo>"])

    def test_xml_05(self):
        self._equal_xml("<foo>das steht auf S.&#x00ad;5</foo>", "<foo> das steht auf S. 5 </foo>")

    def test_xml_06(self):
        self._equal_xml("<foo><bar>na so was -&#x200B;</bar><bar>&gt; bla</bar></foo>", "<foo> <bar> na so was - </bar> <bar> &gt; bla </bar> </foo>")

    def test_xml_07(self):
        self._equal_xml("<foo><text><p>blendend. 👱‍</p></text><text ><blockquote><p>Foo bar baz</p></blockquote></text></foo>", "<foo> <text> <p> blendend . 👱‍ </p> </text> <text> <blockquote> <p> Foo bar baz </p> </blockquote> </text> </foo>")

    def test_xml_08(self):
        self._equal_xml("<text><p>Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt.</p><p>So 🙇🙇 manchen Unionspolitikern gestehe ich schon …</p></text>", "<text> <p> Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt . </p> <p> So 🙇 🙇 manchen Unionspolitikern gestehe ich schon … </p> </text>")

    def test_xml_09(self):
        self._equal_xml("""<text>
<p>Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt.</p>

<p>So 🙇🙇 manchen Unionspolitikern gestehe ich schon noch irgendwie zu, dass sie durchaus das Bedürfnis haben, ihren Bürgern ein gutes Leben zu ermöglichen. Zwar halte ich ihre Vorstellung von einem "guten Leben" und/oder die ☠☣ Wege, auf denen dieses erreicht werden soll, für grundsätzlich falsch - aber da stecken zumindest teilweise durchaus legitim gute Absichten dahinter.</p>

<p>Jens Spahn allerdings mangelt es 🚎 schmerzhaft offensichtlich an 📯🏻 diesem oben genannten Mindestmaß an 👹👹 Anstand. Die Dinge, die er ⤵⤵ erkennbar überzeugt von sich gibt, triefen vor Arroganz und Empathielosigkeit (Hartz IV? Mehr als genug; Gefährlich niedrige Versorgung mit Geburtshilfe? Sollen die 💯🚦 Weiber halt nen Kilometer weiter fahren); die andere Hälfte seiner verbalen Absonderungen ist ♂ schmerzhaft durchsichtiges taktisches Anbiedern an 💕👹 konservative Interessengruppen (jüngst beispielsweise Abtreibungsgegner) mittels plumpmöglichster Populismen.</p>
        </text>""", """<text> <p> Jens Spahn ist 🏽🏽 ein durch und durch ekelerregendes Subjekt . </p> <p> So 🙇 🙇 manchen Unionspolitikern gestehe ich schon noch irgendwie zu , dass sie durchaus das Bedürfnis haben , ihren Bürgern ein gutes Leben zu ermöglichen . Zwar halte ich ihre Vorstellung von einem " guten Leben " und / oder die ☠ ☣ Wege , auf denen dieses erreicht werden soll , für grundsätzlich falsch - aber da stecken zumindest teilweise durchaus legitim gute Absichten dahinter . </p> <p> Jens Spahn allerdings mangelt es 🚎 schmerzhaft offensichtlich an 📯🏻 diesem oben genannten Mindestmaß an 👹 👹 Anstand . Die Dinge , die er ⤵ ⤵ erkennbar überzeugt von sich gibt , triefen vor Arroganz und Empathielosigkeit ( Hartz IV ? Mehr als genug ; Gefährlich niedrige Versorgung mit Geburtshilfe ? Sollen die 💯 🚦 Weiber halt nen Kilometer weiter fahren ) ; die andere Hälfte seiner verbalen Absonderungen ist ♂ schmerzhaft durchsichtiges taktisches Anbiedern an 💕 👹 konservative Interessengruppen ( jüngst beispielsweise Abtreibungsgegner ) mittels plumpmöglichster Populismen . </p> </text>""")

    def test_xml_10(self):
        self._equal_xml("<foo><p>foo bar</p>\n\n<p>foo bar</p></foo>", "<foo> <p> foo bar </p> <p> foo bar </p> </foo>")

    def test_xml_11(self):
        self._equal_xml("<foo bar='baz'>Foo</foo>", ['<foo bar="baz">', 'Foo', '</foo>'])


class TestEmoticons(TestTokenizer):
    def test_emoticons_01(self):
        self._equal("bla🙅fasel", "bla 🙅 fasel")

    def test_emoticons_02(self):
        self._equal("🙄😖✈♨🎧🤒🚗", "🙄 😖 ✈ ♨ 🎧 🤒 🚗")

    def test_emoticons_03(self):
        self._equal("⚡️", "⚡️")

    def test_emoticons_04(self):
        self._equal("\u203C\uFE0F", "\u203C\uFE0F")

    def test_emoticons_05(self):
        self._equal("\u0032\uFE0F\u20E3", "\u0032\uFE0F\u20E3")

    def test_emoticons_06(self):
        self._equal("\U0001F1E8\U0001F1FD", "\U0001F1E8\U0001F1FD")

    def test_emoticons_07(self):
        self._equal("\u270C\U0001F3FC", "\u270C\U0001F3FC")

    def test_emoticons_08(self):
        self._equal("\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466", "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466")

    def test_emoticons_09(self):
        self._equal("\U0001F469\U0001F3FE\u200D\U0001F52C", "\U0001F469\U0001F3FE\u200D\U0001F52C")

    def test_emoticons_10(self):
        self._equal("\U0001F471\U0001F3FB\u200D\u2640\uFE0F", "\U0001F471\U0001F3FB\u200D\u2640\uFE0F")

    def test_emoticons_11(self):
        self._equal("\U0001F468\U0001F3FF\u200D\U0001F9B3", "\U0001F468\U0001F3FF\u200D\U0001F9B3")

    def test_emoticons_12(self):
        self._equal("\U0001F3F4\u200D\u2620\uFE0F", "\U0001F3F4\u200D\u2620\uFE0F")

    def test_emoticons_13(self):
        self._equal("\U0001F468\U0001F3FF\u200D\U0001F9B3\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466\U0001F3F4\u200D\u2620\uFE0F", "\U0001F468\U0001F3FF\u200D\U0001F9B3 \U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466 \U0001F3F4\u200D\u2620\uFE0F")

    def test_emoticons_14(self):
        self._equal("+ 🇺🇦️ Wahlen, Wahlen, Wahlen 🇺🇦️ +", "+ 🇺🇦️ Wahlen , Wahlen , Wahlen 🇺🇦️ +")

    def test_emoticons_15(self):
        self._equal("stage ️ bf0eb1c8cf477518ebdf43469b3246d1 https://t.co/TjNdsPqfr9", "stage bf0eb1c8cf477518ebdf43469b3246d1 https://t.co/TjNdsPqfr9")

    def test_emoticons_16(self):
        self._equal("x'D", "x'D")

    def test_emoticons_17(self):
        self._equal(":^)", ":^)")

    def test_emoticons_18(self):
        self._equal("I want to :scream:!", "I want to :scream: !")

    def test_emoticons_19(self):
        self._equal(":stuck_out_tongue_winking_eye:", ":stuck_out_tongue_winking_eye:")

    def test_emoticons_20(self):
        self._equal(":clock230::point_up_2:", ":clock230: :point_up_2:")

    def test_emoticons_21(self):
        """Entire set from textfac.es"""
        self._equal("( ͡° ͜ʖ ͡°) ¯\\_(ツ)_/¯ ̿̿ ̿̿ ̿̿ ̿'̿'\\̵͇̿̿\\з= ( ▀ ͜͞ʖ▀) =ε/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿ ▄︻̷̿┻̿═━一 ( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°) ʕ•ᴥ•ʔ (▀̿Ĺ̯▀̿ ̿) (ง ͠° ͟ل͜ ͡°)ง ༼ つ ◕_◕ ༽つ ಠ_ಠ (づ｡◕‿‿◕｡)づ ̿'̿'\\̵͇̿̿\\з=( ͠° ͟ʖ ͡°)=ε/̵͇̿̿/'̿̿ ̿ ̿ ̿ ̿ ̿ (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ) [̲̅$̲̅(̲̅5̲̅)̲̅$̲̅] ┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴ ( ͡°╭͜ʖ╮͡° ) (͡ ͡° ͜ つ ͡͡°) (• ε •) (ง'̀-'́)ง (ಥ﹏ಥ) ﴾͡๏̯͡๏﴿ O'RLY? (ノಠ益ಠ)ノ彡┻━┻ [̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅] (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ (☞ﾟ∀ﾟ)☞ | (• ◡•)| (❍ᴥ❍ʋ) (◕‿◕✿) (ᵔᴥᵔ) (╯°□°)╯︵ ʞooqǝɔɐɟ (¬‿¬) (☞ﾟヮﾟ)☞ ☜(ﾟヮﾟ☜) (づ￣ ³￣)づ ლ(ಠ益ಠლ) ಠ╭╮ಠ ̿ ̿ ̿'̿'\\̵͇̿̿\\з=(•_•)=ε/̵͇̿̿/'̿'̿ ̿ /╲/\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\╱\\ (;´༎ຶД༎ຶ`) ♪~ ᕕ(ᐛ)ᕗ ♥‿♥ ༼ つ  ͡° ͜ʖ ͡° ༽つ ༼ つ ಥ_ಥ ༽つ (╯°□°）╯︵ ┻━┻ ( ͡ᵔ ͜ʖ ͡ᵔ ) ヾ(⌐■_■)ノ♪ ~(˘▾˘~) ◉_◉ \\ (•◡•) / (~˘▾˘)~ (._.) ( l: ) ( .-. ) ( :l ) (._.) ༼ʘ̚ل͜ʘ̚༽ ༼ ºل͟º ༼ ºل͟º ༼ ºل͟º ༽ ºل͟º ༽ ºل͟º ༽ ┬┴┬┴┤(･_├┬┴┬┴ ᕙ(⇀‸↼‶)ᕗ ᕦ(ò_óˇ)ᕤ ┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻ ⚆ _ ⚆ (•_•) ( •_•)>⌐■-■ (⌐■_■) (｡◕‿‿◕｡) ಥ_ಥ ヽ༼ຈل͜ຈ༽ﾉ ⌐╦╦═─ (☞ຈل͜ຈ)☞ ˙͜ʟ˙ ☜(˚▽˚)☞ (•ω•) (ง°ل͜°)ง (｡◕‿◕｡) （╯°□°）╯︵( .o.) :') ┬──┬ ノ( ゜-゜ノ) (っ˘ڡ˘ς) ಠ⌣ಠ ლ(´ڡ`ლ) (°ロ°)☝ ｡◕‿‿◕｡ ( ಠ ͜ʖರೃ) ╚(ಠ_ಠ)=┐ (─‿‿─) ƪ(˘⌣˘)ʃ (；一_一) (¬_¬) ( ⚆ _ ⚆ ) (ʘᗩʘ') ☜(⌒▽⌒)☞ ｡◕‿◕｡ ¯\\(°_o)/¯ (ʘ‿ʘ) ლ,ᔑ•ﺪ͟͠•ᔐ.ლ (´・ω・`) ಠ~ಠ (° ͡ ͜ ͡ʖ ͡ °) ┬─┬ノ( º _ ºノ) (´・ω・)っ由 ಠ_ಥ Ƹ̵̡Ӝ̵̨̄Ʒ (>ლ) ಠ‿↼ ʘ‿ʘ (ღ˘⌣˘ღ) ಠoಠ ರ_ರ (▰˘◡˘▰) ◔̯◔ ◔ ⌣ ◔ (✿´‿`) ¬_¬ ب_ب ｡゜(｀Д´)゜｡ (ó ì_í)=óò=(ì_í ò) °Д° ( ﾟヮﾟ) ┬─┬ ︵ /(.□. ） ٩◔̯◔۶ ≧☉_☉≦ ☼.☼ ^̮^ (>人<) 〆(・∀・＠) (~_^) ^̮^ ^̮^ >_> (^̮^) (/) (°,,°) (/) ^̮^ ^̮^ =U (･.◤)", ["( ͡° ͜ʖ ͡°)", "¯\\_(ツ)_/¯", "̿̿ ̿̿ ̿̿ ̿'̿'\\̵͇̿̿\\з= ( ▀ ͜͞ʖ▀) =ε/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿", "▄︻̷̿┻̿═━一", "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)", "ʕ•ᴥ•ʔ", "(▀̿Ĺ̯▀̿ ̿)", "(ง ͠° ͟ل͜ ͡°)ง", "༼ つ ◕_◕ ༽つ", "ಠ_ಠ", "(づ｡◕‿‿◕｡)づ", "̿'̿'\\̵͇̿̿\\з=( ͠° ͟ʖ ͡°)=ε/̵͇̿̿/'̿̿ ̿ ̿ ̿ ̿ ̿", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)", "[̲̅$̲̅(̲̅5̲̅)̲̅$̲̅]", "┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴", "( ͡°╭͜ʖ╮͡° )", "(͡ ͡° ͜ つ ͡͡°)", "(• ε •)", "(ง'̀-'́)ง", "(ಥ﹏ಥ)", "﴾͡๏̯͡๏﴿ O'RLY?", "(ノಠ益ಠ)ノ彡┻━┻", "[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "(☞ﾟ∀ﾟ)☞", "| (• ◡•)| (❍ᴥ❍ʋ)", "(◕‿◕✿)", "(ᵔᴥᵔ)", "(╯°□°)╯︵ ʞooqǝɔɐɟ", "(¬‿¬)", "(☞ﾟヮﾟ)☞", "☜(ﾟヮﾟ☜)", "(づ￣ ³￣)づ", "ლ(ಠ益ಠლ)", "ಠ╭╮ಠ", "̿ ̿ ̿'̿'\\̵͇̿̿\\з=(•_•)=ε/̵͇̿̿/'̿'̿ ̿", "/╲/\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\╱\\", "(;´༎ຶД༎ຶ`)", "♪~ ᕕ(ᐛ)ᕗ", "♥‿♥", "༼ つ ͡° ͜ʖ ͡° ༽つ", "༼ つ ಥ_ಥ ༽つ", "(╯°□°）╯︵ ┻━┻", "( ͡ᵔ ͜ʖ ͡ᵔ )", "ヾ(⌐■_■)ノ♪", "~(˘▾˘~)", "◉_◉", "\\ (•◡•) /", "(~˘▾˘)~", "(._.) ( l: ) ( .-. ) ( :l ) (._.)", "༼ʘ̚ل͜ʘ̚༽", "༼ ºل͟º ༼ ºل͟º ༼ ºل͟º ༽ ºل͟º ༽ ºل͟º ༽", "┬┴┬┴┤(･_├┬┴┬┴", "ᕙ(⇀‸↼‶)ᕗ", "ᕦ(ò_óˇ)ᕤ", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻", "⚆ _ ⚆", "(•_•) ( •_•)>⌐■-■ (⌐■_■)", "(｡◕‿‿◕｡)", "ಥ_ಥ", "ヽ༼ຈل͜ຈ༽ﾉ", "⌐╦╦═─", "(☞ຈل͜ຈ)☞", "˙͜ʟ˙", "☜(˚▽˚)☞", "(•ω•)", "(ง°ل͜°)ง", "(｡◕‿◕｡)", "（╯°□°）╯︵( .o.)", ":')", "┬──┬ ノ( ゜-゜ノ)", "(っ˘ڡ˘ς)", "ಠ⌣ಠ", "ლ(´ڡ`ლ)", "(°ロ°)☝", "｡◕‿‿◕｡", "( ಠ ͜ʖರೃ)", "╚(ಠ_ಠ)=┐", "(─‿‿─)", "ƪ(˘⌣˘)ʃ", "(；一_一)", "(¬_¬)", "( ⚆ _ ⚆ )", "(ʘᗩʘ')", "☜(⌒▽⌒)☞", "｡◕‿◕｡", "¯\\(°_o)/¯", "(ʘ‿ʘ)", "ლ,ᔑ•ﺪ͟͠•ᔐ.ლ", "(´・ω・`)", "ಠ~ಠ", "(° ͡ ͜ ͡ʖ ͡ °)", "┬─┬ノ( º _ ºノ)", "(´・ω・)っ由", "ಠ_ಥ", "Ƹ̵̡Ӝ̵̨̄Ʒ", "(>ლ)", "ಠ‿↼", "ʘ‿ʘ", "(ღ˘⌣˘ღ)", "ಠoಠ", "ರ_ರ", "(▰˘◡˘▰)", "◔̯◔", "◔ ⌣ ◔", "(✿´‿`)", "¬_¬", "ب_ب", "｡゜(｀Д´)゜｡", "(ó ì_í)=óò=(ì_í ò)", "°Д°", "( ﾟヮﾟ)", "┬─┬ ︵ /(.□. ）", "٩◔̯◔۶", "≧☉_☉≦", "☼.☼", "^̮^", "(>人<)", "〆(・∀・＠)", "(~_^)", "^̮^", "^̮^", ">_>", "(^̮^)", "(/) (°,,°) (/)", "^̮^", "^̮^", "=U", "(･.◤)"])

    def test_emoticons_22(self):
        """Entire set from Signal"""
        self._equal(":-) ;-) (-: :-> :-D \\o/ :-P B-) :-$ :-* O:-) =-O O_O O_o o_O :O :-! :-x :-| :-\\ :-(:'(:-[>:-(^.^ ^_^ \\(ˆ˚ˆ)/ ヽ(°◇° )ノ ¯\\(°_o)/¯ ¯\\_(ツ)_/¯ (¬_¬) (>_<) (╥﹏╥) (☞ﾟヮﾟ)☞ ☜(ﾟヮﾟ☜) ☜(⌒▽⌒)☞ (╯°□°)╯︵┻━┻ ┬─┬ ノ(°–°ノ) (^._.^)ﾉ ฅ^•ﻌ•^ฅ ʕ•ᴥ•ʔ (•_•) ■-■¬ <(•_•) (■_■¬) ƪ(ړײ)‎ƪ​​", [":-)", ";-)", "(-:", ":->", ":-D", "\\o/", ":-P", "B-)", ":-$", ":-*", "O:-)", "=-O", "O_O", "O_o", "o_O", ":O", ":-!", ":-x", ":-|", ":-\\", ":-(", ":'(", ":-[", ">:-(", "^.^", "^_^", "\\(ˆ˚ˆ)/", "ヽ(°◇° )ノ", "¯\\(°_o)/¯", "¯\\_(ツ)_/¯", "(¬_¬)", "(>_<)", "(╥﹏╥)", "(☞ﾟヮﾟ)☞", "☜(ﾟヮﾟ☜)", "☜(⌒▽⌒)☞", "(╯°□°)╯︵", "┻━┻", "┬─┬", "ノ(°–°ノ)", "(^._.^)ﾉ", "ฅ^•ﻌ•^ฅ", "ʕ•ᴥ•ʔ", "(•_•)", "■-■¬ <(•_•)", "(■_■¬)", "ƪ(ړײ)ƪ"])

    def test_emoticons_23(self):
        """not all occurrences of : ( are a smiley"""
        self._equal("Tel: ( 0049) Tel: (+49 123 4567)", "Tel : ( 0049 ) Tel : ( +49 123 4567 )")

    def test_emoticons_24(self):
        self._equal(":;-))", ":;-))")

    def test_emoticons_25(self):
        self._equal("Ooh, wie süüß <3!", "Ooh , wie süüß <3 !")

    def test_emoticons_26(self):
        self._equal("Ooh, wie süüß <3 <3 <3!", "Ooh , wie süüß <3 <3 <3 !")

    def test_emoticons_27(self):
        self._equal("Ooh, wie süüß <3<3<3!", "Ooh , wie süüß <3 <3 <3 !")

    def test_emoticons_28(self):
        self._equal("Es gilt 2<3!", "Es gilt 2 < 3 !")

    def test_emoticons_29(self):
        self._equal("Das kostet <300", "Das kostet < 300")

    def test_emoticons_30(self):
        self._equal(":-*", ":-*")

    def test_emoticons_31(self):
        self._equal("*<:-)", "*<:-)")

    def test_emoticons_32(self):
        self._equal(":!:", ":!:")

    def test_emoticons_33(self):
        self._equal(";p", ";p")


class TestUnderline(TestTokenizer):
    def test_underline_01(self):
        self._equal("eine _reife_ Leistung", "eine _ reife _ Leistung")

    def test_underline_02(self):
        self._equal("Wir gehen ins _Sub", "Wir gehen ins _Sub")

    def test_underline_03(self):
        self._equal("Achtung _sehr wichtig_:", "Achtung _ sehr wichtig _ :")

    def test_underline_04(self):
        self._equal("Achtung _sehr wichtig _!", "Achtung _sehr wichtig _ !")

    @unittest.expectedFailure
    def test_underline_05(self):
        self._equal("Wir _gehen ins _Sub_", "Wir _ gehen ins _Sub _")

    def test_underline_06(self):
        self._equal("Achtung _ sehr wichtig_!", "Achtung _ sehr wichtig_ !")


class TestPunctuation(TestTokenizer):
    def test_punctuation_01(self):
        self._equal("Test etc....", "Test etc. ...")

    def test_punctuation_02(self):
        self._equal("$25", "$ 25")

    def test_punctuation_03(self):
        self._equal("25$", "25 $")

    def test_punctuation_04(self):
        self._equal("§12", "§ 12")

    def test_punctuation_05(self):
        self._equal("90°", "90 °")

    def test_punctuation_06(self):
        self._equal("5-2=3", "5 - 2 = 3")

    def test_punctuation_07(self):
        """Unicode minus sign"""
        self._equal("5−2=3", "5 − 2 = 3")

    def test_punctuation_08(self):
        self._equal("~12", "~ 12")

    def test_punctuation_09(self):
        self._equal("Das ist ein Zitat im ``LaTeX-Stil''!", "Das ist ein Zitat im `` LaTeX-Stil '' !")

    def test_punctuation_10(self):
        self._equal("Das ist ein 'Zitat', gell?", "Das ist ein ' Zitat ' , gell ?")

    def test_punctuation_11(self):
        self._equal('Das ist ein "Zitat", gell?', 'Das ist ein " Zitat " , gell ?')

    def test_punctuation_12(self):
        self._equal("Student*innen", "Student*innen")

    def test_punctuation_13(self):
        self._equal("Student*Innen", "Student*Innen")

    def test_punctuation_14(self):
        self._equal("Student_innen", "Student_innen")

    def test_punctuation_15(self):
        self._equal("Student_Innen", "Student_Innen")

    def test_punctuation_16(self):
        self._equal("Durch's Haselholz in's Thal hinab,", "Durch's Haselholz in's Thal hinab ,")

    def test_punctuation_17(self):
        self._equal("Acht Kegel hinter'm Brett herauf,", "Acht Kegel hinter'm Brett herauf ,")

    def test_punctuation_18(self):
        self._equal("Am Ende säh' ich selber mich,", "Am Ende säh' ich selber mich ,")

    def test_punctuation_19(self):
        self._equal("Und dann... Taxifahrer, Kellner,.... In", "Und dann ... Taxifahrer , Kellner , .... In")

    def test_punctuation_21(self):
        self._equal("neue (eMail)Adressen", "neue ( eMail ) Adressen")

    def test_punctuation_22(self):
        self._equal("LKWs=Lärm", "LKWs = Lärm")

    def test_punctuation_23(self):
        self._equal("Verzicht(bewusst)", "Verzicht ( bewusst )")

    def test_punctuation_24(self):
        self._equal("so 'nem", "so 'nem")

    def test_punctuation_25(self):
        self._equal("Dein Papa hat mir den Tip gegeben mal hier deine Blogs zu bewundern ; ) Echt stark für dein Alter !!", "Dein Papa hat mir den Tip gegeben mal hier deine Blogs zu bewundern ;) Echt stark für dein Alter !!")

    def test_punctuation_26(self):
        self._equal("der Student/die Studentin", "der Student / die Studentin")

    def test_punctuation_27(self):
        self._equal("der/die Student(in)", "der / die Student(in)")

    def test_punctuation_28(self):
        self._equal("``Wort''", "`` Wort ''")

    def test_punctuation_29(self):
        self._equal("`Wort'", "` Wort '")

    def test_punctuation_30(self):
        self._equal("Blabla ^3", "Blabla ^3")

    def test_punctuation_31(self):
        self._equal("5^3=125", "5 ^ 3 = 125")

    def test_punctuation_32(self):
        self._equal("5 ^3=125", "5 ^ 3 = 125")

    def test_punctuation_33(self):
        self._equal("5 ^3 = 125", "5 ^ 3 = 125")

    def test_punctuation_34(self):
        self._equal("<- bla bla ->", "<- bla bla ->")

    def test_punctuation_35(self):
        self._equal("<Medien weggelassen>", "< Medien weggelassen >")

    def test_punctuation_36(self):
        self._equal("Ich lese IhreAnnäherungen,Beobachtungen,Vergleiche", "Ich lese Ihre Annäherungen , Beobachtungen , Vergleiche")

    @unittest.expectedFailure
    def test_punctuation_37(self):
        self._equal('"bla bla"-Taktik', '" bla bla " - Taktik')

    @unittest.expectedFailure
    def test_punctuation_38(self):
        self._equal('"bla"-Taktik', '"bla"-Taktik')

    @unittest.expectedFailure
    def test_punctuation_39(self):
        self._equal("..i.d.Regel", ".. i. d. Regel")

    def test_punctuation_40(self):
        self._equal("i.d.Regel", "i. d. Regel")

    def test_punctuation_41(self):
        self._equal("vgl.Regel", "vgl. Regel")

    def test_punctuation_42(self):
        self._equal("vgl.z.B.die", "vgl. z. B. die")

    def test_punctuation_43(self):
        self._equal("Google+", "Google+")

    @unittest.expectedFailure
    def test_punctuation_44(self):
        self._equal("Industrie4.0", "Industrie4.0")

    @unittest.expectedFailure
    def test_punctuation_45(self):
        self._equal("WP:DISK", "WP:DISK")

    @unittest.expectedFailure
    def test_punctuation_46(self):
        self._equal("WP:BNS", "WP:BNS")

    @unittest.expectedFailure
    def test_punctuation_47(self):
        self._equal("Bla:[2]", "Bla : [ 2 ]")

    def test_punctuation_48(self):
        self._equal("Herford–Lage–Detmold–Altenbeken–Paderborn", "Herford – Lage – Detmold – Altenbeken – Paderborn")

    def test_punctuation_49(self):
        self._equal("The book 'Algorithm Design', too", "The book ' Algorithm Design ' , too")

    def test_punctuation_50(self):
        self._equal("Mir gefällt La Porte de l'Enfer besser als L'Éternelle idole", "Mir gefällt La Porte de l'Enfer besser als L'Éternelle idole")

    def test_punctuation_51(self):
        self._equal("E.ON ist ein Stromanbieter.", "E.ON ist ein Stromanbieter .")

    def test_punctuation_52(self):
        self._equal("Ich bin Kunde bei E.ON.", "Ich bin Kunde bei E.ON .")

    def test_punctuation_53(self):
        self._equal("Problem: Setzer*in macht einen Fehler", "Problem : Setzer*in macht einen Fehler")

    def test_punctuation_54(self):
        self._equal("Wir suchen Mitarbeiter*innen, die bla", "Wir suchen Mitarbeiter*innen , die bla")

    def test_punctuation_55(self):
        self._equal("Wir suchen C#-Entwickler.", "Wir suchen C#-Entwickler .")

    def test_punctuation_56(self):
        self._equal("Programmiersprachen: C++, C#, F#, .Net", "Programmiersprachen : C++ , C# , F# , .Net")

    def test_punctuation_57(self):
        self._equal(")foo", ") foo")

    def test_punctuation_58(self):
        self._equal(" )foo", ") foo")

    def test_punctuation_59(self):
        self._equal("machst du's?", "machst du's ?")

    @unittest.expectedFailure
    def test_punctuation_60(self):
        self._equal("foo 'bar -> baz' qux 'bar baz' qux", "foo ' bar -> baz ' qux ' bar baz ' qux")

    def test_punctuation_61(self):
        self._equal('foo "bar -> baz" qux "bar baz" qux', 'foo " bar -> baz " qux " bar baz " qux')

    def test_punctuation_62(self):
        self._equal("Das ist großartig… /s", "Das ist großartig … /s")

    def test_punctuation_63(self):
        self._equal("Dagegen sollte man endlich etwas tun! /rant", "Dagegen sollte man endlich etwas tun ! /rant")

    @unittest.expectedFailure
    def test_punctuation_64(self):
        self._equal("Verd****e Sonnenmilch ist nichts f**king weiter als sch**ß Sonnenschutzlotion zur H**le.", "Verd****e Sonnenmilch ist nichts f**king weiter als sch**ß Sonnenschutzlotion zur H**le .")

    def test_punctuation_65(self):
        self._equal("Was gibt 7x4?", "Was gibt 7 x 4 ?")

    def test_punctuation_66(self):
        self._equal("Was gibt 7×4? Und 3*9?", "Was gibt 7 × 4 ? Und 3 * 9 ?")

    def test_punctuation_67(self):
        self._equal("☆☆☆Wir", "☆ ☆ ☆ Wir")

    @unittest.expectedFailure
    def test_punctuation_68(self):
        self._equal("Wir suchen eine/n Mitarbeiter/in", "Wir suchen eine/n Mitarbeiter/in")

    def test_punctuation_69(self):
        self._equal("Mitarbeiter:in", "Mitarbeiter:in")

    def test_punctuation_70(self):
        self._equal("Mitarbeiter*in", "Mitarbeiter*in")

    def test_punctuation_71(self):
        self._equal("Christian von Faber-Castell, 4. Juli 2014 ​\n", "Christian von Faber-Castell , 4. Juli 2014")

    @unittest.expectedFailure
    def test_punctuation_72(self):
        self._equal("Punkte 2-4. Das System", "Punkte 2 - 4 . Das System")

    def test_punctuation_73(self):
        self._equal("Am Ende dieses Satzes steht 12.03.2023.", "Am Ende dieses Satzes steht 12. 03. 2023 .")


class TestEmailsURLs(TestTokenizer):
    def test_emails_urls_01(self):
        self._equal("In der Zeitung (http://www.sueddeutsche.de) stand", "In der Zeitung ( http://www.sueddeutsche.de ) stand")

    def test_emails_urls_02(self):
        self._equal("In den Nachrichten (bspw. http://www.sueddeutsche.de) stand", "In den Nachrichten ( bspw. http://www.sueddeutsche.de ) stand")

    def test_emails_urls_03(self):
        self._equal("http://www.sueddeutsche.de/bla/test_(geheim).html", "http://www.sueddeutsche.de/bla/test_(geheim).html")

    def test_emails_urls_04(self):
        self._equal("http://www.sueddeutsche.de/bla/test_(geheim)", "http://www.sueddeutsche.de/bla/test_(geheim)")

    @unittest.expectedFailure
    def test_emails_urls_05(self):
        self._equal("bla (http://www.sueddeutsche.de/bla/test_(geheim).html) foo", "bla ( http://www.sueddeutsche.de/bla/test_(geheim).html ) foo")

    @unittest.expectedFailure
    def test_emails_urls_06(self):
        self._equal("bla (http://www.sueddeutsche.de/bla/test_(geheim)) foo", "bla ( http://www.sueddeutsche.de/bla/test_(geheim) ) foo")

    def test_emails_urls_07(self):
        self._equal("vorname_nachname@provider.eu", "vorname_nachname@provider.eu")

    def test_emails_urls_08(self):
        self._equal("r/foo/bar", "r/foo/bar")

    def test_emails_urls_09(self):
        self._equal("/r/foo/bar", "/r/foo/bar")

    def test_emails_urls_10(self):
        self._equal("l/de", "l/de")

    def test_emails_urls_11(self):
        self._equal("/u/quatschkopf", "/u/quatschkopf")

    def test_emails_urls_12(self):
        self._equal("/r/foo/bar/", "/r/foo/bar/")

    def test_emails_urls_13(self):
        self._equal("Schau mal die Doku auf kla.tv an", "Schau mal die Doku auf kla.tv an")

    def test_emails_urls_14(self):
        self._equal("Eine kla.tv-Zuschauerin hat…", "Eine kla.tv-Zuschauerin hat …")

    @unittest.expectedFailure
    def test_emails_urls_15(self):
        self._equal("Schau mal die Doku auf kla.tv/dokus an", "Schau mal die Doku auf kla.tv/dokus an")

    def test_emails_urls_16(self):
        self._equal("http://de.m.wikipedia.org/wiki/Troll_(Netzkultur)", "http://de.m.wikipedia.org/wiki/Troll_(Netzkultur)")

    def test_emails_urls_17(self):
        self._equal("doi:10.1371/journal.pbio.0020449.g001", "doi:10.1371/journal.pbio.0020449.g001")

    def test_emails_urls_18(self):
        self._equal("doi: 10.1371/journal.pbio.0020449.g001", "doi : 10.1371/journal.pbio.0020449.g001")

    def test_emails_urls_19(self):
        self._equal("http://de.m.wikipedia.org/wiki/Troll/", "http://de.m.wikipedia.org/wiki/Troll/")

    def test_emails_urls_20(self):
        self._equal("die tagesschau.de-App", "die tagesschau.de-App")

    def test_emails_urls_21(self):
        self._equal("foo-bar.com", "foo-bar.com")

    def test_emails_urls_22(self):
        self._equal("bla.foo-bar.com", "bla.foo-bar.com")

    def test_emails_urls_23(self):
        self._equal("security-medium.png", "security-medium.png")

    def test_emails_urls_24(self):
        self._equal("directory/image.png", "directory/image.png")

    def test_emails_urls_25(self):
        self._equal("name [at] provider [dot] com", ["name[at]provider[dot]com"])

    def test_emails_urls_26(self):
        self._equal("link: [https://one_link.com](https://other_link.com).", "link : [ https://one_link.com ] ( https://other_link.com ) .")

    def test_emails_urls_27(self):
        self._equal("link: [Linktext „viel“ Text](https://other_link.com).", "link : [ Linktext „ viel “ Text ] ( https://other_link.com ) .")

    def test_emails_urls_28(self):
        self._equal("link: <https://one_link.com>.", "link : < https://one_link.com > .")

    def test_emails_urls_29(self):
        self._equal("*[Neubau](https://www.some-link.com)*", "* [ Neubau ] ( https://www.some-link.com ) *")

    def test_emails_urls_30(self):
        self._equal("[Konfiguration](https://a-link.com)\\\\", "[ Konfiguration ] ( https://a-link.com ) \\\\")


class TestAbbreviations(TestTokenizer):
    def test_abbreviations_01(self):
        self._equal("Englisch: tl;dr. Deutsch: zl;ng.", "Englisch : tl;dr . Deutsch : zl;ng .")

    @unittest.expectedFailure
    def test_abbreviations_02(self):
        self._equal("c&c.", "c & c .")

    def test_abbreviations_03(self):
        self._equal("andere &c.", "andere &c.")

    def test_abbreviations_04(self):
        self._equal("Der hat 100 PS.", "Der hat 100 PS .")

    def test_abbreviations_05(self):
        self._equal("PS. Morgen ist Weihnachten", "PS. Morgen ist Weihnachten")

    def test_abbreviations_06(self):
        self._equal("Best.-Nr.", "Best.-Nr.")

    def test_abbreviations_07(self):
        self._equal("Foo.-Nr.", "Foo.-Nr.")

    def test_abbreviations_08(self):
        self._equal("Foo.Nr.", "Foo.Nr.")

    def test_abbreviations_09(self):
        self._equal("Forsch.frage", "Forsch.frage")

    def test_abbreviations_10(self):
        self._equal("dieForsch.frage", "die Forsch.frage")

    def test_abbreviations_11(self):
        self._equal("bla…", "bla …")

    def test_abbreviations_12(self):
        self._equal("bla….", "bla … .")

    def test_abbreviations_13(self):
        self._equal("bla…..", "bla …..")

    def test_abbreviations_14(self):
        self._equal("Stefan-Evert-Str. 2", "Stefan-Evert-Str. 2")

    def test_abbreviations_15(self):
        self._equal("Parkstr. 2", "Parkstr. 2")

    def test_abbreviations_16(self):
        self._equal("Hey Mr. Schlauberger", "Hey Mr. Schlauberger")

    def test_abbreviations_17(self):
        self._equal("Nach Art. 1 Grundgesetz", "Nach Art. 1 Grundgesetz")

    def test_abbreviations_17a(self):
        self._equal("Meine Art. Genau", "Meine Art . Genau")


class TestHashtagsMentions(TestTokenizer):
    def test_hashtag_mentions_01(self):
        self._equal("#Refugeeswelcome-Bewegung", "#Refugeeswelcome-Bewegung")

    def test_hashtag_mentions_02(self):
        self._equal("Bumble Bee Menga wünscht ein schönen Sonntag ! #staystrong#fckcorona#action#germany.", "Bumble Bee Menga wünscht ein schönen Sonntag ! #staystrong #fckcorona #action #germany .")

    def test_hashtag_mentions_03(self):
        self._equal("#hashtag", "#hashtag")

    def test_hashtag_mentions_04(self):
        self._equal("#hashtag1", "#hashtag1")

    def test_hashtag_mentions_05(self):
        self._equal("@PianoMan @1000_MHz @kaeferchen", "@PianoMan @1000_MHz @kaeferchen")


class TestNumbers(TestTokenizer):
    def test_numbers_01(self):
        self._equal("WS05/06", "WS 05/06")

    def test_numbers_02(self):
        self._equal("8-fach", "8-fach")

    def test_numbers_03(self):
        self._equal("66cent", "66 cent")

    def test_numbers_04(self):
        self._equal("12kg", "12 kg")

    def test_numbers_05(self):
        self._equal("5h", "5 h")

    def test_numbers_06(self):
        self._equal("1/2kg", "1/2 kg")

    def test_numbers_07(self):
        self._equal("51cm", "51 cm")

    def test_numbers_08(self):
        self._equal("heute 300.000.000 Videominuten", "heute 300.000.000 Videominuten")

    def test_numbers_09(self):
        self._equal("(65).", "( 65 ) .")

    def test_numbers_10(self):
        self._equal("mein Sohn(7)", "mein Sohn ( 7 )")

    def test_numbers_11(self):
        self._equal("1 ) bla 2 ) blubb", "1 ) bla 2 ) blubb")

    def test_numbers_12(self):
        self._equal("1)Einleitung", "1 ) Einleitung")

    @unittest.expectedFailure
    def test_numbers_13(self):
        self._equal("das dauert nur 15m. hoffe ich", "das dauert nur 15 m. hoffe ich")

    def test_numbers_14(self):
        self._equal("1.1.1 Allgemeines", "1.1.1 Allgemeines")

    def test_numbers_15(self):
        self._equal("1.1.1. Allgemeines", "1.1.1. Allgemeines")

    @unittest.expectedFailure
    def test_numbers_16(self):
        self._equal("Das ist ab 18+", "Das ist ab 18+")

    @unittest.expectedFailure
    def test_numbers_17(self):
        self._equal("Wir haben 500+ Gäste", "Wir haben 500+ Gäste")

    def test_numbers_18(self):
        self._equal("toll +1", "toll +1")

    def test_numbers_19(self):
        self._equal("blöd -1", "blöd -1")

    @unittest.expectedFailure
    def test_numbers_20(self):
        self._equal("1998/99", "1998 / 99")

    @unittest.expectedFailure
    def test_numbers_21(self):
        self._equal("2009/2010", "2009 / 2010")

    def test_numbers_22(self):
        self._equal("1970er", "1970er")

    def test_numbers_23(self):
        self._equal("Punkte 1,2,3,4,5,6,7 sind bla", "Punkte 1 , 2 , 3 , 4 , 5 , 6 , 7 sind bla")

    def test_numbers_24(self):
        self._equal("1.1 Allgemeines", "1.1 Allgemeines")

    @unittest.expectedFailure
    def test_numbers_25(self):
        self._equal("1.1. Allgemeines", "1.1. Allgemeines")

    def test_numbers_26(self):
        self._equal("IP-Adresse des Routers: 192.0.2.42.", "IP-Adresse des Routers : 192.0.2.42 .")

    def test_numbers_27(self):
        self._equal("ISBN 978-0-596-52068-7", "ISBN 978-0-596-52068-7")

    def test_numbers_28(self):
        self._equal("ISBN-13: 978-0-596-52068-7", "ISBN-13 : 978-0-596-52068-7")

    def test_numbers_29(self):
        self._equal("978 0 596 52068 7", "9780596520687")

    def test_numbers_30(self):
        self._equal("9780596520687", "9780596520687")

    def test_numbers_31(self):
        self._equal("ISBN-10 0-596-52068-9", "ISBN-10 0-596-52068-9")

    def test_numbers_32(self):
        self._equal("0-596-52068-9", "0-596-52068-9")

    def test_numbers_33(self):
        self._equal("ISBN 3-570-02690-6.", "ISBN 3-570-02690-6 .")

    def test_numbers_34(self):
        self._equal("ISBN 978-0-596-52068-7: Foo", "ISBN 978-0-596-52068-7 : Foo")

    def test_numbers_35(self):
        self._equal("Was für eine ISBN: ISBN-10, ISBN-13?", "Was für eine ISBN : ISBN-10 , ISBN-13 ?")

    def test_numbers_36(self):
        self._equal("100 Mbit/s", "100 Mbit/s")

    def test_numbers_37(self):
        self._equal("das III. Geschwader", "das III. Geschwader")

    def test_numbers_38(self):
        self._equal("Ludwig XIV. war", "Ludwig XIV. war")

    def test_numbers_39(self):
        self._equal("die COVID-19 Pandemie ist", "die COVID-19 Pandemie ist")

    def test_numbers_39a(self):
        self._equal("die COVID-19-Pandemie ist", "die COVID-19-Pandemie ist")

    def test_numbers_39b(self):
        self._equal("die COVID19-Pandemie ist", "die COVID19-Pandemie ist")

    def test_numbers_39c(self):
        self._equal("der G20-Gipfel war", "der G20-Gipfel war")

    def test_numbers_39d(self):
        self._equal("eine FFP2-Maske hilft", "eine FFP2-Maske hilft")

    def test_numbers_40(self):
        self._equal("fährt 10 km/h zu schnell", "fährt 10 km/h zu schnell")

    def test_numbers_40a(self):
        self._equal("fährt 10km/h zu schnell", "fährt 10 km/h zu schnell")

    def test_numbers_40b(self):
        self._equal("fährt 100 km/h. Zu schnell", "fährt 100 km/h . Zu schnell")

    def test_numbers_40c(self):
        self._equal("fährt 100km/h. Zu schnell", "fährt 100 km/h . Zu schnell")

    @unittest.expectedFailure
    def test_numbers_41(self):
        self._equal("jenseits der 100-°C-Grenze bla", "jenseits der 100-°C-Grenze bla")

    def test_numbers_42(self):
        self._equal("eine 18-Jährigen-Falle.", "eine 18-Jährigen-Falle .")

    def test_numbers_43(self):
        self._equal("Ü-oder-U-18", "Ü-oder-U-18")

    def test_numbers_44(self):
        self._equal("das macht 1.234,56–2.345,67 €", "das macht 1.234,56 – 2.345,67 €")
        self._equal("das macht 1.234,56-2.345,67 €", "das macht 1.234,56 - 2.345,67 €")

    def test_numbers_45(self):
        self._equal("etwa 1/2–3/4 voll", "etwa 1/2 – 3/4 voll")
        self._equal("etwa 1/2-3/4 voll", "etwa 1/2 - 3/4 voll")

    def test_numbers_46(self):
        self._equal("-3.42e-4–+3.42e-4", "-3.42e-4 – +3.42e-4")
        self._equal("-3.42e-4-+3.42e-4", "-3.42e-4 - +3.42e-4")

    def test_numbers_47(self):
        self._equal("etwa 4–6 Personen", "etwa 4 – 6 Personen")
        self._equal("etwa 4-6 Personen", "etwa 4 - 6 Personen")


class TestCamelCase(TestTokenizer):
    def test_camelcase_01(self):
        self._equal("Gehen wir zu McDonalds?", "Gehen wir zu McDonalds ?")

    def test_camelcase_02(self):
        self._equal("Gehen wir zu McDonald's?", "Gehen wir zu McDonald's ?")

    def test_camelcase_03(self):
        self._equal("AutorIn", "AutorIn")

    def test_camelcase_04(self):
        self._equal("fReiE", "fReiE")

    def test_camelcase_05(self):
        self._equal("bla WordPress bla", "bla WordPress bla")

    def test_camelcase_06(self):
        self._equal("auf WordPress.com bla", "auf WordPress.com bla")

    def test_camelcase_07(self):
        self._equal("ImmobilienScout24.de", "ImmobilienScout24.de")

    def test_camelcase_08(self):
        self._equal("eBay", "eBay")

    def test_camelcase_09(self):
        self._equal("gGmbH", "gGmbH")

    @unittest.expectedFailure
    def test_camelcase_10(self):
        self._equal("und auchE-Mail", "und auch E-Mail")

    def test_camelcase_11(self):
        self._equal("derVgl. hinkt", "der Vgl. hinkt")

    def test_camelcase_12(self):
        self._equal("vorgestellteUntersuchung", "vorgestellte Untersuchung")

    def test_camelcase_13(self):
        self._equal("d.eigenenUnters", "d. eigenen Unters")


class TestEnglish(TestEnglishTokenizer):
    def test_english_01(self):
        self._equal("I don't know.", "I do n't know .")

    def test_english_02(self):
        self._equal("This is Peter's book.", "This is Peter 's book .")

    def test_english_03(self):
        self._equal("This is Alex' book .", "This is Alex ' book .")

    def test_english_04(self):
        self._equal("What's up?", "What 's up ?")

    def test_english_05(self):
        self._equal("I'll see you", "I 'll see you")

    def test_english_06(self):
        self._equal("You cannot come!", "You can not come !")

    def test_english_07(self):
        self._equal("You know 'twas just a joke.", "You know 't was just a joke .")

    def test_english_08(self):
        self._equal("I'd like to try ``Sarah's cake''.", "I 'd like to try `` Sarah 's cake '' .")

    def test_english_09(self):
        self._equal("Blah'twas", "Blah'twas")

    # def test_english_10(self):
    #     self._equal("the center-north of the country", "the center - north of the country")

    def test_english_11(self):
        self._equal("1970s", "1970s")

    def test_english_12(self):
        self._equal("Sunni and Shi'ite clerics", "Sunni and Shi'ite clerics")

    def test_english_13(self):
        self._equal("The book 'Algorithm Design', too", "The book ' Algorithm Design ' , too")

    def test_english_14(self):
        self._equal("People were encouraged to submit their designs online at www.flag.govt.nz and suggest what the flag should mean on www.standfor.co.nz.", "People were encouraged to submit their designs online at www.flag.govt.nz and suggest what the flag should mean on www.standfor.co.nz .")

    def test_english_15(self):
        self._equal("bla 21st century", "bla 21st century")

    def test_english_16(self):
        self._equal("bla 50,000th visitor", "bla 50,000th visitor")

    def test_english_17(self):
        self._equal("Mr. ARCHIBALD: Hello", "Mr. ARCHIBALD : Hello")

    def test_english_18(self):
        self._equal("Give me all your lovin' please", "Give me all your lovin' please")

    def test_english_19(self):
        self._equal("foo bar--my favourite---gave me", "foo bar -- my favourite --- gave me")

    def test_english_20(self):
        self._equal("this is anti-foobar baz", "this is anti-foobar baz")

    def test_english_21(self):
        self._equal("this is anty-foobar baz", "this is anty - foobar baz")

    def test_english_22a(self):
        self._equal("bla 3°C foo", "bla 3 °C foo")

    def test_english_22b(self):
        self._equal("bla 3 °C foo", "bla 3 °C foo")

    def test_english_23(self):
        self._equal("foo the U.S., L.A., 1750 A.D., e.g. J.F.K., etc.", "foo the U.S. , L.A. , 1750 A.D. , e.g. J.F.K. , etc.")

    def test_english_24(self):
        self._equal("!!!!!!!!!!???????? *************", "!!!!!!!!!!???????? *************")

    def test_english_25(self):
        self._equal("It's not 17:30 or 5:30p.m. but 5.30am", "It 's not 17:30 or 5:30 p.m. but 5.30 am")

    def test_english_26(self):
        self._equal("bla approval/decline bar", "bla approval / decline bar")

    def test_english_27(self):
        self._equal("bar on 01/24/2001 11:16:25 AM foo", "bar on 01/24/2001 11:16:25 AM foo")

    def test_english_28(self):
        self._equal('"Well," said Mr. Blue.', '" Well , " said Mr. Blue .')

    def test_english_29(self):
        self._equal("a duper-e-stimator, a super-e-stimator", "a duper - e - stimator , a super-e-stimator")

    def test_english_30(self):
        self._equal("my number:456-123-7654!", "my number : 456-123-7654 !")

    def test_english_31(self):
        self._equal("I prefer La Porte de l'Enfer to L'Éternelle idole", "I prefer La Porte de l'Enfer to L'Éternelle idole")

class TesttCustomAbbreviation(TestCustomTokenizer):
        def test_abbreviations_custom(self):
            self._equal("Brem.GBl.", "Brem. GBl.")

class TestDeprecated(TestTokenizerDeprecated):
    def test_deprecated_01(self):
        self._equal("foo bar baz", "foo bar baz")

    def test_deprecated_02(self):
        self._equal_xml("<p>foo bar baz</p>", "<p> foo bar baz </p>")
