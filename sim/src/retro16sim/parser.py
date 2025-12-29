import re
from typing import NamedTuple, Literal, List

from .lang import (
    Program,
    Stmt,
    Assign,
    While,
    If,
    Literal as LitExpr,
    Expr,
    UnaryOp,
    BinaryOp,
    Var,
)

TokenKind = Literal[
    "IDENT",
    "INT",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "EQEQ",
    "EQ",
    "NEQ",
    "LT",
    "LE",
    "GT",
    "GE",
    "ANDAND",
    "OROR",
    "BAMG",
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
    # multi characters first
    ("LE", r"<="),
    ("GE", r">="),
    ("EQEQ", r"=="),
    ("NEQ", r"!="),
    ("LT", r"<"),
    ("GT", r">"),
    ("ANDAND", r"&&"),
    ("OROR", r"\|\|"),
    ("BANG", r"!"),
    ("EQ", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
]

MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []
    for m in MASTER_RE.finditer(src):
        kind = m.lastgroup
        text = m.group()
        pos = m.start()

        if kind == "WS":
            continue
        if kind == "IDENT" and text in KEYWORDS:
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
        cond = self.parse_expr()
        self.eat("RPAREN")
        body = self.parse_block()
        return While(cond=cond, body=body)

    def parse_if(self) -> If:
        self.eat("IF")
        self.eat("LPAREN")
        cond = self.parse_expr()
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

    # ---- expression grammar (precedence) ----
    # expr        := equality
    # equality    := relational ( (==|!=) relational )*
    # relational  := additive ( (<|<=|>|>=) additive )*
    # additive    := term ( (+|-) term )*
    # term        := unary ( (*|/) unary )*
    # unary       := ('+'|'-'|'!') unary | primary
    # primary     := INT | IDENT | '(' expr ')'

    def parse_expr(self) -> Expr:
        return self.parse_equality()

    def parse_equality(self) -> Expr:
        expr = self.parse_relational()
        while self.cur().kind in ("EQEQ", "NEQ"):
            if self.cur().kind == "EQEQ":
                self.eat("EQEQ")
                right = self.parse_relational()
                expr = BinaryOp(left=expr, op="==", right=right)
            else:
                self.eat("NEQ")
                right = self.parse_relational()
                expr = BinaryOp(left=expr, op="!=", right=right)
        return expr

    def parse_relational(self) -> Expr:
        expr = self.parse_additive()
        while self.cur().kind in ("LT", "LE", "GT", "GE"):
            tok = self.cur()
            if tok.kind == "LT":
                self.eat("LT")
                right = self.parse_additive()
                expr = BinaryOp(left=expr, op="<", right=right)
            elif tok.kind == "LE":
                self.eat("LE")
                right = self.parse_additive()
                expr = BinaryOp(left=expr, op="<=", right=right)
            elif tok.kind == "GT":
                self.eat("GT")
                right = self.parse_additive()
                expr = BinaryOp(left=expr, op=">", right=right)
            else:
                self.eat("GE")
                right = self.parse_additive()
                expr = BinaryOp(left=expr, op=">=", right=right)
        return expr

    def parse_additive(self) -> Expr:
        expr = self.parse_term()
        while self.cur().kind in ("PLUS", "MINUS"):
            if self.cur().kind == "PLUS":
                self.eat("PLUS")
                right = self.parse_term()
                expr = BinaryOp(left=expr, op="+", right=right)
            else:
                self.eat("MINUS")
                right = self.parse_term()
                expr = BinaryOp(left=expr, op="-", right=right)
        return expr

    def parse_term(self) -> Expr:
        expr = self.parse_unary()
        while self.cur().kind in ("STAR", "SLASH"):
            if self.cur().kind == "STAR":
                self.eat("STAR")
                right = self.parse_unary()
                expr = BinaryOp(left=expr, op="*", right=right)
            else:
                self.eat("SLASH")
                right = self.parse_unary()
                expr = BinaryOp(left=expr, op="/", right=right)
        return expr

    def parse_unary(self) -> Expr:
        tok = self.cur()
        if tok.kind == "PLUS":
            self.eat("PLUS")
            return self.parse_unary()
        if tok.kind == "MINUS":
            self.eat("MINUS")
            # -E -> 0 - E
            return UnaryOp(op="-", expr=self.parse_unary())
        if tok.kind == "BANG":
            self.eat("BANG")
            return UnaryOp(op="!", expr=self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> Expr:
        tok = self.cur()
        if tok.kind == "INT":
            value = int(self.eat("INT").value)
            return LitExpr(value=value)

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
    return Parser(tokenize(src)).parse_program()
