from typing import Optional, Iterable

from QuICT.core import Circuit
from QuICT.core.gate import CX
from math import ceil, log2


class CnotLinear:
    """Optimize a linear CNOT circuit, in which all CNOT gates use last gate's target
        qubit as its control qubit.

    Examples:
        >>> from QuICT.qcda.optimization.cnot_dag import CnotLinear
        >>> cl = CnotLinear()
        >>> # Input circuit has these CNOT gates: (4, 3), (3, 2), (2, 1), (1, 0).
        >>> circ = cl.execute(5, [4, 3, 2, 1, 0])
    """

    @classmethod
    def execute(cls, n: int, perm: Optional[Iterable[int]] = None) -> Circuit:
        if perm is None:
            perm = [i for i in range(n)]
        if not isinstance(perm, tuple):
            perm = tuple(perm)
        assert n == len(perm), "Qubit number must be the same with qubit index permutation length."
        assert n > 1, "Must include at least one leaf!"
        # check if it's a permutation
        test = all(map(lambda tp: tp[0] == tp[1], enumerate(sorted(perm))))
        assert test, "Input chain must be a permutation!"
        circ = Circuit(n)
        lg = ceil(log2(n))
        m = 2 ** lg
        for j in range(1, lg + 1):
            for k in range(m // (2 ** j) + 1):
                x = k * (2 ** j) + 2 ** (j - 1) - 1
                y = k * (2 ** j) + 2 ** j - 1
                if x < n and y < n:
                    x = perm[x]
                    y = perm[y]
                    CX | circ([x, y])
        for j in range(lg - 1, 0, -1):
            for k in range(1, m // (2 ** j) + 1):
                x = k * (2 ** j) - 1
                y = k * (2 ** j) + 2 ** (j - 1) - 1
                if x < n and y < n:
                    x = perm[x]
                    y = perm[y]
                    CX | circ([x, y])
        return circ
