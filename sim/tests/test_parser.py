from retro16sim.parser import parse_program
from retro16sim.lang import compile_program_to_rom
from retro16sim import Machine, build_test_rom


def test_parse_while_countdown(machine: Machine) -> None:
    src = """
    x = 3;
    while (x != 0) {
        x = x - 1;
    }
    """
    prog = parse_program(src)
    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100)
    assert machine.cpu.reg[1] == 0


def test_parse_if_taken(machine: Machine) -> None:
    src = """
    x = 3;
    if (x != 0) {
        x = 5;
    }
    """

    prog = parse_program(src)
    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100)
    assert machine.cpu.reg[1] == 5


def test_parse_if_not_taken(machine: Machine) -> None:
    src = """
    x = 3;
    if (x == 0) {
        x = 5;
    }
    """

    prog = parse_program(src)
    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100)
    assert machine.cpu.reg[1] == 3


def test_parse_if_else_if_taken(machine: Machine) -> None:
    src = """
    x = 3;
    if (x != 0) {
        x = 5;
    } else {
        x = 10;
    }
    """

    prog = parse_program(src)
    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100)
    assert machine.cpu.reg[1] == 5


def test_parse_if_else_else_taken(machine: Machine) -> None:
    src = """
    x = 3;
    if (x == 0) {
        x = 5;
    } else {
        x = 10;
    }
    """

    prog = parse_program(src)
    rom_words = compile_program_to_rom(prog)
    rom = build_test_rom(rom_words)
    machine.load_rom(rom, 0x0000)

    machine.run_n_steps(100)
    assert machine.cpu.reg[1] == 10
