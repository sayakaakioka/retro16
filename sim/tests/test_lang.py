from retro16sim.lang import (
    Program,
    Assign,
    While,
    If,
    Var,
    Literal,
    UnaryOp,
    BinaryOp,
    compile_program_to_rom,
)
from retro16sim import Machine, build_test_rom


def test_while_countdown(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", Literal(3)),
            While(
                cond=BinaryOp(left=Var("x"), op="!=", right=Literal(0)),
                body=[
                    Assign("x", BinaryOp(left=Var("x"), op="-", right=Literal(1))),
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
            Assign("x", Literal(0)),
            While(
                cond=BinaryOp(left=Var("x"), op="==", right=Literal(0)),
                body=[
                    Assign("x", BinaryOp(left=Var("x"), op="+", right=Literal(1))),
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
            Assign("x", Literal(1)),
            If(
                cond=BinaryOp(left=Var("x"), op="!=", right=Literal(0)),
                then_body=[
                    Assign("x", BinaryOp(left=Var("x"), op="-", right=Literal(1)))
                ],
                else_body=[
                    Assign("x", BinaryOp(left=Var("x"), op="+", right=Literal(2)))
                ],
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
            Assign("x", Literal(0)),
            If(
                cond=BinaryOp(left=Var("x"), op="!=", right=Literal(0)),
                then_body=[
                    Assign("x", BinaryOp(left=Var("x"), op="-", right=Literal(1)))
                ],
                else_body=[
                    Assign("x", BinaryOp(left=Var("x"), op="+", right=Literal(2)))
                ],
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
            Assign("x", Literal(1)),
            Assign("y", BinaryOp(left=Var("x"), op="!=", right=Literal(0))),
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
            Assign("x", Literal(1)),
            Assign("y", Literal(2)),
            Assign("z", BinaryOp(left=Var("x"), op="!=", right=Var("y"))),
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
        stmts=[
            Assign("x", Literal(3)),
            Assign("y", BinaryOp(left=Var("x"), op="!=", right=Literal(0))),
        ]
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
            Assign("x", BinaryOp(left=Literal(1), op="==", right=Literal(1))),
            Assign("y", Literal(0)),
            If(cond=Var("x"), then_body=[Assign("y", Literal(1))]),
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
            Assign("x", Literal(3)),
            While(
                cond=BinaryOp(
                    left=BinaryOp(left=Var("x"), op="-", right=Literal(1)),
                    op="!=",
                    right=Literal(0),
                ),
                body=[
                    Assign("x", BinaryOp(left=Var("x"), op="-", right=Literal(1))),
                ],
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1


def test_logic_and_true_true(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", BinaryOp(left=Literal(3), op="&&", right=Literal(2))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1


def test_logic_and_false_true(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", BinaryOp(left=Literal(0), op="&&", right=Literal(2))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 0


def test_logic_or_true_false(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", BinaryOp(left=Literal(3), op="||", right=Literal(0))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1


def test_logic_or_false_true(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", BinaryOp(left=Literal(0), op="||", right=Literal(3))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1


def test_logic_or_false_false(machine: Machine) -> None:
    prog = Program(
        stmts=[
            Assign("x", BinaryOp(left=Literal(0), op="||", right=Literal(0))),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 0


def test_logic_not_combined(machine: Machine) -> None:
    # !(1 && 0) == 1
    prog = Program(
        stmts=[
            Assign(
                "x", UnaryOp("!", BinaryOp(left=Literal(3), op="&&", right=Literal(0)))
            ),
        ]
    )

    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(50, trace=False)
    assert machine.cpu.reg[1] == 1
