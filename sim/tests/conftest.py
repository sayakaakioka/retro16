import pytest

from dataclasses import dataclass
from typing import Protocol

from retro16sim import Machine, build_test_rom
from retro16sim.lang import compile_program_to_rom
from retro16sim.parser import parse_program


@dataclass(frozen=True)
class RunResult:
    machine: Machine
    steps: int


class RunWords(Protocol):
    def __call__(
        self,
        rom_words: list[int],
        *,
        steps: int = 100,
        trace: bool = False,
        reset: bool = True,
        load_addr: int = 0x0000,
    ) -> RunResult: ...


class RunSrc(Protocol):
    def __call__(
        self,
        src: str,
        *,
        steps: int = 100,
        trace: bool = False,
        reset: bool = True,
        load_addr: int = 0x0000,
    ) -> RunResult: ...


class CompileSrc(Protocol):
    def __call__(self, src: str) -> list[int]: ...


@pytest.fixture
def machine() -> Machine:
    m = Machine()
    m.reset()
    return m


@pytest.fixture
def run_words(machine: Machine) -> RunWords:
    def _run(
        rom_words: list[int],
        *,
        steps: int = 100,
        trace: bool = False,
        reset: bool = True,
        load_addr: int = 0x0000,
    ) -> RunResult:

        if reset:
            machine.reset()

        rom = build_test_rom(rom_words)
        machine.load_rom(rom, load_addr)
        before = machine.cycles
        machine.run_n_steps(steps, trace=trace)
        after = machine.cycles
        return RunResult(machine=machine, steps=(after - before))

    return _run


@pytest.fixture
def compile_src() -> CompileSrc:
    def _compile(src: str) -> list[int]:
        prog = parse_program(src)
        return compile_program_to_rom(prog)

    return _compile


@pytest.fixture
def run_src(run_words: RunWords, compile_src: CompileSrc) -> RunSrc:
    def _run(
        src: str,
        *,
        steps: int = 100,
        trace: bool = False,
        reset: bool = True,
        load_addr: int = 0x0000,
    ) -> RunResult:
        rom_words = compile_src(src)
        return run_words(
            rom_words,
            steps=steps,
            trace=trace,
            reset=reset,
            load_addr=load_addr,
        )

    return _run
