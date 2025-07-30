from QuICT.core.gate import CompositeGate, CX, CCX

from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class MuThCtrlAdder(CompositeGate):
    r"""
    A controlled ripple-carry in-place half adder that in total requires `2n + 3` qubits.
    For two n-qubit binary encoded integers `a` and `b`, calculate their sum and store
    the result on the second register only when the control bit is `1`:

    $$
        \vert{\text{ctrl}}\rangle \vert{a}\rangle_n \vert{0}\rangle \vert{b}\rangle_n
        \vert{0}\rangle
        \to
        \vert{\text{ctrl}}\rangle \vert{a}\rangle_n  \vert{\text{ctrl} * a + b}\rangle_{n+1}
        \vert{0}\rangle
    $$

    Applying this gate on two 2-qubit sized register, $a:=\vert{q_1q_2}\rangle$ and $b:=\vert{q_4q_5}\rangle$
    with the control bit on $\vert{q_0}\rangle$, output carry on $\vert{q_3}\rangle$ and one ancilla qubit
    on $\vert{q_6}\rangle$ looks like:

        q_0: |0>─────────■────────────────────■─────────────■─────────────■─────────
                         │   ┌─────┐          │             │   ┌─────┐   │
        q_1: |0>──■──────■───┤ ccx ├───■──────┼──────■──────■───┤ ccx ├───┼─────■───
                  │      │   └──┬──┘   │      │      │      │   └──┬──┘   │     │
        q_2: |0>──┼──────┼──────■──────┼──────┼──────┼──────┼──────■──────■─────┼───
                  │   ┌──┴──┐   │      │   ┌──┴──┐   │      │      │      │     │
        q_3: |0>──┼───┤ ccx ├───┼──────┼───┤ ccx ├───┼──────┼──────┼──────┼─────┼───
                ┌─┴──┐└─────┘   │      │   └──┬──┘   │   ┌──┴──┐   │      │   ┌─┴──┐
        q_4: |0>┤ cx ├──────────┼──────■──────┼──────■───┤ ccx ├───┼──────┼───┤ cx ├
                └────┘          │      │      │      │   └─────┘   │   ┌──┴──┐└────┘
        q_5: |0>────────────────■──────┼──────┼──────┼─────────────■───┤ ccx ├──────
                                    ┌──┴──┐   │   ┌──┴──┐              └─────┘
        q_6: |0>────────────────────┤ ccx ├───■───┤ ccx ├───────────────────────────
                                    └─────┘       └─────┘

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import MuThCtrlAdder

        circuit = Circuit(7)
        MuThCtrlAdder(2) | circuit
        ```

    !!! Note "Implementation Details(Asymptotic)"

        | Parameter    | Info      |
        | ------------ | --------- |
        | Input Size   | $n$       |
        | num. ctrl    | $1$       |
        | Input carry  | $0$       |
        | Output carry | $1$       |
        | num. ancilla | $1$       |
        | Gate set     | $CCX, CX$ |
        | Width        | $2n+3$    |
        | Depth        | $5n-1$    |
        | Size         | $7n-4$    |
        | CX count     | $4n-6$    |
        | CCX count    | $3n+2$    |

    References:
        [1]: "Quantum Circuit Design of a T-count Optimized Integer Multiplier" by Edgard Muñoz-Coreas and
        Himanshu Thapliyal <https://ieeexplore.ieee.org/document/8543237>.
    """

    def __init__(
        self,
        qreg_size: int,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Input register size for both addends. Needs to be greater than or euqal to 2.
            name (str): Name of the adder gate.
        Raises:
            GateParametersAssignedError: If the `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 2 but given {qreg_size}."
            )

        self._reg_size = qreg_size

        self._ctrl_bit = 0
        self._reg_a_list = list(range(1, 1 + qreg_size))
        self._reg_carry = 1 + qreg_size
        self._reg_b_list = list(range(qreg_size + 2, 2 * qreg_size + 2))
        self._anci_bit = 2 * qreg_size + 2

        super().__init__(name)
        if name is None:
            self.name = "CtrlAdder"

        # step 1
        for i in range(qreg_size - 1):
            CX | self([self._reg_a_list[i], self._reg_b_list[i]])

        # step 2
        CCX | self([self._ctrl_bit, self._reg_a_list[0], self._reg_carry])
        for i in range(qreg_size - 2):
            CX | self([self._reg_a_list[i + 1], self._reg_a_list[i]])

        # step 3
        for i in range(qreg_size - 1):
            CCX | self([
                self._reg_b_list[-1 - i],
                self._reg_a_list[-1 - i],
                self._reg_a_list[-2 - i]
            ])

        # step 4
        CCX | self([self._reg_b_list[0], self._reg_a_list[0], self._anci_bit])
        CCX | self([self._ctrl_bit, self._anci_bit, self._reg_carry])
        CCX | self([self._reg_b_list[0], self._reg_a_list[0], self._anci_bit])

        # step 5
        for i in range(qreg_size - 1):
            CCX | self([self._ctrl_bit, self._reg_a_list[i], self._reg_b_list[i]])
            CCX | self([
                self._reg_b_list[i + 1],
                self._reg_a_list[i + 1],
                self._reg_a_list[i]
            ])
        CCX | self([self._ctrl_bit, self._reg_a_list[-1], self._reg_b_list[-1]])

        # step 6
        for i in range(qreg_size - 2):
            CX | self([self._reg_a_list[-2 - i], self._reg_a_list[-3 - i]])

        # step 7
        for i in range(qreg_size - 1):
            CX | self([self._reg_a_list[i], self._reg_b_list[i]])
