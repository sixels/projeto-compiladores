"""
Destino sugerido: %PROJETO%/src/lang/parser/expressions.py

Parser de expressões: precedence climbing + prefixos + primários.

    parse_expression(min_precedence) -> parse_prefix() -> parse_primary()
"""

from lang.ast import (
    ArrayLiteralExpr,
    BinaryExpr,
    CallExpr,
    Expr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
)
from lang.parser.base import ParserBase
from lang.tokens import (
    Delimiter,
    Keyword,
    Operator,
    TokenBool,
    TokenDecimal,
    TokenDelimiter,
    TokenEOF,
    TokenIdentifier,
    TokenInt,
    TokenKeyword,
    TokenOperator,
    TokenString,
)

# --------------------------------------------------------------------------
# Tabelas de operadores
# --------------------------------------------------------------------------

# Maior número = liga mais forte. Operadores fora da tabela (=, .., ->, !, &)
# nunca são consumidos como binários, então `a..b` e `x = ...` terminam a
# expressão naturalmente.
BINARY_PRECEDENCE: dict[Operator, int] = {
    Operator.OR: 1,
    Operator.AND: 2,
    Operator.EQ_EQ: 3,
    Operator.NOT_EQ: 3,
    Operator.LT: 4,
    Operator.GT: 4,
    Operator.LT_EQ: 4,
    Operator.GT_EQ: 4,
    Operator.PLUS: 5,
    Operator.MINUS: 5,
    Operator.STAR: 6,
    Operator.SLASH: 6,
    Operator.PERCENT: 6,
}

# STAR é unário (deref) e binário (multiplicação); o contexto decide.
UNARY_OPERATORS: set[Operator] = {
    Operator.PLUS,
    Operator.MINUS,
    Operator.BANG,
    Operator.AMPERSAND,
    Operator.STAR,
}


class ExpressionParser(ParserBase):
    """Mixin de expressões. Os demais módulos (statements, funções...) podem
    herdar desta classe, ou o Parser final pode herdar de todos os mixins."""

    # ---- nível 1: binários por precedência --------------------------------

    def parse_expression(self, min_precedence: int = 0) -> Expr:
        """Consome operadores binários com peso >= min_precedence."""
        left = self.parse_prefix()

        while True:
            tok = self.current()
            if type(tok) is not TokenOperator:
                break

            prec = BINARY_PRECEDENCE.get(tok.kind)
            if prec is None or prec < min_precedence:
                break

            self.advance()  # consome o operador
            # prec + 1 => associatividade à esquerda: a - b - c = (a - b) - c
            right = self.parse_expression(prec + 1)
            left = BinaryExpr(span=left.span, left=left, operator=tok.kind, right=right)

        return left

    # ---- nível 2: unários prefixados --------------------------------------

    def parse_prefix(self) -> Expr:
        """Trata +x, -x, !x, &x, *x (encadeáveis: !!x, -*p)."""
        tok = self.current()
        if type(tok) is TokenOperator and tok.kind in UNARY_OPERATORS:
            self.advance()
            # Recursão em parse_prefix: unário liga mais forte que qualquer
            # binário, então -a * b == (-a) * b.
            operand = self.parse_prefix()
            return UnaryExpr(span=tok.span, operator=tok.kind, operand=operand)
        return self.parse_primary()

    # ---- nível 3: primários ------------------------------------------------

    def parse_primary(self) -> Expr:
        """Literais, variáveis, chamadas, ( expr ) e [ a, b, c ]."""
        tok = self.current()

        match tok:
            case TokenInt(value, span) | TokenDecimal(value, span):
                self.advance()
                return LiteralExpr(span=span, value=value)

            case TokenString(value, span):
                self.advance()
                return LiteralExpr(span=span, value=value)

            case TokenBool(value, span):
                self.advance()
                return LiteralExpr(span=span, value=value)

            case TokenKeyword(kind, _) if kind in (
                Keyword.INT,
                Keyword.DECIMAL,
                Keyword.STRING,
                Keyword.BOOL,
            ):
                if getattr(self.peek(), "kind", None) == Delimiter.LPAREN:
                    return self.parse_call()
                raise self.error("expressão esperada")

            case TokenIdentifier(id_, span):
                self.advance()
                # identificador seguido de '(' => chamada de função
                if self.match_delimiter(Delimiter.LPAREN):
                    args = self._parse_expression_list(
                        Delimiter.RPAREN, "esperado ')' ao fim dos argumentos"
                    )
                    return CallExpr(span=span, callee_id=id_, arguments=args)
                return VariableExpr(span=span, id=id_)

            case TokenDelimiter(Delimiter.LPAREN, _):
                self.advance()
                expr = self.parse_expression(0)  # reinicia a precedência
                self.expect_delimiter(Delimiter.RPAREN, "esperado ')' após a expressão")
                return expr  # parênteses só agrupam; não geram nó

            case TokenDelimiter(Delimiter.LBRACKET, span):
                self.advance()
                elements = self._parse_expression_list(
                    Delimiter.RBRACKET, "esperado ']' ao fim da lista"
                )
                return ArrayLiteralExpr(span=span, elements=elements)

            case TokenEOF():
                raise self.error("expressão esperada, mas o arquivo terminou")

            case _:
                raise self.error("expressão esperada")

    def _parse_expression_list(self, closing: Delimiter, msg: str) -> list[Expr]:
        """Lista separada por vírgulas até `closing` (que é consumido).
        O delimitador de abertura já deve ter sido consumido. Aceita lista
        vazia e vírgula final."""
        items: list[Expr] = []

        if not self.check_delimiter(closing):
            while True:
                items.append(self.parse_expression(0))
                if not self.match_delimiter(Delimiter.COMMA):
                    break
                if self.check_delimiter(closing):  # vírgula final
                    break

        self.expect_delimiter(closing, msg)
        return items
