from lang.ast import AssignStmt, DerefAssignStmt, TypeNode, VarDeclStmt
from lang.parser.base import ParserBase
from lang.tokens import Delimiter, Keyword, Operator


class DeclParserMixin(ParserBase):
    TIPOS_PRIMITIVOS = (Keyword.INT, Keyword.DECIMAL, Keyword.STRING, Keyword.BOOL)

    def parse_type(self) -> TypeNode:
        """
        Regras da gramática:
            <tipo>             ::= <modificador_tipo> <tipo_base> <tipo_array>
            <modificador_tipo> ::= "&" | λ
            <tipo_base>        ::= "int" | "decimal" | "string" | "bool" | <identificador>
            <tipo_array>       ::= "[]" | λ
        """
        # Posicao do token
        span = self.current().span
        # Se é &
        is_ref = self.match_operator(Operator.AMPERSAND)
        # tipo base
        base = None
        for kind in self.TIPOS_PRIMITIVOS:
            if self.match_keyword(kind):
                base = kind
                break
        if base is None:
            raise self.error("esperava um tipo (int, decimal, string ou bool)")
        # Se é "[]"
        is_array = False
        if self.match_delimiter(Delimiter.LBRACKET):
            self.expect_delimiter(
                Delimiter.RBRACKET, "esperava ']' para fechar o tipo vetor"
            )
            is_array = True

        return TypeNode(span=span, base=base, is_array=is_array, is_ref=is_ref)

    def parse_var_decl(self) -> VarDeclStmt:
        """
        Regra da gramática:
            <declaracao_var> ::= "var" <identificador> <tipo> "=" <expressao> ";"
        """
        # Verifica se começa com var
        var_token = self.expect_keyword(Keyword.VAR, "esperava 'var'")
        span = var_token.span
        # Verifica nome da variável
        name_token = self.expect_identifier("esperava o nome da variável")
        # Verifica tipo
        type_node = self.parse_type()
        # Verifica "="
        self.expect_operator(Operator.EQ, "esperava '=' após o tipo")
        # Guarda expressao
        initializer = self.parse_expression()
        # Verifica ";"
        self.expect_delimiter(
            Delimiter.SEMICOLON, "esperava ';' ao final da declaração"
        )

        return VarDeclStmt(
            span=span,
            name_id=name_token.id,
            type_node=type_node,
            initializer=initializer,
        )

    def parse_assignment(self) -> AssignStmt | DerefAssignStmt:
        """
        Regras da gramática:
            <atribuicao>   ::= <lvalue> "=" <expressao> ";"
            <lvalue>       ::= <ponteiro_opt> <identificador> <index_opt>
            <ponteiro_opt> ::= "*" | λ
            <index_opt>    ::= "[" <expressao> "]" | λ
        """
        span = self.current().span
        # Verifica "*" opcional:
        is_deref = self.match_operator(Operator.STAR)
        # Verifica nome da variável alvo
        target_token = self.expect_identifier("esperava o nome da variável")
        # Verifica "="
        self.expect_operator(Operator.EQ, "esperava '=' na atribuição")
        # Guarda expressao
        value = self.parse_expression()
        # ";"
        self.expect_delimiter(
            Delimiter.SEMICOLON, "esperava ';' ao final da atribuição"
        )

        if is_deref:
            return DerefAssignStmt(span=span, target_id=target_token.id, value=value)
        return AssignStmt(span=span, target_id=target_token.id, value=value)
