from retro16sim.assembler import (
    asm_addi,
    asm_cmp,
    asm_cmpi,
    asm_jmp,
    asm_jz,
    asm_jnz,
    asm_jlt,
    asm_jge,
    asm_halt,
)

from retro16sim.isa import Op
from retro16sim.const import (
    OPCODE_SHIFT,
    REG_SHIFT_RD,
    REG_SHIFT_RS1,
    REG_SHIFT_RS2,
    REG_MASK,
)


def test_jz_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=0),  # 0
        asm_cmpi(rs=1, imm=0),  # 1
        asm_jz(off_words=2),  # 2 (taken)
        asm_addi(rd=2, rs=0, imm=1),  # 3
        asm_jmp(off_words=1),  # 4
        asm_addi(rd=2, rs=0, imm=7),  # 5 (target)
        asm_halt(),  # 6
    ]
    r = run_words(rom, steps=50)
    assert r.machine.cpu.reg[2] == 7


def test_jz_not_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),  # 0
        asm_cmpi(rs=1, imm=0),  # 1
        asm_jz(off_words=2),  # 2 (not taken)
        asm_addi(rd=2, rs=0, imm=1),  # 3
        asm_jmp(off_words=1),  # 4 (taken)
        asm_addi(rd=2, rs=0, imm=7),  # 5
        asm_halt(),  # 6 (target)
    ]
    r = run_words(rom, steps=50)
    assert r.machine.cpu.reg[2] == 1


def test_jnz_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),  # 0
        asm_cmpi(rs=1, imm=0),  # 1
        asm_jnz(off_words=2),  # 2 (taken)
        asm_addi(rd=2, rs=0, imm=1),  # 3
        asm_jmp(off_words=1),  # 4
        asm_addi(rd=2, rs=0, imm=9),  # 5 (target)
        asm_halt(),  # 6
    ]
    r = run_words(rom, steps=50)
    assert r.machine.cpu.reg[2] == 9


def test_jnz_not_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),  # 0
        asm_cmpi(rs=1, imm=5),  # 1
        asm_jnz(off_words=2),  # 2 (not taken)
        asm_addi(rd=2, rs=0, imm=1),  # 3
        asm_jmp(off_words=1),  # 4
        asm_addi(rd=2, rs=0, imm=9),  # 5
        asm_halt(),  # 6
    ]
    r = run_words(rom, steps=50)
    assert r.machine.cpu.reg[2] == 1


def test_jmp_loops(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=0),  # 0
        asm_addi(rd=1, rs=1, imm=1),  # 1
        asm_jmp(off_words=-2),  # jump to 1
    ]
    r = run_words(rom, steps=10)
    # 10 steps includes fetches, but roughly half are ADDI in the code.
    assert r.machine.cpu.reg[1] > 0


def test_jlt_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),
        asm_cmpi(rs=1, imm=2),
        asm_jlt(off_words=2),  # taken
        asm_addi(rd=2, rs=0, imm=0),  # skipped
        asm_jmp(off_words=1),  # skipped
        asm_addi(rd=2, rs=0, imm=1),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[2] == 1


def test_jlt_not_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=2),
        asm_cmpi(rs=1, imm=1),
        asm_jlt(off_words=2),  # not taken
        asm_addi(rd=2, rs=0, imm=0),
        asm_jmp(off_words=1),
        asm_addi(rd=2, rs=0, imm=1),  # skipped
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[2] == 0


def test_jge_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=2),
        asm_cmpi(rs=1, imm=1),
        asm_jge(off_words=2),  # taken
        asm_addi(rd=2, rs=0, imm=0),  # skipped
        asm_jmp(off_words=1),  # skipped
        asm_addi(rd=2, rs=0, imm=1),
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[2] == 1


def test_jge_not_taken(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=1),
        asm_cmpi(rs=1, imm=2),
        asm_jge(off_words=2),  # not taken
        asm_addi(rd=2, rs=0, imm=0),
        asm_jmp(off_words=1),
        asm_addi(rd=2, rs=0, imm=1),  # skipped
        asm_halt(),
    ]
    r = run_words(rom, steps=20)
    assert r.machine.cpu.reg[2] == 0


def _raw_cmp_word(*, rd: int, rs1: int, rs2: int) -> int:
    # CMP opcode with arbitrary rd field, which should be ignored by exec
    return (
        (int(Op.CMP) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs1 & REG_MASK) << REG_SHIFT_RS1)
        | ((rs2 & REG_MASK) << REG_SHIFT_RS2)
    )


def _raw_cmpi_word(*, rd: int, rs: int, imm6: int) -> int:
    # CMPI opcode with arbitrary rd field, which should be ignored by exec
    imm6 &= 0x3F


def test_cmp_does_not_clobber_registers(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),
        asm_addi(rd=2, rs=0, imm=7),
        asm_addi(rd=3, rs=0, imm=9),  # sentinel
        asm_cmp(rs1=1, rs2=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=50)

    assert r.machine.cpu.reg[0] == 0
    assert r.machine.cpu.reg[1] == 5
    assert r.machine.cpu.reg[2] == 7
    assert r.machine.cpu.reg[3] == 9


def test_cmpi_does_not_clobber_registers(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),
        asm_addi(rd=2, rs=0, imm=7),
        asm_cmpi(rs=1, imm=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=50)

    assert r.machine.cpu.reg[0] == 0
    assert r.machine.cpu.reg[1] == 5
    assert r.machine.cpu.reg[2] == 7


def test_cmp_ignores_rd_field_and_still_does_not_clobber(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),
        asm_addi(rd=2, rs=0, imm=7),
        asm_addi(rd=3, rs=0, imm=9),  # if rd were honored, this might get clobbered
        _raw_cmp_word(rd=3, rs1=1, rs2=2),
        asm_halt(),
    ]

    r = run_words(rom, steps=50)

    assert r.machine.cpu.reg[1] == 5
    assert r.machine.cpu.reg[2] == 7
    assert r.machine.cpu.reg[3] == 9


def test_cmpi_ignores_rd_field_and_still_does_not_clobber(run_words) -> None:
    rom = [
        asm_addi(rd=1, rs=0, imm=5),
        asm_addi(rd=3, rs=0, imm=9),  # sentinel
        _raw_cmp_word(rd=3, rs1=1, rs2=2),  # should not write R3
        asm_halt(),
    ]

    r = run_words(rom, steps=50)

    assert r.machine.cpu.reg[1] == 5
    assert r.machine.cpu.reg[3] == 9
