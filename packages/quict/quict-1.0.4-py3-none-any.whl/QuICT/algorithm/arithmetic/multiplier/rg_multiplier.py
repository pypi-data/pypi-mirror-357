from typing import Optional
from numpy import pi

from QuICT.core.gate import CompositeGate, CU1, CCX
from QuICT.algorithm.qft import QFT, IQFT

from QuICT.tools.exception.core import GateParametersAssignedError


class RGMultiplier(CompositeGate):
    r"""
    A QFT based out-of-place quantum multiplier using schoolbook method. For `qreg_size` equals `n`,
    this gate requires in total `4n` qubits. For two binary encoded n-qubits integers `a` and `b`,
    calculates their product and store the result on `2n` clean qubits.

    $$
        \vert{a}\rangle_n \vert{b}\rangle_n \vert{0}\rangle_{2n}
        \to
        \vert{a}\rangle_n \vert{b}\rangle_n \vert{a*b}\rangle_{2n}
    $$

    Applying this multiplier on two 2-qubit sized register, $a:=\vert{q_0q_1}\rangle$ and
    $b:=\vert{q_2q_3}\rangle$ with output register $\vert{q_4...q_7}\rangle$ looks like:

                                       ┌──────────┐
        q_0: |0>───────────────────────┤0         ├────────────
                           ┌──────────┐│          │
        q_1: |0>───────────┤0         ├┤          ├────────────
                           │          ││          │
        q_2: |0>───────────┤1         ├┤1         ├────────────
                           │          ││          │
        q_3: |0>───────────┤2         ├┤2 cg_dder ├────────────
                ┌─────────┐│          ││          │┌──────────┐
        q_4: |0>┤0        ├┤3 cg_dder ├┤3         ├┤0         ├
                │         ││          ││          ││          │
        q_5: |0>┤1        ├┤4         ├┤4         ├┤1         ├
                │  cg_QFT ││          ││          ││  cg_IQFT │
        q_6: |0>┤2        ├┤5         ├┤5         ├┤2         ├
                │         ││          │└──────────┘│          │
        q_7: |0>┤3        ├┤6         ├────────────┤3         ├
                └─────────┘└──────────┘            └──────────┘

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import RGMultiplier

        circuit = Circuit(8)
        RGMultiplier(2) | circuit
        ```

    !!! Note "Implementation Details(Asymptotic)"

        | Parameter      | Info                             |
        | -------------- | -------------------------------- |
        | Input Size     | $n$                              |
        | num. ancilla   | $0$                              |
        | Gate set       | $CCX, CU_1, H$                   |
        | Width          | $4n$                             |
        | Depth          | $5n^3+{5\over2}n^2+{1\over2}n+6$ |
        | Size           | $5n^3+9n^2+2n$                   |
        | Two-qubit gate | $3n^3+7n^2-2n$                   |
        | CCX count      | $2n^3+2n^2$                      |

    References:
        [1]: "Quantum arithmetic with the Quantum Fourier Transform" by Lidia Ruiz-Perez and
        Juan Carlos Garcia-Escartin <https://arxiv.org/abs/1411.5949v2>.
    """

    def __init__(
        self,
        qreg_size: int,
        qreg_size_b: Optional[int] = None,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Register size for the first input register
            qreg_size_b (int | None): Register size for the second input register, will be the same as
                the first input register if not given.
            name (str): Name of the gate.
        Raises:
            GateParametersAssignedError: If `qreg_size` or `qreg_size_b` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(f"Input register size must be larger than but given {qreg_size}.")

        if qreg_size_b is None:
            qreg_size_b = qreg_size
        elif qreg_size_b < 2:
            raise GateParametersAssignedError(
                f"The second input register size must be larger than 1 but given {qreg_size_b}."
            )

        self._reg_a_list = list(range(qreg_size))
        self._reg_b_list = list(range(qreg_size, qreg_size + qreg_size_b))
        self._reg_prod_list = list(range(qreg_size + qreg_size_b, 2 * (qreg_size + qreg_size_b)))

        super().__init__(name)
        if name is None:
            self.name = "RGMultiplier"

        # construct circuit
        QFT(qreg_size + qreg_size_b) | self(self._reg_prod_list)
        # cumulatively add 'b << i' to result register controlled by a's i_th bit
        for i in range(qreg_size):
            self._build_ctrl_phi_shift_adder(
                reg_size_a=qreg_size_b,
                reg_size_b=qreg_size + qreg_size_b - i
            ) | self([qreg_size - 1 - i] + self._reg_b_list + self._reg_prod_list[:qreg_size + qreg_size_b - i])

        IQFT(qreg_size + qreg_size_b) | self(self._reg_prod_list)

    def _build_CCU1(self, theta) -> CompositeGate:
        """ Construct a doubly controlled U1 gate by given rotation angle theta. """
        CCU1 = CompositeGate("CCU1")

        CU1(theta / 2) | CCU1([0, 1])
        CCX | CCU1([0, 1, 2])
        CU1(-theta / 2) | CCU1([0, 2])
        CCX | CCU1([0, 1, 2])
        CU1(theta / 2) | CCU1([0, 2])

        return CCU1

    def _build_ctrl_phi_shift_adder(self, reg_size_a, reg_size_b) -> CompositeGate:
        """
        A controlled adder that add (a << shift) to b in fourier space assuming both registers
        already in qft basis.

        |c>|a>|b> ---> |c>|a>|b + c * (a << shift)>

        Circuit width: `1 + reg_size_a + reg_size_b`
        """
        c_adder = CompositeGate("cAdder")

        ctrl = 0
        reg_a = list(range(1, 1 + reg_size_a))
        reg_b = list(range(1 + reg_size_a, 1 + reg_size_a + reg_size_b))

        for k in range(reg_size_a):
            for j in range(reg_size_b - k):
                theta = pi / (1 << (reg_size_b - k - 1 - j))
                self._build_CCU1(theta) | c_adder([ctrl, reg_a[-1 - k], reg_b[j]])

        return c_adder
