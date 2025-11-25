from .const import ADDR_MASK, BYTE_BITS, BYTE_MASK, MEM_SIZE, ROM_START, ROM_END


class Bus:
    def __init__(self):
        self.mem = bytearray(MEM_SIZE)
        # TODO: PPU/APU connects here

    def load8(self, addr: int) -> int:
        addr &= ADDR_MASK

        # if VRAM_START <= addr <= VRAM_END:
        #    return self.ppu.load_vram(addr)

        return self.mem[addr]

    def store8(self, addr: int, val: int) -> None:
        addr &= ADDR_MASK
        if ROM_START <= addr <= ROM_END:
            # ROM area
            return

        val &= BYTE_MASK
        self.mem[addr] = val

    def load16(self, addr: int) -> int:
        l = self.load8(addr)
        h = self.load8(addr + 1)
        return l | (h << BYTE_BITS)

    def store16(self, addr: int, val: int) -> None:
        self.store8(addr, val & BYTE_MASK)
        self.store8(addr + 1, (val >> BYTE_BITS) & BYTE_MASK)
