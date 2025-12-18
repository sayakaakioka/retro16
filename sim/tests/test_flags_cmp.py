import pytest

from retro16sim.assembler import asm_addi, asm_cmp, asm_cmpi, asm_halt
from retro16sim import Machine, build_test_rom


def assert_flags(
    machine: Machine,
    *,
    z: bool | None = None,
    n: bool | None = None,
    c: bool | None = None,
    v: bool | None = None,
    lt: bool | None = None,
) -> None:
    cpu = machine.cpu

    if z is not None:
        assert cpu.flag_z is z

    if n is not None:
        assert cpu.flag_n is n

    if c is not None:
        assert cpu.flag_c is c

    if v is not None:
        assert cpu.flag_v is v

    if lt is not None:
        assert cpu.flag_lt is lt


def test_cmpi_eq_sets_z(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),
        asm_cmpi(rs=1, imm=1),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=True, n=False, v=False, c=True, lt=False)


def test_cmpi_lt_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),
        asm_cmpi(rs=1, imm=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=False, n=True, v=False, c=False, lt=True)


def test_cmpi_gt_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=2),
        asm_cmpi(rs=1, imm=1),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=False, n=False, v=False, c=True, lt=False)


def test_cmpi_overflow_positive_minus_negative(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=0x7FFF),
        asm_cmpi(rs=1, imm=-1),
        asm_halt(),
    ]

    pytest.skip(
        "This test should be skipped if ADDI imm6 constrain fails to generate immediate value"
    )


def test_cmpi_overflow_negative_minus_positive(run_words) -> None:
    pytest.skip(
        "This test should be skipped before implementation of the way to load immediate value"
    )


def test_cmp_eq_sets_z(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=3),
        asm_addi(rd=2, rs=0, imm=3),
        asm_cmp(rs1=1, rs2=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=True, n=False, v=False, c=True, lt=False)


def test_cmp_lt_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),
        asm_addi(rd=2, rs=0, imm=2),
        asm_cmp(rs1=1, rs2=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=False, n=True, v=False, c=False, lt=True)


def test_cmp_gt_basic(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=2),
        asm_addi(rd=2, rs=0, imm=1),
        asm_cmp(rs1=1, rs2=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=20)
    assert_flags(r.machine, z=False, n=False, v=False, c=True, lt=False)
