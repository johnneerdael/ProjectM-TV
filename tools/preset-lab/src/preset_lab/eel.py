import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Expr:
    kind: str
    value: str = ""
    children: tuple = ()
    line: int = 1


def tokenize(code: str) -> list[tuple[str, int]]:
    def blank(match):
        return "".join("\n" if c == "\n" else " " for c in match.group())
    code = re.sub(r"/\*.*?\*/|//[^\n]*", blank, code, flags=re.S)
    pattern = re.compile(r"\s+|(?:0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)[fF]?|[A-Za-z_]\w*|(?:==|!=|<=|>=|\+=|-=|\*=|/=|%=|&&|\|\||\+\+|--|<<|>>|&=|\|=)|[+*/%\-^<>=!&|?:,;(){}\[\].]")
    tokens, offset, line = [], 0, 1
    for match in pattern.finditer(code):
        if match.start() != offset:
            raise ValueError(f"unsupported token at code line {line}")
        text = match.group()
        if not text.isspace():
            tokens.append((text, line))
        line += text.count("\n")
        offset = match.end()
    if offset != len(code):
        raise ValueError(f"unsupported trailing syntax at code line {line}")
    return tokens + [("<end>", line)]


class Parser:
    PRECEDENCE = {"=": 1, "+=": 1, "-=": 1, "*=": 1, "/=": 1, "%=": 1, "&=": 1, "|=": 1,
                  "?": 2, "||": 3, "&&": 4, "|": 5, "&": 6,
                  "==": 7, "!=": 7, "<": 8, ">": 8, "<=": 8, ">=": 8,
                  "<<": 9, ">>": 9, "+": 10, "-": 10, "*": 11, "/": 11, "%": 11, "^": 12}

    def __init__(self, code: str, case_sensitive: bool = False):
        self.tokens = tokenize(code)
        self.index = 0
        self.case_sensitive = case_sensitive

    def peek(self) -> str:
        return self.tokens[self.index][0]

    def take(self, expected: str | None = None) -> tuple[str, int]:
        token = self.tokens[self.index]
        if expected is not None and token[0] != expected:
            raise ValueError(f"expected {expected!r} at code line {token[1]}, found {token[0]!r}")
        self.index += 1
        return token

    def expression(self, minimum: int = 0) -> Expr:
        text, line = self.take()
        if re.match(r"^[A-Za-z_]", text):
            left = Expr("var", text if self.case_sensitive else text.lower(), line=line)
        elif re.match(r"^(?:\d|\.\d)", text):
            left = Expr("constant", text, line=line)
        elif text in ("+", "-", "!"):
            left = Expr("unary", text, (self.expression(13),), line)
        elif text == "(":
            children = []
            while self.peek() != ")":
                children.append(self.expression())
                if self.peek() == ";":
                    self.take()
                    if self.peek() == ")":
                        break
                else:
                    break
            self.take(")")
            left = Expr("sequence", children=tuple(children), line=line)
        else:
            raise ValueError(f"unsupported expression {text!r} at code line {line}")
        while True:
            op = self.peek()
            if op == "(":
                if left.kind != "var":
                    raise ValueError("unsupported indirect function call")
                self.take()
                args = []
                while self.peek() != ")":
                    args.append(self.expression())
                    if self.peek() != ",":
                        break
                    self.take()
                self.take(")")
                left = Expr("call", left.value, tuple(args), line)
                continue
            if op == ".":
                self.take()
                member, _ = self.take()
                left = Expr("member", member, (left,), line)
                continue
            if op == "[":
                self.take()
                subscript = self.expression()
                self.take("]")
                left = Expr("index", children=(left, subscript), line=line)
                continue
            precedence = self.PRECEDENCE.get(op, -1)
            if precedence < minimum:
                break
            self.take()
            if op == "?":
                yes = self.expression()
                self.take(":")
                left = Expr("branch", children=(left, yes, self.expression(precedence)), line=line)
                continue
            assignment = op.endswith("=") and op not in ("==", "!=", "<=", ">=")
            right = self.expression(precedence if assignment or op == "^" else precedence + 1)
            left = Expr("assign" if assignment else "binary", op, (left, right), line)
        return left

    def statements(self, terminator: str = "<end>") -> Expr:
        children = []
        while self.peek() != terminator:
            if self.peek() == ";":
                self.take()
                continue
            children.append(self.expression())
            if self.peek() not in (";", terminator):
                raise ValueError(f"unsupported statement separator {self.peek()!r}")
        return Expr("sequence", children=tuple(children))


def parse_eel(code: str) -> Expr:
    return Parser(code).statements()
