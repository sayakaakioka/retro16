import pytest


def test_logic_and_short_circuit_skips_rhs_div0(run_src) -> None:
    src = """
    x = 0 && (1 / 0);
    """
    r = run_src(src, steps=50)
    assert r.machine.cpu.reg[1] == 0


def test_logic_or_short_circuit_skips_rhs_div0(run_src) -> None:
    src = """
    x = 1 || (1 / 0);
    """
    r = run_src(src, steps=50)
    assert r.machine.cpu.reg[1] == 1


def test_logic_and_evaluate_rhs_when_needed_div0_raises(run_src) -> None:
    src = """
    s = 1 && (1 / 0);
    """
    with pytest.raises(ZeroDivisionError):
        run_src(src, steps=50)


def test_logic_or_evaluate_rhs_when_needed_div0_raises(run_src) -> None:
    src = """
    s = 0 || (1 / 0);
    """
    with pytest.raises(ZeroDivisionError):
        run_src(src, steps=50)


def test_parse_logic_and_or(run_src) -> None:
    src = """
    x = 3;
    y = 0;
    if (x != 0 && y == 0 || x == 0) {
        y = 1;
    } else {
        y = 2;
    }
    """
    r = run_src(src, steps=200)
    assert r.machine.cpu.reg[1] == 3
    assert r.machine.cpu.reg[2] == 1
