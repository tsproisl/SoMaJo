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


class TestWhitespace(TestTokenizer):
    """"""
    def test_whitespace_01(self):
        # self.assertEqual(self.tokenizer.tokenize("Petra und Simone gehen ins Kino"), "Petra und Simone gehen ins Kino".split())
        self._equal("Petra und Simone gehen ins Kino", "Petra und Simone gehen ins Kino")


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
        self._equal("du bist echt ein a...", "du bist echt ein a...")

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
        self._equal("+s", "+s")

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

    def test_time_15(self):
        self._equal("ca. 20°C", "ca. 20 ° C")

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
        self._equal("Punkte 2-4. Das System", "Punkte 2 - 4 . Das System")


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
        self._equal("handfest un direkt- so sind se...die Pottler", "handfest un direkt - so sind se ... die Pottler")

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
        self._equal("das dauert nur 15m. hoffe ich", "das dauert nur 15 m. hoffe ich")

    def test_own_23(self):
        self._equal("der Student/die Studentin", "der Student / die Studentin")

    def test_own_24(self):
        self._equal("der/die Student(in)", "der / die Student(in)")

    def test_own_25(self):
        self._equal("``Wort''", "`` Wort ''")

    def test_own_26(self):
        self._equal("`Wort'", "` Wort '")

    def test_own_27(self):
        self._equal("c&c.", "c & c .")

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
        self._equal("und auchE-Mail", "und auch E-Mail")

    def test_own_62(self):
        self._equal('"bla bla"-Taktik', '" bla bla " - Taktik')

    def test_own_63(self):
        self._equal('"bla"-Taktik', '"bla"-Taktik')

    def test_own_64(self):
        self._equal("derVgl. hinkt", "der Vgl. hinkt")

    def test_own_65(self):
        self._equal("vorgestellteUntersuchung", "vorgestellte Untersuchung")

    def test_own_66(self):
        self._equal("d.eigenenUnters", "d. eigenen Unters")

    def test_own_67a(self):
        self._equal("..i.d.Regel", ".. i. d. Regel")

    def test_own_67b(self):
        self._equal("i.d.Regel", "i. d. Regel")

    def test_own_67c(self):
        self._equal("vgl.Regel", "vgl. Regel")

    def test_own_68(self):
        self._equal("vgl.z.B.die", "vgl. z. B. die")

    def test_own_69(self):
        self._equal("1.1.1 Allgemeines", "1.1.1 Allgemeines")

    def test_own_70(self):
        self._equal("1.1.1. Allgemeines", "1.1.1. Allgemeines")

    def test_own_71(self):
        self._equal("Google+", "Google+")

    def test_own_72(self):
        self._equal("Industrie4.0", "Industrie4.0")

    def test_own_73(self):
        self._equal("Das ist ab 18+", "Das ist ab 18+")

    def test_own_74(self):
        self._equal("Wir haben 500+ Gäste", "Wir haben 500+ Gäste")

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
        self._equal("WP:DISK", "WP:DISK")

    def test_own_83(self):
        self._equal("WP:BNS", "WP:BNS")

    def test_own_84(self):
        self._equal("Bla:[2]", "Bla : [ 2 ]")

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
        self._equal("1998/99", "1998 / 99")

    def test_own_92(self):
        self._equal("2009/2010", "2009 / 2010")


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


class TestJunk(TestTokenizer):
    """"""
    def test_junk_01(self):
        # zero width space
        self._equal("foo​bar", "foobar")

    def test_junk_02(self):
        # soft hyphen
        self._equal("foo­bar", "foobar")

    def test_junk_03(self):
        # soft hyphen
        self._equal("foo\nbar", "foo bar")

    def test_junk_04(self):
        # control characters
        self._equal("foobarbazquxalphabetagamma", "foobarbazquxalphabetagamma")


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
