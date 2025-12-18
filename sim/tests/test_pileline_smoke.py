def test_pipeline_while_countdown(run_src) -> None:
    src = """
    x = 3;
    while (x != 0) {
        x = x - 1;
    }
    """
    r = run_src(src, steps=200)
    assert r.machine.cpu.reg[1] == 0


def test_pipeline_if_else(run_src) -> None:
    src = """
    x = 3;
    if (x == 0) {
        x = 5;
    } else {
        x = 10;
    }
    """
    r = run_src(src, steps=200)
    assert r.machine.cpu.reg[1] == 10
