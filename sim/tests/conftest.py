import pytest

from retro16sim.machine import Machine, build_test_rom


@pytest.fixture
def machine() -> Machine:
    m = Machine()
    m.reset()
    return m


@pytest.fixture
def machine_with_test_rom(machine: Machine) -> Machine:
    rom = build_test_rom()
    machine.load_rom(rom, 0x0000)
    return machine
