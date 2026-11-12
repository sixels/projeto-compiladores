# Testes automaticos do lexer.
# Minha parte (Integrante 5): symbol_table e esses testes.

# ATENCAO: pra rodar isso precisa ser com Python 3.14 (o projeto exige essa
# versao, ta escrito no arquivo .python-version do repo).

# Como o lexer funciona (resumo pra lembrar):
#   scanner = Scanner(caminho_do_arquivo)
#   lexer = Lexer(scanner)
#   token = lexer.next_token()   # chama isso varias vezes ate vir um TokenEOF
#   se o codigo tiver erro, ele levanta um LexicalError (de lang.errors)

# Roda com: pytest test_lexer.py -v

from pathlib import Path

import pytest

from lang.errors import LexicalError
from lang.lexer import Lexer
from lang.scanner import Scanner
from lang.symbol_table import SymbolTable
from lang.tokens import (
    Token,
    TokenBool,
    TokenDecimal,
    TokenDelimiter,
    TokenEOF,
    TokenIdentifier,
    TokenKeyword,
    TokenOperator,
    TokenString,
)

SAMPLES_DIR = Path(__file__).parent / "samples"


def tokenize(nome_do_arquivo) -> tuple[list[Token], SymbolTable]:
    symbol_table = SymbolTable()
    # abre o arquivo, roda o lexer nele e devolve a lista de tokens gerados
    scanner = Scanner(str(SAMPLES_DIR / nome_do_arquivo))
    lexer = Lexer(scanner, symbol_table)

    tokens = []
    while True:
        token = lexer.next_token()
        if isinstance(token, TokenEOF):
            break  # chegou no fim do arquivo, para de ler
        tokens.append(token)
    return (tokens, symbol_table)


# --------------------------------------------------
# valid_1.txt eh o exemplo oficial da gramatica
# --------------------------------------------------


def test_valid_1_nao_da_erro():
    # so confere que rodou e gerou token, sem quebrar
    tokens, _ = tokenize("valid_1.txt")
    assert len(tokens) > 0


def test_valid_1_reconhece_a_palavra_function():
    tokens, _ = tokenize("valid_1.txt")
    assert any(
        isinstance(t, TokenKeyword) and t.kind.value == "function" for t in tokens
    )


def test_valid_1_reconhece_operadores():
    tokens, _ = tokenize("valid_1.txt")
    valores_encontrados = {t.kind.value for t in tokens if isinstance(t, TokenOperator)}
    # -> seta de retorno, || e && sao "ou"/"e", & e * sao referencia/ponteiro
    assert {"->", "||", "&&", "&", "*"} <= valores_encontrados


def test_valid_1_reconhece_colchetes_do_array():
    tokens, _ = tokenize("valid_1.txt")
    delimitadores = {t.kind.value for t in tokens if isinstance(t, TokenDelimiter)}
    assert {"[", "]"} <= delimitadores


def test_valid_1_reconhece_string():
    tokens, _ = tokenize("valid_1.txt")
    strings = [t.value for t in tokens if isinstance(t, TokenString)]
    assert any("Hello" in s for s in strings)


def test_valid_1_reconhece_decimal():
    tokens, _ = tokenize("valid_1.txt")
    assert any(isinstance(t, TokenDecimal) for t in tokens)


def test_valid_1_reconhece_booleano():
    tokens, _ = tokenize("valid_1.txt")
    assert any(isinstance(t, TokenBool) for t in tokens)


def test_valid_1_reconhece_identificador():
    tokens, st = tokenize("valid_1.txt")
    nomes = {
        e.name
        for t in tokens
        if isinstance(t, TokenIdentifier) and (e := st.consultar(t.id)) is not None
    }
    # esses nomes aparecem no codigo de exemplo (funcoes e variaveis)
    assert {"exemplo", "outro", "lista"} <= nomes


# --------------------------------------------------
# valid_2.txt tem comparacoes, negativo, else-if, array vazio
# --------------------------------------------------


def test_valid_2_reconhece_comparacoes():
    tokens, _ = tokenize("valid_2.txt")
    valores_encontrados = {t.kind.value for t in tokens if isinstance(t, TokenOperator)}
    assert {"<=", "==", "&&", ">", "<", "!"} <= valores_encontrados


def test_valid_2_reconhece_array_vazio():
    tokens, _ = tokenize("valid_2.txt")
    delimitadores = [t.kind.value for t in tokens if isinstance(t, TokenDelimiter)]
    # array vazio eh um "[" logo seguido de "]", sem nada no meio
    tem_array_vazio = any(
        a == "[" and b == "]" for a, b in zip(delimitadores, delimitadores[1:])
    )
    assert tem_array_vazio


def test_valid_2_reconhece_nome_da_funcao():

    tokens, st = tokenize("valid_2.txt")

    nomes = {
        e.name
        for t in tokens
        if isinstance(t, TokenIdentifier) and (e := st.consultar(t.id)) is not None
    }
    assert "menorOuIgual" in nomes


# --------------------------------------------------
# esses 3 arquivos tem erro de proposito, entao tem que dar erro mesmo
# --------------------------------------------------


def test_caractere_invalido_da_erro():
    with pytest.raises(LexicalError, match="Caractere inesperado"):
        tokenize("invalid_char.txt")


def test_string_sem_fechar_da_erro():
    with pytest.raises(LexicalError, match="String não fechada"):
        tokenize("invalid_string.txt")


def test_numero_mal_formado_da_erro():
    with pytest.raises(LexicalError, match="Número mal formado"):
        tokenize("invalid_number.txt")
