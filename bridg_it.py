import math
from itertools import product
from lcapy import Circuit
import networkx as nx
import random
import sympy

# Utility functions for dealing with move notation

def _to_numeric(alpha):
    """Convert move (or position) from alphanumeric ('A3') to numeric (1, 3) notation."""
    col_letter, row_num = alpha[0], int(alpha[1])
    return ord(col_letter) - ord("A") + 1, row_num

def _to_alpha(x, y):
    """Convert move (or position) from numeric (1, 3) to alphanumeric ('A3') notation."""
    return f"{chr(x + ord('A') - 1)}{y}"

def is_valid_move(move, M=3):
    """Check if a move is a valid move on a board of size `M`."""
    x, y = _to_numeric(move)
    return 0 < x < 2 * M and 0 < y < 2 * M and (x + y) % 2 == 0

def valid_moves(M=3):
    """Return all the valid moves on the board of size `M`."""
    for (x, y) in product(range(1, 2 * M), range(1, 2 * M)):
        if (x + y) % 2 == 0:
            yield _to_alpha(x, y)


class BridgIt:
    """A Bridg-It board containing the moves of both players,
    and a graph of connections for each player.
    
    Here is a starting board of size `M`=3:

         ● - ● - ●  
    5  ○   ○   ○   ○
    4  | ●   ●   ● |
    3  ○   ○   ○   ○
    2  | ●   ●   ● |
    1  ○   ○   ○   ○
         ● - ● - ●  
         A B C D E  
    """

    def __init__(self, M=3):
        self.M = M
        self.moves = []
        self.white_graph = nx.Graph()
        self.black_graph = nx.Graph()
        # add the initial connections at each side of the board
        for i in range(M - 1):
            self.white_graph.add_edge((0, 2 * i + 1), (0, 2 * i + 3))
            self.black_graph.add_edge((2 * i + 1, 0), (2 * i + 3, 0))
            self.white_graph.add_edge((2 * M, 2 * i + 1), (2 * M, 2 * i + 3))
            self.black_graph.add_edge((2 * i + 1, 2 * M), (2 * i + 3, 2 * M))

    def _move_to_edge(self, x, y, white):
        """Convert a numeric move to an edge."""
        if (white and x % 2 == 0) or (not white and x % 2 == 1):
            return (x, y - 1), (x, y + 1)
        else:
            return (x - 1, y), (x + 1, y)

    def white_has_won(self):
        """Check if white has won, by joining the left and right sides of the board."""
        return len(list(nx.connected_components(self.white_graph))) == 1

    def black_has_won(self):
        """Check if black has won, by joining the top and bottom sides of the board."""
        return len(list(nx.connected_components(self.black_graph))) == 1

    def move(self, move):
        """Apply the given move to the current board and return the resulting board."""
        if not is_valid_move(move, self.M):
            raise ValueError(f"Invalid move: {move}")
        if move in self.moves:
            raise ValueError(f"Move {move} has already been made")
        x, y = _to_numeric(move)
        if len(self.moves) % 2 == 0: # white move
            edge = self._move_to_edge(x, y, True)
            self.white_graph.add_edge(*edge)
        else: # black move
            edge = self._move_to_edge(x, y, False)
            self.black_graph.add_edge(*edge)
        self.moves.append(move)
        return self

    def __str__(self):
        """Return a printable representation of this board"""
        M = self.M
        s = ""
        for y in range(2 * M, -1, -1):
            # numbers on left side
            if 0 < y < 2 * M:
                s += f"{y} "
            else:
                s += "  "
            # main grid
            for x in range(0, 2 * M + 1):
                if (x + y) % 2 == 0: # edge
                    # TODO: use _move_to_edge here
                    if x % 2 == 0 and ((x, y - 1), (x, y + 1)) in self.white_graph.edges():
                        s += "| "
                    elif x % 2 == 0 and ((x - 1, y), (x + 1, y)) in self.black_graph.edges():
                        s += "- "
                    elif x % 2 == 1  and ((x - 1, y), (x + 1, y)) in self.white_graph.edges():
                        s += "- "
                    elif x % 2 == 1  and ((x, y - 1), (x, y + 1)) in self.black_graph.edges():
                        s += "| "
                    else:
                        s += "  "
                else: # node
                    if x % 2 == 0:
                        s += "○ "
                    else:
                        s += "● "
            s = s + "\n"
        # letters on bottom row
        s += "  "
        for x in range(0, 2 * M + 1):
            if 0 < x < 2 * M:
                s += f"{chr(x + ord('A') - 1)} "
            else:
                s += "  "
        s = s + "\n"
        return s


class BirdCage:
    """A Bird Cage board containing the moves of both players, and a "bird cage" graph.
    """

    def __init__(self, M=3, moves=None):
        self.M = M
        self.moves = []
        # unlike BridgIt, we use a single graph to represent the state
        self.G = nx.Graph()
        # add all valid moves as edges of weight 1
        for move in valid_moves(self.M):
            x, y = _to_numeric(move)
            u, v = self._move_to_edge(x, y)
            self.G.add_edge(u, v, weight=1)
        # play any moves
        for move in moves or []:
            self.move(move)

    def _move_to_edge(self, x, y):
        """Convert a numeric move to an edge."""
        if x % 2 == 1:
            return self._map_node(x, y - 1), self._map_node(x, y + 1)
        else:
            return self._map_node(x - 1, y), self._map_node(x + 1, y)
        
    def _map_node(self, x, y):
        """Convert top and bottom row nodes into a single node"""
        if y in (0, 2 * self.M):
            return self.M, y
        return x, y

    def white_has_won(self):
        """Check if white has won, by CUTting all paths from top to bottom."""
        top_node = self._map_node(0, 2 * self.M)
        bottom_node = self._map_node(0, 0)
        return not nx.has_path(self.G, top_node, bottom_node)

    def black_has_won(self):
        """Check if black has won, by SHORTing a path from top to bottom."""
        top_node = self._map_node(0, 2 * self.M)
        bottom_node = self._map_node(0, 0)
        return nx.shortest_path_length(self.G, top_node, bottom_node, weight="weight") == 0

    def move(self, move):
        """Apply the given move to the current board and return the resulting board."""
        if not is_valid_move(move, self.M):
            raise ValueError(f"Invalid move: {move}")
        if move in self.moves:
            raise ValueError(f"Move {move} has already been made")
        x, y = _to_numeric(move)
        u, v = self._move_to_edge(x, y)
        if len(self.moves) % 2 == 0: # white moves are CUT (remove from graph)
            self.G.remove_edge(u, v)
        else: # black moves are SHORT (weight 0)
            self.G.add_edge(u, v, weight=0)
        self.moves.append(move)
        return self

    def __str__(self):
        """Return a printable representation of this board"""
        M = self.M
        s = ""
        for y in range(2 * M, -1, -1):
            # numbers on left side
            if 0 < y < 2 * M:
                s += f"{y} "
            else:
                s += "  "
            # main grid
            for x in range(0, 2 * M + 1):
                if (x + y) % 2 == 0: # edge
                    edge = self._move_to_edge(x, y)
                    if edge in self.G.edges():
                        weight = self.G.get_edge_data(*edge)["weight"]
                        if y % 2 == 0:
                            s += "- " if weight == 1 else "= "
                        else:
                            s += "| " if weight == 1 else "‖ "
                    else:
                        s += "  "
                else: # node
                    if y % 2 == 0:
                        s += "● "
                    else:
                        s += "  "
            s = s + "\n"
        # letters on bottom row
        s += "  "
        for x in range(0, 2 * M + 1):
            if 0 < x < 2 * M:
                s += f"{chr(x + ord('A') - 1)} "
            else:
                s += "  "
        s = s + "\n"        
        return s

class Random:
    def play(self, board):
        all_moves = valid_moves(board.M)
        candidate_moves = set(all_moves) - set(board.moves)
        return random.choice(list(candidate_moves))

    def __str__(self):
        return "Random"

class Shannon:

    def __init__(self, use_pull_up_resistors=True):
        self.use_pull_up_resistors = use_pull_up_resistors

    def play(self, board):
        birdcage = BirdCage(board.M, board.moves)
        voltage_diffs = self._get_voltage_diffs(birdcage)
        return next(iter(voltage_diffs))

    def _get_voltage_diffs(self, birdcage):
        """Return a dictionary voltage diffs, keyed by move, in order of decreasing voltage diff"""
        all_moves = valid_moves(birdcage.M)
        candidate_moves = set(all_moves) - set(birdcage.moves)
        # sort moves from top-left to bottom-right (in case of ties)
        candidate_moves = sorted(candidate_moves, key=lambda x: (-int(x[1]), x[0]))
        
        circuit = self._create_circuit(birdcage)
        #circuit.draw(f"birdcage_move{len(birdcage.moves)}.png", label_ids=False, label_values=False, draw_nodes="all")
        voltage_diffs = {}
        for move in candidate_moves:
            x, y = _to_numeric(move)
            n1, n2 = birdcage._move_to_edge(x, y)
            v1 = self._get_voltage(circuit, n1)
            v2 = self._get_voltage(circuit, n2)
            voltage_diffs[move] = abs(v1 - v2)
        # sort by value and return largest
        voltage_diffs = {k: v for k, v in sorted(voltage_diffs.items(), key=lambda item: -item[1])}
        return voltage_diffs

    def _orientation(self, u, v):
        """Return a Lcapy orientation hint for a component placed between two nodes"""
        if u == v:
            raise ValueError()
        ux, uy = u
        vx, vy = v
        if ux == vx:
            return "up" if uy < vy else "down"
        if uy == vy:
            return "right" if ux < vx else "left"
        angle = math.degrees(math.atan2(vy - uy, vx - ux))
        return f"rotate={angle}"

    def _to_circuit_node(self, node):
        return f"{node[0]}_{node[1]}"

    def _create_circuit(self, birdcage):
        """Create a Lcapy circuit from the bird cage graph"""
        M = birdcage.M
        G = birdcage.G
        f = self._to_circuit_node

        s = 'V1 "Q" 0 1; down\n'
        s += f'W "Q" "{M}_{2 * M}"; right={M / 2}\n'
        s += f'W 0 "{M}_0"; right={M / 2}\n'
        for n1, n2, d in G.edges(data=True):
            R = d["weight"]
            orient = self._orientation(n1, n2)
            if R == 0:
                s += f'W "{f(n1)}" "{f(n2)}"; {orient}\n' # wire
            else:
                s += f'R__{f(n1)}__{f(n2)} "{f(n1)}" "{f(n2)}" {R}; {orient}\n' # resistor
        if self.use_pull_up_resistors:
            # need pull-up resistors to avoid errors if part of circuit is not connected
            for n in G.nodes():
                s += f'R__{f(n)}__Q "{f(n)}" "Q" 30\n' # pull-up resistor
        return Circuit(s)

    def _get_voltage(self, circuit, node):
        v = circuit[self._to_circuit_node(node)].V
        # convert to a SymPy Rational
        return v.dc.as_expr().expr

    def __str__(self):
        return "Shannon"