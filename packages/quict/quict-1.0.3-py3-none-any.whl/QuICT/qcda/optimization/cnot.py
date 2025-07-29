from typing import List, Tuple, Optional, Iterable
from QuICT.core import Circuit

from QuICT.qcda.optimization.cnot_without_ancilla import CnotWithoutAncilla
from QuICT.qcda.optimization.cnot_dag import CnotLinear, CnotStar, CnotBipartite


class CnotOptimization:
    STRATEGIES = (
        "no_ancilla",
        "linear",
        "star",
        "bipartite",
    )

    @classmethod
    def exec_no_ancilla(cls, circuit_segment: Circuit) -> Circuit:
        return CnotWithoutAncilla.execute(circuit_segment)

    @classmethod
    def exec_linear(cls, n: int, perm: Optional[Iterable[int]] = None) -> Circuit:
        return CnotLinear.execute(n, perm)

    @classmethod
    def exec_star(
        cls, n: int, perm: Optional[Iterable[int]] = None, root_to_leaf: bool = True
    ) -> Circuit:
        return CnotStar.execute(n, perm, root_to_leaf)

    @classmethod
    def exec_bipartite(
        cls, left: int, right: int, edges: List[Tuple[int, int]], n_ancilla: int = 0
    ) -> Circuit:
        return CnotBipartite.execute(left, right, edges, n_ancilla)

    @classmethod
    def execute(cls, *args, strategy: str = "no_ancilla", **kwargs) -> Circuit:
        assert (
            strategy in cls.STRATEGIES
        ), f"Must provide strategy from {cls.STRATEGIES}!"
        fn = eval(f"cls.exec_{strategy}")
        return fn(*args, **kwargs)
