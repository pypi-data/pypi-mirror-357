from typing import List, Tuple, Iterable, Optional, Dict

from QuICT.core import Circuit
from QuICT.core.gate import CX
from .star import CnotStar


class CnotBipartite:
    """Optimize a bipartite CNOT circuit. A CNOT circuit is said to be bipartite if all the control qubits
    and target qubits of CNOT gates can be grouped into 2 seperated subset of qubits.

    Examples:
    >>> from QuICT.qcda.optimization.cnot_dag import CnotBipartite
    >>> cb = CnotBipartite()
    >>> # Input circuit has 3 qubits on each side of bipartite.
    >>> # Every qubit is connected with all qubits on the other side.
    >>> circ = cb.execute(3, 3, [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)])
    """

    @classmethod
    def _start(cls, circ: Circuit, e_from: Dict[int, List[int]], e_ancillae: Dict[Tuple[int, int], int]):
        """Move information from start qubits into ancillary qubits.

        Args:
            circ (Circuit): Quantum circuit.
            e_from (Dict[int, List[int]]): Edge dict from starting vertex to ending vertices.
            e_ancillae (Dict[Tuple[int, int], int]): Ancillary qubit dict from edge to qubit index.

        Returns:
            Constructed quantum circuit.
        """
        for root, leaves in e_from.items():
            leaves = map(lambda leaf: e_ancillae[root, leaf], leaves)
            leaves = list(leaves)
            n_star = 1 + len(leaves)
            star_perm = [root]
            for leaf in leaves:
                star_perm.append(leaf)
            star = CnotStar.execute(n=n_star, root_to_leaf=True)
            for cnot_gate in star.fast_gates:
                c = cnot_gate.carg
                t = cnot_gate.targ
                c, t = star_perm[c], star_perm[t]
                CX | circ([c, t])
        return circ

    @classmethod
    def _to(cls, circ: Circuit, e_to: Dict[int, List[int]], e_ancillae: Dict[Tuple[int, int], int]):
        """Move information from ancillary qubits into ending qubits.

        Args:
            circ (Circuit): Quantum circuit.
            e_to (Dict[int, List[int]]): Edge dict from ancillary vectex to ending vertices.
            e_ancillae (Dict[Tuple[int, int], int]): Ancillary qubit dict from edge to qubit index.

        Returns:
            Constructed quantum circuit.
        """
        for root, leaves in e_to.items():
            leaves = map(lambda leaf: e_ancillae[leaf, root], leaves)
            leaves = list(leaves)
            n_star = 1 + len(leaves)
            star_perm = [root]
            for leaf in leaves:
                star_perm.append(leaf)
            star = CnotStar.execute(n=n_star, root_to_leaf=False)
            for cnot_gate in star.fast_gates:
                c = cnot_gate.carg
                t = cnot_gate.targ
                c, t = star_perm[c], star_perm[t]
                CX | circ([c, t])
        return circ

    @classmethod
    def _partition_exec(cls, circ: Circuit, edges: List[Tuple[int, int]], n_ancilla: int):
        """Execute the main algorithm on part of qubits, using other qubits as dirty ancillae.

        Args:
            circ (Circuit): Quantum circuit to be extended.
            edges (List[Tuple[int, int]]): Part of original edges, occupying up to one third of qubits.
            n_ancilla (int): The number of ancillary qubits.

        Returns:
            Constructed quantum circuit.
        """
        assert n_ancilla >= len(
            edges), "Number of ancillary qubits must be larger than number of edges in partition mode!"
        n_ancilla = min(n_ancilla, len(edges))
        left = set()
        right = set()
        part_perm = []
        part_perm_inv = {}
        for f, t in edges:
            left.add(f)
            right.add(t)
        for b in left:
            part_perm.append(b)
            part_perm_inv[b] = len(part_perm) - 1
        for b in right:
            part_perm.append(b)
            part_perm_inv[b] = len(part_perm) - 1
        n = len(left) + len(right) + n_ancilla
        ancilla = set(range(n)) - left - right
        for b in ancilla:
            part_perm.append(b)
            part_perm_inv[b] = len(part_perm) - 1
        _edges = []
        for f, t in edges:
            f, t = part_perm_inv[f], part_perm_inv[t]
            _edges.append((f, t))
        left, right = len(left), len(right)
        part = cls.execute(left=left, right=right, edges=_edges, n_ancilla=n_ancilla)
        for cnot_gate in part.fast_gates:
            c = cnot_gate.carg
            t = cnot_gate.targ
            c, t = part_perm[c], part_perm[t]
            CX | circ([c, t])
        return circ

    @classmethod
    def execute(
            cls, left: int, right: int, edges: List[Tuple[int, int]], n_ancilla: int = 0,
    ) -> Circuit:
        """Execute optimization.

        Args:
            left (int): The number of qubits on left side of bipartite.
            right (int): The number of qubits on right side of bipartite.
            edges (List[Tuple[int, int]]): All CNOT gates as edges starting from control qubits and ending
                at target qubits.
            n_ancilla (int): The number of ancillary qubits, default 0. If provided, ancillae number must
                be larger than number of edges.
        """
        n = left + right + n_ancilla
        if n_ancilla > 0:
            assert n_ancilla == len(
                edges), "If using ancilla, the number of ancillary qubits must be the same with bipartite edges."

        circ = Circuit(n)

        if len(edges) == 0:
            return circ

        if n <= 2:
            for c, t in edges:
                CX | circ([c, t])
            return circ

        e_from = {}
        e_to = {}
        e_ancillae = {}
        _a = n - n_ancilla
        for f, t in edges:
            assert f < left, "Edge must start from left part of bipartite!"
            assert left <= t < left + right, "Edge must end in right part of bipartite!"
            e_ancillae[f, t] = _a
            _a += 1
            if f not in e_from:
                e_from[f] = []
            e_from[f].append(t)
            if t not in e_to:
                e_to[t] = []
            e_to[t].append(f)

        # if no ancilla, we use part of original qubits.
        if n_ancilla == 0:
            seg = n // 3
            part_n_ancilla = n - 2 * seg

            for i in range((len(edges) + seg - 1) // seg):
                start = i * seg
                end = min((i + 1) * seg, len(edges))
                circ = cls._partition_exec(circ=circ, edges=edges[start:end], n_ancilla=part_n_ancilla)
            return circ

        e_ancillae = {}
        _a = n - n_ancilla
        for f, t in edges:
            e_ancillae[f, t] = _a
            _a += 1

        circ = cls._start(circ, e_from, e_ancillae)
        circ = cls._to(circ, e_to, e_ancillae)
        circ = cls._start(circ, e_from, e_ancillae)
        circ = cls._to(circ, e_to, e_ancillae)

        return circ
