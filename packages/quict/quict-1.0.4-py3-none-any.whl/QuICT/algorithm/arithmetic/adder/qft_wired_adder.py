from typing import Literal, List
from numpy import pi

from QuICT.core.gate import CompositeGate, SX, SX_dagger, U1, CU1, CCRz, CX
from QuICT.algorithm.qft import QFT
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class QFTWiredAdder(CompositeGate):
    r"""
    A wired in-place adder in fourier basis. One of the addend is given classically and will be
    written into the adder when constructing the gate. For an n-qubit binary encoded addends `a`
    and a classically given integer `X`, this adder calculates the result and store it in place:

    $$
        \vert{a}\rangle_n \to \vert{X+a \mod 2^n}\rangle_n
    $$

    Applying this adder with `X = 5` on a 4-qubit sized register looks like:

                ┌──────────┐┌──────────┐┌──────────┐
        q_0: |0>┤0         ├┤ u1(5π/8) ├┤0         ├
                │          │├──────────┤│          │
        q_1: |0>┤1         ├┤ u1(5π/4) ├┤1         ├
                │  cg_yQFT │├──────────┤│  cg_IQFT │
        q_2: |0>┤2         ├┤ u1(5π/2) ├┤2         ├
                │          │└┬────────┬┘│          │
        q_3: |0>┤3         ├─┤ u1(5π) ├─┤3         ├
                └──────────┘ └────────┘ └──────────┘

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import RCFourierAdderWired

        X = 5
        circuit = Circuit(4)
        RCFourierAdderWired(4, addend=X) | circuit
        ```

    References:
        [1]: "High Performance Quantum Modular Multipliers" by Rich Rines, Isaac Chuang
        <https://arxiv.org/abs/1801.01081>
    """

    def __init__(
        self,
        qreg_size: int,
        addend: int,
        num_control: int = 0,
        in_fourier: bool = False,
        out_fourier: bool = False,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Size of the quantum register waiting to be added. Needs to be greater than or
                equal to 2.
            addend (int): The integer that will be added to the qreg.
            num_control (int): Indicates the number of qubits for controlling the wired adder, up to 2 qubits.
                If not 0, the control bits will be on the highest bits.
            in_fourier (bool): If True, assuming the input register is already in qft basis.
            out_fourier (bool): If True, after the addition, the qreg will be left in qft basis.
            name (str): Name of the wired adder gate.
        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The wired Fourier adder needs at least two qubits but given {qreg_size}."
            )
        if num_control < 0 or num_control > 2:
            raise ValueError("Number of control qubits not supported. Should be in the range: [0, 2].")

        self._addend = addend
        self._num_control = num_control

        super().__init__(name)
        if name is None:
            self.name = f"rc_add({addend})"

        self._ctrl_reg = list(range(num_control))
        self._data_reg = list(range(num_control, num_control + qreg_size))

        if num_control == 2:
            core_adder = self._build_c2_phi_adder(qreg_size, addend)
        elif num_control == 1:
            core_adder = self._build_ctl_phi_adder(qreg_size, addend)
        else:
            core_adder = self._build_phi_adder(qreg_size, addend)

        if not in_fourier:
            QFT(qreg_size) | self(self._data_reg)
        core_adder | self(self._ctrl_reg + self._data_reg)
        if not out_fourier:
            QFT(qreg_size).inverse() | self(self._data_reg)

    @property
    def control_q(self) -> List[int]:
        """ A list of int indicating the indices of the control qubits. """
        return self._ctrl_reg

    @property
    def addend(self) -> int:
        """ The classical addend in use for constructing the adder gate. """
        return self._addend

    def _build_phi_adder(
        self,
        qreg_size: int,
        addend: int
    ) -> CompositeGate:
        phi_adder = CompositeGate()

        for k in range(qreg_size):
            theta = pi * addend / (1 << k)
            U1(theta) | phi_adder([qreg_size - 1 - k])

        return phi_adder

    def _build_ctl_phi_adder(
        self,
        qreg_size: int,
        addend: int
    ) -> CompositeGate:
        c_phi_adder = CompositeGate()

        for k in range(qreg_size):
            theta = pi * addend / (1 << k)
            CU1(theta) | c_phi_adder([0, qreg_size - k])

        return c_phi_adder

    def _build_c2_phi_adder(
        self,
        qreg_size: int,
        addend: int
    ):
        def _CCU1(theta) -> CompositeGate:
            """ Construct a doubly controlled U1 gate by given rotation angle theta. """
            ccu1 = CompositeGate("CCU1")

            CU1(theta / 2) | ccu1([1, 2])
            CX | ccu1([0, 1])
            CU1(-theta / 2) | ccu1([1, 2])
            CX | ccu1([0, 1])
            CU1(theta / 2) | ccu1([0, 2])

            return ccu1

        c2_phi_adder = CompositeGate()

        for k in range(qreg_size):
            theta = pi * addend / (1 << k)
            _CCU1(theta) | c2_phi_adder([0, 1, qreg_size - k + 1])

        return c2_phi_adder
