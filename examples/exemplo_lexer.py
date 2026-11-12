import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from src.lang.scanner import Scanner
from src.lang.lexer import Lexer
from src.lang.symbol_table import SymbolTable
from src.lang.tokens import *

scan = Scanner("examples/a.txt")
symbol_table = SymbolTable()
lexer = Lexer(scan, symbol_table)
token = None

while not isinstance(token, TokenEOF):
    token = lexer.next_token()
    valor_token = getattr(token, 'value', getattr(token, 'kind', getattr(token, 'name', '')))
    print(f"[{type(token).__name__}] Valor: {valor_token} na linha {token.span.line} e coluna {token.span.col}")
