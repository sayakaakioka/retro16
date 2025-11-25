import pytest
from .test_helpers import (
    prog_infinite_loop_r1_add,
    prog_add_two_then_halt,
    prog_countdown,
)
from retro16sim.machine import Machine


@pytest.mark.parametrize(
    ("rom_words", "steps", "expected_r1"),
    [
        (prog_add_two_then_halt(), 5, 2),
        (prog_infinite_loop_r1_add(), 10, 5),
        (prog_countdown(), 100, 0),
    ],
)
def test_r1_updates_as_expected(
    machine_with_test_rom: Machine, steps: int, expected_r1: int
) -> None:
    m = machine_with_test_rom
    m.run_n_steps(steps, trace=False)

    actual_r1 = m.cpu.reg[1]
    assert actual_r1 == expected_r1
