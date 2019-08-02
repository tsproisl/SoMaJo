#!/usr/bin/env python3

import unittest

from somajo import Tokenizer


class TestTokenizer(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(split_camel_case=True)

    def _equal(self, raw, tokenized):
        """"""
        self.assertEqual(self.tokenizer.tokenize(raw), tokenized.split())

    def _equal_xml(self, raw, tokenized):
        """"""
        self.assertEqual(self.tokenizer.tokenize_xml(raw, is_file=False), tokenized.split())

    def _fail_means_improvement(self, raw, tokenized):
        """"""
        self.assertNotEqual(self.tokenizer.tokenize(raw), tokenized.split())


class TestEnglishTokenizer(TestTokenizer):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(split_camel_case=True, language="en")


class TestWhitespace(TestTokenizer):
    """"""
    def test_whitespace_01(self):
        # self.assertEqual(self.tokenizer.tokenize("Petra und Simone gehen ins Kino"), "Petra und Simone gehen ins Kino".split())
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


class TestPunctuation(TestTokenizer):
    """"""
    def test_punctuation_01(self):
        self._equal("Als ich ihn sah, war es bereits zu spät.", "Als ich ihn sah , war es bereits zu spät .")

    def test_punctuation_02(self):
        self._equal("Das hab ich mich auch schon gefragt...", "Das hab ich mich auch schon gefragt ...")

    def test_punctuation_03(self):
        self._equal("Das ist ein Test?!", "Das ist ein Test ?!")

    def test_punctuation_04(self):
        self._equal("bh's", "bh's")

    def test_punctuation_05(self):
        self._equal("mit'm Fahrrad", "mit'm Fahrrad")

    def test_punctuation_06(self):
        self._equal("des Virus'", "des Virus'")

    def test_punctuation_07(self):
        self._fail_means_improvement("du bist echt ein a...", "du bist echt ein a...")

    def test_punctuation_08(self):
        self._equal("Test.......", "Test .......")

    def test_punctuation_09(self):
        self._equal("Test????????", "Test ????????")

    def test_punctuation_10(self):
        self._equal("Test!!!", "Test !!!")

    def test_punctuation_11(self):
        self._equal("Test?!?!?!", "Test ?!?!?!")

    def test_punctuation_12(self):
        self._equal("In der 2....", "In der 2. ...")

    def test_punctuation_13(self):
        self._equal("Test etc....", "Test etc. ...")

    def test_punctuation_14(self):
        self._equal("Test....????!!!!", "Test .... ????!!!!")

    def test_punctuation_15(self):
        self._equal("Laub- und Nadelbäume", "Laub- und Nadelbäume")

    def test_punctuation_16(self):
        self._equal("Hals-Nasen-Ohren-Arzt", "Hals-Nasen-Ohren-Arzt")

    def test_punctuation_17(self):
        self._equal("10%", "10 %")

    def test_punctuation_18(self):
        self._equal("200€", "200 €")

    def test_punctuation_19(self):
        self._equal("§§48", "§§ 48")

    def test_punctuation_20(self):
        self._equal("11+21=33", "11 + 21 = 33")

    def test_punctuation_21(self):
        self._equal("$25", "$ 25")

    def test_punctuation_22(self):
        self._equal("25$", "25 $")

    def test_punctuation_23(self):
        self._equal("§12", "§ 12")

    def test_punctuation_24(self):
        self._equal("90°", "90 °")

    def test_punctuation_25(self):
        self._equal("5-2=3", "5 - 2 = 3")

    def test_punctuation_26(self):
        """Unicode minus sign"""
        self._equal("5−2=3", "5 − 2 = 3")

    def test_punctuation_27(self):
        self._equal("~12", "~ 12")

    def test_punctuation_28(self):
        self._equal("Avril_Lavigne", "Avril_Lavigne")

    def test_punctuation_29(self):
        self._fail_means_improvement("+s", "+s")

    def test_punctuation_30(self):
        self._equal("-v", "-v")

    def test_punctuation_31(self):
        self._equal("f->d", "f -> d")

    def test_punctuation_32(self):
        self._equal("f - > d", "f -> d")

    def test_punctuation_32a(self):
        self._equal("f→d", "f → d")

    def test_punctuation_33(self):
        self._equal("(Neu-)Veröffentlichung", "( Neu- ) Veröffentlichung")

    def test_punctuation_34(self):
        self._equal("Student(inn)en", "Student(inn)en")

    def test_punctuation_35(self):
        self._equal("Student/innen", "Student/innen")

    def test_punctuation_36(self):
        self._equal("i-„Pott“", "i- „ Pott “")

    def test_punctuation_37(self):
        self._equal("Experten/Expertinnen", "Experten / Expertinnen")

    def test_punctuation_38(self):
        self._equal("(“normale”/saisonale) Grippe", "( “ normale ” / saisonale ) Grippe")

    def test_punctuation_39(self):
        self._equal("Vitamin C-Mangel", "Vitamin C-Mangel")

    def test_punctuation_40(self):
        self._equal("Magen- Darm- Erkrankung", "Magen- Darm- Erkrankung")

    def test_punctuation_41(self):
        self._equal("Das ist ein Zitat im ``LaTeX-Stil''!", "Das ist ein Zitat im `` LaTeX-Stil '' !")

    def test_punctuation_42(self):
        self._equal("Das ist ein 'Zitat', gell?", "Das ist ein ' Zitat ' , gell ?")

    def test_punctuation_43(self):
        self._equal('Das ist ein "Zitat", gell?', 'Das ist ein " Zitat " , gell ?')


class TestTimeDate(TestTokenizer):
    """"""
    def test_time_01(self):
        self._equal("6.200", "6.200")

    def test_time_02(self):
        self._equal("6.200,-", "6.200,-")

    def test_time_03(self):
        self._equal("das dauert 2:40 std.", "das dauert 2:40 std.")

    def test_time_04(self):
        self._equal("-1,5", "-1,5")

    def test_time_05(self):
        """Unicode minus sign"""
        self._equal("−1,5", "−1,5")

    def test_time_06(self):
        self._equal("-1.5", "-1.5")

    def test_time_07(self):
        """Unicode minus sign"""
        self._equal("−1.5", "−1.5")

    def test_time_08(self):
        self._equal("1/2 h", "1/2 h")

    def test_time_09(self):
        self._equal("1 / 2 h", "1 / 2 h")

    def test_time_10(self):
        self._equal("14:00-18:00", "14:00 - 18:00")

    def test_time_11(self):
        """Halbgeviertstrich (Bis-Strich)"""
        self._equal("14:00–18:00", "14:00 – 18:00")

    def test_time_12(self):
        self._equal("14–18 Uhr", "14 – 18 Uhr")

    def test_time_13(self):
        self._equal("1-3 Semester", "1 - 3 Semester")

    def test_time_14(self):
        self._equal("30-50kg", "30 - 50 kg")

    def test_time_15a(self):
        self._equal("ca. 20°C", "ca. 20 ° C")

    def test_time_15b(self):
        self._equal("ca. 20 °C", "ca. 20 ° C")

    def test_time_16(self):
        self._equal("ca. 20 GHz", "ca. 20 GHz")

    def test_time_17(self):
        self._equal("4-11mal", "4 - 11mal")

    def test_time_18(self):
        self._equal("16.07.2013", "16. 07. 2013")

    def test_time_19(self):
        self._equal("16. Juli 2013", "16. Juli 2013")

    def test_time_20(self):
        self._equal("21/07/1980", "21/ 07/ 1980")

    def test_time_21(self):
        self._equal("Weimarer Klassik", "Weimarer Klassik")

    def test_time_22(self):
        self._equal("Hälfte des XIX Jh. = Anfang 1796", "Hälfte des XIX Jh. = Anfang 1796")

    def test_time_23(self):
        self._equal("WS04", "WS 04")

    def test_time_24(self):
        self._equal("24-stündig", "24-stündig")

    def test_time_25(self):
        self._fail_means_improvement("Punkte 2-4. Das System", "Punkte 2 - 4 . Das System")


class TestAbbreviations(TestTokenizer):
    """"""
    def test_abbreviations_01(self):
        self._equal("etc.", "etc.")

    def test_abbreviations_02(self):
        self._equal("d.h.", "d. h.")

    def test_abbreviations_03(self):
        self._equal("d. h.", "d. h.")

    def test_abbreviations_04(self):
        self._equal("o.ä.", "o. ä.")

    def test_abbreviations_05(self):
        self._equal("u.dgl.", "u. dgl.")

    def test_abbreviations_06(self):
        self._equal("std.", "std.")

    def test_abbreviations_07(self):
        self._equal("Mat.-Nr.", "Mat.-Nr.")

    def test_abbreviations_08(self):
        self._equal("Wir kauften Socken, Hemden, Schuhe etc. Danach hatten wir alles.", "Wir kauften Socken , Hemden , Schuhe etc. Danach hatten wir alles .")

    def test_abbreviations_09(self):
        self._equal("zB", "zB")

    def test_abbreviations_10(self):
        self._equal("Zeitschr.titel", "Zeitschr.titel")

    def test_abbreviations_11(self):
        self._equal("A9", "A9")

    def test_abbreviations_12(self):
        self._equal("cu Peter", "cu Peter")

    def test_abbreviations_13(self):
        self._equal("Bruce Springsteen aka The Boss", "Bruce Springsteen aka The Boss")


class TestTypos(TestTokenizer):
    """"""
    def test_typos_01(self):
        self._equal("die stehen da schona ber ohne preise", "die stehen da schona ber ohne preise")

    def test_typos_02(self):
        self._equal("tag quaki : )", "tag quaki :)")

    def test_typos_03(self):
        self._equal("Ich hab da noch maldrüber nachgedacht", "Ich hab da noch maldrüber nachgedacht")

    def test_typos_04(self):
        self._equal("Anna,kannst du mal", "Anna , kannst du mal")

    def test_typos_05(self):
        self._fail_means_improvement("handfest un direkt- so sind se...die Pottler", "handfest un direkt - so sind se ... die Pottler")

    def test_typos_06(self):
        self._equal("Warst du vom Zeugnis überraschtß", "Warst du vom Zeugnis überraschtß")


class TestContractions(TestTokenizer):
    """"""
    def test_contractions_01(self):
        self._equal("stimmt’s", "stimmt’s")

    def test_contractions_02(self):
        self._equal("waren’s", "waren’s")


class TestCamelCase(TestTokenizer):
    """"""
    def test_camel_case_01(self):
        self._equal("Zu welchemHandlungsbereich gehört unsereKomm hier? Bildung?Freizeit?Mischung?", "Zu welchem Handlungsbereich gehört unsere Komm hier ? Bildung ? Freizeit ? Mischung ?")

    def test_camel_case_02(self):
        self._equal("derText", "der Text")

    def test_camel_case_03(self):
        self._equal("PepsiCo", "PepsiCo")


class TestTags(TestTokenizer):
    """"""
    def test_tags_01(self):
        self.assertEqual(self.tokenizer.tokenize('<A target="_blank" href="https://en.wikipedia.org/w/index.php?tit-le=Talk:PRISM_(surveillance_program)&oldid=559238329#Known_Counter_Measures_deleted_.21">'), ['<A target="_blank" href="https://en.wikipedia.org/w/index.php?tit-le=Talk:PRISM_(surveillance_program)&oldid=559238329#Known_Counter_Measures_deleted_.21">'])

    def test_tags_02(self):
        self._equal("</A>", "</A>")

    def test_tags_03(self):
        self.assertEqual(self.tokenizer.tokenize("<?xml version='1.0' encoding='US-ASCII' standalone='yes' ?>"), ["<?xml version='1.0' encoding='US-ASCII' standalone='yes' ?>"])

    def test_tags_04(self):
        self.assertEqual(self.tokenizer.tokenize('<?xml version="1.0" encoding="UTF-8"?>'), ['<?xml version="1.0" encoding="UTF-8"?>'])


class TestEntities(TestTokenizer):
    """"""
    def test_tags_01(self):
        self._equal("&amp;", "&amp;")

    def test_tags_02(self):
        self._equal("&#x2fb1;", "&#x2fb1;")

    def test_tags_03(self):
        self._equal("&#75;", "&#75;")

    def test_tags_04(self):
        self._equal("foo&amp;bar", "foo &amp; bar")


class TestEmailsURLs(TestTokenizer):
    """"""
    def test_emails_urls_01(self):
        self._equal("michael.beisswenger@tu-dortmund.de", "michael.beisswenger@tu-dortmund.de")

    def test_emails_urls_02(self):
        self._equal("https://en.wikipedia.org/wiki/Main_Page", "https://en.wikipedia.org/wiki/Main_Page")

    def test_emails_urls_03(self):
        self._equal("http://www.shortnews.de", "http://www.shortnews.de")

    def test_emails_urls_04(self):
        self._equal("shortnews.de", "shortnews.de")

    def test_emails_urls_05(self):
        self._equal("Auf www.shortnews.de, der besten Seite.", "Auf www.shortnews.de , der besten Seite .")

    def test_emails_urls_06(self):
        self._equal("Auf shortnews.de, der besten Seite.", "Auf shortnews.de , der besten Seite .")

    def test_emails_urls_07(self):
        self._equal("In der Zeitung (http://www.sueddeutsche.de) stand", "In der Zeitung ( http://www.sueddeutsche.de ) stand")

    def test_emails_urls_08(self):
        self._equal("In den Nachrichten (bspw. http://www.sueddeutsche.de) stand", "In den Nachrichten ( bspw. http://www.sueddeutsche.de ) stand")

    def test_emails_urls_09(self):
        self._equal("http://www.sueddeutsche.de/bla/test_(geheim).html", "http://www.sueddeutsche.de/bla/test_(geheim).html")

    def test_emails_urls_10(self):
        self._equal("http://www.sueddeutsche.de/bla/test_(geheim)", "http://www.sueddeutsche.de/bla/test_(geheim)")

    def test_emails_urls_11(self):
        self._fail_means_improvement("bla (http://www.sueddeutsche.de/bla/test_(geheim).html) foo", "bla ( http://www.sueddeutsche.de/bla/test_(geheim).html ) foo")

    def test_emails_urls_12(self):
        self._fail_means_improvement("bla (http://www.sueddeutsche.de/bla/test_(geheim)) foo", "bla ( http://www.sueddeutsche.de/bla/test_(geheim) ) foo")

    def test_emails_urls_13(self):
        self._equal("vorname_nachname@provider.eu", "vorname_nachname@provider.eu")


class TestEmoticons(TestTokenizer):
    """"""
    def test_emoticons_01(self):
        self._equal(":-)", ":-)")

    def test_emoticons_02(self):
        self._equal(":-)))))", ":-)))))")

    def test_emoticons_03(self):
        self._equal(";-)", ";-)")

    def test_emoticons_04(self):
        self._equal(":)", ":)")

    def test_emoticons_05(self):
        self._equal(";)", ";)")

    def test_emoticons_06(self):
        self._equal(":-(", ":-(")

    def test_emoticons_07(self):
        self._equal("8)", "8)")

    def test_emoticons_08(self):
        self._equal(":D", ":D")

    def test_emoticons_09(self):
        self._equal("^^", "^^")

    def test_emoticons_10(self):
        self._equal("o.O", "o.O")

    def test_emoticons_11(self):
        self._equal("oO", "oO")

    def test_emoticons_12(self):
        self._equal("\O/", "\O/")

    def test_emoticons_13(self):
        self._equal("\m/", "\m/")

    def test_emoticons_14(self):
        self._equal(":;))", ":;))")

    def test_emoticons_15(self):
        self._equal("_))", "_))")

    def test_emoticons_16(self):
        self._equal("hallo peter ; )", "hallo peter ;)")

    def test_emoticons_17(self):
        self._equal("Das hab ich auch schon gehört (find ich super :-)", "Das hab ich auch schon gehört ( find ich super :-)")

    def test_emoticons_18(self):
        self._equal("bla🙅fasel", "bla 🙅 fasel")

    def test_emoticons_19(self):
        self._equal("🙄😖✈♨🎧🤒🚗", "🙄 😖 ✈ ♨ 🎧 🤒 🚗")

    def test_emoticons_20(self):
        self._equal("⚡️", "⚡️")

    def test_emoticons_21(self):
        self._equal("\u203C\uFE0F", "\u203C\uFE0F")

    def test_emoticons_22(self):
        self._equal("\u0032\uFE0F\u20E3", "\u0032\uFE0F\u20E3")

    def test_emoticons_23(self):
        self._equal("\U0001F1E8\U0001F1FD", "\U0001F1E8\U0001F1FD")

    def test_emoticons_24(self):
        self._equal("\u270C\U0001F3FC", "\u270C\U0001F3FC")

    def test_emoticons_25(self):
        self._equal("\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466", "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466")

    def test_emoticons_26(self):
        self._equal("\U0001F469\U0001F3FE\u200D\U0001F52C", "\U0001F469\U0001F3FE\u200D\U0001F52C")

    def test_emoticons_27(self):
        self._equal("\U0001F471\U0001F3FB\u200D\u2640\uFE0F", "\U0001F471\U0001F3FB\u200D\u2640\uFE0F")

    def test_emoticons_28(self):
        self._equal("\U0001F468\U0001F3FF\u200D\U0001F9B3", "\U0001F468\U0001F3FF\u200D\U0001F9B3")

    def test_emoticons_29(self):
        self._equal("\U0001F3F4\u200D\u2620\uFE0F", "\U0001F3F4\u200D\u2620\uFE0F")

    def test_emoticons_30(self):
        self._equal("\U0001F468\U0001F3FF\u200D\U0001F9B3\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466\U0001F3F4\u200D\u2620\uFE0F", "\U0001F468\U0001F3FF\u200D\U0001F9B3 \U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466 \U0001F3F4\u200D\u2620\uFE0F")

    def test_emoticons_31(self):
        self._equal("+ 🇺🇦️ Wahlen, Wahlen, Wahlen 🇺🇦️ +", "+ 🇺🇦️ Wahlen , Wahlen , Wahlen 🇺🇦️ +")

    def test_emoticons_32(self):
        self._equal("stage ️ bf0eb1c8cf477518ebdf43469b3246d1 https://t.co/TjNdsPqfr9", "stage bf0eb1c8cf477518ebdf43469b3246d1 https://t.co/TjNdsPqfr9")


class TestActions(TestTokenizer):
    """"""
    def test_actions_01(self):
        self._equal("*grübel*", "* grübel *")

    def test_actions_02(self):
        self._equal("*auf locher rumhüpf & konfetti mach*", "* auf locher rumhüpf & konfetti mach *")

    def test_actions_03(self):
        self._equal("*dichmalganzdolleknuddelt*", "* dichmalganzdolleknuddelt *")

    def test_actions_04(self):
        self._equal("immer noch nicht fassen kann", "immer noch nicht fassen kann")

    def test_actions_05(self):
        self._equal("quakirenntdemflöppymitdeneiswürfelnnach*", "quakirenntdemflöppymitdeneiswürfelnnach *")

    def test_actions_06(self):
        self._equal("+s*", "+ s *")

    def test_actions_07(self):
        self._equal("*danachdenraminmeinenrechnereinbau*G*", "* danachdenraminmeinenrechnereinbau * G *")

    def test_actions_08(self):
        self._equal("quaki knuddelt Thor", "quaki knuddelt Thor")


class TestAddressing(TestTokenizer):
    """"""
    def test_addressing_01(self):
        self._equal("@bine23", "@bine23")

    def test_addressing_02(self):
        self._equal("@alle", "@alle")

    def test_addressing_03(self):
        self._equal("winke@bochum", "winke @bochum")

    def test_addressing_04(self):
        self._equal("@bine23: hallöchen! :-)", "@bine23 : hallöchen ! :-)")


class TestHashtags(TestTokenizer):
    """"""
    def test_hashtags_01(self):
        self._equal("#urlaub", "#urlaub")

    def test_hashtags_02(self):
        self._equal("#SPD", "#SPD")


class OwnAdditions(TestTokenizer):
    """"""
    def test_own_01(self):
        self._equal("WS05/06", "WS 05/06")

    def test_own_02(self):
        self._equal("8-fach", "8-fach")

    def test_own_03a(self):
        self._equal("66cent", "66 cent")

    def test_own_03b(self):
        self._equal("12kg", "12 kg")

    def test_own_03c(self):
        self._equal("5h", "5 h")

    def test_own_03d(self):
        self._equal("66cent", "66 cent")

    def test_own_03e(self):
        self._equal("51cm", "51 cm")

    def test_own_04(self):
        self._equal("Und dann... Taxifahrer, Kellner,.... In", "Und dann ... Taxifahrer , Kellner , .... In")

    def test_own_05(self):
        self._equal("neue (eMail)Adressen", "neue ( eMail ) Adressen")

    def test_own_06(self):
        self._equal("heute 300.000.000 Videominuten", "heute 300.000.000 Videominuten")

    def test_own_07(self):
        self._equal("(65).", "( 65 ) .")

    def test_own_08(self):
        self._equal("#hashtag", "#hashtag")

    def test_own_09(self):
        self._equal("#hashtag1", "#hashtag1")

    def test_own_10(self):
        self._equal("LKWs=Lärm", "LKWs = Lärm")

    def test_own_11(self):
        self._equal("Verzicht(bewusst)", "Verzicht ( bewusst )")

    def test_own_11a(self):
        self._equal("mein Sohn(7)", "mein Sohn ( 7 )")

    def test_own_12(self):
        self._equal("1 ) bla 2 ) blubb", "1 ) bla 2 ) blubb")

    def test_own_13(self):
        self._equal("1)Einleitung", "1 ) Einleitung")

    def test_own_14(self):
        self._equal("@PianoMan @1000_MHz @kaeferchen", "@PianoMan @1000_MHz @kaeferchen")

    def test_own_15(self):
        self._equal("so 'nem", "so 'nem")

    def test_own_16(self):
        self._equal("2016-01-27", "2016 -01 -27")

    def test_own_17(self):
        self._equal("01-27-2016", "01- 27- 2016")

    def test_own_18(self):
        self._equal("(am 20.06.2008)", "( am 20. 06. 2008 )")

    def test_own_19(self):
        self._equal("http://de.m.wikipedia.org/wiki/Troll_(Netzkultur)", "http://de.m.wikipedia.org/wiki/Troll_(Netzkultur)")

    def test_own_20(self):
        self._equal("Dein Papa hat mir den Tip gegeben mal hier deine Blogs zu bewundern ; ) Echt stark für dein Alter !!", "Dein Papa hat mir den Tip gegeben mal hier deine Blogs zu bewundern ;) Echt stark für dein Alter !!")

    def test_own_21(self):
        self._equal("WS15/16", "WS 15/16")

    def test_own_22(self):
        self._fail_means_improvement("das dauert nur 15m. hoffe ich", "das dauert nur 15 m. hoffe ich")

    def test_own_23(self):
        self._equal("der Student/die Studentin", "der Student / die Studentin")

    def test_own_24(self):
        self._fail_means_improvement("der/die Student(in)", "der / die Student(in)")

    def test_own_25(self):
        self._equal("``Wort''", "`` Wort ''")

    def test_own_26(self):
        self._equal("`Wort'", "` Wort '")

    def test_own_27(self):
        self._fail_means_improvement("c&c.", "c & c .")

    def test_own_28(self):
        self._equal("andere &c.", "andere &c.")

    def test_own_29(self):
        self._equal("http://de.m.wikipedia.org/wiki/Troll/", "http://de.m.wikipedia.org/wiki/Troll/")

    def test_own_30(self):
        self._equal("Der hat 100 PS.", "Der hat 100 PS .")

    def test_own_31(self):
        self._equal("PS. Morgen ist Weihnachten", "PS. Morgen ist Weihnachten")

    def test_own_32(self):
        self._equal("Blabla ^3", "Blabla ^3")

    def test_own_33(self):
        self._equal("5^3=125", "5 ^ 3 = 125")

    def test_own_34(self):
        self._equal("5 ^3=125", "5 ^ 3 = 125")

    def test_own_35(self):
        self._equal("5 ^3 = 125", "5 ^ 3 = 125")

    def test_own_36(self):
        self._equal("Gehen wir zu McDonalds?", "Gehen wir zu McDonalds ?")

    def test_own_37(self):
        self._equal("Gehen wir zu McDonald's?", "Gehen wir zu McDonald's ?")

    def test_own_38(self):
        self._equal("AutorIn", "AutorIn")

    def test_own_39(self):
        self._equal("fReiE", "fReiE")

    def test_own_40(self):
        self._equal("bla WordPress bla", "bla WordPress bla")

    def test_own_41(self):
        self._equal("auf WordPress.com bla", "auf WordPress.com bla")

    def test_own_42(self):
        self._equal("<- bla bla ->", "<- bla bla ->")

    def test_own_43(self):
        self._equal("<Medien weggelassen>", "< Medien weggelassen >")

    def test_own_44(self):
        self._equal("ImmobilienScout24.de", "ImmobilienScout24.de")

    def test_own_45(self):
        self._equal("eBay", "eBay")

    def test_own_46(self):
        self._equal("gGmbH", "gGmbH")

    def test_own_47(self):
        self._equal("Best.-Nr.", "Best.-Nr.")

    def test_own_48(self):
        self._equal("Foo.-Nr.", "Foo.-Nr.")

    def test_own_49(self):
        self._equal("Foo.Nr.", "Foo.Nr.")

    def test_own_50(self):
        self._equal("die tagesschau.de-App", "die tagesschau.de-App")

    def test_own_51(self):
        self._equal("foo-bar.com", "foo-bar.com")

    def test_own_52(self):
        self._equal("bla.foo-bar.com", "bla.foo-bar.com")

    def test_own_53(self):
        self._equal("security-medium.png", "security-medium.png")

    def test_own_54(self):
        self._equal("Forsch.frage", "Forsch.frage")

    def test_own_55(self):
        self._equal("dieForsch.frage", "die Forsch.frage")

    def test_own_56(self):
        self._equal("bla…", "bla …")

    def test_own_57(self):
        self._equal("bla….", "bla … .")

    def test_own_58(self):
        self._equal("bla…..", "bla …..")

    def test_own_59(self):
        self._equal("Stefan-Evert-Str. 2", "Stefan-Evert-Str. 2")

    def test_own_60(self):
        self._equal("Ich lese IhreAnnäherungen,Beobachtungen,Vergleiche", "Ich lese Ihre Annäherungen , Beobachtungen , Vergleiche")

    def test_own_61(self):
        self._fail_means_improvement("und auchE-Mail", "und auch E-Mail")

    def test_own_62(self):
        self._fail_means_improvement('"bla bla"-Taktik', '" bla bla " - Taktik')

    def test_own_63(self):
        self._fail_means_improvement('"bla"-Taktik', '"bla"-Taktik')

    def test_own_64(self):
        self._equal("derVgl. hinkt", "der Vgl. hinkt")

    def test_own_65(self):
        self._equal("vorgestellteUntersuchung", "vorgestellte Untersuchung")

    def test_own_66(self):
        self._equal("d.eigenenUnters", "d. eigenen Unters")

    def test_own_67a(self):
        self._fail_means_improvement("..i.d.Regel", ".. i. d. Regel")

    def test_own_67b(self):
        self._equal("i.d.Regel", "i. d. Regel")

    def test_own_67c(self):
        self._equal("vgl.Regel", "vgl. Regel")

    def test_own_68(self):
        self._equal("vgl.z.B.die", "vgl. z. B. die")

    def test_own_69(self):
        self._equal("1.1.1 Allgemeines", "1.1.1 Allgemeines")

    def test_own_70(self):
        self._fail_means_improvement("1.1.1. Allgemeines", "1.1.1. Allgemeines")

    def test_own_71(self):
        self._equal("Google+", "Google+")

    def test_own_72(self):
        self._equal("Industrie4.0", "Industrie4.0")

    def test_own_73(self):
        self._fail_means_improvement("Das ist ab 18+", "Das ist ab 18+")

    def test_own_74(self):
        self._fail_means_improvement("Wir haben 500+ Gäste", "Wir haben 500+ Gäste")

    def test_own_75(self):
        self._equal("toll +1", "toll +1")

    def test_own_76(self):
        self._equal("blöd -1", "blöd -1")

    def test_own_77(self):
        self._equal("doi:10.1371/journal.pbio.0020449.g001", "doi:10.1371/journal.pbio.0020449.g001")

    def test_own_78(self):
        self._equal("doi: 10.1371/journal.pbio.0020449.g001", "doi : 10.1371/journal.pbio.0020449.g001")

    def test_own_79(self):
        self._equal("&lt;", "&lt;")

    def test_own_80(self):
        self._equal(":-*", ":-*")

    def test_own_81(self):
        self._equal("*<:-)", "*<:-)")

    def test_own_82(self):
        self._fail_means_improvement("WP:DISK", "WP:DISK")

    def test_own_83(self):
        self._fail_means_improvement("WP:BNS", "WP:BNS")

    def test_own_84(self):
        self._fail_means_improvement("Bla:[2]", "Bla : [ 2 ]")

    def test_own_85(self):
        self._equal("Herford–Lage–Detmold–Altenbeken–Paderborn", "Herford – Lage – Detmold – Altenbeken – Paderborn")

    def test_own_86(self):
        self._equal("directory/image.png", "directory/image.png")

    def test_own_87(self):
        self.assertEqual(self.tokenizer.tokenize("name [at] provider [dot] com"), ["name [at] provider [dot] com"])

    def test_own_88(self):
        self._equal(":!:", ":!:")

    def test_own_89(self):
        self._equal(";p", ";p")

    def test_own_90(self):
        self._equal(":;-))", ":;-))")

    def test_own_91(self):
        self._fail_means_improvement("1998/99", "1998 / 99")

    def test_own_92(self):
        self._fail_means_improvement("2009/2010", "2009 / 2010")

    def test_own_93(self):
        self._equal("1970er", "1970er")

    def test_own_94(self):
        self._equal("The book 'Algorithm Design', too", "The book ' Algorithm Design ' , too")

    def test_own_95(self):
        self._equal("Mir gefällt La Porte de l'Enfer besser als L'Éternelle idole", "Mir gefällt La Porte de l'Enfer besser als L'Éternelle idole")

    def test_own_96(self):
        self._equal("E.ON ist ein Stromanbieter.", "E.ON ist ein Stromanbieter .")

    def test_own_97(self):
        self._equal("Ich bin Kunde bei E.ON.", "Ich bin Kunde bei E.ON .")


class TestSuffixes(TestTokenizer):
    """"""
    def test_suffixes_01(self):
        self.tokenizer.replacement_counter = 0
        self.assertEqual(self.tokenizer._get_unique_suffix(), "aaaaaaa")

    def test_suffixes_02(self):
        self.tokenizer.replacement_counter = 1
        self.assertEqual(self.tokenizer._get_unique_suffix(), "aaaaaab")

    def test_suffixes_03(self):
        self.tokenizer.replacement_counter = 26
        self.assertEqual(self.tokenizer._get_unique_suffix(), "aaaaaba")

    def test_suffixes_04(self):
        self.tokenizer.replacement_counter = 27
        self.assertEqual(self.tokenizer._get_unique_suffix(), "aaaaabb")
        self.assertEqual(self.tokenizer._get_unique_suffix(), "aaaaabc")


class TestUnderline(TestTokenizer):
    """"""
    def test_underline_01(self):
        self._equal("eine _reife_ Leistung", "eine _ reife _ Leistung")

    def test_underline_02(self):
        self._equal("Wir gehen ins _Sub", "Wir gehen ins _Sub")

    def test_underline_03(self):
        self._equal("Achtung _sehr wichtig_:", "Achtung _ sehr wichtig _ :")

    def test_underline_04(self):
        self._equal("Achtung _sehr wichtig _!", "Achtung _sehr wichtig _ !")

    def test_underline_05(self):
        self._fail_means_improvement("Wir _gehen ins _Sub_", "Wir _ gehen ins _Sub _")

    def test_underline_06(self):
        self._equal("Achtung _ sehr wichtig_!", "Achtung _ sehr wichtig_ !")


class TestJunk(TestTokenizer):
    """"""
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


class TestXML(TestTokenizer):
    """"""
    def test_xml_01(self):
        self._equal_xml("<foo><p>Most of myWork is in the areas of <a>language technology</a>, stylometry&amp;Digital Humanities. Recurring key aspects of my research are:</p>foobar</foo>", "<foo> <p> Most of my Work is in the areas of <a> language technology </a> , stylometry &amp; Digital Humanities . Recurring key aspects of my research are : </p> foobar </foo>")

    def test_xml_02(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! : )</foo>", "<foo> der beste Betreuer ? -&gt; Prof Smith ! :) </foo>")

    def test_xml_03(self):
        self._equal_xml("<foo>der beste Betreuer? - &gt;ProfSmith! <x>:</x>)</foo>", "<foo> der beste Betreuer ? -&gt; Prof Smith ! <x> : </x> ) </foo>")

    def test_xml_04(self):
        self.assertEqual(self.tokenizer.tokenize_xml("<foo>href in fett: &lt;a href='<b>href</b>'&gt;</foo>", is_file=False), ["<foo>", "href", "in", "fett", ":", "&lt;a href='", "<b>", "href", "</b>", "'&gt;", "</foo>"])


class TestTokenizerExtra(unittest.TestCase):
    """"""
    def setUp(self):
        """Necessary preparations"""
        self.tokenizer = Tokenizer(split_camel_case=True, extra_info=True)

    def _equal(self, raw, tokenized):
        """"""
        tokens, extra_info = zip(*self.tokenizer.tokenize(raw))
        self.assertEqual(list(tokens), tokenized.split())


class TestMisc(TestTokenizerExtra):
    """"""
    def test_misc_01(self):
        self._equal("[Alt] + 240 =­\n", "[ Alt ] + 240 =")

    def test_misc_02(self):
        self._equal("[Alt] + 240 =\n", "[ Alt ] + 240 =")

    def test_misc_03(self):
        self._equal("foo­bar", "foobar")

    def test_misc_04(self):
        self._equal("foo­ bar", "foo bar")

    def test_misc_05(self):
        self._equal("foo­", "foo")

    def test_misc_06(self):
        self._equal("Christian von Faber-Castell, 4. Juli 2014 ​\n", "Christian von Faber-Castell , 4. Juli 2014")

    def test_misc_07(self):
        self._equal("Vgl. Schott, E., Markt und Geschäftsbeziehung beim Outsourcing ­\n", "Vgl. Schott , E. , Markt und Geschäftsbeziehung beim Outsourcing")

    def test_misc_08(self):
        self._equal("foo ­ ​ bar", "foo bar")

    def test_misc_09(self):
        self.assertEqual(self.tokenizer.tokenize("­ \n­"), [])


class TestEnglish(TestEnglishTokenizer):
    """"""
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

    def test_english_14(self):
        self._equal("I prefer La Porte de l'Enfer to L'Éternelle idole", "I prefer La Porte de l'Enfer to L'Éternelle idole")

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
