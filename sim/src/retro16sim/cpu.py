from .const import (
    WORD_MASK,
    ADDR_MASK,
    NEGATIVE_BIT,
    IMM6_MASK,
    IMM6_SIGNBIT,
    OPCODE_SHIFT,
    OPCODE_MASK,
    OFF12_MASK,
    OFF12_SIGNBIT,
    REG_MASK,
    REG_SHIFT_RS1,
    REG_SHIFT_RS2,
    REG_SHIFT_RD,
    SP,
)
from .isa import Op


class CPU:
    def __init__(self, bus):
        self.reg = [0] * 8  # R0..R7
        self.pc = 0  # program counter by byte
        self.flag_z = False  # zero
        self.flag_n = False  # negative (MSB=1)
        self.flag_c = False  # carry/borrow
        self.flag_v = False  # overflow (signed)
        self.bus = bus  # for memory access
        self.halted = False

        self._handlers = {
            Op.ADD: self._exec_add,
            Op.SUB: self._exec_sub,
            Op.ADDI: self._exec_addi,
            Op.LD: self._exec_ld,
            Op.ST: self._exec_st,
            Op.JMP: self._exec_jmp,
            Op.JZ: self._exec_jz,
            Op.CMP: self._exec_cmp,
            Op.CMPI: self._exec_cmpi,
            Op.JNZ: self._exec_jnz,
        }

    @property
    def sp(self) -> int:
        return self.reg[SP]

    @sp.setter
    def sp(self, value: int) -> None:
        self.reg[SP] = value & WORD_MASK

    def fetch(self) -> int:
        instr = self.bus.load16(self.pc)
        self.pc = (self.pc + 2) & WORD_MASK
        return instr

    def step(self, trace=False) -> int:
        pc_before = self.pc
        instr = self.fetch()
        opcode_val = (instr >> OPCODE_SHIFT) & OPCODE_MASK
        opcode = Op(opcode_val)  # mask is temporary
        if trace:
            print(f"PC={pc_before:04X}, INSTR={instr:04X}, OPCODE={opcode.name}")

        if trace:
            print(
                "REG:",
                [f"{r:04X}" for r in self.reg],
                "FLAGS: ZNVC=",
                int(self.flag_z),
                int(self.flag_n),
                int(self.flag_c),
                int(self.flag_v),
            )

        if opcode == Op.HALT:
            self.halted = True
            return 0

        try:
            handler = self._handlers[opcode]
        except KeyError:
            raise RuntimeError(f"Unknown opcode: {opcode_val}")

        handler(instr)
        return 1

    Reg = int
    Imm = int
    Base = int
    Offset = int

    def _decode_r(self, instr) -> tuple[Reg, Reg, Reg]:
        # [2:0] unused
        # [5:3] rs2
        rs2 = (instr >> REG_SHIFT_RS2) & REG_MASK
        # [8:6] rs1
        rs1 = (instr >> REG_SHIFT_RS1) & REG_MASK
        # [11:9] rd
        rd = (instr >> REG_SHIFT_RD) & REG_MASK
        # [15:12] opcode
        return rd, rs1, rs2

    def _decode_i(self, instr) -> tuple[Reg, Reg, Imm]:
        # [5:0] imm6 (signed)
        imm = instr & IMM6_MASK
        if imm & IMM6_SIGNBIT:
            imm -= IMM6_MASK + 1
        # [8:6] rs
        rs = (instr >> REG_SHIFT_RS1) & REG_MASK
        # [11:9] rd
        rd = (instr >> REG_SHIFT_RD) & REG_MASK
        # [15:12] opcode
        return rd, rs, imm

    def _decode_m(self, instr) -> tuple[Reg, Base, Offset]:
        # [5:0] off6 (signed)
        off = instr & IMM6_MASK
        if off & IMM6_SIGNBIT:
            off -= IMM6_MASK + 1
        # [8:6] base
        base = (instr >> REG_SHIFT_RS1) & REG_MASK
        # [11:9] rd/rs
        r = (instr >> REG_SHIFT_RD) & REG_MASK
        # [15:12] opcode
        return r, base, off

    def _decode_j(self, instr) -> Offset:
        # [11:0] offset12 (relative to PC / signed)
        off = instr & OFF12_MASK
        if off & OFF12_SIGNBIT:
            off -= OFF12_MASK + 1
        # [15:12] opcode
        return off

    def _update_flags_add(self, a, b, result) -> None:
        self.flag_z = True if result == 0 else False
        self.flag_n = bool(result & NEGATIVE_BIT)

        # False if no carry, True otherwise
        self.flag_c = (a + b) > WORD_MASK

        sa = bool(a & NEGATIVE_BIT)
        sb = bool(b & NEGATIVE_BIT)
        sr = bool(result & NEGATIVE_BIT)
        self.flag_v = True if (sa == sb and sa != sr) else False

    def _update_flags_sub(self, a, b, result) -> None:
        # result = a - b
        self.flag_z = True if result == 0 else False
        self.flag_n = bool(result & NEGATIVE_BIT)

        # True if no borrow, False otherwise
        self.flag_c = a >= b

        sa = bool(a & NEGATIVE_BIT)
        sb = bool(b & NEGATIVE_BIT)
        sr = bool(result & NEGATIVE_BIT)
        self.flag_v = True if (sa != sb and sa != sr) else False

    def _exec_add(self, instr) -> None:
        rd, rs1, rs2 = self._decode_r(instr)
        a = self.reg[rs1]
        b = self.reg[rs2]
        result = (a + b) & WORD_MASK
        self.reg[rd] = result
        self._update_flags_add(a, b, result)

    def _exec_addi(self, instr) -> None:
        rd, rs, imm = self._decode_i(instr)
        a = self.reg[rs]
        b = imm & WORD_MASK
        result = (a + b) & WORD_MASK
        self.reg[rd] = result
        self._update_flags_add(a, b, result)

    def _exec_sub(self, instr) -> None:
        rd, rs1, rs2 = self._decode_r(instr)
        a = self.reg[rs1]
        b = self.reg[rs2]
        result = (a - b) & WORD_MASK
        self.reg[rd] = result
        self._update_flags_sub(a, b, result)

    def _exec_cmp(self, instr) -> None:
        rd, rs1, rs2 = self._decode_r(instr)
        a = self.reg[rs1]
        b = self.reg[rs2]
        result = (a - b) & WORD_MASK
        self._update_flags_sub(a, b, result)

    def _exec_cmpi(self, instr) -> None:
        rd, rs, imm = self._decode_i(instr)
        a = self.reg[rs]
        b = imm & WORD_MASK
        result = (a - b) & WORD_MASK
        self._update_flags_sub(a, b, result)

    def _exec_ld(self, instr) -> None:
        rd, base, off = self._decode_m(instr)
        addr = (self.reg[base] + off) & ADDR_MASK
        val = self.bus.load16(addr)
        self.reg[rd] = val
        self.flag_z = True if val == 0 else False
        self.flag_n = bool(val & NEGATIVE_BIT)

    def _exec_st(self, instr) -> None:
        rs, base, off = self._decode_m(instr)
        addr = (self.reg[base] + off) & ADDR_MASK
        self.bus.store16(addr, self.reg[rs])

    def _exec_jmp(self, instr) -> None:
        off = self._decode_j(instr)
        # print(f"    [DEBUG] JMP: pc(before_exec) = {self.pc:04X}, off={off}")
        self.pc = (self.pc + off * 2) & WORD_MASK
        # print(f"    [DEBUG] JMP: pc(after_exec) = {self.pc:04X}")

    def _exec_jz(self, instr) -> None:
        off = self._decode_j(instr)
        if self.flag_z:
            self.pc = (self.pc + off * 2) & WORD_MASK

    def _exec_jnz(self, instr) -> None:
        off = self._decode_j(instr)
        if not self.flag_z:
            self.pc = (self.pc + off * 2) & WORD_MASK
