from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lang.symbol_table import SymbolTable
from lang.tokens import Keyword, Operator, Span


# Membro 1: Base
@dataclass(frozen=True, slots=True)
class ASTNode:
    span: Span


@dataclass(frozen=True, slots=True)
class Program(ASTNode):
    functions: list[FunctionDecl]

    def display(self, symbol_table: SymbolTable) -> str:
        def get_symbol(id: int) -> str:
            entry = symbol_table.consultar(id)
            return entry.name if entry is not None else "?"

        def format_type(t: TypeNode | None) -> str:
            if t is None:
                return "None"
            return f"TypeNode(base=Keyword.{t.base.name}, is_array={t.is_array}, is_ref={t.is_ref})"

        def format_expr(expr: Expr) -> str:
            match expr:
                case LiteralExpr(value=v):
                    val_str = f'"{v}"' if isinstance(v, str) else str(v)
                    return f"LiteralExpr(value={val_str})"
                case VariableExpr(id=id_):
                    return f"VariableExpr(id='{get_symbol(id_)}')"
                case ArrayLiteralExpr(elements=elems):
                    elems_str = ", ".join(format_expr(e) for e in elems)
                    return f"ArrayLiteralExpr(elements=[{elems_str}])"
                case UnaryExpr(operator=op, operand=sub):
                    return (
                        f"UnaryExpr(operator='{op.value}', operand={format_expr(sub)})"
                    )
                case BinaryExpr(left=l, operator=op, right=r):
                    return f"BinaryExpr(left={format_expr(l)}, operator='{op.value}', right={format_expr(r)})"
                case CallExpr(callee_id=cid, arguments=args):
                    args_str = ", ".join(format_expr(a) for a in args)
                    return f"CallExpr(callee_id='{get_symbol(cid)}', arguments=[{args_str}])"

        def to_tree(stmt: ASTNode) -> tuple[str, list[Any]]:
            match stmt:
                case VarDeclStmt(name_id=nid, type_node=tn, initializer=init):
                    return (
                        f"VarDeclStmt(name_id='{get_symbol(nid)}', type_node={format_type(tn)}, initializer={format_expr(init)})",
                        [],
                    )
                case AssignStmt(target_id=tid, value=val):
                    return (
                        f"AssignStmt(target_id='{get_symbol(tid)}', value={format_expr(val)})",
                        [],
                    )
                case DerefAssignStmt(target_id=tid, value=val):
                    return (
                        f"DerefAssignStmt(target_id='{get_symbol(tid)}', value={format_expr(val)})",
                        [],
                    )
                case ReturnStmt(value=val):
                    return (
                        f"ReturnStmt(value={format_expr(val)})"
                        if val is not None
                        else "ReturnStmt(value=None)",
                        [],
                    )
                case CallExpr():
                    return format_expr(stmt), []
                case LoopInfiniteStmt(body=body):
                    return "LoopInfiniteStmt", [to_tree(s) for s in body.statements]
                case LoopRangeStmt(iterator_id=iid, start=st, end=en, body=body):
                    return (
                        f"LoopRangeStmt(iterator_id='{get_symbol(iid)}', start={format_expr(st)}, end={format_expr(en)})",
                        [to_tree(s) for s in body.statements],
                    )
                case LoopIteratorStmt(iterator_id=iid, collection=coll, body=body):
                    return (
                        f"LoopIteratorStmt(iterator_id='{get_symbol(iid)}', collection={format_expr(coll)})",
                        [to_tree(s) for s in body.statements],
                    )
                case BlockStmt(statements=stmts):
                    return f"BlockStmt(len={len(stmts)})", [to_tree(s) for s in stmts]
                case IfStmt(condition=cond, then_branch=then_b, else_branch=else_b):
                    if else_b is None:
                        return f"IfStmt(condition={format_expr(cond)})", [
                            (
                                "then_branch: BlockStmt",
                                [to_tree(s) for s in then_b.statements],
                            )
                        ]
                    then_node = (
                        "then_branch: BlockStmt",
                        [to_tree(s) for s in then_b.statements],
                    )
                    if isinstance(else_b, IfStmt):
                        lbl, ch = to_tree(else_b)
                        else_node = (f"else_branch: {lbl}", ch)
                    else:
                        else_node = (
                            "else_branch: BlockStmt",
                            [to_tree(s) for s in else_b.statements],
                        )
                    return f"IfStmt(condition={format_expr(cond)})", [
                        then_node,
                        else_node,
                    ]
                case _:
                    return str(stmt), []

        def render(items: list[tuple[str, list[Any]]], prefix: str = "") -> list[str]:
            lines: list[str] = []
            for i, (label, children) in enumerate(items):
                connector = "└── " if i == len(items) - 1 else "├── "
                lines.append(f"{prefix}{connector}{label}")
                if children:
                    child_prefix = prefix + ("    " if i == len(items) - 1 else "│   ")
                    lines.extend(render(children, child_prefix))
            return lines

        func_blocks: list[str] = []
        for f in self.functions:
            params_str = ", ".join(
                f"Param(name_id='{get_symbol(p.name_id)}', type_node={format_type(p.type_node)})"
                for p in f.params
            )
            header = (
                f"FunctionDecl(name_id='{get_symbol(f.name_id)}', "
                f"params=[{params_str}], return_type={format_type(f.return_type)})"
            )
            lines = [header]
            lines.extend(render([to_tree(s) for s in f.body.statements]))
            func_blocks.append("\n".join(lines))

        return "\n\n".join(func_blocks)


# Membro 2: Expressões
type Expr = (
    BinaryExpr | UnaryExpr | LiteralExpr | VariableExpr | ArrayLiteralExpr | CallExpr
)


@dataclass(frozen=True, slots=True)
class BinaryExpr(ASTNode):
    left: Expr
    operator: Operator
    right: Expr


@dataclass(frozen=True, slots=True)
class UnaryExpr(ASTNode):
    operator: Operator
    operand: Expr


@dataclass(frozen=True, slots=True)
class LiteralExpr(ASTNode):
    value: int | float | str | bool


@dataclass(frozen=True, slots=True)
class VariableExpr(ASTNode):
    id: int


@dataclass(frozen=True, slots=True)
class ArrayLiteralExpr(ASTNode):
    elements: list[Expr]


# Membro 3: Tipos e Declarações
@dataclass(frozen=True, slots=True)
class TypeNode(ASTNode):
    base: Keyword
    is_array: bool
    is_ref: bool


@dataclass(frozen=True, slots=True)
class VarDeclStmt(ASTNode):
    name_id: int
    type_node: TypeNode
    initializer: Expr


@dataclass(frozen=True, slots=True)
class AssignStmt(ASTNode):
    target_id: int
    value: Expr


@dataclass(frozen=True, slots=True)
class DerefAssignStmt(ASTNode):
    target_id: int
    value: Expr


# Membro 4: Controle de Fluxo
@dataclass(frozen=True, slots=True)
class BlockStmt(ASTNode):
    statements: list[ASTNode]


@dataclass(frozen=True, slots=True)
class IfStmt(ASTNode):
    condition: Expr
    then_branch: BlockStmt
    else_branch: BlockStmt | IfStmt | None


@dataclass(frozen=True, slots=True)
class LoopInfiniteStmt(ASTNode):
    body: BlockStmt


@dataclass(frozen=True, slots=True)
class LoopRangeStmt(ASTNode):
    iterator_id: int
    start: Expr
    end: Expr
    body: BlockStmt


@dataclass(frozen=True, slots=True)
class LoopIteratorStmt(ASTNode):
    iterator_id: int
    collection: Expr
    body: BlockStmt


# Membro 5: Funções e Chamadas
@dataclass(frozen=True, slots=True)
class Param(ASTNode):
    name_id: int
    type_node: TypeNode


@dataclass(frozen=True, slots=True)
class FunctionDecl(ASTNode):
    name_id: int
    params: list[Param]
    return_type: TypeNode | None
    body: BlockStmt


@dataclass(frozen=True, slots=True)
class ReturnStmt(ASTNode):
    value: Expr | None


@dataclass(frozen=True, slots=True)
class CallExpr(ASTNode):
    callee_id: int
    arguments: list[Expr]
