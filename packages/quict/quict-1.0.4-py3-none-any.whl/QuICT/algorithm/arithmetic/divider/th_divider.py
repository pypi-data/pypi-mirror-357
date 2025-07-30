from QuICT.algorithm.arithmetic.adder import TRIOCarryAdder, MuThCtrlAdder
from QuICT.core.gate import CompositeGate, X, CX
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class SubtractionModule(CompositeGate):
    r"""
        Implement a quantum subtractor named subtraction which is a module of the following divider.
        For `qreg_size` equals `n`, this gate requires in total `2n` qubits.
        For both operands, the highest digit must set to $\vert{0}\rangle$
        due to 2's complement positive binary.

        $$
            \vert{b}\rangle_n \vert{a}\rangle_n
            \to
            \vert{b - a }\rangle_n \vert{a}\rangle_n
        $$

        Input:
            The first "n" qubits are subtrahend of which the higher digit in lower lines.<br>
            The following "n" qubits are minuend of which the higher digit in lower lines.

        Output:
            The first "n" qubits are the result of "b-a".<br>
            The following "n" qubits are reserved for the minuend.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
            Args:
                qreg_size (int): The input quantum register size for subtrahend and minuend.
                name (str): The name of subtraction module.
            Raises:
                GateParametersAssignedError: If `qreg_size` is smaller than 3.
        """
        if qreg_size < 3:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 3 but given {qreg_size}"
            )
        super().__init__(name)

        self._qreg_a_list = list(range(qreg_size, 2 * qreg_size))
        self._qreg_b_list = list(range(qreg_size))

        # calculate ~b
        for i in self._qreg_b_list:
            X | self([i])

        # apply TRIOCarryAdder
        adder_apply_list = self._qreg_b_list.copy()
        adder_apply_list.extend(self._qreg_a_list[1::])
        adder_apply_list.append(self._qreg_a_list[0])
        TRIOCarryAdder(qreg_size - 1) | self(adder_apply_list)

        # calculate ~(~b+a)
        for i in self._qreg_b_list:
            X | self([i])


class CtrlAddSubModule(CompositeGate):
    r"""
        Implement a quantum adder-subtractor circuit named Ctrl-AddSub
        which is a module of following divider. For `qreg_size` equals `n`,
        this gate requires in total `2n + 1` qubits. For both operands,
        the highest digit must set to $\vert{0}\rangle$ due to 2's complement positive binary.

        $$
            \vert{\text{ctrl}}\rangle \vert{b}\rangle_n \vert{a}\rangle_n
            \to
            \vert{\text{ctrl}}\rangle \vert{b + \left(-1\right)^{\text{ctrl}} * a }\rangle_n
            \vert{a}\rangle_n
        $$

        Input:
            The first qubit is the "ctrl" qubit which determine
            whether the module is an adder or subtractor.<br>
            The following "n" qubits are first operand of which the higher digit in lower lines.<br>
            The last "n" qubits are second operand of which the higher digit in lower lines.

        Output:
            The first qubit is reserved for 'ctrl' qubit.<br>
            The following "n" qubits are the result of "b-a" or "b+a".<br>
            The last "n" qubits are reserved for the operand.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
            Args:
                qreg_size (int): The input quantum register size for operands.
                name (str): The name of CtrlAddSubModule.
            Raises:
                GateParametersAssignedError: If `qreg_size` is smaller than 3.
        """
        if qreg_size < 3:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 3 but given {qreg_size}"
            )
        super().__init__(name)

        self._ctrl_qubit = [0]
        self._qreg_a_list = list(range(qreg_size + 1, 2 * qreg_size + 1))
        self._qreg_b_list = list(range(1, qreg_size + 1))

        # ctrl-calculate ~b
        for i in self._qreg_b_list:
            CX | self([self._ctrl_qubit[0], i])

        # apply TRIOCarryAdder
        adder_apply_list = self._qreg_b_list.copy()
        adder_apply_list.extend(self._qreg_a_list[1::])
        adder_apply_list.append(self._qreg_a_list[0])
        TRIOCarryAdder(qreg_size - 1) | self(adder_apply_list)

        # ctrl-calculate ~(~b+a)
        for i in self._qreg_b_list:
            CX | self([self._ctrl_qubit[0], i])


class CtrlAddNopModule(CompositeGate):
    r"""
        Implement a quantum conditional addition circuit called Ctrl_AddNop
        which is a module of following divider. For `qreg_size` equals `n`,
        this gate requires in total `2n + 1` qubits. For both addends,
        the highest digit must set to $\vert{0}\rangle$ due to 2's complement positive binary.

        $$
            \vert{\text{ctrl}}\rangle \vert{b}\rangle_n \vert{a}\rangle_n
            \to
            \vert{\text{ctrl}}\rangle \vert{\text{ctrl} * a + b}\rangle_n
            \vert{a}\rangle_n
        $$

        Input:
            The first qubit is the "ctrl" qubit which determine whether to do add.<br>
            The following "n" qubits are first addend of which the higher digit in lower lines.<br>
            The last "n" qubits are second addend of which the higher digit in lower lines.

        Output:
            The first qubit is reserved for 'ctrl' qubit.<br>
            The following "n" qubits are the result of "b + a" or reserved for the first addend.<br>
            The last "n" qubits are reserved for the second addend.
    """

    def __init__(
            self,
            qreg_size: int,
            name: str = None
    ):
        """
            Args:
                qreg_size (int): The input quantum register size for addends.
                name (str): The name of CtrlAddNopModule.
            Raises:
                GateParametersAssignedError: If `qreg_size` is smaller than 3.
        """
        if qreg_size < 3:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 3 but given {qreg_size}"
            )
        super().__init__(name)

        self._ctrl_qubit = [0]
        self._qreg_a_list = list(range(qreg_size + 1, 2 * qreg_size + 1))
        self._qreg_b_list = list(range(1, qreg_size + 1))

        # apply MuThCtrlAdder
        adder_apply_list = self._ctrl_qubit.copy()
        adder_apply_list.extend(self._qreg_a_list[1::])
        adder_apply_list.extend(self._qreg_b_list)
        adder_apply_list.append(self._qreg_a_list[0])
        MuThCtrlAdder(qreg_size - 1) | self(adder_apply_list)


class THRestoreDivider(CompositeGate):
    r"""
        A quantum divider using Restoring Division Algorithm. For `qreg_size` equals `n`, this
        gate requires in total `3n` qubits. For n-qubit binary encoded dividend and divisor,
        calculates quotient and remainder. The quotient will be stored on extra `n` clean qubits
        and the remainder will be stored on dividend's register.

        $$
            \vert{0}\rangle_n \vert{b}\rangle_n \vert{a}\rangle_n
            \to
            \vert{b//a}\rangle_n \vert{b\%a}\rangle_n \vert{a}\rangle_n
        $$

        Note:
            The dividend and divisor are 2’s complement positive binary.<br>
            If divisor is set to zero, the result of running this divider is：

            $$
            \vert{0}\rangle_n \vert{b}\rangle_n \vert{0}\rangle_n
            \to
            \vert{1}\rangle_n \vert{b}\rangle_n \vert{0}\rangle_n
            $$

        Examples:
            ``` python
            from QuICT.core import Circuit
            from QuICT.algorithm.arithmetic import THRestoreDivider

            circuit = Circuit(9)
            THRestoreDivider(3) | circuit
            ```

        !!! Note "Implementation Details(Asymptotic)"

            | Parameter      | Info                          |
            | -------------- | ----------------------------- |
            | Input Size     | $n$                           |
            | Quotient Size  | $n$                           |
            | Remainder Size | $n$                           |
            | num. ancilla   | $0$                           |
            | Gate set       | $CCX, CX, X, H, T, T^\dagger$ |
            | Width          | $3n$                          |
            | Depth          | $13n^2-4n-2$                  |
            | Size           | $31n^2-33n$                   |
            | CX count       | $14n^2-18n$                   |
            | CCX count      | $4n^2-3n$                     |

        References:
            [1]: "Quantum Circuit Designs of Integer Division Optimizing T-count and T-depth"
            by Himanshu Thapliyal, Edgard Muñoz-Coreas, T.S.S.Varun and Travis S.Humble
            <https://ieeexplore.ieee.org/document/8691552>.
    """

    def __init__(self, qreg_size, name: str = None):
        """
            Args:
                qreg_size (int): The input quantum register size for divisor and dividend.
                name (str): The name of the divider gate. Default to None.
            Raises:
                GateParametersAssignedError: If `qreg_size` is smaller than 3.
        """
        if qreg_size < 3:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 3 but given {qreg_size}"
            )
        super().__init__(name)
        if name is None:
            self.name = "THRestoreDivider"

        self._qreg_q_list = list(range(qreg_size))
        self._qreg_r_list = list(range(qreg_size, 2 * qreg_size))
        self._qreg_a_list = list(range(2 * qreg_size, 3 * qreg_size))

        for i in range(qreg_size):
            iteration = self._qreg_q_list[i::].copy()
            iteration.extend(self._qreg_r_list[:i + 1:])
            iteration.extend(self._qreg_a_list)
            self._build_normal_iteration(qreg_size) | self(iteration)

    def _build_normal_iteration(self, qreg_size) -> CompositeGate:
        """
            Construct the circuit generation of iteration of quantum restoring division circuit.
        """
        iteration = CompositeGate()

        # step 1
        SubtractionModule(qreg_size) | iteration(list(range(1, 2 * qreg_size + 1)))
        # step 2
        CX | iteration([1, 0])
        # step 3
        CtrlAddNopModule(qreg_size) | iteration(list(range(2 * qreg_size + 1)))
        # step 4
        X | iteration(0)

        return iteration


class THNonRestDivider(CompositeGate):
    r"""
    A quantum divider using Non-Restoring Division Algorithm. For `qreg_size` equals `n`,
    this gate requires in total `3n-1` qubits. For n-qubit binary encoded dividend and divisor,
    calculates quotient and remainder.

    $$
        \vert{0}\rangle_{n-1} \vert{b}\rangle_n \vert{a}\rangle_n
        \to
        \vert{b//a}\rangle_n \vert{b\%a}\rangle_{n-1} \vert{a}\rangle_n
    $$


    Note:
        The dividend and divisor are 2’s complement positive binary.<br>
        If divisor is set to zero, the result of running this divider is：

        $$
        \vert{0}\rangle_{n-1} \vert{b}\rangle_n \vert{0}\rangle_n
        \to
        \vert{1}\rangle_n \vert{b}\rangle_{n-1} \vert{0}\rangle_n
        $$

    Examples:
        ``` python
        from QuICT.core import Circuit
        from QuICT.algorithm.arithmetic import THRestoreDivider

        circuit = Circuit(11)
        THNonRestDivider(4) | circuit
        ```

    !!! Note "Implementation Details(Asymptotic)"

        | Parameter      | Info                          |
        | -------------- | ----------------------------- |
        | Input Size     | $n$                           |
        | Quotient Size  | $n$                           |
        | Remainder Size | $n-1$                         |
        | num. ancilla   | $0$                           |
        | Gate set       | $CCX, CX, X, H, T, T^\dagger$ |
        | Width          | $3n-1$                        |
        | Depth          | $10n^2+2n-9$                  |
        | Size           | $24n^2-16n-18$                |
        | CX count       | $12n^2-7n-14$                 |
        | CCX count      | $n^2+n-4$                     |

    References:
        [1]: "Quantum Circuit Designs of Integer Division Optimizing T-count and T-depth"
        by Himanshu Thapliyal, Edgard Muñoz-Coreas, T.S.S.Varun and Travis S.Humble
        <https://ieeexplore.ieee.org/document/8691552>.
    """

    def __init__(self, qreg_size: int, name: str = None):
        """
        Args:
            qreg_size (int): The input quantum register size for divisor and dividend.
            name (str): The name of divider gate. Default to None.
        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 4.
        """
        if qreg_size < 4:
            raise GateParametersAssignedError(
                f"Register size must be greater than or equal to 4 but given {qreg_size}"
            )
        super().__init__(name)
        if name is None:
            self.name = "THNonRestDivider"

        self._qreg_q_list = list(range(qreg_size))
        self._qreg_r_list = list(range(qreg_size, 2 * qreg_size - 1))
        self._qreg_a_list = list(range(2 * qreg_size - 1, 3 * qreg_size - 1))

        # step 1
        sub_list = self._qreg_q_list.copy()
        sub_list.extend(self._qreg_a_list)
        SubtractionModule(qreg_size) | self(sub_list)

        # step 2
        for i in range(qreg_size - 1):
            iteration = self._qreg_q_list[i::].copy()
            iteration.extend(self._qreg_r_list[:i + 1:])
            iteration.extend(self._qreg_a_list)
            X | self([self._qreg_q_list[i]])
            CtrlAddSubModule(qreg_size) | self(iteration)

        # step 3
        add_nop_list = [self._qreg_q_list[qreg_size - 1]]
        add_nop_list.extend(self._qreg_r_list)
        add_nop_list.extend(self._qreg_a_list[1::])
        CtrlAddNopModule(qreg_size - 1) | self(add_nop_list)
        X | self([self._qreg_q_list[qreg_size - 1]])
