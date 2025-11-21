import pytest


def test_machine_with_test_rom_runs_10_steps(machine_with_test_rom) -> None:
    m = machine_with_test_rom
    m.run_n_steps(10, trace=False)

    actual_r1 = m.cpu.reg[1]
    expected_r1 = 0x0005
    assert actual_r1 == expected_r1
