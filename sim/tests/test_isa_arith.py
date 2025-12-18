import pytest

from retro16sim.assembler import (
    asm_add,
    asm_addi,
    asm_sub,
    asm_mul,
    asm_div,
    asm_cmp,
    asm_cmpi,
    asm_halt,
)


def test_addi_sets_reg(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),  # ADDI R1, R0, #5
        asm_halt(),
    ]
    r = run_words(rom, steps=10)
    assert r.machine.cpu.reg[1] == 5


def test_add_adds_two_regs(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=2),
        asm_addi(rd=2, rs=0, imm=3),
        asm_add(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[3] == 5


def test_sub_subtracts_two_regs(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=10),
        asm_addi(rd=2, rs=0, imm=4),
        asm_sub(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[3] == 6


def test_addi_negative_imm(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=3),
        asm_addi(rd=1, rs=1, imm=-1),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[1] == 2


def test_addi_sets_reg_and_flags(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),  # ADDI R1, R0, #5
        asm_halt(),
    ]
    r = run_words(rom, steps=10)

    assert r.machine.cpu.reg[1] == 5
    assert r.machine.cpu.flag_z is False
    assert r.machine.cpu.flag_n is False


def test_addi_negative_sets_n(run_words) -> None:
    # R1 = 0 + (-1) = 0xFFFF
    rom = [
        asm_addi(rd=1, rs=0, imm=-1),
        asm_halt(),
    ]
    r = run_words(rom, steps=10)

    assert r.machine.cpu.reg[1] == 0xFFFF
    assert r.machine.cpu.flag_n is True


def test_mul_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=6),
        asm_addi(rd=2, rs=0, imm=7),
        asm_mul(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)

    assert r.machine.cpu.reg[3] == 42


def test_div_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=7),
        asm_addi(rd=2, rs=0, imm=3),
        asm_div(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)

    assert r.machine.cpu.reg[3] == 2


def test_div_by_zero_raises(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=7),
        asm_addi(rd=2, rs=0, imm=0),
        asm_div(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]
    with pytest.raises(ZeroDivisionError):
        run_words(rom, steps=20)


def test_cmpi_equal_sets_z(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=3),  # ADDI R1, R0, #3
        asm_cmpi(rs=1, imm=3),  # CMPI R1, #3
        asm_halt(),  # HALT
    ]
    r = run_words(rom, steps=10)

    assert r.machine.cpu.flag_z is True


def test_cmp_not_equal_clears_z(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),  # ADDI R1, R0, #1
        asm_addi(rd=2, rs=0, imm=2),  # ADDI R2, R0, #2
        asm_cmp(rs1=1, rs2=2),  # CMP R1, R2
        asm_halt(),  # HALT
    ]
    r = run_words(rom, steps=10)

    assert r.machine.cpu.flag_z is False
