from .cpu import CPU
from .bus import Bus
from .assembler import build_test_rom


class Machine:
    def __init__(self):
        self.bus = Bus()
        self.cpu = CPU(self.bus)
        # TODO: self.ppu = PPU(self.bus)
        # TODO: self.apu = APU(self.bus)
        self.cycles = 0

    def reset(self) -> None:
        self.cpu.pc = 0x0000
        self.cpu.reg = [0] * 8
        self.cpu.flag_z = self.cpu.flag_n = self.cpu.flag_c = self.cpu.flag_v = False
        self.cpu.halted = False

    def load_rom(self, data: bytes, addr=0x0000) -> None:
        for i, b in enumerate(data):
            self.bus.mem[addr + i] = b

    def run_frame(self) -> None:
        # cycles in a frame
        for _ in range(10000):
            if self.cpu.halted:
                break
            self.cpu.step()
            self.cycles += 1
            # TODO: handle PPU/APU

    def run_step(self, trace=False) -> None:
        if not self.cpu.halted:
            self.cpu.step(trace=trace)
            self.cycles += 1

    def run_n_steps(self, n: int, trace=False) -> None:
        for _ in range(n):
            if self.cpu.halted:
                break
            self.run_step(trace=trace)


def run_test_program(steps: int = 10, trace: bool = False) -> "Machine":
    m = Machine()
    m.reset()
    rom = build_test_rom()
    m.load_rom(rom, 0x0000)

    # test steps
    m.run_n_steps(steps, trace=True)

    return m


if __name__ == "__main__":
    m = run_test_program(10, trace=True)
    print("Final R1 = ", hex(m.cpu.reg[1]))
