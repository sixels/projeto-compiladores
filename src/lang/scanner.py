import sys


class Scanner:
    EOF = "-1"

    def __init__(self, file_path):
        self.__row = 0
        self.__column = 0
        self.__text_index = 0
        self.__text: str

        try:
            with open(file_path, "r") as file:
                self.__text = file.read()
        except FileNotFoundError:
            print(f"Erro, arquivo ou diretório '{file_path}' não existe.")
            sys.exit(-1)

    ## Retorna a linha atual em que estamos
    def get_row(self) -> int:
        return self.__row + 1

    ## Retorna a coluna atual em que estamos
    def get_column(self) -> int:
        return self.__column + 1

    def __column_increment(self):
        self.__column += 1

    def __row_increment(self):
        self.__row += 1
        self.__column = 0

    def __get_text_index(self) -> int:
        return self.__text_index

    def __text_index_increment(self):
        self.__text_index += 1

    ## Consome um caractere e avança
    def advance(self) -> str:
        ## IGNORA ESPAÇO EM BRANCO
        # if self.peek() == "\r" or self.peek() == "\t" or self.peek() == " ":
        #     dummy = " "
        #     while dummy == "\r" or dummy == "\t" or dummy == " ":
        #         self.__text_index_increment()
        #         dummy = self.peek()

        ## IGNORA LINHAS DE COMENTÁRIO
        # if self.peek() == "/" and self.peek_next() == "/":
        #     self.__text_index = self.__text.find("\n", self.__get_text_index())

        ## TRATA O CARACTERE LIDO
        if self.eof():
            return Scanner.EOF

        elif self.peek() == "\n":
            self.__row_increment()
        else:
            self.__column_increment()

        return_val = self.peek()
        self.__text_index_increment()

        ## RETORNA O CARACTERE CONSUMIDO
        return return_val

    ## Verifica se estamos no fim do arquivo na poxição (atual+length)
    def eof(self, length=0) -> bool:
        is_eof = self.__get_text_index() + length > len(self.__text) - 1
        return is_eof

    ## Retorna o caracter sem o consumir
    def peek(self) -> str:
        if self.eof():
            return Scanner.EOF

        return self.__text[self.__get_text_index()]

    ## Retorna o próximo caracter sem consumir
    def peek_next(self) -> str:
        if self.eof(1):
            return Scanner.EOF

        return self.__text[self.__get_text_index() + 1]

    ## Consome caso o próximo caracter seja igual à expected
    def match(self, expected: str) -> str | None:
        if self.peek_next() == expected:
            return self.advance()
        return None
