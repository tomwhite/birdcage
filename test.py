from birdcage import *
import pytest

"""                      
     ● - ● - ●           ●     Q
5  ○   ○   ○   ○       / | \ 
4  | ●   ●   ● |     ● - ● - ●
3  ○   ○   ○   ○     |   |   |
2  | ●   ●   ● |     ● - ● - ●
1  ○   ○   ○   ○       \ | /
     ● - ● - ●           ●     0
     A B C D E       A B C D E
"""


def test_is_valid_move():
    b = Board()

    assert not b.is_valid_move("A0")
    assert b.is_valid_move("A1")
    assert not b.is_valid_move("A2")
    assert b.is_valid_move("A3")
    assert not b.is_valid_move("A4")
    assert b.is_valid_move("A5")
    assert not b.is_valid_move("A6")

    assert not b.is_valid_move("B0")
    assert not b.is_valid_move("B1")
    assert b.is_valid_move("B2")
    assert not b.is_valid_move("B3")
    assert b.is_valid_move("B4")
    assert not b.is_valid_move("B5")
    assert not b.is_valid_move("B6")

    assert not b.is_valid_move("F2")


def test_valid_moves():
    b = Board()

    assert b.valid_moves() == {'A1', 'A3', 'A5', 'B2', 'B4', 'C1', 'C3', 'C5', 'D2', 'D4', 'E1', 'E3', 'E5'}


def test_move_to_edge():
    b = Board()

    assert b.move_to_edge("A1") == ("0", "A2")
    assert b.move_to_edge("A3") == ("A2", "A4")
    assert b.move_to_edge("A5") == ("A4", "Q")

    with pytest.raises(ValueError):
        b.move_to_edge("A2")
    with pytest.raises(ValueError):
        b.move_to_edge("A4")

    assert b.move_to_edge("B2") == ("A2", "C2")
    assert b.move_to_edge("B4") == ("A4", "C4")

    with pytest.raises(ValueError):
        b.move_to_edge("B1")
    with pytest.raises(ValueError):
        b.move_to_edge("B3")
    with pytest.raises(ValueError):
        b.move_to_edge("B5")


def test_edge_to_move():
    b = Board()

    for move in b.valid_moves():
        edge = b.move_to_edge(move)
        assert b.edge_to_move(*edge) == move
        assert b.edge_to_move(edge[1], edge[0]) == move

    with pytest.raises(ValueError):
        b.edge_to_move("A2", "A5")
    with pytest.raises(ValueError):
        b.edge_to_move("A2", "D2")
    with pytest.raises(ValueError):
        b.edge_to_move("0", "Q")


def test_initial_voltages():
    B = Birdcage()

    voltages = B.get_voltage_differences()
    assert voltages[('A4', 'Q')] == pytest.approx(5/3)
    assert voltages[('C4', 'Q')] == pytest.approx(5/3)
    assert voltages[('E4', 'Q')] == pytest.approx(5/3)

    assert voltages[('A4', 'C4')] == 0
    assert voltages[('C4', 'E4')] == 0

    assert voltages[('A2', 'A4')] == pytest.approx(5/3)
    assert voltages[('C2', 'C4')] == pytest.approx(5/3)
    assert voltages[('E2', 'E4')] == pytest.approx(5/3)

    assert voltages[('A2', 'C2')] == 0
    assert voltages[('C2', 'E2')] == 0

    assert voltages[('0', 'A2')] == pytest.approx(5/3)
    assert voltages[('0', 'C2')] == pytest.approx(5/3)
    assert voltages[('0', 'E2')] == pytest.approx(5/3)


def test_minimal_failure():
    # from "Bridg-It – Beating Shannon’s Analog Heuristic" by Thomas Fisher
    # https://www.minet.uni-jena.de//math-net/reports/sources/2009/09-07report.pdf

    B = Birdcage()

    B.cut("A4", "Q")
    B.short("Q", "C4")

    voltages = B.get_voltage_differences()
    assert voltages[('A4', 'Q')] == pytest.approx(5 * (129 - 89) / 129)

    voltages = B.get_voltages()
    print(voltages.nodes)
    print(nx.get_node_attributes(voltages, "voltage"))

