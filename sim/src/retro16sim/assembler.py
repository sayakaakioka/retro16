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

type Reg = int
type Imm = int


def asm_add(rd: Reg, rs1: Reg, rs2: Reg) -> int:
    return _encode_r(opcode=Op.ADD, rd=rd, rs1=rs1, rs2=rs2)


def asm_sub(rd: Reg, rs1: Reg, rs2: Reg) -> int:
    return _encode_r(opcode=Op.SUB, rd=rd, rs1=rs1, rs2=rs2)


def asm_mul(rd: int, rs1: int, rs2: int) -> int:
    return _encode_r(Op.MUL, rd, rs1, rs2)


def asm_div(rd: int, rs1: int, rs2: int) -> int:
    return _encode_r(Op.DIV, rd, rs1, rs2)


def asm_addi(rd: Reg, rs: Reg, imm: Imm) -> int:
    return _encode_i(opcode=Op.ADDI, rd=rd, rs=rs, imm=imm)


def asm_cmp(rs1: Reg, rs2: Reg) -> int:
    return _encode_r(opcode=Op.CMP, rd=0, rs1=rs1, rs2=rs2)


def asm_cmpi(rs: Reg, imm: Imm) -> int:
    return _encode_i(opcode=Op.CMPI, rd=0, rs=rs, imm=imm)


def asm_jmp(off_words: int) -> int:
    return _encode_j(opcode=Op.JMP, off_words=off_words)


def asm_jz(off_words: int) -> int:
    return _encode_j(opcode=Op.JZ, off_words=off_words)


def asm_jnz(off_words: int) -> int:
    return _encode_j(opcode=Op.JNZ, off_words=off_words)


def asm_jlt(off_words: int) -> int:
    return _encode_j(Op.JLT, off_words)


def asm_jge(off_words: int) -> int:
    return _encode_j(Op.JGE, off_words)


def asm_halt():
    return _encode_j(opcode=Op.HALT, off_words=0)


def _encode_i(opcode: Op, rd: int, rs: int, imm: int) -> int:
    if rd is None:
        raise TypeError("rd must be int")

    if rs is None:
        raise TypeError("rs must be int")

    if imm is None:
        raise TypeError("imm must be int")

    imm &= IMM6_MASK  # use 6 bits only (decoder takes care of sign)
    return (
        ((opcode & OPCODE_MASK) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs & REG_MASK) << REG_SHIFT_RS1)
        | imm
    )


def _encode_r(opcode: Op, rd: int, rs1: int, rs2: int) -> int:
    if rd is None:
        raise TypeError("rd must be int")

    if rs1 is None:
        raise TypeError("rs1 must be int")

    if rs2 is None:
        raise TypeError("rs2 must be int")

    return (
        ((opcode & OPCODE_MASK) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs1 & REG_MASK) << REG_SHIFT_RS1)
        | ((rs2 & REG_MASK) << REG_SHIFT_RS2)
    )


def _encode_j(opcode: Op, off_words: int) -> int:
    if off_words is None:
        raise TypeError("off_words must be int")

    off = off_words & OFF12_MASK  # signed 12 bits
    return ((opcode & OPCODE_MASK) << OPCODE_SHIFT) | off


# for test
def build_test_rom(rom_words: list[int]) -> bytes:
    rom_bytes = bytearray()
    for w in rom_words:
        rom_bytes.append(w & BYTE_MASK)  # low byte
        rom_bytes.append((w >> BYTE_BITS) & BYTE_MASK)  # high byte
    return bytes(rom_bytes)
