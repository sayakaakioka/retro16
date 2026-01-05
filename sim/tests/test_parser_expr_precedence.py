from retro16sim.parser import parse_program
from retro16sim.lang import Assign, Literal, BinaryOp, Program


def test_expr_precedence_mul_over_add() -> None:
    src = "x = 1 + 2 * 3;"
    prog = parse_program(src)
    assert isinstance(prog, Program)

    stmt0 = prog.stmts[0]
    assert isinstance(stmt0, Assign)
    assert stmt0.name == "x"

    # expected: 1 + (2 * 3)
    e = stmt0.expr
    assert isinstance(e, BinaryOp)
    assert e.op == "+"
    assert isinstance(e.left, Literal) and e.left.value == 1
    assert isinstance(e.right, BinaryOp) and e.right.op == "*"
