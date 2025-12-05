def test_machine_initial_state(machine):
    assert len(machine.cpu.reg) > 0


def test_cpu_reset(machine):
    assert machine.cpu.pc == 0
