# Testes automaticos do parser (fase 2 do projeto).
# Minha parte (Membro 5): parser/func.py e esses testes.

# ATENCAO: roda com Python 3.14 (igual no test_lexer.py).

# parse_function/parse_return/parse_call dependem de partes que outros
# membros ainda nao entregaram (parse_expression do Membro 2, parse_block
# do Membro 4)
# Quando o parser inteiro estiver pronto (juntando a parte de todo mundo),
# os 2 testes marcados como "skip" no final passam a valer de verdade.

from pathlib import Path

import pytest

from lang.ast import BlockStmt, LiteralExpr, VariableExpr
from lang.errors import SyntacticError
from lang.lexer import Lexer
from lang.parser.base import Parser as ParserBase
from lang.parser.decl import DeclParserMixin
from lang.parser.func import FuncParserMixin
from lang.scanner import Scanner
from lang.symbol_table import SymbolTable
from lang.tokens import (
    Delimiter,
    TokenBool,
    TokenDecimal,
    TokenEOF,
    TokenIdentifier,
    TokenInt,
    TokenString,
)

SAMPLES_DIR = Path(__file__).parent / "samples"


# --------------------------------------------------
# dublês: ficam no lugar das partes que ainda nao existem
# --------------------------------------------------

class _ExprStub:
    # no lugar do parse_expression de verdade (Membro 2)
    # so reconhece numero/string/bool/identificador, que ja basta pra testar
    def parse_expression(self, min_precedence: int = 0):
        tok = self.current()
        if isinstance(tok, (TokenInt, TokenDecimal, TokenString, TokenBool)):
            self.advance()
            return LiteralExpr(span=tok.span, value=tok.value)
        if isinstance(tok, TokenIdentifier):
            self.advance()
            return VariableExpr(span=tok.span, id=tok.id)
        raise self.error("expr stub: token inesperado")


class _StmtStub:
    # no lugar do parse_block de verdade (Membro 4)
    # so pula tudo que tem entre '{' e '}', sem entender o que tem dentro
    def parse_block(self):
        open_tok = self.expect_delimiter(Delimiter.LBRACE, "esperava '{'")
        while not self.check_delimiter(Delimiter.RBRACE):
            self.advance()
        self.expect_delimiter(Delimiter.RBRACE, "esperava '}'")
        return BlockStmt(span=open_tok.span, statements=[])


class _TestParser(ParserBase, DeclParserMixin, _ExprStub, _StmtStub, FuncParserMixin):
    def __init__(self, tokens, symbol_table):
        super().__init__(tokens)
        self.symbol_table = symbol_table


def parse_trecho(codigo: str):
    # transforma um pedacinho de codigo em tokens e devolve um parser pronto
    caminho = SAMPLES_DIR / "_tmp_trecho.txt"
    caminho.write_text(codigo)

    symbol_table = SymbolTable()
    scanner = Scanner(str(caminho))
    lexer = Lexer(scanner, symbol_table)

    tokens = []
    while True:
        token = lexer.next_token()
        tokens.append(token)
        if isinstance(token, TokenEOF):
            break

    return _TestParser(tokens, symbol_table), symbol_table


# --------------------------------------------------
# testes de parse_function / parse_parameters
# --------------------------------------------------

def test_funcao_com_parametros_e_retorno():
    p, _ = parse_trecho(
        "function exemplo(_lista int[], outro &decimal) -> int {\n"
        "    x = 1;\n"
        "}"
    )
    fn = p.parse_function()

    assert len(fn.params) == 2
    assert fn.params[0].type_node.is_array is True  # _lista eh um array (int[])
    assert fn.params[1].type_node.is_ref is True  # outro eh uma referencia (&decimal)
    assert fn.return_type.base.value == "int"
    assert p.is_at_end()  # leu o arquivo inteiro, sem sobrar nada


def test_funcao_sem_parametros_e_sem_retorno():
    p, _ = parse_trecho("function main() {\n}")
    fn = p.parse_function()

    assert fn.params == []
    assert fn.return_type is None


# --------------------------------------------------
# testes de parse_return
# --------------------------------------------------

def test_return_com_valor():
    p, _ = parse_trecho("return 123;")
    r = p.parse_return()
    assert r.value.value == 123


def test_return_sem_valor():
    p, _ = parse_trecho("return;")
    r = p.parse_return()
    assert r.value is None


# --------------------------------------------------
# testes de parse_call
# --------------------------------------------------

def test_chamada_com_argumentos():
    p, _ = parse_trecho("soma(1, x, 2)")
    call = p.parse_call()
    assert len(call.arguments) == 3


def test_chamada_sem_argumentos():
    p, _ = parse_trecho("main()")
    call = p.parse_call()
    assert call.arguments == []


def test_chamada_de_conversao_de_tipo_cast():
    # int(3.0), decimal(x) etc: o "nome" da chamada eh um tipo, nao um
    # identificador comum
    p, symbol_table = parse_trecho("int(3.0)")
    call = p.parse_call()

    assert len(call.arguments) == 1
    # confere que o id usado pro "int" eh o mesmo que ta na tabela de simbolos
    assert call.callee_id == symbol_table.consultar_por_nome("int").id


# --------------------------------------------------
# testes de erro (esses 3 arquivos/trechos tem erro de proposito)
# --------------------------------------------------

def test_parametro_sem_tipo_da_erro():
    p, _ = parse_trecho("function f(a,) { }")
    with pytest.raises(SyntacticError):
        p.parse_function()


def test_funcao_sem_parenteses_da_erro():
    p, _ = parse_trecho("function f { }")
    with pytest.raises(SyntacticError):
        p.parse_function()


def test_chamada_sem_fechar_parenteses_da_erro():
    p, _ = parse_trecho("soma(1, 2")
    with pytest.raises(SyntacticError):
        p.parse_call()


# --------------------------------------------------
# esses 2 so vao rodar de verdade quando o parser completo existir
# (juntando as partes do Membro 2 e do Membro 4)
# --------------------------------------------------

@pytest.mark.skip(reason="esperando parser/expr.py (Membro 2) e parser/stmt.py (Membro 4)")
def test_valid_1_gera_ast_sem_erro():
    ...


@pytest.mark.skip(reason="esperando parser/expr.py (Membro 2) e parser/stmt.py (Membro 4)")
def test_valid_2_gera_ast_sem_erro():
    ...
