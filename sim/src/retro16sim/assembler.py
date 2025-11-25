from .const import (
    BYTE_BITS,
    BYTE_MASK,
    IMM6_MASK,
    OPCODE_SHIFT,
    OPCODE_MASK,
    OFF12_MASK,
    REG_MASK,
    REG_SHIFT_RS1,
    REG_SHIFT_RS2,
    REG_SHIFT_RD,
)

from .isa import Op


def asm_add(rd: int, rs1: int, rs2: int) -> int:
    return _encode_r(Op.ADD, rd, rs1, rs2)


def asm_sub(rd: int, rs1: int, rs2: int) -> int:
    return _encode_r(Op.SUB, rd, rs1, rs2)


def asm_addi(rd: int, rs: int, imm: int) -> int:
    return _encode_i(Op.ADDI, rd, rs, imm)


def asm_cmp(rd: int, rs1: int, rs2: int) -> int:
    return _encode_r(Op.CMP, rd, rs1, rs2)


def asm_cmpi(rd: int, rs: int, imm: int) -> int:
    return _encode_i(Op.CMPI, rd, rs, imm)


def asm_jmp(off_words: int) -> int:
    return _encode_j(Op.JMP, off_words)


def asm_jz(off_words: int) -> int:
    return _encode_j(Op.JZ, off_words)


def asm_jnz(off_words: int) -> int:
    return _encode_j(Op.JNZ, off_words)


def asm_halt():
    return _encode_j(Op.HALT, 0)


def _encode_i(opcode: int, rd: int, rs: int, imm: int) -> int:
    imm &= IMM6_MASK  # use 6 bits only (decoder takes care of sign)
    return (
        ((opcode & OPCODE_MASK) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs & REG_MASK) << REG_SHIFT_RS1)
        | imm
    )


def _encode_r(opcode: int, rd: int, rs1: int, rs2: int) -> int:
    return (
        ((opcode & OPCODE_MASK) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs1 & REG_MASK) << REG_SHIFT_RS1)
        | ((rs2 & REG_MASK) << REG_SHIFT_RS2)
    )


def _encode_j(opcode: int, off_words: int) -> int:
    off = off_words & OFF12_MASK  # signed 12 bits
    return ((opcode & OPCODE_MASK) << OPCODE_SHIFT) | off


# for test
def build_test_rom(rom_words: list[int]) -> bytes:

    # w0 = assemble_addi(Op.ADDI, rd=1, rs=1, imm=1)  # ADDI R1, R1, #1
    # w1 = assemble_jmp(Op.JMP, off_words=-2)  # JMP -2
    # rom_words = [w0, w1]

    rom_bytes = bytearray()
    for w in rom_words:
        rom_bytes.append(w & BYTE_MASK)  # low byte
        rom_bytes.append((w >> BYTE_BITS) & BYTE_MASK)  # high byte
    return bytes(rom_bytes)
