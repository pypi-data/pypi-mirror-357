from typing import Optional
from QuICT.core.gate import CompositeGate, CCX
from QuICT.algorithm.arithmetic.adder import MuThCtrlAdder

from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class MuThMultiplier(CompositeGate):
    r"""
    An out-of-place reversible quantum multiplier using schoolbook method. For `qreg_size` equals `n`,
    this gate requires in total `4n+1` qubits. For two binary encoded n-qubits integers `a` and `b`,
    calculates their product and store the result on `2n` clean qubits.

    $$
        \vert{a}\rangle_n \vert{b}\rangle_n \vert{0}\rangle_{2n} \vert{0}\rangle
        \to
        \vert{a}\rangle_n \vert{b}\rangle_n \vert{a*b}\rangle_{2n} \vert{0}\rangle
    $$

    Applying this multiplier on two 3-qubit sized register, $a:=\vert{q_0q_1q_2}\rangle$ and
    $b:=\vert{q_3q_4q_5}\rangle$ with output register $\vert{q_6...q_{11}}\rangle$ and ancilla qubit
    $\vert{q_{12}}\rangle$ looks like:

                                                  ┌──────────┐
         q_0: |0>─────────────────────────────────┤0         ├
                                      ┌──────────┐│          │
         q_1: |0>─────────────────────┤0         ├┤          ├
                                      │          ││          │
         q_2: |0>───■──────■──────■───┤          ├┤          ├
                    │      │      │   │          ││          │
         q_3: |0>───┼──────┼──────■───┤1         ├┤1         ├
                    │      │      │   │          ││          │
         q_4: |0>───┼──────■──────┼───┤2         ├┤2         ├
                    │      │      │   │          ││          │
         q_5: |0>───■──────┼──────┼───┤3         ├┤3         ├
                    │      │      │   │          ││          │
         q_6: |0>───┼──────┼──────┼───┤          ├┤4 cg_cAdd ├
                    │      │      │   │  cg_cAdd ││          │
         q_7: |0>───┼──────┼──────┼───┤4         ├┤5         ├
                    │      │      │   │          ││          │
         q_8: |0>───┼──────┼──────┼───┤5         ├┤6         ├
                    │      │   ┌──┴──┐│          ││          │
         q_9: |0>───┼──────┼───┤ ccx ├┤6         ├┤7         ├
                    │   ┌──┴──┐└─────┘│          ││          │
        q_10: |0>───┼───┤ ccx ├───────┤7         ├┤          ├
                 ┌──┴──┐└─────┘       │          ││          │
        q_11: |0>┤ ccx ├──────────────┤          ├┤          ├
                 └─────┘              │          ││          │
        q_12: |0>─────────────────────┤8         ├┤8         ├
                                      └──────────┘└──────────┘

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import MuThMultiplier

        circuit = Circuit(13)
        MuThMultiplier(3) | circuit
        ```

    !!! Note "Implementation Details(Asymptotic)"

        | Parameter    | Info         |
        | ------------ | ------------ |
        | Input Size   | $n$          |
        | num. ancilla | $1$          |
        | Gate set     | $CCX, CX$    |
        | Width        | $4n+1$       |
        | Depth        | $5n^2-5n+1$  |
        | Size         | $7n^2-10n+4$ |
        | CX count     | $4n^2-10n+6$ |
        | CCX count    | $3n^2-2$     |

    References:
        [1]: "Quantum Circuit Design of a T-count Optimized Integer Multiplier" by
        Edgard Muñoz-Coreas and Himanshu Thapliyal <https://ieeexplore.ieee.org/document/8543237>.
    """

    def __init__(
        self,
        qreg_size: int,
        qreg_size_b: Optional[int] = None,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Register size for the first input register.
            qreg_size_b (int | None): Register size for the second input register, will be the same as
                the first input register if not given.
            name (str): Name of the multiplier gate.
        Raises:
            GateParametersAssignedError: If the `qreg_size` or `qreg_size_b` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(f"Input register size must be larger than 1 but given {qreg_size}.")

        if qreg_size_b is None:
            qreg_size_b = qreg_size
        elif qreg_size_b < 2:
            raise GateParametersAssignedError(
                f"The second input register size must be larger than 1 but given {qreg_size_b}."
            )

        self._reg_a_list = list(range(qreg_size))
        self._reg_b_list = list(range(qreg_size, qreg_size + qreg_size_b))
        self._reg_prod_list = list(range(qreg_size + qreg_size_b, 2 * (qreg_size + qreg_size_b)))
        self._ancilla = [2 * (qreg_size + qreg_size_b)]

        super().__init__(name)
        if name is None:
            self.name = "MuThMultiplier"

        # step 1
        for i in range(qreg_size_b):
            CCX | self([
                self._reg_a_list[-1],
                self._reg_b_list[-1 - i],
                self._reg_prod_list[-1 - i]
            ])

        # step 2 & 3
        ctrl_adder_gate = MuThCtrlAdder(qreg_size_b)
        for i in range(qreg_size - 1):
            ctrl_bit = [self._reg_a_list[-2 - i]]
            target_reg = self._reg_prod_list[qreg_size - 2 - i: qreg_size + qreg_size_b - 1 - i]
            ctrl_adder_gate | self(
                ctrl_bit + self._reg_b_list + target_reg + self._ancilla
            )
