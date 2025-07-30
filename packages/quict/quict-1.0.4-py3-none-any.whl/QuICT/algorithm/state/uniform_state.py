from typing import List
from QuICT.core.gate import CompositeGate, X, H, CH, Ry, CRy, ID, SX, SX_dagger, CCRz, CU1, CX
from numpy import binary_repr, arccos, sqrt, pi


class UniformState(CompositeGate):
    """

    Reference:
        [1]: Shukla, Alok, and Prakash Vedula. “An Efficient Quantum Algorithm for Preparation of Uniform
            Quantum Superposition States.” Quantum Information Processing 23, no. 2 (January 29, 2024): 38.
            https://doi.org/10.1007/s11128-024-04258-4.

    """

    def __init__(
        self,
        N: int,
        control: bool = False,
        name: str = None
    ):
        if name is None:
            name = f"Uniform-{N}"
            if control:
                name = "c" + name
        super().__init__(name)

        if control:
            gate_l_end = self._build_control_unif(N)
            application_indices = gate_l_end.qubits[:1] + gate_l_end.qubits[:0:-1]
        else:
            gate_l_end = self._build_unif(N)
            application_indices = gate_l_end.qubits[::-1]

        for gate in (gate_l_end & application_indices):
            gate | self

    def _build_unif(self, N: int) -> CompositeGate:
        cg = CompositeGate()

        if N == 1:
            ID | cg(0)
            return cg

        N_bin_rev = binary_repr(N)[::-1]

        l_list = []
        for idx, bit in enumerate(N_bin_rev):
            if bit == "1":
                l_list.append(idx)

        # Algorithm 1: line 4
        for l in l_list[1:]:
            X | cg(l)

        # line 6
        for i in range(l_list[0]):
            H | cg(i)

        if N == (1 << (len(N_bin_rev) - 1)):
            return cg

        # line 8
        M = 1 << l_list[0]
        Ry(-2 * arccos(sqrt(M / N))) | cg(l_list[1])

        # line 9
        X | cg(l_list[1])
        for i in range(l_list[0], l_list[1]):
            CH | cg([l_list[1], i])
        X | cg(l_list[1])

        # line 10
        for m in range(1, len(l_list) - 1):
            X | cg(l_list[m])
            CRy(-2 * arccos(sqrt((1 << l_list[m]) / (N - M)))) | cg(l_list[m:m + 2])
            X | cg(l_list[m])

            X | cg(l_list[m + 1])
            for i in range(l_list[m], l_list[m + 1]):
                CH | cg([l_list[m + 1], i])
            X | cg(l_list[m + 1])

            M += 1 << l_list[m]

        return cg

    def _build_control_unif(self, N: int) -> CompositeGate:
        cg = CompositeGate()

        if N == 1:
            ID | cg(0)
            ID | cg(1)
            return cg

        N_bin_rev = binary_repr(N)[::-1]

        l_list = []
        for idx, bit in enumerate(N_bin_rev):
            if bit == "1":
                l_list.append(idx)

        # Algorithm 1: line 4
        for l in l_list[1:]:
            CX | cg([0, l + 1])

        # line 6
        for i in range(l_list[0]):
            CH | cg([0, i + 1])

        if N == (1 << (len(N_bin_rev) - 1)):
            return cg

        # line 8
        M = 1 << l_list[0]
        CRy(-2 * arccos(sqrt(M / N))) | cg([0, l_list[1] + 1])

        # line 9
        X | cg(l_list[1] + 1)
        for i in range(l_list[0], l_list[1]):
            self._CCH() | cg([0, l_list[1] + 1, i + 1])
        X | cg(l_list[1] + 1)

        # line 10
        for m in range(1, len(l_list) - 1):
            X | cg(l_list[m] + 1)
            self._CCRy(-2 * arccos(sqrt((1 << l_list[m]) / (N - M)))) | cg([0, l_list[m] + 1, l_list[m + 1] + 1])
            X | cg(l_list[m] + 1)

            X | cg(l_list[m + 1] + 1)
            for i in range(l_list[m], l_list[m + 1]):
                self._CCH() | cg([0, l_list[m + 1] + 1, i + 1])
            X | cg(l_list[m + 1] + 1)

            M += 1 << l_list[m]

        return cg

    def _CCRy(self, theta) -> CompositeGate:
        ccry = CompositeGate("CCRy")

        SX | ccry(2)
        CCRz(theta) | ccry([0, 1, 2])
        SX_dagger | ccry(2)

        return ccry

    def _CCU1(self, theta) -> CompositeGate:
        """ Construct a doubly controlled U1 gate by given rotation angle theta. """
        ccu1 = CompositeGate("CCU1")

        CU1(theta / 2) | ccu1([1, 2])
        CX | ccu1([0, 1])
        CU1(-theta / 2) | ccu1([1, 2])
        CX | ccu1([0, 1])
        CU1(theta / 2) | ccu1([0, 2])

        return ccu1

    def _CCH(self) -> CompositeGate:
        cch = CompositeGate("CCH")

        Ry(-pi / 4) | cch(2)
        self._CCU1(pi) | cch([0, 1, 2])
        Ry(pi / 4) | cch(2)

        return cch
