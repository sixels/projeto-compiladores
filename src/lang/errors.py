class LexicalError(Exception):
    # Inicializa o erro léxico
    def __init__(self, mensagem: str, linha: int, coluna: int, linhaCodigo: str = ""):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.linhaCodigo = linhaCodigo

        super().__init__(self.formato())

    # Formata o erro
    def formato(self) -> str:
        result = (
            f"Erro léxico. Linha {self.linha}, Coluna {self.coluna}: {self.mensagem}"
        )

        if self.linhaCodigo != "":
            result += "\n"
            result += self.linhaCodigo.rstrip("\n")  # Adiciona a linha do código
            result += "\n"
            result += " " * max(0, self.coluna - 1)  # Posiciona a "seta"
            result += "^"  # Adiciona a "seta"

        return result


def erro(tipoErro: int, charVal: str, linha: int, coluna: int, linhaCodigo: str):
    if tipoErro == 0:
        mensagem = caractereInesperado(charVal)
    elif tipoErro == 1:
        mensagem = stringNaoFechada()
    elif tipoErro == 2:
        mensagem = numeroMalFormado(charVal)
    else:
        mensagem = "Erro léxico desconhecido"

    return LexicalError(mensagem, linha, coluna, linhaCodigo)


# Erro para caractere inesperado
def caractereInesperado(char: str):
    return f"Caractere inesperado {char!r}"


# Erro para string não fechada
def stringNaoFechada():
    return "String não fechada"


# Erro para número mal formado
def numeroMalFormado(val: str):
    return f"Número mal formado {val!r}"


class SyntacticError(Exception):
    def __init__(
        self,
        mensagem: str,
        linha: int,
        coluna: int,
        linhaCodigo: str = "",
    ):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.linhaCodigo = linhaCodigo
        super().__init__(self.formato())

    # Formata o erro
    def formato(self) -> str:
        result = (
            f"Erro Sintático. Linha {self.linha}, Coluna {self.coluna}: {self.mensagem}"
        )

        if self.linhaCodigo != "":
            result += "\n"
            result += self.linhaCodigo.rstrip("\n")  # Adiciona a linha do código
            result += "\n"
            result += " " * max(0, self.coluna - 1)  # Posiciona a "seta"
            result += "^"  # Adiciona a "seta"

        return result
