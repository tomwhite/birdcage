from birdcage import *

from blessed import Terminal

def play_interactive(board, player1, player2, M=3, term=None):
    with term.fullscreen(), term.hidden_cursor():
        print(term.move(0, 0) + "{} (W) - {} (B)".format(player1, player2))
        print(term.move(1, 0) + str(board))
        while True:
            with term.cbreak(): # wait for key press
                inp = term.inkey()
            move = player1.play(board)
            board = board.move(move)
            print(term.move(1, 0) + str(board))
            if board.white_has_won():
                print(f"{player1} wins")
                break

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
    term = Terminal()
    board = BridgIt()
    player1 = Shannon()
    player2 = Random()
    play_interactive(board, player1, player2, term=term)