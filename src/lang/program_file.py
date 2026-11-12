from pathlib import Path


class ProgramFile:
    """
    Representa o arquivo de código-fonte do programa
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.content: str = f.read()
        self.lines: list[str] = self.content.splitlines()

    @classmethod
    def from_string(cls, content: str, name: str = "<string>") -> ProgramFile:
        """Cria uma instância de ProgramFile a partir de uma string em memória."""
        obj = cls.__new__(cls)
        obj.file_path = Path(name)
        obj.content = content
        obj.lines = content.splitlines()
        return obj

    def get_line(self, line_number: int) -> str:
        """
        Retorna o texto da linha especificada.
        Retorna string vazia caso o número da linha esteja fora dos limites.
        """
        if 1 <= line_number <= len(self.lines):
            return self.lines[line_number - 1]
        return ""

    def get_line_count(self) -> int:
        """Retorna a quantidade total de linhas no arquivo."""
        return len(self.lines)

    def format_error(self, line_number: int, column: int) -> str:
        """Formata a linha do código com o indicador '^' apontando para a coluna."""
        line_text = self.get_line(line_number)
        if not line_text:
            return ""
        arrow = " " * max(0, column - 1) + "^"
        return f"{line_text}\n{arrow}"
