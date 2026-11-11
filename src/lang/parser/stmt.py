from lang.ast_nodes import (
    ASTNode,
    BlockStmt,
    IfStmt,
    LoopInfiniteStmt,
    LoopIteratorStmt,
    LoopRangeStmt,
)
from lang.tokens import (
    Delimiter,
    Keyword,
    Operator,
    TokenDelimiter,
    TokenIdentifier,
    TokenKeyword,
)

#4 tipos primitivos da linguagem 
#Uso de frozenset ao invés de lista: é um conjunto imutável e faz a busca com 'in' mais rapidamente
TIPOS_BASE: frozenset[Keyword] = frozenset(
    {Keyword.INT, Keyword.DECIMAL, Keyword.STRING, Keyword.BOOL}
)

#Controle de fluxo
class StmtParserMixin:

    def parse_block(self) -> BlockStmt:
        #Consome o '{'
        abre_chaves = self.expect_delimiter(Delimiter.LBRACE, "Esperado '{' para abrir um bloco")

        #Lista vazia que cresce a cada nó criado
        comandos: list[ASTNode] = []

        #Lê os comandos internos, parando no '}' do fechamento OU no fim do arquivo
        while not self.is_at_end() and not self.check_delimiter(Delimiter.RBRACE):
            comandos.append(self.parse_statement())

        #Se saiu do laço porque o arquivo acabou, não foi encontrado o '}'
        if self.is_at_end():
            raise self.error("Esperado '}' para fechar o bloco", self.current().span)

        #Consome o '}' e monta o nó
        self.expect_delimiter(Delimiter.RBRACE, "Esperado '}' para fechar o bloco")

        return BlockStmt(span=abre_chaves.span, statements=comandos)

    def parse_if(self) -> IfStmt:
        #Consome o 'if'
        if_kw = self.expect_keyword(Keyword.IF, "Esperado 'if'")

        #Consome a condição (não é delimitado por '{}')
        condicao = self.parse_expression()

        #Consome a instrução (que é um bloco entre '{}')
        then_branch = self.parse_block()

        #Se existir o 'else', há 2 casos possíveis:
        else_branch: BlockStmt | IfStmt | None = None
        if self.match_keyword(Keyword.ELSE):
            if self.check_keyword(Keyword.IF):
                #Caso A — "else if ..." (recursão)
                else_branch = self.parse_if()
            else:
                #Caso B — "else { ... }"
                else_branch = self.parse_block()

        return IfStmt(span=if_kw.span, condition=condicao, then_branch=then_branch, else_branch=else_branch)

    def parse_loop(self) -> ASTNode:
        #Consome o 'loop'
        loop_kw = self.expect_keyword(Keyword.LOOP, "Esperado 'loop'")

        #Se logo após o 'loop' vem '{', é o formato "loop { ... }"
        if self.check_delimiter(Delimiter.LBRACE):
            corpo = self.parse_block()
            return LoopInfiniteStmt(span=loop_kw.span, body=corpo)

        #Loop com variável (2 formatos possíveis) -> Ambos começam com:  loop <id> in ...
        iterador = self.expect_identifier("Esperado o nome da variável do loop (ou '{' para loop infinito)")
        self.expect_keyword(Keyword.IN, "Esperado 'in' após a variável do loop")

        #Lê a primeira expressão que pode ser um intervalo ou uma lista
        primeira = self.parse_expression()

        #Se loop com intervalo
        if self.match_operator(Operator.DOT_DOT):
            fim = self.parse_expression()
            corpo = self.parse_block()
            return LoopRangeStmt(span=loop_kw.span, iterator_id=iterador.id, start=primeira, end=fim, body=corpo)

        #Loop com coleção
        corpo = self.parse_block()
        return LoopIteratorStmt(span=loop_kw.span, iterator_id=iterador.id, collection=primeira, body=corpo)

    def parse_statement(self) -> ASTNode:
        #Olha o token atual
        token = self.current()

        #If's com as palavras-chave com métodos próprios de leitura
        if self.check_keyword(Keyword.VAR):
            return self.parse_var_decl()
        if self.check_keyword(Keyword.IF):
            return self.parse_if()       
        if self.check_keyword(Keyword.LOOP):
            return self.parse_loop()    
        if self.check_keyword(Keyword.RETURN):
            return self.parse_return()   

        #Caso em que as palavras de tipo indicam conversão (ex: int(3.0))
        if isinstance(token, TokenKeyword) and token.kind in TIPOS_BASE:
            proximo = self.peek() #Lookahed de 1
            if isinstance(proximo, TokenDelimiter) and proximo.kind == Delimiter.LPAREN:
                #Se vem '(' após o tipo é uma conversão
                chamada = self.parse_call()
                #Consome o ';' que encerra o comando
                self.expect_delimiter(Delimiter.SEMICOLON, "Esperado ';' após a chamada")
                return chamada
            #'(' não encontrado no alvo tipo primitivo
            raise self.error(
                "Tipo não pode iniciar comando; para declarar use 'var', e tipos só iniciam comando como chamada",
                token.span,
            )

        #Caso em que o token atual é um identificador 
        if isinstance(token, TokenIdentifier):
            proximo = self.peek()
            if isinstance(proximo, TokenDelimiter) and proximo.kind == Delimiter.LPAREN:
                #Se é seguido por '(' é uma chamada de função
                chamada = self.parse_call()
                self.expect_delimiter(Delimiter.SEMICOLON, "Esperado ';' após a chamada")
                return chamada
            #Qualquer outra coisa é uma atribuição
            return self.parse_assignment()

        #Atribuição por desreferência '*'
        if self.check_operator(Operator.STAR):
            return self.parse_assignment()

        #Nada casa com um comando válido
        raise self.error(
            "Comando inválido: esperado 'var', 'if', 'loop', 'return', um identificador, '*' ou um tipo primitivo seguido de '('",
            token.span,
        )