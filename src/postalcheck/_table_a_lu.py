"""Rules for countries AC to LU, transcribed from the libaddressinput ``zip`` patterns.

Patterns match the compact code (no separators, upper case). Examples are the first
``zipex`` code of each country in its canonical layout.
"""

from __future__ import annotations

from ._rules import (
    Rule,
    british,
    digits,
    drop_prefix,
    rule,
    tail,
    when_length,
    zip_plus_four,
)

GB_AREAS = (
    "AB|AL|B|BA|BB|BD|BF|BH|BL|BN|BR|BS|BT|BX|CA|CB|CF|CH|CM|CO|CR|CT|CV|CW|DA|DD|DE|DG|DH|"
    "DL|DN|DT|DY|E|EC|EH|EN|EX|FK|FY|G|GL|GY|GU|HA|HD|HG|HP|HR|HS|HU|HX|IG|IM|IP|IV|JE|KA|"
    "KT|KW|KY|L|LA|LD|LE|LL|LN|LS|LU|M|ME|MK|ML|N|NE|NG|NN|NP|NR|NW|OL|OX|PA|PE|PH|PL|PO|"
    "PR|RG|RH|RM|S|SA|SE|SG|SK|SL|SM|SN|SO|SP|SR|SS|ST|SW|SY|TA|TD|TF|TN|TQ|TR|TS|TW|UB|W|"
    "WA|WC|WD|WF|WN|WR|WS|WV|YO|ZE"
)
# The inward code never uses C, I, K, M, O or V as a letter.
INWARD = r"\d[ABD-HJLN-UW-Z]{2}"
UK_STYLE = rf"\d[\dA-Z]?{INWARD}"

RULES_A_LU: dict[str, Rule] = {
    "AC": rule(r"ASCN1ZZ", "ASCN 1ZZ", tail(" ", 3)),
    "AD": rule(r"AD[1-7]0\d", "AD100"),
    "AF": digits(4, "1001"),
    "AI": rule(r"(?:AI)?2640", "2640", drop_prefix("AI"), extra=(2,)),
    "AL": digits(4, "1001"),
    "AM": rule(r"(?:37)?\d{4}", "375010"),
    # Argentina: the eight-character CPA, plus the four-digit code it extends, which is
    # still printed on most addresses (and was accepted by 0.1.0).
    "AR": rule(r"[A-HJ-NP-Z]\d{4}[A-Z]{3}|\d{4}", "C1070AAM"),
    "AS": rule(r"96799(?:\d{4})?", "96799", zip_plus_four),
    "AT": digits(4, "1010"),
    "AU": digits(4, "2060"),
    "AX": rule(r"22\d{3}", "22150"),
    "AZ": digits(4, "1000"),
    "BA": digits(5, "71000"),
    "BB": rule(r"BB\d{5}", "BB23026"),
    "BD": digits(4, "1340"),
    "BE": digits(4, "4000"),
    "BG": digits(4, "1000"),
    "BH": rule(r"(?:1[0-2]|[1-9])\d{2}", "317"),
    "BL": rule(r"9[78][01]\d{2}", "97100"),
    "BM": rule(r"[A-Z]{2}[A-Z0-9]{2}", "FL 07", tail(" ", 2)),
    "BN": rule(r"[A-Z]{2}\d{4}", "BT2328", extra=(2,)),
    "BR": rule(r"\d{8}", "40301-110", tail("-", 3)),
    "BT": digits(5, "11001"),
    "BY": digits(6, "223016"),
    "CA": rule(
        r"[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z]\d[ABCEGHJ-NPRSTV-Z]\d", "H3Z 2Y7", tail(" ", 3)
    ),
    "CC": rule(r"6799", "6799"),
    "CH": digits(4, "2544"),
    "CL": digits(7, "8340457"),
    "CN": digits(6, "266033"),
    "CO": digits(6, "111221"),
    "CR": rule(r"\d{4,5}|\d{7}", "1000", when_length(7, tail("-", 4))),
    "CU": digits(5, "10700"),
    "CV": digits(4, "7600"),
    "CX": rule(r"6798", "6798"),
    "CY": digits(4, "2008"),
    "CZ": rule(r"\d{5}", "100 00", tail(" ", 2)),
    "DE": digits(5, "26133"),
    "DK": digits(4, "8660"),
    "DO": digits(5, "11903"),
    "DZ": digits(5, "40304"),
    "EC": digits(6, "090105"),
    "EE": digits(5, "69501"),
    "EG": rule(r"\d{7}|\d{5}", "4460232"),
    "EH": digits(5, "70000"),
    "ES": digits(5, "28039"),
    "ET": digits(4, "1000"),
    "FI": digits(5, "00550"),
    "FK": rule(r"FIQQ1ZZ", "FIQQ 1ZZ", tail(" ", 3)),
    "FM": rule(r"9694[1-4](?:\d{4})?", "96941", zip_plus_four),
    "FO": digits(3, "100"),
    "FR": rule(r"\d{5}", "33380", extra=(2,)),
    "GB": rule(rf"GIR0AA|(?:{GB_AREAS}){UK_STYLE}|BFPO\d{{1,4}}", "EC1Y 8SY", british),
    "GE": digits(4, "0101"),
    "GF": rule(r"9[78]3\d{2}", "97300"),
    "GG": rule(rf"GY{UK_STYLE}", "GY1 1AA", tail(" ", 3)),
    "GI": rule(r"GX111AA", "GX11 1AA", tail(" ", 3)),
    "GL": rule(r"39\d{2}", "3900"),
    "GN": digits(3, "001"),
    "GP": rule(r"9[78][01]\d{2}", "97100"),
    "GR": rule(r"\d{5}", "151 24", tail(" ", 2)),
    "GS": rule(r"SIQQ1ZZ", "SIQQ 1ZZ", tail(" ", 3)),
    "GT": digits(5, "09001"),
    "GU": rule(r"969(?:[12]\d|3[12])(?:\d{4})?", "96910", zip_plus_four),
    "GW": digits(4, "1000"),
    "HM": digits(4, "7050"),
    "HN": digits(5, "31301"),
    "HR": digits(5, "10000"),
    "HT": digits(4, "6120"),
    "HU": digits(4, "1037"),
    "ID": digits(5, "40115"),
    # Ireland: routing key letters as used by the 139 published routing keys, and no
    # letter O anywhere (Eircode FAQ). Stricter than libaddressinput on purpose.
    "IE": rule(r"(?:[AC-FHKNPRTV-Y]\d\d|D6W)[0-9A-NP-Z]{4}", "A65 F4E2", tail(" ", 4)),
    "IL": rule(r"\d{5}(?:\d{2})?", "9614303"),
    "IM": rule(rf"IM{UK_STYLE}", "IM2 1AA", tail(" ", 3)),
    "IN": digits(6, "110034"),
    "IO": rule(r"BBND1ZZ", "BBND 1ZZ", tail(" ", 3)),
    "IQ": digits(5, "31001"),
    "IR": rule(r"\d{10}", "11936-12345", tail("-", 5)),
    "IS": digits(3, "320"),
    "IT": digits(5, "00144"),
    "JE": rule(rf"JE{UK_STYLE}", "JE1 1AA", tail(" ", 3)),
    "JO": digits(5, "11937"),
    "JP": rule(r"\d{7}", "154-0023", tail("-", 4)),
    "KE": digits(5, "20100"),
    "KG": digits(6, "720001"),
    "KH": rule(r"\d{5,6}", "120101"),
    "KR": digits(5, "03051"),
    "KW": digits(5, "54541"),
    "KY": rule(r"KY\d{5}", "KY1-1100", tail("-", 4)),
    "KZ": digits(6, "040900"),
    "LA": digits(5, "01160"),
    "LB": rule(r"\d{4}(?:\d{4})?", "2038 3054", when_length(8, tail(" ", 4))),
    "LI": rule(r"948[5-9]|949[0-8]", "9496"),
    "LK": digits(5, "20000"),
    "LR": digits(4, "1000"),
    "LS": digits(3, "100"),
    "LT": digits(5, "04340"),
    "LU": digits(4, "4750"),
}
