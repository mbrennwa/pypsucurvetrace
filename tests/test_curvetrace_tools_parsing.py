import pytest

from pypsucurvetrace.curvetrace_tools import valuepairs


def test_valuepairs_single_pair():
    pairs = valuepairs("[1.5,2.5]")
    assert pairs == [[1.5], [2.5]]


def test_valuepairs_linear_sweep():
    pairs = valuepairs("[0:10,1:2,3]")
    assert len(pairs) == 2
    assert pairs[0][0] == 0.0
    assert pairs[0][-1] == 10.0
    assert pairs[1][0] == 1.0
    assert pairs[1][-1] == 2.0


def test_valuepairs_rejects_non_numeric_literal():
    with pytest.raises(SystemExit):
        valuepairs("__import__('os').system('echo pwned')")
