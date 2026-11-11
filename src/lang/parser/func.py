# Minha parte (Membro 5): funcoes e chamadas de funcao.
#
# function <nome>(<parametros>) -> <tipo> { ... }
# return <expressao>;
# chamada(1, 2, 3)  -- tanto pra funcao normal quanto pra cast tipo int(3.0)

from lang.ast import CallExpr, FunctionDecl, Param, ReturnStmt
from lang.tokens import Delimiter, Keyword, Operator, TokenIdentifier, TokenKeyword

# tipos que tambem podem aparecer como "nome" de uma chamada, tipo int(3.0)
TIPOS_PRIMITIVOS = (Keyword.INT, Keyword.DECIMAL, Keyword.STRING, Keyword.BOOL)


class FuncParserMixin:
    def parse_function(self) -> FunctionDecl:
        # confere a palavra "function" e pega o nome depois dela
        func_token = self.expect_keyword(Keyword.FUNCTION, "esperava 'function'")
        span = func_token.span
        name_token = self.expect_identifier("esperava o nome da função")

        # le os parametros entre parenteses
        self.expect_delimiter(Delimiter.LPAREN, "esperava '(' após o nome da função")
        params = self.parse_parameters()
        self.expect_delimiter(Delimiter.RPAREN, "esperava ')' para fechar os parâmetros")

        # o "-> tipo" eh opcional (nem toda funcao retorna algo)
        return_type = None
        if self.match_operator(Operator.ARROW):
            return_type = self.parse_type()

        # por fim, o corpo da funcao entre chaves
        body = self.parse_block()

        return FunctionDecl(
            span=span,
            name_id=name_token.id,
            params=params,
            return_type=return_type,
            body=body,
        )

    def parse_parameters(self) -> list[Param]:
        params: list[Param] = []

        # se ja chegou no ')' eh porque nao tem nenhum parametro
        if self.check_delimiter(Delimiter.RPAREN):
            return params

        # le "nome tipo" varias vezes, separados por virgula
        while True:
            name_token = self.expect_identifier("esperava o nome do parâmetro")
            type_node = self.parse_type()
            params.append(
                Param(span=name_token.span, name_id=name_token.id, type_node=type_node)
            )

            if not self.match_delimiter(Delimiter.COMMA):
                break

        return params

    def parse_return(self) -> ReturnStmt:
        return_token = self.expect_keyword(Keyword.RETURN, "esperava 'return'")
        span = return_token.span

        # "return;" sem valor tambem eh permitido
        value = None
        if not self.check_delimiter(Delimiter.SEMICOLON):
            value = self.parse_expression()

        self.expect_delimiter(Delimiter.SEMICOLON, "esperava ';' ao final do return")

        return ReturnStmt(span=span, value=value)

    def parse_call(self) -> CallExpr:
        span = self.current().span
        callee_id = self._parse_call_target()

        self.expect_delimiter(Delimiter.LPAREN, "esperava '(' na chamada de função")
        arguments = self._parse_arguments()
        self.expect_delimiter(Delimiter.RPAREN, "esperava ')' para fechar a chamada")

        return CallExpr(span=span, callee_id=callee_id, arguments=arguments)

    def _parse_call_target(self) -> int:
        # o "nome" da chamada pode ser um identificador normal (soma, print)
        # ou um tipo primitivo usado como conversao (int, decimal, string, bool)
        token = self.current()

        if isinstance(token, TokenIdentifier):
            self.advance()
            return token.id

        if isinstance(token, TokenKeyword) and token.kind in TIPOS_PRIMITIVOS:
            self.advance()
            # guarda o nome do tipo ("int", "decimal"...) na tabela de simbolos
            # tambem, assim ele ganha um id, igual um identificador normal
            return self.symbol_table.inserir(token.kind.value).id

        raise self.error(
            "esperava um nome de função ou tipo (int, decimal, string, bool)"
        )

    def _parse_arguments(self) -> list:
        arguments = []

        # parenteses vazios, tipo main(), eh valido
        if self.check_delimiter(Delimiter.RPAREN):
            return arguments

        # le um valor de cada vez, separados por virgula
        while True:
            arguments.append(self.parse_expression())
            if not self.match_delimiter(Delimiter.COMMA):
                break

        return arguments
