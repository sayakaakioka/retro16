from .const import (
    BYTE_BITS,
    BYTE_MASK,
    IMM6_MASK,
    OPCODE_SHIFT,
    OPCODE_MASK,
    OFF12_MASK,
    REG_MASK,
    REG_SHIFT_RS1,
    REG_SHIFT_RD,
)


def assemble_addi(opcode: int, rd: int, rs: int, imm: int) -> int:
    imm &= IMM6_MASK  # use 6 bits only (decode takes care of sign)
    return (
        ((opcode & OPCODE_MASK) << OPCODE_SHIFT)
        | ((rd & REG_MASK) << REG_SHIFT_RD)
        | ((rs & REG_MASK) << REG_SHIFT_RS1)
        | imm
    )


def assemble_jmp(opcode: int, off_words: int) -> int:
    off = off_words & OFF12_MASK  # signed 12 bits
    return ((opcode & OPCODE_MASK) << OPCODE_SHIFT) | off


# for test
def build_test_rom() -> bytes:
    from .isa import Op

    w0 = assemble_addi(Op.ADDI, rd=1, rs=1, imm=1)  # ADDI R1, R1, #1
    w1 = assemble_jmp(Op.JMP, off_words=-2)  # JMP -2
    rom_words = [w0, w1]

    rom_bytes = bytearray()
    for w in rom_words:
        rom_bytes.append(w & BYTE_MASK)  # low byte
        rom_bytes.append((w >> BYTE_BITS) & BYTE_MASK)  # high byte
    return bytes(rom_bytes)
