import numpy as np

from QuICT.core.gate import H, CU1, Swap, CompositeGate
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class QFT(CompositeGate):
    r""" Implement the Quantum Fourier Transform without the swap gates.

    $$
    \vert{j}\rangle \mapsto \frac{1}{2^{n/2}} \bigotimes_{l=n}^{1}[\vert{0}\rangle + e^{2\pi ij2^{-l}}\vert{1}\rangle]
    $$

    Reference:
        Nielsen, M.A., & Chuang, I.L. (2010). Quantum Computation and Quantum Information (10th Anniversary edition).

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.qft import QFT

        circuit = Circuit(3)
        QFT(3) | circuit
        circuit.draw(method="command", flatten=True)
        ```

                    ┌───┐┌─────┐┌─────┐
            q_0: |0>┤ h ├┤ cu1 ├┤ cu1 ├─────────────────
                    └───┘└──┬──┘└──┬──┘┌───┐┌─────┐
            q_1: |0>────────■──────┼───┤ h ├┤ cu1 ├─────
                                   │   └───┘└──┬──┘┌───┐
            q_2: |0>───────────────■───────────■───┤ h ├
                                                   └───┘
    """
    def __init__(self, targets: int, with_swap: bool = False, name: str = "QFT"):
        """
        Args:
            targets (int): The qubits' number.
            with_swap (bool): If `True`, will include the swap gates in QFT.
            name (str, optional): Name of the QFT gate.
        Raises:
            GateParametersAssignedError: If `targets` is smaller than 2.
        """
        if targets < 2:
            raise GateParametersAssignedError("QFT Gate needs at least two target qubits.")

        self.with_swap = with_swap

        super().__init__(name)

        self._qft_build(targets)

        if with_swap:
            for i in range(targets // 2):
                Swap | self([i, targets - 1 - i])

    def _qft_build(self, targets):
        for i in range(targets):
            H | self(i)
            for j in range(i + 1, targets):
                CU1(2 * np.pi / (1 << j - i + 1)) | self([j, i])

    def inverse(self):
        inverse_gate = IQFT(self.width(), self.with_swap)
        inverse_gate & self.qubits

        return inverse_gate


class IQFT(CompositeGate):
    r""" Implement inverse of the Quantum Fourier Transform without the swap gates.

    $$
    \frac{1}{2^{n/2}} \bigotimes_{l=n}^{1}[\vert{0}\rangle + e^{2\pi ij2^{-l}}\vert{1}\rangle] \mapsto \vert{j}\rangle
    $$

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.qft import IQFT

        circuit = Circuit(3)
        IQFT(3) | circuit
        circuit.draw(method="command", flatten=True)
        ```

                                     ┌─────┐┌─────┐┌───┐
            q_0: |0>─────────────────┤ cu1 ├┤ cu1 ├┤ h ├
                         ┌─────┐┌───┐└──┬──┘└──┬──┘└───┘
            q_1: |0>─────┤ cu1 ├┤ h ├───┼──────■────────
                    ┌───┐└──┬──┘└───┘   │
            q_2: |0>┤ h ├───■───────────■───────────────
                    └───┘
    """
    def __init__(self, targets: int, with_swap: bool = False, name: str = "IQFT"):
        """
        Args:
            targets (int): The qubits' number.
            with_swap (bool): If `True`, will include the swap gates in IQFT.
            name (str, optional): Name of the IQFT gate.
        Raises:
            GateParametersAssignedError: If `targets` is smaller than 2.
        """
        if targets < 2:
            raise GateParametersAssignedError("IQFT Gate needs at least two target qubits.")

        self.with_swap = with_swap

        super().__init__(name)

        if with_swap:
            for i in range(targets // 2):
                Swap | self([i, targets - 1 - i])

        self._iqft_build(targets)

    def _iqft_build(self, targets):
        for i in range(targets - 1, -1, -1):
            for j in range(targets - 1, i, -1):
                CU1(-2 * np.pi / (1 << j - i + 1)) | self([j, i])

            H | self(i)

    def inverse(self):
        inverse_gate = QFT(self.width(), self.with_swap)
        inverse_gate & self.qubits

        return inverse_gate
