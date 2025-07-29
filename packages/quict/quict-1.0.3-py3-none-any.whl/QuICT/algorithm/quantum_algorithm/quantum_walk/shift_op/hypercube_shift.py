from typing import List
from QuICT.core.gate import CompositeGate, X, H
from QuICT.core.gate.backend import MCRWithoutAux
from numpy import ceil, log2, pi, binary_repr


class HyperCubeShiftOp(CompositeGate):
    r""" A shift operator on a degree-n hypercube. Assuming both node and coin are binary encoded as unsigned integers.
    For coin in state |i>, the gate will apply X gate on the ith qubit of the node register:

    $$U\vert{i}\rangle_{\log{n}}\vert{\psi}\rangle_n = \vert{i}\rangle_{\log{n}} X_i\vert{\psi}\rangle_n$$

    $\vert{i}\rangle_{\log{n}}$ is a bit string with length $\log{n}$ and $\vert{\psi}\rangle_n$ is a general state
    on n qubits.

    Reference:
        [1]: Wing-Bocanegra, Allan, and Salvador E. Venegas-Andraca. “Circuit Implementation of Discrete-Time Quantum
        Walks via the Shunt Decomposition Method.” Quantum Information Processing 22, no. 3 (March 13, 2023):
        146. https://doi.org/10.1007/s11128-023-03878-6.

    """

    def __init__(
        self,
        node_deg: int,
        name: str = None
    ):
        if node_deg < 2:
            raise ValueError(f"Node' degree must be larger than 1, but given {node_deg}.")
        require_q = int(ceil(log2(node_deg)))
        self._coin_reg = list(range(require_q))
        self._node_reg = list(range(require_q, require_q + node_deg))

        super().__init__(name)

        mct = CompositeGate("MCT")
        H | mct(require_q)
        MCRWithoutAux(num_ctrl=require_q, theta=pi, targ_rot_mode="u1") | mct(list(range(require_q + 1)))
        H | mct(require_q)

        for i in range(node_deg):
            # ctrl bits binary encoding
            for j in range(require_q):
                if i % (1 << j) == 0:
                    X | self(self._coin_reg[-1 - j])
            mct | self(self._coin_reg + [self._node_reg[-1 - i]])

        for idx, bit in enumerate(binary_repr(node_deg - 1, width=require_q)):
            if bit == "0":
                X | self(self._coin_reg[idx])
