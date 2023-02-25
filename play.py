import sys

from birdcage import *

from blessed import Terminal

import warnings

warnings.filterwarnings("ignore")

def play_interactive(board, player1, player2, term=None):
    with term.fullscreen(), term.hidden_cursor():
        print(term.move(0, 0) + "{} (W) - {} (B)".format(player1, player2))
        print(term.move(1, 0) + str(board))
        while True:
            if not isinstance(player1, Human) and not isinstance(player2, Human):
                with term.cbreak(): # wait for key press
                    inp = term.inkey()
            move = player1.play(board)
            board = board.move(move)
            print(term.move(1, 0) + str(board))
            if board.white_has_won():
                print(f"{player1} wins")
                break
            if not isinstance(player1, Human) and not isinstance(player2, Human):
                with term.cbreak(): # wait for key press
                    inp = term.inkey()
            move = player2.play(board)
            board = board.move(move)
            print(term.move(1, 0) + str(board))
            if board.black_has_won():
                print(f"{player2} wins")
                break
        with term.cbreak(): # wait for key press
            inp = term.inkey()

if __name__ == '__main__':
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    term = Terminal()
    board = BirdCage(M=M)
    player1 = Shannon()
    player2 = Human(term)
    play_interactive(board, player1, player2, term=term)