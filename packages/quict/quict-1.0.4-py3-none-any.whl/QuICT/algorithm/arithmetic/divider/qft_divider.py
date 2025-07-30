from numpy import pi

from QuICT.algorithm.qft import QFT, IQFT
from QuICT.core.gate import CompositeGate, CU1, X, CX
from QuICT.tools.exception.core import GateParametersAssignedError


class CCRk(CompositeGate):
    r"""
        Build two control qubit $R_k$ gate according to the paper.

        References:
            [1]: "Integer Numeric Multiplication Using Quantum Fourier Transform" by Joseph L Pachuau,
            Arnab Roy and Anish Kumar Saha <https://doi.org/10.1007/s40509-021-00262-w>.
    """

    def __init__(
            self,
            k: int,
            name: str = None
    ):
        """
        Args:
            k (int): The value of 'k' in $R_k$.
            name (str, optional): The name of this gate.
        """
        super().__init__(name)
        if name is None:
            self.name = f"R_{k}"

        # init rotation angle
        if k < 0:
            theta = -pi / (1 << (-k))
        else:
            theta = pi / (1 << k)

        CU1(theta) | self([1, 2])
        CX | self([0, 1])
        CU1(-theta) | self([1, 2])
        CX | self([0, 1])
        CU1(theta) | self([0, 2])


class SUBModule(CompositeGate):
    r"""
        Implement a subtractor which is part of the following dividers.
        This module in total requires `2n` qubits.
        $$
            \vert{\Phi (a)}\rangle_n \vert{b}\rangle_n
            \to
            \vert{\Phi (a-b)}\rangle_n \vert{b}\rangle_n
        $$

        References:
            [1]: "Quantum Division Circuit Based on Restoring Division Algorithm"
            by Alireza Khosropour, Hossein Aghababa and Behjat Forouzandeh
            <https://ieeexplore.ieee.org/document/5945378>.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
        Args:
            qreg_size (int): The register size for the operand
                which is same as the register size for the dividend in the following divider.
            name (str, optional): The name of this module.

        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"{self.__class__.__name__} needs register size must to be at least 2 but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = "SUB"

        sub, mapping = self._build_sub(qreg_size)

        self._implement_mapping = [0] * (2 * qreg_size)
        for idx, val in enumerate(mapping):
            self._implement_mapping[val] = idx
        sub = sub & self._implement_mapping

        for gate in sub:
            gate | self

    def _build_sub(self, qreg_size) -> tuple[CompositeGate, list[int]]:
        """The order same as the figure 4 in the paper."""
        b_h2l = list(range(qreg_size))
        a_h2l = list(range(qreg_size, 2 * qreg_size))

        mapping = a_h2l + b_h2l

        sub = CompositeGate()
        for i in range(qreg_size):
            for j in range(i + 1):
                CU1(-(pi / (1 << (i - j)))) | sub([b_h2l[i], a_h2l[j]])

        return sub, mapping


class CtrlAddSubModule(CompositeGate):
    r"""
        Implement a control adder-subtractor module which is part of the following dividers.
        This module in total requires `2n + 1` qubits.
        $$
            \vert{\text{ctrl}}\rangle \vert{\Phi (a)}\rangle_n \vert{b}\rangle_n
            \to
            \vert{\text{ctrl}}\rangle \vert{\Phi (a+(-1)^\text{ctrl}\times b)}\rangle_n \vert{b}\rangle_n
        $$
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
        Args:
            qreg_size (int): The register size for two operands
                which is same as the register size for the dividend in the following dividers.
            name (str): The name of this module.

        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"{self.__class__.__name__} needs register size must to be at least 2 but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = "CtrlSubAdd"

        # the meaning of each line
        ctrl = 0
        a_h2l = range(1, qreg_size + 1)
        b_h2l = range(qreg_size + 1, 2 * qreg_size + 1)

        # construct the module
        for i in range(qreg_size):
            for j in range(i + 1):
                CX | self([ctrl, b_h2l[i]])
                CU1(pi / (1 << (i - j))) | self([b_h2l[i], a_h2l[j]])
                CX | self([ctrl, b_h2l[i]])
                CU1(-pi / (1 << (i - j))) | self([ctrl, a_h2l[j]])


class CtrlADDModule(CompositeGate):
    r"""
        Implement a control adder which is part of the following dividers.
        This module in total requires `2n + 1` qubits.
        $$
            \vert{\text{ctrl}}\rangle \vert{\Phi (a)}\rangle_n \vert{b}\rangle_n
            \to
            \vert{\text{ctrl}}\rangle \vert{\Phi (a+\text{ctrl}\times b)}\rangle_n \vert{b}\rangle_n
        $$

        References:
            [1]: "Quantum Division Circuit Based on Restoring Division Algorithm"
            by Alireza Khosropour, Hossein Aghababa and Behjat Forouzandeh
            <https://ieeexplore.ieee.org/document/5945378>.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
        Args:
            qreg_size (int): The register size for the operand
                which is same as the register size for the dividend in the following dividers.
            name (str, optional): The name of this module.

            Raises:
                 GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"{self.__class__.__name__} needs register size must to be at least 2 but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = "CtrlADD"

        ctrl_add, mapping = self._build_add(qreg_size)
        self._implement_mapping = [0] * (2 * qreg_size + 1)
        for idx, val in enumerate(mapping):
            self._implement_mapping[val] = idx
        ctrl_add = ctrl_add & self._implement_mapping

        for gate in ctrl_add:
            gate | self

    def _build_add(self, qreg_size) -> tuple[CompositeGate, list[int]]:
        """The main part's order same as the figure 4 in the paper."""
        b_h2l = list(range(qreg_size))
        a_h2l = list(range(qreg_size, 2 * qreg_size))
        ctrl = 2 * qreg_size

        mapping = [ctrl] + a_h2l + b_h2l

        ctrl_add = CompositeGate()
        for i in range(qreg_size):
            for j in range(i + 1):
                CCRk(i - j + 1) | ctrl_add([ctrl, b_h2l[i], a_h2l[j]])

        return ctrl_add, mapping


class QFTDivider(CompositeGate):
    r"""
    Implement a quantum divider using non-restoring algorithm based on QFT
    that in total require `3n - 1` qubits.
    $$
        \vert{0}\rangle_{n-1} \vert{b}\rangle_n \vert{a}\rangle_n
        \to
        \vert{b//a}\rangle_n \vert{b%a}\rangle_{n-1} \vert{a}\rangle_n
    $$
    Note:
        The divisor's highest bit must be zero.
        If divisor is set to zero, the result of running this divider is:

        $$
        \vert{0}\rangle_{n-1} \vert{b}\rangle_n \vert{0}\rangle_n
        \to
        \vert{2^n-1}\rangle_n \vert{b_{n-2}...b_0}\rangle_{n-1} \vert{0}\rangle_n
        $$

    References:
        [1]: "Quantum Circuit Designs of Integer Division Optimizing T-count and T-depth"
        by Himanshu Thapliyal, Edgard Muñoz-Coreas, T.S.S.Varun and Travis S.Humble
        <https://ieeexplore.ieee.org/document/8691552>.

        [2]: "Integer Numeric Multiplication Using Quantum Fourier Transform" by Joseph L Pachuau,
        Arnab Roy and Anish Kumar Saha <https://doi.org/10.1007/s40509-021-00262-w>.

        [3]: "Quantum Division Circuit Based on Restoring Division Algorithm"
        by Alireza Khosropour, Hossein Aghababa and Behjat Forouzandeh
        <https://ieeexplore.ieee.org/document/5945378>.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
        Args:
            qreg_size (int): The register size for the dividend and divisor.
            name (str): The name of the divider.

        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 3.
        """
        if qreg_size < 3:
            raise GateParametersAssignedError(
                f"{self.__class__.__name__} needs register size must to be at least 3 but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = "QFTBasedNoResDivider"

        self._build_divider(qreg_size)

    def _build_divider(self, qreg_size):
        zero_list = list(range(qreg_size - 1))
        a_h2l = list(range(qreg_size - 1, 2 * qreg_size - 1))
        b_h2l = list(range(2 * qreg_size - 1, 3 * qreg_size - 1))

        # step 1
        QFT(qreg_size) | self(zero_list + [a_h2l[0]])
        SUBModule(qreg_size) | self(zero_list + [a_h2l[0]] + b_h2l)
        IQFT(qreg_size) | self(zero_list + [a_h2l[0]])
        # step 2
        for i in range(qreg_size - 1):
            X | self(zero_list[i])
            QFT(qreg_size) | self(zero_list[i + 1::] + a_h2l[:i + 2:])
            CtrlAddSubModule(qreg_size) | self(zero_list[i::] + a_h2l[:i + 2:] + b_h2l)
            IQFT(qreg_size) | self(zero_list[i + 1::] + a_h2l[:i + 2:])
        # step 3
        QFT(qreg_size - 1) | self(a_h2l[1::])
        CtrlADDModule(qreg_size - 1) | self(a_h2l + b_h2l[1::])
        IQFT(qreg_size - 1) | self(a_h2l[1::])
        X | self([a_h2l[0]])
