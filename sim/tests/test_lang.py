# import pytest

from retro16sim.lang import (
    Program,
    Assign,
    While,
    If,
    BinOp,
    Var,
    Const,
    Cmp,
    CmpZero,
    compile_program_to_rom,
)
from retro16sim import Machine, build_test_rom


def test_while_countdown(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(3)),
            While(
                cond=CmpZero(expr=Var("x"), op="!="),
                body=[
                    Assign("x", BinOp("-", Var("x"), Const(1))),
                ],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 0


def test_while_countup(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(0)),
            While(
                cond=CmpZero(expr=Var("x"), op="=="),
                body=[
                    Assign("x", BinOp("+", Var("x"), Const(1))),
                ],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 1


def test_if_then_else_if_taken(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(1)),
            If(
                cond=Cmp(Var("x"), op="!=", right=Const(0)),
                then_body=[Assign("x", BinOp("-", Var("x"), Const(1)))],
                else_body=[Assign("x", BinOp("+", Var("x"), Const(2)))],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 0


def test_if_then_else_else_taken(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(0)),
            If(
                cond=Cmp(Var("x"), op="!=", right=Const(0)),
                then_body=[Assign("x", BinOp("-", Var("x"), Const(1)))],
                else_body=[Assign("x", BinOp("+", Var("x"), Const(2)))],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 2


def test_cond_as_value_cmpzero(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(1)),
            Assign("y", CmpZero(expr=Var("x"), op="!=")),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1
    assert machine.cpu.reg[2] == 1


def test_cond_as_value_cmp(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(1)),
            Assign("y", Const(2)),
            Assign("z", Cmp(Var("x"), op="!=", right=Var("y"))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1
    assert machine.cpu.reg[2] == 2
    assert machine.cpu.reg[3] == 1


def test_cond_value_expr_sub(machine: Machine) -> None:
    prog = Program(
        stmts=[Assign("x", Const(3)), Assign("y", CmpZero(expr=Var("x"), op="!="))]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 3
    assert machine.cpu.reg[2] == 1


def test_cond_value_expr_if(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Cmp(Const(1), op="==", right=Const(1))),
            Assign("y", Const(0)),
            If(cond=Var("x"), then_body=[Assign("y", Const(1))]),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1
    assert machine.cpu.reg[2] == 1


def test_cmpzero_with_binop(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(3)),
            While(
                cond=CmpZero(expr=BinOp("-", Var("x"), Const(1)), op="!="),
                body=[
                    Assign("x", BinOp("-", Var("x"), Const(1))),
                ],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1
