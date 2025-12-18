def test_pipeline_mul_precedence(run_src) -> None:
    src = """
    x = 1 + 2 * 3;
    """
    r = run_src(src, steps=50)

    assert r.machine.cpu.reg[1] == 7


def test_pipeline_div(run_src) -> None:
    src = """
    x = 7 / 3 ;
    """
    r = run_src(src, steps=50)

    assert r.machine.cpu.reg[1] == 2
