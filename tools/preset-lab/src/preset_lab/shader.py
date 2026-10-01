import re

from .eel import Expr, Parser


class ShaderParser(Parser):
    def __init__(self, code: str):
        super().__init__(code, case_sensitive=True)

    def statement(self) -> Expr:
        if self.peek() == "{":
            self.take()
            block = self.statements("}")
            self.take("}")
            return Expr("scope", children=block.children)
        if self.peek() == "shader_body":
            self.take()
            return self.statement()
        if self.peek() == "if":
            _, line = self.take()
            self.take("(")
            condition = self.expression()
            self.take(")")
            yes = self.statement()
            no = Expr("sequence")
            if self.peek() == "else":
                self.take()
                no = self.statement()
            return Expr("branch", children=(condition, yes, no), line=line)
        if self.peek() in ("for", "while", "do", "return", "discard", "struct", "#"):
            raise ValueError(f"unsupported shader control/function syntax: {self.peek()}")
        if self.peek() in ("const", "static", "uniform"):
            self.take()
        if re.fullmatch(r"(?:float|half|int|uint|bool|sampler|matrix)(?:[1-4](?:x[1-4])?)?", self.peek()):
            self.take()
            declarations = []
            while True:
                name, line = self.take()
                if self.peek() == "(":
                    raise ValueError("unsupported shader helper function definition")
                value = Expr("constant", "0", line=line)
                if self.peek() == "=":
                    self.take()
                    value = self.expression(2)
                declarations.append(Expr("declare", name, (value,), line))
                if self.peek() != ",":
                    break
                self.take()
            self.take(";")
            return Expr("sequence", children=tuple(declarations))
        node = self.expression()
        self.take(";")
        return node

    def statements(self, terminator: str = "<end>") -> Expr:
        nodes = []
        while self.peek() != terminator:
            if self.peek() == ";":
                self.take()
            else:
                nodes.append(self.statement())
        return Expr("sequence", children=tuple(nodes))


def parse_shader(code: str) -> Expr:
    return ShaderParser(code).statements()
