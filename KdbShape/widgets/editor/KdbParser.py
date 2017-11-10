import collections
import re
import string
from enum import IntEnum

Language = frozenset("xyz")

Controls = frozenset(
    {"do", "if", "while", "select", "update", "delete", "exec", "from", "by", "and", "or", "except", "inter", "like",
     "each", "cross", "vs", "sv", "within", "where", "in", "asof",
     "bin", "binr", "cor", "cov", "cut", "ej", "fby", "div", "ij", "insert", "lj", "ljf", "mavg", "mcount",
     "mdev", "mmax", "mmin", "mmu", "mod", "msum", "over", "prior", "peach", "pj", "scan", "scov", "setenv",
     "ss", "sublist", "uj", "union", "upsert", "wavg", "wsum", "xasc", "xbar", "xcol", "xcols", "xdesc",
     "xexp", "xgroup", "xkey", "xlog", "xprev", "xrank"})

Functions = frozenset(
    {"first", "enlist", "value", "type", "get", "set", "count", "string", "key", "max", "min", "sum", "prd",
     "last", "flip", "distinct", "raze", "neg", "til", "upper", "lower", "abs", "acos", "aj", "aj0", "not",
     "null", "any", "asc", "asin", "attr", "avg", "avgs", "ceiling", "cols", "cos", "csv", "all", "atan",
     "deltas", "desc", "differ", "dsave", "dev", "eval", "exit", "exp", "fills", "fkeys", "floor", "getenv",
     "group", "gtime", "hclose", "hcount", "hdel", "hopen", "hsym", "iasc", "idesc", "inv", "keys", "load",
     "log", "lsq", "ltime", "ltrim", "maxs", "md5", "med", "meta", "mins", "next", "parse", "plist", "prds",
     "prev", "rand", "rank", "ratios", "read0", "read1", "reciprocal", "reverse", "rload", "rotate",
     "rsave", "rtrim", "save", "sdev", "show", "signum", "sin", "sqrt", "ssr", "sums", "svar", "system",
     "tables", "tan", "trim", "txf", "ungroup", "var", "view", "views", "wj", "wj1", "ww"})

KdbToken = collections.namedtuple("KdbToken", "token pos style")

re_keyword = re.compile(r"[a-zA-Z][a-zA-Z0-9_.]*")
re_variable = re.compile(r"\.[a-zA-Z][a-zA-Z0-9_.]*")
re_const = re.compile(r"0[nNwW][hijefcpmdznuvtg]?")
re_datetime = re.compile(
    r"(?:\d+D|\d\d\d\d\.[01]\d\.[0123]\d[DT])(?:[012]\d:[0-5]\d(?::[0-5]\d(?:\.\d+)?)?|([012]\d)?)[zpn]?")
re_time = re.compile(r"[012]\d:[0-5]\d(?::[0-5]\d(\.\d+)?)?[uvtpn]?")
re_date = re.compile(r"\d{4}\.[01]\d\.[0-3]\d[dpnzm]?")
re_float = re.compile(r"(?:(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+|\d+\.\d*|\.\d+)[efpntm]?")
re_int = re.compile(r"(0x[0-9a-fA-F]+|\d+[bhicjefpnuvt]?)")
re_function = re.compile(r"-[1-9][0-9]?\s*!")
re_guid = re.compile(r"[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}")
re_sym = re.compile(r"(`:[:a-zA-Z0-9._/]*|`(?:[a-zA-Z0-9.][:a-zA-Z0-9._]*)?)")
re_operator1 = re.compile(r"('|/:|\\:|':|\\|/|0:|1:|2:)")
re_operator2 = re.compile(r"(?:<=|>=|<>|::)|(?:[$%&@._#*^\-+~,!><=|?:]):?")


class KdbStyle(IntEnum):
    name = 1
    string = 2
    variable = 3
    command = 4
    const = 5
    sym = 6
    type_guid = 7
    type_float = 8
    type_int = 9
    type_datetime = 10
    type_time = 11
    type_date = 12
    keyword_language = 13
    keyword_function = 14
    keyword_control = 15
    keyword_operator = 16
    comment = 17
    text = 20

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class KdbParser:
    @staticmethod
    def get_token_value(reg, line, pos):
        tok = reg.match(line, pos)
        return None if tok is None else tok.group(0)

    def get_next_token(self, line, pos):
        if pos == 0 or line[pos - 1] not in string.ascii_letters + string.digits:
            # Keywords & names
            tok = self.get_token_value(re_keyword, line, pos)
            if tok:
                st = KdbStyle.name
                if tok in Language:
                    st = KdbStyle.keyword_language
                elif tok in Controls:
                    st = KdbStyle.keyword_control
                elif tok in Functions:
                    st = KdbStyle.keyword_function
                return tok, st

            # Function & Variable
            tok = self.get_token_value(re_variable, line, pos)
            if tok:
                if len(tok) > 2 and tok[2] == '.' and tok[1] in "qQhoz":
                    return tok, KdbStyle.keyword_function
                else:
                    return tok, KdbStyle.variable

            # All other patterns
            for r, st in ((re_guid, KdbStyle.type_guid), (re_const, KdbStyle.const),
                          (re_date, KdbStyle.type_date), (re_time, KdbStyle.type_time),
                          (re_datetime, KdbStyle.type_datetime), (re_float, KdbStyle.type_float),
                          (re_function, KdbStyle.keyword_function), (re_int, KdbStyle.type_int)):
                tok = self.get_token_value(r, line, pos)
                if tok:
                    return tok, st

        for r, st in ((re_sym, KdbStyle.sym), (re_operator1, KdbStyle.keyword_operator),
                      (re_operator2, KdbStyle.keyword_operator)):
            tok = self.get_token_value(r, line, pos)
            if tok:
                return tok, st

        return line[pos], KdbStyle.text

    def invalidate(self, text, start, end):
        state = 'q'
        offset = 0
        marker = 0
        tokens = []

        for i, line in enumerate(text[start:end].splitlines(1)):
            pos = 0
            while pos < len(line):
                if state == 'str':
                    b = False
                    while pos < len(line) and (line[pos] != '"' or b):
                        b = False if b else line[pos] == '\\'
                        pos += 1

                    if pos == len(line):
                        continue
                    else:
                        state = 'q'
                        tok, st = (text[marker:offset + pos + 1], KdbStyle.string)
                        pos -= len(tok) - 1  # move back. will be added at last step
                elif line[pos] == '"':
                    marker = offset + pos
                    pos += 1
                    state = 'str'
                    continue
                elif line[pos] == '\\' and pos == 0 and line[pos + 1] in string.whitespace:
                    tokens.append(KdbToken(text[offset + pos:len(text)], offset + pos, KdbStyle.comment))
                    return tokens  # Global end comment. Nothing to do anymore
                elif line[pos] == '/' and (pos == 0 or pos > 0 and line[pos - 1] in string.whitespace):  # Simple
                    tok, st = (line[pos:len(line)], KdbStyle.comment)
                else:
                    tok, st = self.get_next_token(line, pos)

                # If it's text and previous text - just add to previous or append new token
                if st == KdbStyle.text and len(tokens) and tokens[-1].style == KdbStyle.text:
                    tn = tokens[-1]
                    tokens[-1] = KdbToken(tn.token + tok, tn.pos, tn.style)
                else:
                    tokens.append(KdbToken(tok, offset + pos, st))
                pos += len(tok)

            offset += pos
        return tokens
