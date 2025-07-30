from typing import Optional
from numpy import pi

from QuICT.core.gate import CompositeGate, CU1
from QuICT.algorithm.qft import QFT, IQFT

from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class DraperAdder(CompositeGate):
    r"""
    A qft based in-place adder that in total requires `2n` qubits. For two n-qubit binary
    encoded addends `a` and `b`, calculates the result and store it on the second register:

    $$
        \vert{a}\rangle_n\vert{b}\rangle_n \to \vert{a}\rangle_n\vert{a + b \mod{2^n}}\rangle_n
    $$

    Applying this adder on two 3-qubit sized registers, $a:=\vert{q_0q_1q_2}\rangle$ and
    $b:=\vert{q_3q_4q_5}\rangle$, looks like:

        q_0: |0>─────────────────────────────────────────────────■───────────────
                                                                 │
        q_1: |0>───────────────────────────────────■──────■──────┼───────────────
                                                   │      │      │
        q_2: |0>──────────────■──────■──────■──────┼──────┼──────┼───────────────
                ┌─────────┐┌──┴──┐   │      │   ┌──┴──┐   │   ┌──┴──┐┌──────────┐
        q_3: |0>┤0        ├┤ cu1 ├───┼──────┼───┤ cu1 ├───┼───┤ cu1 ├┤0         ├
                │         │└─────┘┌──┴──┐   │   └─────┘┌──┴──┐└─────┘│          │
        q_4: |0>┤1 cg_QFT ├───────┤ cu1 ├───┼──────────┤ cu1 ├───────┤1 cg_IQFT ├
                │         │       └─────┘┌──┴──┐       └─────┘       │          │
        q_5: |0>┤2        ├──────────────┤ cu1 ├─────────────────────┤2         ├
                └─────────┘              └─────┘                     └──────────┘

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import DraperAdder

        circuit = Circuit(6)
        DraperAdder(3) | circuit
        ```

    !!! Note "Implementation Details(Asymptotic)"

        | Parameter      | Info                      |
        | -------------- | ------------------------- |
        | Input Size     | $n$                       |
        | num. ancilla   | 0                         |
        | Gate set       | $CU_1, H$                 |
        | Width          | $2n$                      |
        | Depth          | $4n-1$                    |
        | Size           | $\frac{3}{2}n(n+1)$       |
        | Two-qubit gate | ${3\over2}n^2-{1\over2}n$ |

    References:
        [1]: "Addition on a Quantum Computer" by Thomas G. Draper <https://arxiv.org/abs/quant-ph/0008033v1>.

        [2]: "Quantum arithmetic with the Quantum Fourier Transform" by Lidia Ruiz-Perez and Juan Carlos
        Garcia-Escartin <https://arxiv.org/abs/1411.5949v2>.
    """

    def __init__(
        self,
        qreg_size: int,
        qreg_size_b: Optional[int] = None,
        in_fourier: bool = False,
        out_fourier: bool = False,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Input register size for both addends. Needs to be larger than 1.
            in_fourier (bool): If True, will assume the input register is already in fourier basis.
            out_fourier (bool): If True, after the addition, the register will be left in fourier basis.
            name (str): Name of the adder gate.
        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 1:
            raise GateParametersAssignedError(f"Register size must be greater than or equal to 2 but given {qreg_size}")

        if qreg_size_b is None:
            qreg_size_b = qreg_size
        elif qreg_size_b < 2:
            raise GateParametersAssignedError("Input register size must be larger than 1.")

        self._reg_size = qreg_size

        self._reg_a_list = list(range(qreg_size))
        self._reg_b_list = list(range(qreg_size, qreg_size + qreg_size_b))

        super().__init__(name)
        if name is None:
            self.name = "DraperAdder"

        if not in_fourier:
            QFT(qreg_size_b) | self(self._reg_b_list)
        # addition
        for k in range(qreg_size):
                control = self._reg_a_list[qreg_size - 1 - k]
                for j in range(qreg_size_b - k):
                    target = self._reg_b_list[j]
                    theta = pi / (1 << (qreg_size_b - k - 1 - j))
                    CU1(theta) | self([control, target])
        if not out_fourier:
            IQFT(qreg_size_b) | self(self._reg_b_list)
