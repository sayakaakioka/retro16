import re
from typing import NamedTuple, Literal, List

from .lang import (
    Program,
    Stmt,
    Assign,
    While,
    If,
    Cond,
    Const,
    CmpZero,
    Cmp,
    Expr,
    BinOp,
    Var,
)

TokenKind = Literal[
    "IDENT",
    "INT",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "EQ",
    "EQEQ",
    "NEQ",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "SEMICOLON",
    "WHILE",
    "IF",
    "ELSE",
    "WS",
    "EOF",
]


class Token(NamedTuple):
    kind: TokenKind
    value: str
    pos: int


KEYWORDS = {
    "while": "WHILE",
    "if": "IF",
    "else": "ELSE",
}

TOKEN_SPEC = [
    ("WS", r"[ \t\n\r]+"),
    ("INT", r"-?\d+"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("EQEQ", r"=="),
    ("NEQ", r"!="),
    ("EQ", r"="),  # define EQEQ, NEQ, EQ in this order for the correct parse
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
]

MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    for m in MASTER_RE.finditer(src):
        kind = m.lastgroup
        text = m.group()
        pos = m.start()

        if kind == "WS":
            continue
        elif kind == "IDENT" and text in KEYWORDS:
            tokens.append(Token(KEYWORDS[text], text, pos))
        else:
            tokens.append(Token(kind, text, pos))

    tokens.append(Token("EOF", "", len(src)))
    return tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def cur(self) -> Token:
        return self.tokens[self.pos]

    def eat(self, kind: TokenKind) -> Token:
        tok = self.cur()
        if tok.kind != kind:
            raise SyntaxError(f"expeced {kind}, got {tok.kind} at {tok.pos}")
        self.pos += 1
        return tok

    def parse_program(self) -> Program:
        stmts: List[Stmt] = []
        while self.cur().kind != "EOF":
            stmts.append(self.parse_stmt())
        return Program(stmts=stmts)

    def parse_stmt(self) -> Stmt:
        tok = self.cur()
        if tok.kind == "IDENT":
            # IDENT '=' expr ';'
            name = self.eat("IDENT").value
            self.eat("EQ")
            expr = self.parse_expr()
            self.eat("SEMICOLON")
            return Assign(name=name, expr=expr)

        if tok.kind == "WHILE":
            return self.parse_while()

        if tok.kind == "IF":
            return self.parse_if()

        raise SyntaxError(f"unexpeced token {tok.kind} at {tok.pos}")

    def parse_while(self) -> While:
        self.eat("WHILE")
        self.eat("LPAREN")
        cond = self.parse_cond()
        self.eat("RPAREN")
        body = self.parse_block()
        return While(cond=cond, body=body)

    def parse_if(self) -> If:
        self.eat("IF")
        self.eat("LPAREN")
        cond = self.parse_cond()
        self.eat("RPAREN")
        then_body = self.parse_block()
        else_body: List[Stmt] | None = None

        if self.cur().kind == "ELSE":
            self.eat("ELSE")
            else_body = self.parse_block()

        return If(cond=cond, then_body=then_body, else_body=else_body)

    def parse_block(self) -> List[Stmt]:
        self.eat("LBRACE")
        stmts: List[Stmt] = []
        while self.cur().kind != "RBRACE":
            stmts.append(self.parse_stmt())
        self.eat("RBRACE")
        return stmts

    def parse_cond(self) -> Cond:
        # cond: expr ("==" | "!=") expr
        left = self.parse_expr()
        tok = self.cur()
        if tok.kind == "EQEQ":
            self.eat("EQEQ")
            right = self.parse_expr()

            # expr == 0 ?
            if isinstance(right, Const) and right.value == 0:
                return CmpZero(expr=left, op="==")
            else:
                return Cmp(left=left, op="==", right=right)

        elif tok.kind == "NEQ":
            self.eat("NEQ")
            right = self.parse_expr()

            # expr == 0 ?
            if isinstance(right, Const) and right.value == 0:
                return CmpZero(expr=left, op="!=")
            else:
                return Cmp(left=left, op="!=", right=right)

        else:
            raise SyntaxError(f"unexpected == or != in condition at {tok.pos}")

    def parse_expr(self) -> Expr:
        expr = self.parse_primary()
        while self.cur().kind in ("PLUS", "MINUS"):
            op_tok = self.cur()
            if op_tok.kind == "PLUS":
                self.eat("PLUS")
                right = self.parse_primary()
                expr = BinOp(op="+", left=expr, right=right)
            else:
                self.eat("MINUS")
                right = self.parse_primary()
                expr = BinOp(op="-", left=expr, right=right)
        return expr

    def parse_primary(self) -> Expr:
        tok = self.cur()
        if tok.kind == "INT":
            value = int(self.eat("INT").value)
            return Const(value=value)

        if tok.kind == "IDENT":
            name = self.eat("IDENT").value
            return Var(name=name)

        if tok.kind == "LPAREN":
            self.eat("LPAREN")
            expr = self.parse_expr()
            self.eat("RPAREN")
            return expr

        raise SyntaxError(f"unexpected token {tok.kind} in expr at {tok.pos}")


# entry point
def parse_program(src: str) -> Program:
    tokens = tokenize(src)
    p = Parser(tokens)
    return p.parse_program()
