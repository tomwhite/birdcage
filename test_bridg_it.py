from bridg_it import *
from bridg_it import _to_alpha, _to_numeric
import pytest
from sympy import Rational

"""                      
     ● - ● - ●  
5  ○   ○   ○   ○
4  | ●   ●   ● |
3  ○   ○   ○   ○
2  | ●   ●   ● |
1  ○   ○   ○   ○
     ● - ● - ●  
     A B C D E  
"""


def test_to_numeric():
    assert _to_numeric("A1") == (1, 1)
    assert _to_numeric("A2") == (1, 2)
    assert _to_numeric("A3") == (1, 3)


def test_to_alpha():
    assert _to_alpha(1, 1) == ("A1")
    assert _to_alpha(1, 2) == ("A2")
    assert _to_alpha(1, 3) == ("A3")


def test_is_valid_move():
    assert not is_valid_move("A0")
    assert is_valid_move("A1")
    assert not is_valid_move("A2")
    assert is_valid_move("A3")
    assert not is_valid_move("A4")
    assert is_valid_move("A5")
    assert not is_valid_move("A6")

    assert not is_valid_move("B0")
    assert not is_valid_move("B1")
    assert is_valid_move("B2")
    assert not is_valid_move("B3")
    assert is_valid_move("B4")
    assert not is_valid_move("B5")
    assert not is_valid_move("B6")

    assert not is_valid_move("F2")


def test_valid_moves():
    VALID_MOVES = {
        "A1",
        "A3",
        "A5",
        "B2",
        "B4",
        "C1",
        "C3",
        "C5",
        "D2",
        "D4",
        "E1",
        "E3",
        "E5",
    }
    assert set(valid_moves(M=3)) == VALID_MOVES


def test_game():
    b = BridgIt()
    for move in ["A1", "C3", "C1", "C5", "E1"]:
        assert not b.white_has_won()
        assert not b.black_has_won()
        b = b.move(move)
    assert b.white_has_won()
    assert not b.black_has_won()


def test_bridg_it_long_game():
    # from "Bridg-It – Beating Shannon’s Analog Heuristic" by Thomas Fisher
    # https://www.minet.uni-jena.de//math-net/reports/sources/2009/09-07report.pdf
    b = BridgIt()
    moves = ["A5", "c5", "C3", "a1", "B4", "e3", "E1", "d2", "C1", "b2", "E5", "d4"]
    for move in moves:
        assert not b.white_has_won()
        assert not b.black_has_won()
        b = b.move(move.upper())
        print()
        print(b)
    assert not b.white_has_won()
    assert b.black_has_won()


def test_birdcage_long_game():
    bc = BirdCage()
    moves = ["A5", "c5", "C3", "a1", "B4", "e3", "E1", "d2", "C1", "b2", "E5", "d4"]
    for move in moves:
        assert not bc.white_has_won()
        assert not bc.black_has_won()
        bc = bc.move(move.upper())
        print()
        print(bc)
    assert not bc.white_has_won()
    assert bc.black_has_won()


def test_random():
    bc = BirdCage()
    r = Random()
    move = r.play(bc)
    bc.move(move)
    print(bc)


def test_shannon_voltage_diffs():
    bc = BirdCage(moves=["A5", "C5"])
    s = Shannon(use_pull_up_resistors=False)
    voltage_diffs = s._get_voltage_diffs(bc)
    assert voltage_diffs["C3"] == Rational(129 - 58, 129)


def test_shannon_game_M3_no_pull_ups():
    bc = BirdCage()
    s = Shannon(use_pull_up_resistors=False)
    moves = ["A5", "c5", "C3", "a1", "B4", "e3", "E1", "d2", "C1", "b2", "E5", "d4"]
    for m1, m2 in zip(*[iter(moves)] * 2):
        move = s.play(bc)
        if move != m1:
            # moves differ, but check their voltage differences are the same
            # this checks that Shannon is consistent with the expected moves
            voltage_diffs = s._get_voltage_diffs(bc)
            assert voltage_diffs[move] == voltage_diffs[m1]
        bc.move(m1)
        bc.move(m2.upper())
    assert not bc.white_has_won()
    assert bc.black_has_won()

def test_shannon_game_M3():
    bc = BirdCage()
    s = Shannon()
    moves = ["A1", "c1", "C3", "a5", "B2", "e3", "E5", "d4", "D2", "e1", "B4", "c5"]
    for m1, m2 in zip(*[iter(moves)] * 2):
        move = s.play(bc)
        if move != m1:
            # moves differ, but check their voltage differences are the same
            # this checks that Shannon is consistent with the expected moves
            voltage_diffs = s._get_voltage_diffs(bc)
            assert voltage_diffs[move] == voltage_diffs[m1]
        bc.move(m1)
        bc.move(m2.upper())
    assert not bc.white_has_won()
    assert bc.black_has_won()

@pytest.mark.slow
def test_shannon_game_M4():
    # from "Bridg-It – Beating Shannon’s Analog Heuristic" by Thomas Fisher
    # section 4.2
    bc = BirdCage(M=4)
    s = Shannon()
    moves = [
        "A1",
        "c1",
        "C3",
        "e3",
        "E5",
        "a7",
        "A5",
        "d4",
        "C5",
        "g5",
        "G7",
        "f6",
        "E7",
        "d6",
        "F4",
        "g3",
        "G1",
        "f2",
        "C7",
        "b6",
        "E1",
        "d2",
    ]
    for m1, m2 in zip(*[iter(moves)] * 2):
        move = s.play(bc)
        if move != m1:
            # moves differ, but check their voltage differences are the same
            # this checks that Shannon is consistent with the expected moves
            voltage_diffs = s._get_voltage_diffs(bc)
            assert voltage_diffs[move] == voltage_diffs[m1]
        bc.move(m1)
        bc.move(m2.upper())
    assert not bc.white_has_won()
    assert bc.black_has_won()

def test_part_of_circuit_not_connected():
    bc = BirdCage(moves=["E1", "E3", "D2", "B2", "D4", "B4", "E5"])
    s = Shannon()
    # following should not raise an error
    voltage_diffs = s._get_voltage_diffs(bc)

    s = Shannon(use_pull_up_resistors=False)
    with pytest.raises(Exception):
        voltage_diffs = s._get_voltage_diffs(bc)

@pytest.mark.slow
def test_discrete_voltage_discrimination():
    # There are circuits where the Shannon heuristic breaks down
    # when implemented using a 10-bit analog to digital converter (like the Arduino).
    # This example was found using find_min_delta.py.

    bc = BirdCage(M=4, moves=["A1", "B4", "E3", "D6"])
    s = Shannon(use_pull_up_resistors=False)
    voltage_diffs = s._get_voltage_diffs(bc)
    assert voltage_diffs["C1"] > voltage_diffs["G3"]
    assert round((voltage_diffs["C1"] * 1024).evalf()) == round((voltage_diffs["G3"] * 1024).evalf())