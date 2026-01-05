from abc import ABC
from dataclasses import dataclass
from typing import List, Dict, Tuple
from typing import Literal as TyLit, Union

from .assembler import (
    asm_add,
    asm_addi,
    asm_sub,
    asm_mul,
    asm_div,
    asm_cmp,
    asm_cmpi,
    asm_halt,
    asm_jmp,
    asm_jz,
    asm_jnz,
    asm_jlt,
    asm_jge,
)

from .const import R0, R1

# AST definitions

Value = Union[int, bool]


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class Literal(Expr):
    value: Value


@dataclass(frozen=True)
class Var(Expr):
    name: str


UnaryOpKind = TyLit["-", "!"]
BinaryOpKind = TyLit["+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">=", "&&", "||"]


@dataclass(frozen=True)
class UnaryOp(Expr):
    op: UnaryOpKind
    expr: Expr


@dataclass(frozen=True)
class BinaryOp(Expr):
    left: Expr
    op: BinaryOpKind
    right: Expr


@dataclass(frozen=True)
class Stmt(ABC):
    pass


@dataclass(frozen=True)
class Assign(Stmt):
    name: str
    expr: Expr


@dataclass(frozen=True)
class While(Stmt):
    cond: Expr
    body: List[Stmt]


@dataclass(frozen=True)
class If(Stmt):
    cond: Expr
    then_body: List[Stmt]
    else_body: List[Stmt] | None = None


@dataclass(frozen=True)
class Program:
    stmts: List[Stmt]


JumpKind = TyLit["jmp", "jz", "jnz", "jlt", "jge"]


class Compiler:
    def __init__(self):
        # output (instructions)
        self.rom_words: List[int] = []

        # label -> instruction index
        self.labels: Dict[str, int] = {}

        # jump instructions
        self.patches: List[Tuple[JumpKind, int, str]] = []

        # variable -> register number
        self.var_regs: Dict[str, int] = {}

        # suffix for labels
        self._label_counter = 0

        # suffix for temporary variables
        self._temp_counter = 0

    # utilities
    def alloc_reg_for_var(self, name: str) -> int:
        if name in self.var_regs:
            return self.var_regs[name]

        # R0 is reserved for zero register
        reg = R1 + len(self.var_regs)
        self.var_regs[name] = reg
        return reg

    def reg_of(self, name: str) -> int:
        return self.alloc_reg_for_var(name)

    def _alloc_temp_reg(self) -> int:
        name = f"__tmp{self._temp_counter}"
        self._temp_counter += 1
        return self.alloc_reg_for_var(name)

    def _eval_expr_to_reg(self, expr: Expr) -> int:
        if isinstance(expr, Var):
            return self.reg_of(expr.name)

        else:
            reg = self._alloc_temp_reg()
            self.compile_expr(expr=expr, target_reg=reg)
            return reg

    def current_index(self) -> int:
        return len(self.rom_words)

    def emit(self, word: int) -> None:
        self.rom_words.append(word)

    def mark_label(self, label: str) -> None:
        self.labels[label] = self.current_index()

    def emit_jmp_label(self, label: str) -> None:
        pos = self.current_index()
        self.emit(0)  # placeholder
        self.patches.append(("jmp", pos, label))

    def emit_jz_label(self, label: str) -> None:
        pos = self.current_index()
        self.emit(0)  # placeholder
        self.patches.append(("jz", pos, label))

    def emit_jnz_label(self, label: str) -> None:
        pos = self.current_index()
        self.emit(0)  # placeholder
        self.patches.append(("jnz", pos, label))

    def emit_jlt_label(self, label: str) -> None:
        pos = self.current_index()
        self.emit(0)  # placeholder
        self.patches.append(("jlt", pos, label))

    def emit_jge_label(self, label: str) -> None:
        pos = self.current_index()
        self.emit(0)  # placeholder
        self.patches.append(("jge", pos, label))

    def _new_label(self, prefix: str) -> str:
        name = f"{prefix}_{self._label_counter}"
        self._label_counter += 1
        return name

    def _emit_bool_from_branch(
        self, *, jump_to_true: callable, target_reg: int
    ) -> None:
        true_label = self._new_label("bool_true")
        end_label = self._new_label("bool_end")

        jump_to_true(true_label)
        self.emit(asm_addi(rd=target_reg, rs=R0, imm=0))
        self.emit_jmp_label(end_label)

        self.mark_label(true_label)
        self.emit(asm_addi(rd=target_reg, rs=R0, imm=1))

        self.mark_label(end_label)

    def compile_expr(self, expr: Expr, target_reg: int) -> None:
        if isinstance(expr, Literal):
            value = expr.value
            if isinstance(value, bool):
                imm = 1 if value else 0
            elif isinstance(value, int):
                imm = value
            else:
                raise NotImplementedError(f"unsupported literal: {type(value)}")
            self.emit(asm_addi(rd=target_reg, rs=R0, imm=imm))
            return

        if isinstance(expr, Var):
            src_reg = self.reg_of(expr.name)
            if src_reg == target_reg:
                # do nothing
                return

            self.emit(asm_add(rd=target_reg, rs1=src_reg, rs2=R0))
            return

        if isinstance(expr, UnaryOp):
            reg = self._eval_expr_to_reg(expr.expr)
            op = expr.op
            if op == "-":
                self.emit(asm_sub(rd=target_reg, rs1=R0, rs2=reg))
                return

            if op == "!":
                # target = (r==0) ? 1 : 0
                self.emit(asm_cmpi(rs=reg, imm=0))
                self._emit_bool_from_branch(
                    jump_to_true=lambda lbl: self.emit_jz_label(lbl),
                    target_reg=target_reg,
                )
                return

            raise NotImplementedError(f"unknown unary op {op}")

        if isinstance(expr, BinaryOp):
            op = expr.op
            if op in {"+", "-", "*", "/"}:
                r1 = self._eval_expr_to_reg(expr.left)
                r2 = self._eval_expr_to_reg(expr.right)
                if op == "+":
                    self.emit(asm_add(rd=target_reg, rs1=r1, rs2=r2))
                    return
                elif op == "-":
                    self.emit(asm_sub(rd=target_reg, rs1=r1, rs2=r2))
                    return
                elif op == "*":
                    self.emit(asm_mul(rd=target_reg, rs1=r1, rs2=r2))
                    return
                elif op == "/":
                    self.emit(asm_div(rd=target_reg, rs1=r1, rs2=r2))
                    return
                else:
                    raise AssertionError("unreachable")

            if op in {"==", "!=", "<", "<=", ">", ">="}:
                r1 = self._eval_expr_to_reg(expr.left)
                r2 = self._eval_expr_to_reg(expr.right)
                if op == ">":
                    # a>b -> b<a
                    self.emit(asm_cmp(rs1=r2, rs2=r1))
                    self._emit_bool_from_branch(
                        jump_to_true=lambda lbl: self.emit_jlt_label(lbl),
                        target_reg=target_reg,
                    )
                    return

                self.emit(asm_cmp(rs1=r1, rs2=r2))

                if op == "==":
                    self._emit_bool_from_branch(
                        jump_to_true=lambda lbl: self.emit_jz_label(lbl),
                        target_reg=target_reg,
                    )
                    return

                if op == "!=":
                    self._emit_bool_from_branch(
                        jump_to_true=lambda lbl: self.emit_jnz_label(lbl),
                        target_reg=target_reg,
                    )
                    return

                if op == "<":
                    self._emit_bool_from_branch(
                        jump_to_true=lambda lbl: self.emit_jlt_label(lbl),
                        target_reg=target_reg,
                    )
                    return

                if op == ">=":
                    self._emit_bool_from_branch(
                        jump_to_true=lambda lbl: self.emit_jge_label(lbl),
                        target_reg=target_reg,
                    )
                    return

                if op == "<=":
                    # a<=b -> (a<b) || (a==b)
                    def _jump_to_true(lbl: str) -> None:
                        self.emit_jlt_label(lbl)
                        self.emit_jz_label(lbl)

                    self._emit_bool_from_branch(
                        jump_to_true=_jump_to_true,
                        target_reg=target_reg,
                    )
                    return

                raise AssertionError("unreachable")

            if op in ("&&", "||"):
                # True is "not zero"
                left_reg = self._eval_expr_to_reg(expr.left)

                true_label = self._new_label("logic_true")
                false_label = self._new_label("logic_false")
                end_label = self._new_label("logic_end")

                if op == "&&":
                    # left is zero -> false
                    self.emit(asm_cmpi(rs=left_reg, imm=0))
                    self.emit_jz_label(false_label)

                    # left is true -> evaluate right
                    right_reg = self._eval_expr_to_reg(expr.right)
                    self.emit(asm_cmpi(rs=right_reg, imm=0))
                    self.emit_jz_label(false_label)

                    # right is true -> true
                    self.mark_label(true_label)
                    self.emit(asm_addi(rd=target_reg, rs=R0, imm=1))
                    self.emit_jmp_label(end_label)

                    self.mark_label(false_label)
                    self.emit(asm_addi(rd=target_reg, rs=R0, imm=0))
                    self.mark_label(end_label)

                    return

                if op == "||":
                    # left is not zero -> true
                    self.emit(asm_cmpi(rs=left_reg, imm=0))
                    self.emit_jnz_label(true_label)

                    # left is false -> evaluate right
                    right_reg = self._eval_expr_to_reg(expr.right)
                    self.emit(asm_cmpi(rs=right_reg, imm=0))
                    self.emit_jnz_label(true_label)

                    # right is false -> false
                    self.mark_label(false_label)
                    self.emit(asm_addi(rd=target_reg, rs=R0, imm=0))
                    self.emit_jmp_label(end_label)

                    self.mark_label(true_label)
                    self.emit(asm_addi(rd=target_reg, rs=R0, imm=1))
                    self.mark_label(end_label)

                    return

                raise AssertionError("unreachable")

            raise NotImplementedError(f"unknown BinaryOp {op}")

        raise NotImplementedError(f"unknown expr: {expr!r}")

    def compile_stmt(self, stmt: Stmt) -> None:
        if isinstance(stmt, Assign):
            reg = self.reg_of(stmt.name)
            self.compile_expr(stmt.expr, target_reg=reg)
            return

        if isinstance(stmt, While):
            loop_label = self._new_label("loop")
            end_label = self._new_label("while_end")

            self.mark_label(loop_label)

            cond_reg = self._eval_expr_to_reg(stmt.cond)
            self.emit(asm_cmpi(rs=cond_reg, imm=0))
            self.emit_jz_label(end_label)

            for s in stmt.body:
                self.compile_stmt(s)

            self.emit_jmp_label(loop_label)
            self.mark_label(end_label)
            return

        if isinstance(stmt, If):
            else_label = self._new_label("if_else")
            end_label = self._new_label("if_end")

            cond_reg = self._eval_expr_to_reg(stmt.cond)
            self.emit(asm_cmpi(rs=cond_reg, imm=0))
            self.emit_jz_label(else_label)

            for s in stmt.then_body:
                self.compile_stmt(s)

            if stmt.else_body is not None:
                self.emit_jmp_label(end_label)
                self.mark_label(else_label)

                for s in stmt.else_body:
                    self.compile_stmt(s)

                self.mark_label(end_label)

            else:
                self.mark_label(else_label)
            return

        raise NotImplementedError(f"unknown stmt: {stmt!r}")

    def compile_program(self, prog: Program) -> list[int]:
        for s in prog.stmts:
            self.compile_stmt(s)

        # put HALT in the last
        self.emit(asm_halt())

        # solve all the labels
        self._patch_jumps()

        return self.rom_words

    def _patch_jumps(self) -> None:
        for kind, pos, label in self.patches:
            if label not in self.labels:
                raise RuntimeError(f"label {label!r} not defined")

            target = self.labels[label]

            # pos: index of jump instruction
            # next instruction is pos + 1 -> off = target - (pos + 1)
            off = target - (pos + 1)
            if kind == "jmp":
                self.rom_words[pos] = asm_jmp(off_words=off)
            elif kind == "jz":
                self.rom_words[pos] = asm_jz(off_words=off)
            elif kind == "jnz":
                self.rom_words[pos] = asm_jnz(off_words=off)
            elif kind == "jlt":
                self.rom_words[pos] = asm_jlt(off_words=off)
            elif kind == "jge":
                self.rom_words[pos] = asm_jge(off_words=off)
            else:
                raise RuntimeError(f"unknown jump kind: {kind}")


# entry point
def compile_program_to_rom(prog: Program) -> list[int]:
    return Compiler().compile_program(prog)
