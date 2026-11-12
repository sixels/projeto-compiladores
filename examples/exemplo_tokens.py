from lang.scanner import Scanner
from lang.tokens import (
    # Delimiter,
    # Keyword,
    # Operator,
    Span,
    Token,
    TokenBool,
    # TokenDecimal,
    TokenDelimiter,
    TokenEOF,
    TokenIdentifier,
    # TokenInt,
    TokenKeyword,
    # TokenOperator,
    TokenString,
)


def proximo(scan: Scanner) -> Token:
    # pula espaços e quebras de linha
    while not scan.eof() and scan.peek() in (" ", "\t", "\r", "\n"):
        scan.advance()

    span = Span(scan.get_row(), scan.get_column())

    if scan.eof():
        return TokenEOF(span)

    ch = scan.peek()

    # identificadores, palavras-chave ou booleanos
    if ch.isalpha() or ch == "_":
        texto = ""
        while not scan.eof() and (scan.peek().isalnum() or scan.peek() == "_"):
            texto += scan.advance()

        # literal booleano
        if texto == "true":
            return TokenBool(value=True, span=span)
        if texto == "false":
            return TokenBool(value=False, span=span)

        if (keyword := TokenKeyword.try_from_str(texto, span)) is not None:
            return keyword
        return TokenIdentifier(id=hash(texto), span=span)

    # números
    # em branco nesse exemplo

    # strings
    if ch == '"':
        scan.advance()  # consome a aspa inicial
        texto = ""
        while not scan.eof() and scan.peek() != '"':
            texto += scan.advance()
        scan.advance()  # consome a aspa final
        return TokenString(value=texto, span=span)

    # operadores longos (==, ->, .., ||, &&)
    # em branco nesse exemplo

    # operadores
    # em branco nesse exemplo

    # delimitadores

    if (delim := TokenDelimiter.try_from_str(ch, span)) is not None:
        scan.advance()
        return delim

    raise SyntaxError(f"Caractere inválido ou não implementado '{ch}' em {span}")


if __name__ == "__main__":
    scanner = Scanner("examples/a.txt")
    while not scanner.eof():
        token = proximo(scanner)
        print(token)
