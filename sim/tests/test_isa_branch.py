from retro16sim.assembler import (
    asm_addi,
    asm_cmpi,
    asm_jmp,
    asm_jz,
    asm_jnz,
    asm_halt,
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
