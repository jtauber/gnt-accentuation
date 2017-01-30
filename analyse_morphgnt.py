#!/usr/bin/env python3

import re
import unicodedata

from greek_accentuation.accentuation import get_accent_type
from pysblgnt import morphgnt_rows


def strip_accents(s):
    return unicodedata.normalize("NFC", "".join((c for c in unicodedata.normalize("NFD", s) if c not in ["\u0300", "\u0301", "\u0342"])))


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
    # "μοῦ", "μοί", "μέ",
    # "σου", "σοί", "σέ",
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


for book_num in range(1, 28):
    prev_word = None
    prev_proclitic_extra_accent = None
    prev_enclitic_extra_accent = None

    for row in morphgnt_rows(book_num):
        text = re.sub("[⸀⸂⸁⸃\[\]\(\)—⸄⟦⟧12]", "", row["text"]).lower()
        word = row["word"]
        norm = row["norm"]

        if (word, norm) in INCONSISTENCIES:
            continue

        word = word.lower()
        norm = norm.lower()

        if norm.endswith("(ν)"):
            if strip_accents(word) == strip_accents(norm[:-3]):
                norm = norm[:-3]
            if strip_accents(word) ==  strip_accents(norm[:-3]) + "ν":
                norm = norm[:-3] + "ν"

        if norm.endswith("(ς)"):
            if strip_accents(word) == strip_accents(norm[:-3]):
                norm = norm[:-3]
            if strip_accents(word) ==  strip_accents(norm[:-3]) + "ς":
                norm = norm[:-3] + "ς"

        if (word, norm) in ELISION:
            elision = True
        else:
            elision = False

        if (word, norm) in MOVABLE:
            movable = True
        else:
            movable = False

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

        flags = "".join([
            "*" if val else "-"
            for val in [proclitic, enclitic]
        ]) + " " + "".join([
            "*" if val else "-"
            for val in [elision, movable, final_grave, extra_accent, proclitic_extra_accent, enclitic_lost_accent]
        ])

        if "\u0301" not in unicodedata.normalize("NFD", word2) and "\u0342" not in unicodedata.normalize("NFD", word2):
            at = "--"
        else:
            accent_type = get_accent_type(word2)
            at = str(accent_type[0]) + {"\u0301": "A", "\u0342": "C"}[accent_type[1]]

        if prev_proclitic_extra_accent or prev_enclitic_extra_accent:
            assert enclitic

        prev_proclitic_extra_accent = False
        prev_enclitic_extra_accent = False

        if word in ["ἔστι", "ἔστιν"]:
            if prev_word in [None, "οὐκ", "καὶ", "τοῦτ’", "ἀλλ’", "εἰ"]:
                print(flags, "**", word, norm, row["ccat-pos"], row["bcv"])
            else:
                print(flags, "EM", word, norm, row["ccat-pos"], row["bcv"])
        elif proclitic_extra_accent:
            print(flags, "**", word, norm, row["ccat-pos"], row["bcv"])
            prev_proclitic_extra_accent = True
        elif norm in UNACCENTED_FOREIGN:
            assert norm == strip_accents(norm)
            print(flags, "UF", word, norm, row["ccat-pos"], row["bcv"])
        else:
            print(flags, at, word, norm, row["ccat-pos"], row["bcv"])
            if word != norm:
                if not elision and not movable and not final_grave and not extra_accent and not enclitic_lost_accent:
                    assert enclitic
                    prev_enclitic_extra_accent = True
            if norm == strip_accents(norm):
                assert proclitic or enclitic
        prev_word = word

        if text != word:
            if text[:-1] == word:
                print(text[-1])
                prev_word = None
            else:
                assert False
