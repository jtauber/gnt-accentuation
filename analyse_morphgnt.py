#!/usr/bin/env python3

import re
import unicodedata

from greek_accentuation.accentuation import get_accent_type
from greekutils.trigrams import trigrams
from pysblgnt import morphgnt_rows


def strip_accents(s):
    return unicodedata.normalize("NFC", "".join((
        c for c in unicodedata.normalize("NFD", s)
        if c not in ["\u0300", "\u0301", "\u0342"]
    )))


def has_grave(s):
    return "\u0300" in unicodedata.normalize("NFD", s)


def grave_to_acute(s):
    temp = ""
    for ch in unicodedata.normalize("NFD", s):
        if ch == "\u0300":
            ch = "\u0301"  # OXIA will be normalized to TONOS below if needed
        temp += ch
    return unicodedata.normalize("NFC", temp)


def count_accents(s):
    count = 0
    for c in unicodedata.normalize("NFD", s):
        if c in ["\u0300", "\u0301", "\u0342"]:
            count += 1
    return count


def strip_last_accent(word):
    x = list(word)
    for i, ch in enumerate(x[::-1]):
        s = strip_accents(ch)
        if s != ch:
            x[-i - 1] = s
            break
    return "".join(x)


INCONSISTENCIES = [
    ("ἑλπίδι", "ἐλπίδι"),
    ("Γολγοθα", "Γολγοθᾶ"),
]

ELISION = [
    ("ἀλλ’", "ἀλλά"),
    ("ἀνθ’", "ἀντί"),
    ("ἀπ’", "ἀπό"),
    ("ἀφ’", "ἀπό"),
    ("δ’", "δέ"),
    ("δι’", "διά"),
    ("ἐπ’", "ἐπί"),
    ("ἐφ’", "ἐπί"),
    ("κατ’", "κατά"),
    ("καθ’", "κατά"),
    ("μηδ’", "μηδέ"),
    ("μετ’", "μετά"),
    ("μεθ’", "μετά"),
    ("οὐδ’", "οὐδέ"),
    ("παρ’", "παρά"),
    ("τοῦτ’", "τοῦτο"),
    ("ὑπ’", "ὑπό"),
    ("ὑφ’", "ὑπό"),
]

MOVABLE = [
    ("ἐξ", "ἐκ"),

    ("οὐκ", "οὐ"),
    ("οὐχ", "οὐ"),
]


ENCLITICS = [
    "μου", "μοι", "με",
    "σου", "σοι", "σε",
    "τὶς", "τὶ", "τινός", "τινί", "τινά", "τινές", "τινάς", "τινῶν", "τισίν",
    "πού", "ποτέ", "πώ", "πώς",
    "εἰμί", "εἰσίν", "ἐσμέν", "ἐστέ", "ἐστίν", "ἐστί",
    "φησίν", "φημί", "φασίν",
    "γέ", "τέ",
]


PROCLITICS = [
    "ὁ", "ἡ", "οἱ", "αἱ",
    "ἐν", "εἰς", "ἐξ", "ἐκ",
    "εἰ", "ὡς",
    "οὐ", "οὐκ", "οὐχ",
]


UNACCENTED_FOREIGN = [
    "ταλιθα", "κουμ", "εφφαθα", "ραββουνι", "αββα", "γαββαθα",
]


def analyses(book_num):

    for row in morphgnt_rows(book_num):
        text = row["text"]
        text1 = re.sub("[⸀⸂⸁⸄⸃\[\]\(\)⟦⟧12]", "", text)
        text2 = text1.lower()
        word = row["word"]
        norm = row["norm"]

        if (word, norm) in INCONSISTENCIES:
            continue

        capitalized = (
            text1[0] == text2[0].upper()
            and
            norm[0] != norm[0].upper()
        )

        parenthetical = (text[0] == "(")

        word = word.lower()
        norm = norm.lower()

        if norm.endswith("(ν)"):
            if strip_accents(word) == strip_accents(norm[:-3]):
                norm = norm[:-3]
            elif strip_accents(word) == strip_accents(norm[:-3]) + "ν":
                norm = norm[:-3] + "ν"

        if norm.endswith("(ς)"):
            if strip_accents(word) == strip_accents(norm[:-3]):
                norm = norm[:-3]
            elif strip_accents(word) == strip_accents(norm[:-3]) + "ς":
                norm = norm[:-3] + "ς"

        diff = (word != norm)

        elision = (word, norm) in ELISION
        movable = (word, norm) in MOVABLE

        if has_grave(word) and grave_to_acute(word) == norm:
            final_grave = True
            word2 = grave_to_acute(word)
        else:
            final_grave = False
            word2 = word

        if count_accents(word) > 1 and strip_last_accent(word) == norm:
            extra_accent = True
            word2 = strip_last_accent(word)
        else:
            extra_accent = False
            word2 = word

        if norm in PROCLITICS:
            proclitic = True
            if word != norm and strip_accents(word) == norm:
                proclitic_extra_accent = True
            else:
                proclitic_extra_accent = False
        else:
            proclitic = False
            proclitic_extra_accent = False

        if norm in ENCLITICS:
            enclitic = True
            if word != norm and strip_last_accent(norm) == word:
                enclitic_lost_accent = True
            else:
                enclitic_lost_accent = False
        else:
            enclitic = False
            enclitic_lost_accent = False

        if word in ["οὐκ", "καὶ", "τοῦτ’", "ἀλλ’", "εἰ"]:
            pre_esti_exception = True
        else:
            pre_esti_exception = False

        if "\u0301" not in unicodedata.normalize("NFD", word2) and \
                "\u0342" not in unicodedata.normalize("NFD", word2):
            if final_grave:
                accent_type = "1A"
            else:
                accent_type = "--"
        else:
            accent_type2 = get_accent_type(word2)
            accent_type = str(accent_type2[0]) + \
                {"\u0301": "A", "\u0342": "C"}[accent_type2[1]]

        enclitic_extra_accent = False
        esti = False
        if word in ["ἔστι", "ἔστιν"]:
            esti = True
            accent_type = "??"  # temporary: will change below
        elif proclitic_extra_accent:
            accent_type = "##"
        elif norm in UNACCENTED_FOREIGN:
            assert norm == strip_accents(norm)
            accent_type = "UF"
        else:
            if diff:
                if not elision and not movable and not final_grave and \
                        not extra_accent and not enclitic_lost_accent:
                    assert enclitic
                    enclitic_extra_accent = True
            if norm == strip_accents(norm):
                assert proclitic or enclitic

        punc = None
        if text2 != word:
            if text2[0] == "—":
                assert text2[1:] == word
            elif text2[-2:] in [";—", ".—", ",—"]:
                assert text2[:-2] == word
                punc = text2[-2]
            else:
                assert text2[:-1] == word, (text2, word)
                punc = text2[-1]

        yield {
            "diff": diff,
            "capitalized": capitalized,
            "parenthetical": parenthetical,
            "proclitic": proclitic,
            "enclitic": enclitic,
            "elision": elision,
            "movable": movable,
            "final_grave": final_grave,
            "extra_accent": extra_accent,
            "proclitic_extra_accent": proclitic_extra_accent,
            "enclitic_extra_accent": enclitic_extra_accent,
            "enclitic_lost_accent": enclitic_lost_accent,
            "pre_esti_exception": pre_esti_exception,
            "esti": esti,
            "punc": punc,
            "accent_type": accent_type,
            "word": word,
            "norm": norm,
            "row": row,
        }


for book_num in range(1, 28):
    for prev, this, following in trigrams(analyses(book_num)):

        if prev and (
            prev["proclitic_extra_accent"] or prev["enclitic_extra_accent"]
        ):
            assert this["enclitic"]

        esti_emph = False
        if this["esti"]:
            if not prev or prev["pre_esti_exception"] or prev["punc"]:
                this["accent_type"] = "E#"
            else:
                esti_emph = True
                this["accent_type"] = "EM"
        accent_type = this["accent_type"]

        flags = (
            "#" if this["diff"] else "-"
        ) + "::" + "".join([
            "#" if val else "-"
            for val in [
                prev and prev["proclitic_extra_accent"],
                prev and prev["enclitic_extra_accent"],
                prev and prev["pre_esti_exception"],
                not prev or prev["punc"],
            ]
        ]) + ":" + (prev["accent_type"] if prev else "--") + "::" + "".join([
            "#" if val else "-"
            for val in [
                this["proclitic"],
                this["pre_esti_exception"],
                this["enclitic"],
            ]
        ]) + "::" + "".join([
            "#" if val else "-"
            for val in [
                this["capitalized"],
                this["parenthetical"],
                this["elision"],
                this["movable"],
                this["esti"],
                esti_emph,
            ]
        ]) + ":" + "".join([
            "#" if val else "-"
            for val in [
                this["final_grave"],
                this["extra_accent"],
                this["proclitic_extra_accent"],
                this["enclitic_extra_accent"],
                this["enclitic_lost_accent"],
            ]
        ]) + ":" + accent_type + "::" + (
            "#" if bool(this["punc"]) else "-"
        ) + ":" + "".join([
            "#" if val else "-"
            for val in [
                following and following["capitalized"],
                following and following["parenthetical"],
                following and following["enclitic"],
            ]
        ])

        print(
            this["row"]["bcv"],
            flags,
            this["row"]["text"],
            this["row"]["norm"],
            this["row"]["lemma"]
        )

        if this["punc"] not in [None, ","] and this["final_grave"]:
            assert (this["row"]["bcv"], this["row"]["text"]) in [
                ("071302", "ἐὰν⸅"),  # has grave despite textual variant symbol
                ("071437", "⸀ἐστὶν·"),  # has grave despite colon
                #                        partly due to being textual variant?
            ]

        if this["accent_type"] == "1A" and not this["final_grave"] and \
                not this["punc"] and \
                not following["parenthetical"] and \
                not following["capitalized"] and \
                not following["enclitic"] and \
                not this["row"]["lemma"] in ["τίς", "ἱνατί"]:

            assert (this["row"]["bcv"], this["row"]["text"]) in [
                ("011514", "ὁδηγοί"),  # due to textual variant?
                ("011515", "παραβολήν"),  # due to textual variant?
                ("020727", "γάρ"),  # due to textual variant?
                ("020947", "καλόν"),  # due to textual variant?
                ("032339", "αὐτόν"),  # due to textual variant?
                ("050906", "⸂ὅ"),  # textual variant or something else?
                ("060834", "ὅς"),  # due to textual variant?
                ("270911", "Ἀβαδδών"),  # due to textual variant?

                ("071416", "Ἀμήν"),  # some texts have comma but not SBLGNT?

                ("012115", "Δαυίδ"),  # why?
                ("020402", "πολλά"),  # why?
                ("031805", "αὐτήν"),  # why?
                ("051029", "μεταπεμφθείς"),  # why?
                ("190306", "⸀ὅς"),  # why?
                ("190810", "θεόν"),  # why?
            ]

# 070916 good example of a trigram condition (plus others in same commit)
