from copy import copy
from typing import Optional, Iterable

from QuICT.core import Circuit
from QuICT.core.gate import CX


class CnotStar:
    """Optimize a star-like CNOT circuit. Every CNOT gate in such circuits
        has the same control qubit and different target qubits(or in reverse).

    Examples:
        >>> from QuICT.qcda.optimization.cnot_dag import CnotStar
        >>> cs = CnotStar()
        >>> # this circuit has CNOT gates: (3, 2), (3, 1), (3, 0)
        >>> circuit = cs.execute(4, [3, 2, 1, 0])
    """

    @classmethod
    def _check_perm(cls, perm: Iterable[int]) -> bool:
        test = all(map(lambda tp: tp[0] == tp[1], enumerate(sorted(perm))))
        return test

    @classmethod
    def execute(cls, n: int, perm: Optional[Iterable[int]] = None, root_to_leaf: bool = True) -> Circuit:
        if perm is None:
            perm = [i for i in range(n)]
        if not isinstance(perm, tuple):
            perm = tuple(perm)
        assert cls._check_perm(perm), "Root and leaves must form a permutation!"

        assert n == len(perm), "Qubit number must be the same with qubit permutation length."
        assert n > 1, "Must include at least one leaf!"

        circ = Circuit(n)

        if n == 2:
            x, y = perm
            if not root_to_leaf:
                x, y = y, x
            CX | circ([x, y])
            return circ

        k = (n + 1) // 2
        for i in range(k):
            x = i
            y = i + k
            if not root_to_leaf:
                x, y = y, x
            if x < n and y < n:
                x, y = perm[x], perm[y]
                CX | circ([x, y])
        star = cls.execute(k, range(k), root_to_leaf)
        for cnot_gate in star.fast_gates:
            c = cnot_gate.carg
            t = cnot_gate.targ
            CX | circ([perm[c], perm[t]])
        for i in range(1, k):
            x = i
            y = i + k
            if not root_to_leaf:
                x, y = y, x
            if x < n and y < n:
                x, y = perm[x], perm[y]
                CX | circ([x, y])
        return circ
