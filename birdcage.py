from lcapy import Circuit
import networkx as nx
from networkx.drawing import nx_agraph

class Birdcage:

    def __init__(self, M=3):
        self.M = M
        self.G_orig = self._create_network()
        self.G = self.G_orig.copy()
        self.removed_nodes = {} # mapping to equivalents in G

    def _create_network(self):
        M = self.M
        G = nx.Graph()
        for i in range(M - 1):
            for j in range(M):
                if i == 0: # join top row to Q
                    G.add_edge(f"{i}_{j}", "Q", R=1.0)
                if i == M - 2: # join bottom row to P (0)
                    G.add_edge("0", f"{i}_{j}", R=1.0)
                if i < M - 2: # join right
                    G.add_edge(f"{i}_{j}", f"{i+1}_{j}", R=1.0)
                if j < M - 1: # join down
                    G.add_edge(f"{i}_{j}", f"{i}_{j+1}", R=1.0)
        return G

    def _normalize_nodes(self, n1, n2):
        """Ensure node is in G"""
        rn = self.removed_nodes
        return rn.get(n1, n1), rn.get(n2, n2)

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

    def get_voltages(self):
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

    def write_dot(self):
        G = self.G
        M = self.M
        A = nx_agraph.to_agraph(G)
        if "Q" in G.nodes:
            A.add_subgraph(['Q'], rank='same')
        for i in range(M):
            subgraph = [n for n in G.nodes if n != 0 and n.startswith(f"{i}_")]
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

    B.print_voltages()
    print(B.get_voltages())

    B.cut("0_0", "Q")
    B.short("Q", "0_1")
    B.print_voltages()
    print(B.get_voltages())

    B.cut("0_1", "1_1")
    B.short("1_0", "0")
    B.print_voltages()
    print(B.get_voltages())

    B.write_dot()
