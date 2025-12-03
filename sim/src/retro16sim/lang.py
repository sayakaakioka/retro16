from abc import ABC
from dataclasses import dataclass
from typing import List, Dict, Tuple, Literal

from .assembler import (
    asm_add,
    asm_addi,
    asm_cmp,
    asm_cmpi,
    asm_halt,
    asm_jmp,
    asm_jz,
    asm_jnz,
)

from .const import R0, R1

# AST definitions


@dataclass
class Expr(ABC):
    pass


@dataclass
class Const(Expr):
    value: int


@dataclass
class Var(Expr):
    name: str


@dataclass
class BinOp(Expr):
    op: str  # "+" or "-"
    left: Expr
    right: Expr


@dataclass
class Cond(Expr):
    pass


@dataclass
class CmpZero(Cond):
    expr: Expr
    op: Literal["==", "!="]  # "==" or "!="


@dataclass
class Cmp(Cond):
    left: Expr
    op: Literal["==", "!="]
    right: Expr


@dataclass
class Stmt(ABC):
    pass


@dataclass
class Assign(Stmt):
    name: str
    expr: Expr


@dataclass
class While(Stmt):
    cond: Cond
    body: List[Stmt]


@dataclass
class If(Stmt):
    cond: Cond
    then_body: List[Stmt]
    else_body: List[Stmt] | None = None


@dataclass
class Program:
    stmts: List[Stmt]


type JumpKind = Literal["jmp", "jz", "jnz"]


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

        # suffix for temporary valuables
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
        tmp_name = f"__tmp{self._temp_counter}"
        self._temp_counter += 1
        return self.alloc_reg_for_var(tmp_name)

    def _eval_expr_to_reg(self, expr: Expr) -> int:
        if isinstance(expr, Var):
            return self.reg_of(expr.name)

        # other than variables, use the temporary registers
        reg = self._alloc_temp_reg()
        self.compile_expr(expr, target_reg=reg)
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

    def compile_expr(self, expr: Expr, target_reg: int) -> None:
        if isinstance(expr, Const):
            # target_reg = const
            # notice R0 is utilized as zero register
            self.emit(asm_addi(rd=target_reg, rs=R0, imm=expr.value))

        elif isinstance(expr, Var):
            src_reg = self.reg_of(expr.name)
            if src_reg == target_reg:
                # do nothing
                return

            # no MOV so far
            self.emit(asm_add(rd=target_reg, rs1=src_reg, rs2=R0))

        elif isinstance(expr, BinOp):
            # assume "Var +/- Const" for now
            if isinstance(expr.left, Var) and isinstance(expr.right, Const):
                var_reg = self.reg_of(expr.left.name)
                imm = expr.right.value
                if expr.op == "+":
                    self.emit(asm_addi(rd=target_reg, rs=var_reg, imm=imm))
                elif expr.op == "-":
                    self.emit(asm_addi(rd=target_reg, rs=var_reg, imm=-imm))
                else:
                    raise NotImplementedError(f"unknown op {expr.op}")
            else:
                raise NotImplementedError(
                    "BinOp accepts only Var +/- Const style for now"
                )

        elif isinstance(expr, Cond):
            # evaluate condition as 0 or not 0 sentence
            # but place holder for now
            raise NotImplementedError("Cond cannot be used as value Expr yet")

        else:
            raise NotImplementedError(f"unknown expr: {expr!r}")

    def compile_cond(self, cond: Cond, false_label: str) -> None:
        # evaluate conditions and insert jump to false_label when cond is false
        if isinstance(cond, CmpZero):
            expr = cond.expr
            if isinstance(expr, Var):
                reg = self._eval_expr_to_reg(expr)
                self.emit(asm_cmpi(rs=reg, imm=0))

            elif isinstance(expr, Const):
                reg = self._eval_expr_to_reg(expr)
                self.emit(asm_cmpi(rs=reg, imm=0))

            else:
                raise NotImplementedError(
                    "CmpZero currently supports Var or Const only"
                )

            if cond.op == "!=":
                # condition: expr != 0
                # jump to false_label if expr == 0
                self.emit_jz_label(false_label)

            elif cond.op == "==":
                # condition: expr == 0
                # jump to false_label if expr != 0
                self.emit_jnz_label(false_label)

            else:
                raise NotImplementedError(f"unknown op {cond.op}")

        elif isinstance(cond, Cmp):
            left = cond.left
            right = cond.right

            if isinstance(left, Var) and isinstance(right, Var):
                r1 = self.reg_of(left.name)
                r2 = self.reg_of(right.name)
                self.emit(asm_cmp(rs1=r1, rs2=r2))

            elif isinstance(left, Var) and isinstance(right, Const):
                r1 = self.reg_of(left.name)
                self.emit(asm_cmpi(rs=r1, imm=right.value))

            elif isinstance(left, Const) and isinstance(right, Var):
                raise NotImplementedError("Cmp(Const, Var) is not supported yet")

            else:
                raise NotImplementedError(
                    "Cmp supports only (Var vs Var) or (Var vs Const) for not "
                )

            # JUMP POLICY: JUMP IF FALSE
            if cond.op == "==":
                # Z==1 if the result is equal
                # -> false condition: not equals to zero
                self.emit_jnz_label(false_label)

            elif cond.op == "!=":
                # Z==0 if the result is not equal
                # -> false condition: equals to zero
                self.emit_jz_label(false_label)

            else:
                raise NotImplementedError(f"unknown op {cond.op}")

        else:
            raise NotImplementedError(f"unknown cond: {cond!r}")

    def compile_stmt(self, stmt: Stmt) -> None:
        if isinstance(stmt, Assign):
            reg = self.reg_of(stmt.name)
            self.compile_expr(stmt.expr, target_reg=reg)

        elif isinstance(stmt, While):
            loop_label = self._new_label("loop")
            end_label = self._new_label("while_end")

            self.mark_label(loop_label)
            self.compile_cond(stmt.cond, false_label=end_label)

            for s in stmt.body:
                self.compile_stmt(s)

            self.emit_jmp_label(loop_label)
            self.mark_label(end_label)

        elif isinstance(stmt, If):
            else_label = self._new_label("if_else")
            end_label = self._new_label("if_end")

            self.compile_cond(stmt.cond, false_label=else_label)

            for s in stmt.then_body:
                self.compile_stmt(s)

            if stmt.else_body:
                self.emit_jmp_label(end_label)
                self.mark_label(else_label)

                for s in stmt.else_body:
                    self.compile_stmt(s)

                self.mark_label(end_label)

            else:
                self.mark_label(else_label)

        else:
            raise NotImplementedError(f"unknown stmt: {stmt!r}")

    def compile_program(self, prog: Program) -> list[int]:
        for s in prog.stmts:
            self.compile_stmt(s)

        # put HALT in the last
        self.emit(asm_halt())

        # solve all the labels
        self._patch_jumps()

        return self.rom_words

    def _new_label(self, prefix: str) -> str:
        name = f"{prefix}_{self._label_counter}"
        self._label_counter += 1
        return name

    def _patch_jumps(self) -> None:
        for kind, pos, label in self.patches:
            try:
                target = self.labels[label]
            except KeyError:
                raise RuntimeError(f"label {label!r} not defined")

            # pos: index of jump instruction
            # next instruction is pos + 1 -> off = target - (pos + 1)
            off = target - (pos + 1)
            if kind == "jmp":
                self.rom_words[pos] = asm_jmp(off_words=off)
            elif kind == "jz":
                self.rom_words[pos] = asm_jz(off_words=off)
            elif kind == "jnz":
                self.rom_words[pos] = asm_jnz(off_words=off)
            else:
                raise RuntimeError(f"unknown jump kind: {kind}")


# entry point
def compile_program_to_rom(prog: Program) -> list[int]:
    c = Compiler()
    return c.compile_program(prog)
