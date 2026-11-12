from lang.ast import Program
from lang.errors import SyntacticError
from lang.parser.base import ParserBase
from lang.parser.decl import DeclParserMixin
from lang.parser.expr import ExpressionParser
from lang.parser.func import FuncParserMixin
from lang.parser.stmt import StmtParserMixin
from lang.program_file import ProgramFile
from lang.symbol_table import SymbolTable
from lang.tokens import Token


class Parser(
    StmtParserMixin,
    FuncParserMixin,
    DeclParserMixin,
    ExpressionParser,
    ParserBase,
):
    """Analisador sintático completo para a linguagem lang."""

    def __init__(
        self,
        tokens: list[Token],
        symbol_table: SymbolTable | None = None,
        program_file: ProgramFile | None = None,
    ):
        super().__init__(tokens, symbol_table, program_file)

    def parse(self) -> Program:
        """Executa a análise sintática completa e retorna o nó raiz Program."""
        span = self.current().span
        functions = []
        while not self.is_at_end():
            try:
                functions.append(self.parse_function())
            except SyntacticError as e:
                self.errors.append(e)
                self.synchronize()
        return Program(span=span, functions=functions)
