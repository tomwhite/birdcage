from itertools import product
from lcapy import Circuit
import networkx as nx
from networkx.drawing import nx_agraph


def is_valid_move(move, M=3):
    col_letter, row_num = move[0], int(move[1])
    if row_num < 1 or row_num > 2 * M - 1:
        return False
    if ord(col_letter) < ord("A") or ord(col_letter) > ord("A") + 2 * M - 2:
        return False
    return (ord(col_letter) + row_num) % 2 == 0


def col_range(M=3):
    for c in range(ord("A"), ord("A") + 2 * M - 1):
        yield chr(c)


def row_range(M=3):
    for r in range(1, 2 * M):
        yield r


def all_positions(M=3):
    return {f"{c}{r}" for (c, r) in product(col_range(M), row_range(M))}

def valid_moves(M=3):
    return {move for move in all_positions(M) if is_valid_move(move, M)}


def move_to_edge(move, M=3):
    """Convert a move like 'A3' to a pair of nodes defining an edge."""
    if not is_valid_move(move, M):
        raise ValueError(f"Invalid move: {move}")
    col_letter, row_num = move[0], int(move[1])
    if ord(col_letter) % 2 == 0:
        prev_col_letter = chr(ord(col_letter) - 1)
        next_col_letter = chr(ord(col_letter) + 1)
        return f"{prev_col_letter}{row_num}", f"{next_col_letter}{row_num}"
    else:
        if row_num == 1:
            # bottom row nodes are all "0"
            return "0", f"{col_letter}{row_num+1}"
        elif row_num == 2 * M - 1:
            # top row nodes are all "Q"
            return f"{col_letter}{row_num-1}", "Q"
        else:
            return f"{col_letter}{row_num-1}", f"{col_letter}{row_num+1}"


def edge_to_move(u, v, M=3):
    if u > v:
        u, v = v, u # sort nodes in edge
    if u == "0" and v == "Q":
        raise ValueError(f"Invalid edge {(u, v)}")
    if u == "0":
        vc, vr = v[0], int(v[1])
        uc, ur = vc, 0
    elif v == "Q":
        uc, ur = u[0], int(u[1])
        vc, vr = uc, 2 * M
    else:
        uc, ur = u[0], int(u[1])
        vc, vr = v[0], int(v[1])
    if uc == vc:
        if abs(ur - vr) != 2:
            raise ValueError(f"Invalid edge {(u, v)}")
        row_num = (ur + vr) // 2
        return f"{uc}{row_num}"
    elif ur == vr:
        if abs(ord(uc) - ord(vc)) != 2:
            raise ValueError(f"Invalid edge {(u, v)}")
        col_letter = chr((ord(uc) + ord(vc)) // 2)
        return f"{col_letter}{ur}"


class Birdcage:

    def __init__(self, M=3):
        self.M = M
        self.G_orig = self._create_network()
        self.G = self.G_orig.copy()
        self.removed_nodes = {} # mapping to equivalents in G

    def _create_network(self):
        M = self.M
        G = nx.Graph()
        for move in valid_moves(M):
            u, v = move_to_edge(move, M)
            G.add_edge(u, v, R=1.0)
        return G

    def _normalize_nodes(self, *nodes):
        """Ensure node is in G"""
        rn = self.removed_nodes
        return tuple(rn.get(n, n) for n in nodes)

    def cut(self, n1, n2):
        n1, n2 = self._normalize_nodes(n1, n2)
        self.G.remove_edge(n1, n2)

    def short(self, n1, n2):
        n1, n2 = self._normalize_nodes(n1, n2)
        # ensure "0" is never removed, and "Q" is kept until the end
        if not(n1 in (0, "0") and n2 == "Q") and n2 in (0, "0", "Q"):
            n1, n2 = n2, n1
        contracted_nodes(self.G, n1, n2)
        self.removed_nodes.update((k, n1) for k, v in self.removed_nodes.items() if v == n2)
        self.removed_nodes[n2] = n1

    def _create_circuit(self):
        s = 'V1 "Q" 0 V\n'
        for e in self.G.edges(data=True):
            R = e[2]["R"]
            s += f'R__{e[0]}__{e[1]} "{e[0]}" "{e[1]}" {R}\n'
        return Circuit(s)

    def print_voltages(self):
        M = self.M
        cct = self._create_circuit()
        def format_voltage(v):
            return v.dc
            # return v.dc.val
        print(format_voltage(cct["Q"].V))
        for i in range(M - 1):
            for j in range(M):
                node = f"{i}_{j}"
                node = self.removed_nodes.get(node, node)
                print(format_voltage(cct[node].V), end="")
                print(", ", end="")
            print()
        print(format_voltage(cct[0].V))

    def get_voltage_differences(self):
        # want voltages for whole (original) network
        cct = self._create_circuit()
        def voltage(v):
            return v.dc.evaluate(5)
        voltages = {}
        for u, v in self.G_orig.edges():
            un, vn = self._normalize_nodes(u, v)
            if u > v:
                u, v = v, u # sort nodes in edge
            voltages[(u, v)] = abs(voltage(cct[un].V) - voltage(cct[vn].V))
        return voltages

    def get_voltages(self):
        # want voltages for whole (original) network
        cct = self._create_circuit()
        def voltage(v):
            return v.dc.evaluate(5)
        G = self.G_orig.copy()
        attrs = {}
        for node in G:
            nn = self._normalize_nodes(node)[0]
            v = voltage(cct[nn].V)
            attrs[node] = dict(voltage=v)
        nx.set_node_attributes(G, attrs)
        return G

    def write_dot(self):
        G = self.G
        M = self.M
        A = nx_agraph.to_agraph(G)
        if "Q" in G.nodes:
            A.add_subgraph(['Q'], rank='same')
        for i in range(1, 2 * M):
            # TODO: fails if 2M > 10
            subgraph = [n for n in G.nodes if n != 0 and n.endswith(f"{i}")]
            if len(subgraph) > 0:
                A.add_subgraph(subgraph, rank='same')
        A.add_subgraph(['0'], rank='same')
        A.draw('G.png', prog='dot')

def contracted_nodes(G, u, v):
    # based on networkx implementation, but combines resistance values correctly
    new_edges = (
            (u, w if w != v else u, d)
            for x, w, d in G.edges(v, data=True)
            if w != u
    )
    new_edges = list(new_edges)

    v_data = G.nodes[v]
    G.remove_node(v)
    for u, v, d in new_edges:
        if G.has_edge(u, v):
            r1 = d["R"]
            r2 = G.get_edge_data(u, v)["R"]
            R=combine_R_parallel(r1, r2)
        else:
            R=d["R"]
        G.add_edge(u, v, R=R)
    return G

def combine_R_parallel(r1, r2):
    return 1 / ((1 / r1) + (1 / r2))

if __name__ == "__main__":
    B = Birdcage()

    #B.print_voltages()
    voltages = B.get_voltages()
    print(nx.get_node_attributes(voltages, "voltage"))
    print(B.get_voltage_differences())

    B.cut("A4", "Q")
    B.short("Q", "C4")
    #B.print_voltages()
    voltages = B.get_voltages()
    print(nx.get_node_attributes(voltages, "voltage"))
    print(B.get_voltage_differences())

    B.cut("C4", "C2")
    B.short("A2", "0")
    #B.print_voltages()
    voltages = B.get_voltages()
    print(nx.get_node_attributes(voltages, "voltage"))
    print(B.get_voltage_differences())

    B.write_dot()
