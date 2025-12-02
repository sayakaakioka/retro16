# import pytest

from retro16sim.lang import (
    Program,
    Assign,
    While,
    BinOp,
    Var,
    Const,
    CmpZero,
    compile_program_to_rom,
)
from retro16sim import Machine, build_test_rom


def test_while_countdown_lang(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(3)),
            While(
                cond=CmpZero("x", op="!="),
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


def test_while_countup_lang(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Const(0)),
            While(
                cond=CmpZero("x", op="=="),
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
