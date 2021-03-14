from birdcage import *
import pytest

def test_initial_voltages():
    B = Birdcage()

    voltages = B.get_voltage_differences()
    assert voltages[('0_0', 'Q')] == pytest.approx(5/3)
    assert voltages[('0_1', 'Q')] == pytest.approx(5/3)
    assert voltages[('0_2', 'Q')] == pytest.approx(5/3)

    assert voltages[('0_0', '0_1')] == 0
    assert voltages[('0_1', '0_2')] == 0

    assert voltages[('0_0', '1_0')] == pytest.approx(5/3)
    assert voltages[('0_1', '1_1')] == pytest.approx(5/3)
    assert voltages[('0_2', '1_2')] == pytest.approx(5/3)

    assert voltages[('1_0', '1_1')] == 0
    assert voltages[('1_1', '1_2')] == 0

    assert voltages[('0', '1_0')] == pytest.approx(5/3)
    assert voltages[('0', '1_1')] == pytest.approx(5/3)
    assert voltages[('0', '1_2')] == pytest.approx(5/3)


def test_minimal_failure():
    # from "Bridg-It – Beating Shannon’s Analog Heuristic" by Thomas Fisher
    # https://www.minet.uni-jena.de//math-net/reports/sources/2009/09-07report.pdf

    B = Birdcage()

    B.cut("0_0", "Q")
    B.short("Q", "0_1")

    voltages = B.get_voltage_differences()
    assert voltages[('0_0', 'Q')] == pytest.approx(5 * (129 - 89) / 129)

