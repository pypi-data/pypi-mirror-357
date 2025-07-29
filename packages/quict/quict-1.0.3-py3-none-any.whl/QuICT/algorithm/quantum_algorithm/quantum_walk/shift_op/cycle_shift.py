from typing import Literal
from QuICT.core.gate import CompositeGate, X, CX, CCX
from QuICT.algorithm.arithmetic.adder import QFTWiredAdder
from QuICT.algorithm.arithmetic.basic import Comparator
from numpy import log2, ceil

_IMPLEMENT_MODE = Literal["simple", "exact"]


class CycleShiftOp(CompositeGate):
    r""" A shift operator on a cycle of `N` nodes modified from bea's modular adder.

    $$U\vert{c}\rangle\vert{x}\rangle\vert{0}\rangle
    =\vert{c}\rangle\vert{x + (-1)^{1 - c} \mod N}\rangle\vert{0}\rangle$$

    assuming node indices are encoded as signed positive integers on the node register.

    Reference:
        [1]: "Circuit for Shor's algorithm using 2n+3 qubits": http://arxiv.org/abs/quant-ph/0205095v3
    """

    def __init__(
        self,
        node_num: int,
        qreg_size: int = None,
        in_fourier: bool = False,
        out_fourier: bool = False,
        mode: _IMPLEMENT_MODE = "simple",
        name: str = None
    ):
        """
        Args:
            node_num (int): total number of nodes/vertices in the cycle graph.
            qreg_size (int): register size for the node register.
            in_fourier (bool): If True, will assume the input register is already in fourier basis.
            out_fourier (bool): If True, after the addition, the register will be left in fourier basis.
            mode (string): cycle shift gate in `simple` mode has lower depth and size with the restriction that
                the value in the node register has to be `< N`, otherwise the clean ancilla qubit cannot be reset.
                `exact` mode does not have above restriction but with larger depth and size.
        """
        require_q = int(ceil(log2(node_num))) + 1
        if qreg_size is None:
            qreg_size = require_q
        if require_q > qreg_size:
            raise ValueError(f"The number of nodes requires at least {require_q} qubits, "
                             f"but given {qreg_size}.")

        if mode not in ["simple", "exact"]:
            raise ValueError("Please choose mode from: [\"simple\", \"exact\"].")

        super().__init__(name)

        self._ctrl_reg = [0]
        self._data_reg = list(range(1, qreg_size + 1))
        self._anci_reg = [qreg_size + 1]

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=-node_num + 2,
            num_control=1,
            in_fourier=in_fourier,
            out_fourier=True
        ) | self(self._ctrl_reg + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=-1,
            in_fourier=True
        ) | self(self._data_reg)

        CX | self([self._data_reg[0], self._anci_reg[0]])

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=node_num,
            num_control=1,
            out_fourier=True
        ) | self(self._anci_reg[:1] + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=node_num - 2,
            num_control=1,
            in_fourier=True,
            out_fourier=True
        ) | self(self._ctrl_reg + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=1 - node_num,
            in_fourier=True
        ) | self(self._data_reg)

        X | self(self._data_reg[0])
        CX | self([self._data_reg[0], self._anci_reg[0]])
        X | self(self._data_reg[0])

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=-node_num + 2,
            num_control=1,
            out_fourier=True
        ) | self(self._ctrl_reg + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=node_num - 1,
            in_fourier=True,
            out_fourier=out_fourier or (mode == "exact")
        ) | self(self._data_reg)

        if mode == "exact":
            QFTWiredAdder(
                qreg_size=qreg_size,
                addend=1,
                num_control=1,
                in_fourier=True
            ) | self(self._anci_reg + self._data_reg)

            CCX | self(self._ctrl_reg + self._anci_reg + self._data_reg[:1])
            QFTWiredAdder(
                qreg_size=qreg_size - 1,
                addend=node_num - 2,
                num_control=1
            ) | self(self._data_reg)
            CCX | self(self._ctrl_reg + self._anci_reg + self._data_reg[:1])

            Comparator(
                qreg_size=qreg_size,
                const=node_num,
                out_fourier=out_fourier,
                mode="ge"
            ) | self(self._data_reg + self._anci_reg)

        self.set_ancilla(self._data_reg[:1] + self._anci_reg)
