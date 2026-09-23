from lang.errors import erro
from lang.scanner import Scanner
from lang.symbol_table import SymbolTable
from lang.tokens import *  # pyright: ignore[reportWildcardImportFromLibrary]


class Lexer:
    def __init__(self, scanner: Scanner, symbol_table: SymbolTable):
        self.scanner = scanner
        self.char = ""
        self.symbol_table = symbol_table

        # Rastreamento da posição (o Scanner não zera a coluna no \n)
        # self.line = 1
        # self.column = 0
        self.source_line = ""  # Para guardar a linha do erro

    # Função para substituir scanner.advance() para tambem guardar a linha do código
    def _advancedSource(self) -> str:
        c = self.scanner.advance()
        if c == "\n":
            # self.line += 1
            # self.column = 0
            self.source_line = ""
        elif c != Scanner.EOF:
            # self.column += 1
            self.source_line += c
        return c

    # Posição do PRÓXIMO caractere a ser lido.
    def _position(self) -> Span:
        return Span(line=self.scanner.get_row(), col=self.scanner.get_column())

    # Quando detectado um erro, termina de ler a linha para montar a mensagem de erro
    def _readUntilEnd(self):
        while self.char not in ("\n", Scanner.EOF):
            self._advancedSource()
            self.char = self.scanner.peek()

    def _skip(self):
        # Pular comentarios ou espaços em brancos, quebras de linhas
        while True:
            if self.char in (" ", "\t", "\r", "\n"):
                self._advancedSource()
                self.char = self.scanner.peek()
            elif self.char == "/" and self.scanner.peek_next() == "/":
                while self.char not in ("\n", Scanner.EOF):
                    self._advancedSource()
                    self.char = self.scanner.peek()
            else:
                break

    def next_token(self) -> Token:
        self.char = self.scanner.peek()
        self._skip()
        self.char = self.scanner.peek()

        span_atual = self._position()

        if self.char == Scanner.EOF:
            return TokenEOF(span=span_atual)
        if self.char.isalpha() or self.char == "_":
            return self._read_letter(span_atual)
        elif self.char.isdigit():
            return self._read_number(span_atual)
        elif self.char == '"':
            return self._read_string(span_atual)
        else:
            return self._read_operator_or_delimiter(span_atual)

    def _read_number(self, span: Span) -> Token:
        # Retorna token decimal ou inteiro
        num_txt = ""
        dot_count = 0

        while self.char != Scanner.EOF and (self.char.isdigit() or self.char == "."):
            if self.char == ".":
                if self.scanner.peek_next() == ".":
                    break
                if dot_count == 1:
                    break
                dot_count += 1

            num_txt += self.char
            self._advancedSource()
            self.char = self.scanner.peek()

        wrongNumber = num_txt.endswith(".") or (self.char == "." and dot_count == 1)
        if wrongNumber:
            # consome o "pedaço" restante para mostrar tudo na mensagem
            while self.char.isdigit() or self.char == ".":
                num_txt += self.char
                self._advancedSource()
                self.char = self.scanner.peek()
            self._readUntilEnd()
            raise erro(2, num_txt, span.line, span.col, self.source_line)

        if dot_count == 0:
            return TokenInt(value=int(num_txt), span=span)
        else:
            return TokenDecimal(value=float(num_txt), span=span)

    def _read_letter(self, span: Span) -> Token:
        # Identifica se é  um booleano, um token Keyword(palavra reservada)
        # ou um token Identifier (nome dado pelo programador(a))

        texto = ""
        while self.char != Scanner.EOF and (self.char.isalnum() or self.char == "_"):
            texto += self.char
            self._advancedSource()
            self.char = self.scanner.peek()

        if texto == "true":
            return TokenBool(value=True, span=span)
        elif texto == "false":
            return TokenBool(value=False, span=span)

        token_keyword = TokenKeyword.try_from_str(texto, span)
        if token_keyword is not None:
            return token_keyword

        symbol = self.symbol_table.inserir(texto)
        return TokenIdentifier(id=symbol.id, span=span)

    def _read_string(self, span: Span) -> Token:
        # Identifica strings (consome apenas o que está dentro dos "")
        texto = ""

        self._advancedSource()
        self.char = self.scanner.peek()

        while self.char not in (Scanner.EOF, '"', "\n"):
            texto += self.char
            self._advancedSource()
            self.char = self.scanner.peek()

        if self.char in (Scanner.EOF, "\n"):
            self._readUntilEnd()
            raise erro(1, "", span.line, span.col, self.source_line)

        self._advancedSource()
        self.char = self.scanner.peek()

        return TokenString(value=texto, span=span)

    def _read_operator_or_delimiter(self, span: Span) -> Token:
        # Tenta operador duplo (ex: =!)
        token_operator = TokenOperator.try_from_str(
            self.char + self.scanner.peek_next(), span
        )
        if token_operator is not None:
            self._advancedSource()
            self._advancedSource()
            self.char = self.scanner.peek()
            return token_operator

        # Tenta operador com 1 caractere
        token_operator = TokenOperator.try_from_str(self.char, span)
        if token_operator is not None:
            self._advancedSource()
            self.char = self.scanner.peek()
            return token_operator

        # Tenta delimitador (ex: ';', '(', ')', '{')
        token_delim = TokenDelimiter.try_from_str(self.char, span)
        if token_delim is not None:
            self._advancedSource()
            self.char = self.scanner.peek()
            return token_delim

        simbolo_invalido = self.char
        self._readUntilEnd()
        raise erro(0, simbolo_invalido, span.line, span.col, self.source_line)
