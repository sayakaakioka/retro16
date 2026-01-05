from retro16sim.lang import (
    Program,
    Assign,
    If,
    Literal,
    Var,
    UnaryOp,
    BinaryOp,
    compile_program_to_rom,
)
from retro16sim import build_test_rom, Machine


def test_cmp_lt_value(machine: Machine) -> None:
    prog = Program([Assign("x", BinaryOp(left=Literal(1), op="<", right=Literal(2)))])

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 1


def test_cmp_ge_value(machine: Machine) -> None:
    prog = Program([Assign("x", BinaryOp(left=Literal(2), op=">=", right=Literal(2)))])

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 1


def test_cmp_le_value(machine: Machine) -> None:
    prog = Program([Assign("x", BinaryOp(left=Literal(2), op="<=", right=Literal(1)))])

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 0


def test_if_with_compare(machine: Machine) -> None:
    prog = Program(
        [
            Assign("x", Literal(0)),
            If(
                cond=BinaryOp(Literal(1), "<", Literal(2)),
                then_body=[Assign("x", Literal(7))],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(200, trace=False)
    assert machine.cpu.reg[1] == 7


def test_unary_minus(machine: Machine) -> None:
    prog = Program(
        [
            Assign("x", Literal(3)),
            Assign("y", UnaryOp("-", Var("x"))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[1] == 3
    assert machine.cpu.reg[2] == (0xFFFF - 2)


def test_unary_not(machine: Machine) -> None:
    prog = Program(
        [
            Assign("x", Literal(0)),
            Assign("y", UnaryOp("!", Var("x"))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[2] == 1


def test_unary_not_nonzero(machine: Machine) -> None:
    prog = Program(
        [
            Assign("x", Literal(5)),
            Assign("y", UnaryOp("!", Var("x"))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)
    machine.run_n_steps(100, trace=False)
    assert machine.cpu.reg[2] == 0
