from typing import List
from QuICT.core.gate import CompositeGate, X, CX, CRy
from numpy import arccos, sqrt


class WState(CompositeGate):
    """

    Reference:
        [1]: Cruz, Diogo, Romain Fournier, Fabien Gremion, Alix Jeannerot, Kenichi Komagata, Tara Tosic,
            Jarla Thiesbrummel, et al. “Efficient Quantum Algorithms for $GHZ$ and $W$ States, and
            Implementation on the IBM Quantum Computer.” Advanced Quantum Technologies 2, no. 5-6
            (June 2019): 1900015. https://doi.org/10.1002/qute.201900015.

    """
    def __init__(
        self,
        N: int,
        method: str = "linear",
        name: str = "W"
    ):
        if N < 1:
            raise ValueError(f"N can not be smaller than 1, but given {N}.")

        if method not in ["linear", "tree"]:
            raise ValueError(f"method must be chosen from [linear, tree] but given {method}.")

        super().__init__(name)

        X | self(0)

        B = self._b_gate

        if method == "linear":
            for i in range(N - 1):
                B(pN=N - i) | self([i, i + 1])
            return

    def _b_gate(self, pN: int, pM: int = 1) -> CompositeGate:

        cg = CompositeGate("B")

        theta = 2 * arccos(sqrt(pM / pN))
        CRy(theta) | cg([0, 1])
        CX | cg([1, 0])

        return cg
