# lang

## Pré-requisitos

Instale o `uv`:

```bash
# Linux e macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

Ou através do pip:

```bash
pip install uv
```

## Instalação e Configuração

Na raiz do projeto, instale o Python e sincronize o ambiente:

```bash
uv sync
```

## Executando o Projeto

Execute o programa passando o caminho do arquivo de código:

```bash
uv run lang <caminho_do_arquivo>
```

Exemplo:

```bash
uv run lang examples/a.txt
```

## Testes

Para rodar os testes:

```bash
uv run pytest
```
