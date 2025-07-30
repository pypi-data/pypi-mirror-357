from typing import Tuple, List

import numpy as np

from QuICT.core.gate import CompositeGate, X, CX, CCX, ID, CSwap, Swap
from QuICT.tools.exception.core import GateParametersAssignedError


def var_controlled_x(n_control) -> CompositeGate:
    """0 to 2 controlled-X

    Args:
        n_control (int): the number of control qubits
    """
    if n_control == 0:
        return X
    elif n_control == 1:
        return CX
    elif n_control == 2:
        return CCX
    else:
        raise ValueError("control number", "0-2", f"{n_control}")


class Carry(CompositeGate):
    r"""
    Construct a module called 'Carry' which is part of Toffoli based modular multiplier used to factor.
    This module compute the overflow of $a(\text{quantum})+c(\text{classical})$ with borrowed ancilla qubits called 'g'.
    it's worth noting that at most 2 control qubits can be used in this module.

    $$
        \vert{0}\rangle \vert{\text{ctrls}}\rangle \vert{a}\rangle_n \vert{g}\rangle_{n-1}
        \to
        \vert{\text{overflow}}\rangle \vert{\text{ctrls}}\rangle \vert{a}\rangle_n \vert{g}\rangle_{n-1}
    $$

    Note:
        If the number of control qubits is 2 and the quantum register size of $a$ is 1, then the module will do:

         $$
            \vert{0}\rangle_1 \vert{\text{ctrls}}\rangle_2 \vert{a}\rangle_1 \vert{g}\rangle_1
            \to
            \vert{\text{overflow}}\rangle_1 \vert{\text{ctrls}}\rangle_2 \vert{a}\rangle_1 \vert{g}\rangle_1
        $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_a: int,
        n_control: int,
        val_c: int,
        name: str = None
    ):
        """
        Args:
            qreg_a (int): The quantum register size for the quantum addend.
            n_control (int): The number of control qubits, which ranges from 0 to 2.
            val_c (int): The value of the classical addend.
            name (str): The name of this module. Defaults to None.
        """
        if qreg_a < 1:
            raise GateParametersAssignedError(
                f"The quantum register size for the quantum addend in Carry module needs at least one qubits "
                f"but given {qreg_a}."
            )

        if n_control < 0 or n_control > 2:
            raise GateParametersAssignedError(
                f"The control qubits' number in Carry module ranges from 0 to 2 but given {n_control}."
            )

        if val_c >> qreg_a != 0:
            raise GateParametersAssignedError(
                f"The given value of classical addend in Carry module is {val_c}, "
                f"and can not be represented by {qreg_a} bits."
            )

        super().__init__(name)
        if name is None:
            self.name = "Carry"

        if qreg_a == 1 and n_control == 2:
            self._implement_mapping = [0] * 5
        else:
            self._implement_mapping = [0] * (2 * qreg_a + n_control)

        carry, mapping = self._build_carry(qreg_a, n_control, val_c)
        for idx, val in enumerate(mapping):
            self._implement_mapping[val] = idx

        carry = carry & self._implement_mapping

        for gate in carry:
            gate | self

    @staticmethod
    def _build_carry(
        qreg_a: int,
        n_control: int,
        val_c: int
    ) -> Tuple[CompositeGate, List]:
        """
        THe order same as Fig.3 in the paper.

        Args:
            qreg_a (int): The quantum register size for the quantum addend.
            n_control (int): The number of control qubits, which ranges from 0 to 2.
            val_c (int): The value of the classical addend.

        Return:
            The carry module with the same order as Fig.3 in the paper.
        """
        a_list = [0]
        g_list = []
        for i in range(qreg_a - 1):
            a_list.append(2 * i + 1)
            g_list.append(2 * i + 2)
        overflow = [2 * qreg_a - 1]
        ctrl_list = []
        for i in range(n_control):
            ctrl_list.append(2 * qreg_a + i)

        if qreg_a == 1 and n_control == 2:
            g_list = [4]

        mapping = overflow + ctrl_list + list(reversed(a_list)) + list(reversed(g_list))

        # construct the 'carry' module
        cg = CompositeGate()
        # for special case when the lowest two bits of val_c is zero
        ID | cg([0])
        ID | cg([1])
        for i in ctrl_list:
            ID | cg([i])
        # The case that the quantum register size is 1
        if qreg_a == 1:
            if val_c & 1 == 1:
                if n_control == 0:
                    CX | cg(a_list + overflow)
                elif n_control == 1:
                    CCX | cg(ctrl_list + a_list + overflow)
                else:
                    CCX | cg(a_list + g_list + overflow)
                    CCX | cg(ctrl_list + g_list)
                    CCX | cg(a_list + g_list + overflow)
                    CCX | cg(ctrl_list + g_list)
        # The case that the quantum register size is greater than 1
        else:
            # step 1:
            if n_control == 0:
                CX | cg([g_list[-1]] + overflow)
            elif n_control == 1:
                CCX | cg([g_list[-1]] + ctrl_list + overflow)
            else:
                CCX | cg([g_list[-1], a_list[-1]] + overflow)
                CCX | cg(ctrl_list + [a_list[-1]])
                CCX | cg([g_list[-1], a_list[-1]] + overflow)
                CCX | cg(ctrl_list + [a_list[-1]])

            # step 2
            for i in range(qreg_a - 1, 1, -1):
                if val_c & 1 << i > 0:
                    CX | cg([a_list[i], g_list[i - 1]])
                    X | cg(a_list[i])
                CCX | cg([g_list[i - 2], a_list[i], g_list[i - 1]])
            if val_c & 1 << 1 > 0:
                CX | cg([a_list[1], g_list[0]])
                X | cg(a_list[1])
            if val_c & 1 > 0:
                CCX | cg([a_list[0], a_list[1], g_list[0]])

            # step 3
            for i in range(qreg_a - 2):
                CCX | cg([g_list[i], a_list[i + 2], g_list[i + 1]])
            if n_control == 0:
                CX | cg([g_list[-1]] + overflow)
            elif n_control == 1:
                CCX | cg([g_list[-1]] + ctrl_list + overflow)
            else:
                CCX | cg([g_list[-1], a_list[-1]] + overflow)
                CCX | cg(ctrl_list + [a_list[-1]])
                CCX | cg([g_list[-1], a_list[-1]] + overflow)
                CCX | cg(ctrl_list + [a_list[-1]])

            # step 4: un-computation
            for i in range(qreg_a - 3, -1, -1):
                CCX | cg([g_list[i], a_list[i + 2], g_list[i + 1]])

            # step 5: un-computation
            if val_c & 1 > 0:
                CCX | cg([a_list[0], a_list[1], g_list[0]])
            if val_c & 1 << 1 > 0:
                X | cg(a_list[1])
                CX | cg([a_list[1], g_list[0]])
            for i in range(2, qreg_a):
                CCX | cg([g_list[i - 2], a_list[i], g_list[i - 1]])
                if val_c & 1 << i > 0:
                    X | cg(a_list[i])
                    CX | cg([a_list[i], g_list[i - 1]])

        return cg, mapping


class Incrementer(CompositeGate):
    r"""
       Construct a module called 'Incrementer' which is part of Toffoli based modular multiplier used to factor.

       $$
           \vert{\text{ctrls}}\rangle_m \vert{v}\rangle_n \vert{g}\rangle_{n+m}
           \to
           \vert{\text{ctrls}}\rangle_m \vert{v+1}\rangle_n \vert{g}\rangle_{n+m}
       $$

       References:
           [1]: Craig Gidney. StackExchange: Creating bigger controlled nots from single qubit, Toffoli, and
           CNOT gates, without workspace. 2015. http://cs.stackexchange.com/questions/40933/.
        """

    def __init__(
        self,
        qreg_size: int,
        ctrl: bool = False,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the operator 'v'.
            ctrl (bool): whether this incrementer have control qubit. Defaults to False.
            name (str): The name of this module. Defaults to None.
        """
        if qreg_size < 1:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in Incrementer module needs at least one qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = "Incrementer"

        if ctrl:
            qreg_size += 1

        self._implement_mapping = [0] * (2 * qreg_size)

        inc, mapping = self._build_incrementer(qreg_size, ctrl)
        for idx, val in enumerate(mapping):
            self._implement_mapping[val] = idx

        inc = inc & self._implement_mapping

        for gate in inc:
            gate | self

    @staticmethod
    def _build_incrementer(qreg_size: int, ctrl: bool) -> Tuple[CompositeGate, List]:
        """
        The order same as the reference.

        Args:
            qreg_size (int): The quantum register size for the operator 'v'.

        Return:
            The composite gate of this incrementer.
        """
        v = []
        g = []
        for i in range(qreg_size):
            g.append(2 * i)
            v.append(2 * i + 1)

        if ctrl:
            mapping = [v[0]] + list(reversed(v[1::])) + list(reversed(g))
        else:
            mapping = list(reversed(v)) + list(reversed(g))

        # construct
        cg = CompositeGate()
        # step 1
        for i in range(qreg_size):
            CX | cg([g[0], v[i]])
        # step 2
        for i in range(1, qreg_size):
            X | cg(g[i])
        X | cg([v[-1]])

        # step 3
        for i in range(qreg_size - 1):
            CX | cg([g[i], v[i]])
            CX | cg([g[i + 1], g[i]])
            CCX | cg([g[i], v[i], g[i + 1]])
        CX | cg([g[-1], v[-1]])
        for i in range(qreg_size - 2, -1, -1):
            CCX | cg([g[i], v[i], g[i + 1]])
            CX | cg([g[i + 1], g[i]])
            CX | cg([g[i + 1], v[i]])

        # step 4
        for i in range(1, qreg_size):
            X | cg(g[i])

        # step 5
        for i in range(qreg_size - 1):
            CX | cg([g[i], v[i]])
            CX | cg([g[i + 1], g[i]])
            CCX | cg([g[i], v[i], g[i + 1]])
        CX | cg([g[-1], v[-1]])
        for i in range(qreg_size - 2, -1, -1):
            CCX | cg([g[i], v[i], g[i + 1]])
            CX | cg([g[i + 1], g[i]])
            CX | cg([g[i + 1], v[i]])

        # step 6
        for i in range(qreg_size):
            CX | cg([g[0], v[i]])

        if ctrl:
            X | cg(v[0])

        return cg, mapping


class RecAdder(CompositeGate):
    r"""
    The recursively applied partial-circuit in HRSAdder.The order of input is different from Fig.5 in the reference.

    $$
        \vert{ctrl}\rangle \vert{x_H}\rangle_{\lfloor{n/2}\rfloor} \vert{x_L}\rangle_{\lceil{n/2}\rceil}
        \vert{g}\rangle_2
        \to
        \vert{ctrl}\rangle \vert{c_H}\rangle_{\lfloor{n/2}\rfloor} \vert{c_L}\rangle_{\lceil{n/2}\rceil}
        \vert{g}\rangle_2
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_size: int,
        val_c: int,
        ctrl: bool = False,
        name: str = None
    ):
        """
            qreg_size (int): The quantum register size for the quantum addend.
            val_c (int): The value of the classical addend.
            ctrl (bool): Whether this module have control qubit. Defaults to False.
            name (str): The name of this module. Defaults to None.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in RecAdder module needs at least two qubits "
                f"but given {qreg_size}."
            )
        super().__init__(name)
        if name is None:
            self.name = "RecAdder"

        adder_rec = self._build_adder_rec(qreg_size, val_c, ctrl)

        for gate in adder_rec:
            gate | self

    def _build_adder_rec(self, qreg_size: int, val_c: int, ctrl: bool) -> CompositeGate:
        """
        Args:
            qreg_size (int): The quantum register size for the operator 'x'.
            val_c (int): The value of the classical addend.
            ctrl (bool): Whether this module have control qubit.

        Return:
            The composite gate of the recursive part of the HRSAdder.
        """
        # construct
        cg = CompositeGate()

        if qreg_size == 1:
            return cg

        offset = 0
        control = []
        if ctrl:
            control = [0]
            offset = 1
        x_H_size = qreg_size // 2
        x_L_size = qreg_size - x_H_size
        x_H = list(range(offset, x_H_size + offset))
        x_L = list(range(x_H_size + offset, qreg_size + offset))
        val_c_H = val_c >> x_L_size
        val_c_L = val_c % (2 ** x_L_size)
        anc_c = [qreg_size + offset]
        anc_g = [qreg_size + 1 + offset]

        # step 1
        Incrementer(x_H_size, True) | cg(anc_c + x_H + x_L + anc_g[:1 - x_L_size + x_H_size:])
        # step 2
        for i in x_H:
            CX | cg(anc_c + [i])
        # step 3
        Carry(x_L_size, offset, val_c_L) | cg(anc_c + control + x_L + x_H[:x_L_size - 1:])
        # step 4
        Incrementer(x_H_size, True) | cg(anc_c + x_H + x_L + anc_g[:1 - x_L_size + x_H_size:])
        # step 5
        Carry(x_L_size, offset, val_c_L) | cg(anc_c + control + x_L + x_H[:x_L_size - 1:])
        # step 6
        for i in x_H:
            CX | cg(anc_c + [i])
        # step 7
        self._build_adder_rec(x_L_size, val_c_L, ctrl) | cg(control + x_L + anc_c + anc_g)
        self._build_adder_rec(x_H_size, val_c_H, ctrl) | cg(control + x_H + anc_c + anc_g)

        return cg


class CtrlHRSSubtractor(CompositeGate):
    r"""
    Compute x(quantum) - c(classical) with borrowed qubits with 1-controlled.

    Constructed on the basis of CtrlHRSAdder with complement technique.

    $$
        \vert{ctrl}\rangle \vert{x}\rangle_n \vert{g}\rangle_2
        \to
        \vert{ctrl}\rangle \vert{(x-c)%2^n}\rangle_n \vert{g}\rangle_2
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_size: int,
        val_c: int,
        name: str = "CtrlHRSSubtractor"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the minus.
            val_c (int): The value of the classical minus.
            name (str): The name of this module. Defaults to "CtrlHRSSubtractor".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in CtrlHRSSubtractor needs at least two qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        val_c = 2 ** qreg_size - val_c
        RecAdder(qreg_size, val_c, True) | self(list(range(qreg_size + 3)))
        for i in range(qreg_size):
            if val_c & 1 << i:
                CX | self([0, qreg_size - i])


class HRSCompare(CompositeGate):
    r"""
    Compare x(quantum) and c(classical) with borrowed qubits with at most 2-controlled.
    The Indicator toggles if c > x, not if c <= x.

    Constructed on the basis of Carry.

    $$
        \vert{0}\rangle \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{g}\rangle_{n-1}
        \to
        \vert{c > x}\rangle \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{g}\rangle_{n-1}
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_size: int,
        n_control: int,
        val_c: int,
        name: str = "HRSCompare"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the quantum number.
            n_control (int): The number of control qubits, which ranges from 0 to 2.
            val_c (int): The value of the classical number.
            name (str): The name of this module. Defaults to None.
        """
        if qreg_size < 1:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in HRSCompare module needs at least one qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        # x=2**n-x-1
        for i in range(1 + n_control, qreg_size + 1 + n_control):
            X | self([i])
        # apply Carry
        Carry(qreg_size, n_control, val_c) | self(list(range(2 * qreg_size + n_control)))
        # recover
        for i in range(1 + n_control, qreg_size + 1 + n_control):
            X | self([i])


class HRSAdder(CompositeGate):
    r"""
    Compute x(quantum) + c(classical) with borrowed qubits without controlled.

    $$
        \vert{x}\rangle_n \vert{g}\rangle_2
        \to
        \vert{(x+c)%2^n}\rangle_n \vert{g}\rangle_2
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_size: int,
        val_c: int,
        name: str = "HRSAdder"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the addend.
            val_c (int): The value of the classical addend.
            name (str): The name of this module. Defaults to "HRSAdder".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in HRSAdder needs at least two qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        RecAdder(qreg_size, val_c) | self(list(range(qreg_size + 2)))
        for i in range(qreg_size):
            if val_c & 1 << i:
                X | self([qreg_size - 1 - i])


class CtrlHRSAdder(CompositeGate):
    r"""
    Compute x(quantum) + c(classical) with borrowed qubits with 1-controlled.

    $$
        \vert{ctrl}\rangle \vert{x}\rangle_n \vert{g}\rangle_2
        \to
        \vert{ctrl}\rangle \vert{(x+c)%2^n}\rangle_n \vert{g}\rangle_2
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.
    """

    def __init__(
        self,
        qreg_size: int,
        val_c: int,
        name: str = "CtrlHRSAdder"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the addend.
            val_c (int): The value of the classical addend.
            name (str): The name of this module. Defaults to "CtrlHRSAdder".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in CtrlHRSAdder needs at least two qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        RecAdder(qreg_size, val_c, True) | self(list(range(qreg_size + 3)))
        for i in range(qreg_size):
            if val_c & 1 << i:
                CX | self([0, qreg_size - i])


class HRSAdderMod(CompositeGate):
    r"""
    Compute b(quantum) + a(classical) mod N(classical), with n-1 dirty ancilla qubits g and
    one clean ancilla qubit indicator. The controlled qubits number of this adder is range from 0 to 2.

    $$
        \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{g}\rangle_{n-1} \vert{indicator}\rangle
        \to
        \vert{\text{ctrls}}\rangle \vert{(x+a)%N}\rangle_n \vert{g}\rangle_{n-1} \vert{indicator}\rangle
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.

    Note:
        [1]: Note that this circuit works only when n > 2. So for smaller numbers, use another design.
        [2]: If you want to recover dirty ancilla qubits, b and a must be smaller than N.
    """

    def __init__(
        self,
        qreg_size: int,
        val_a: int,
        val_n: int,
        n_control: int = 0,
        reverse: bool = False,
        name: str = "HRSAdderMod"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the addend.
            val_a (int): The value of the classical addend.
            val_n (int): The value of the classical modulus.
            n_control (int): The number of control qubits, which ranges from 0 to 2. Defaults to 0.
            reverse (bool): Whether reverse the circuit of this adder.
            name (str): The name of this module. Defaults to "HRSAdderMod".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in HRSAdderMod needs at least three qubits "
                f"but given {qreg_size}."
            )

        if n_control < 0 or n_control > 2:
            raise GateParametersAssignedError(
                f"The control qubits' number in HRSAdderMod ranges from 0 to 2 but given {n_control}."
            )

        super().__init__(name)
        if reverse:
            val_a = val_n - val_a

        # init
        control = list(range(n_control))
        qubit_b = list(range(n_control, n_control + qreg_size))
        g = list(range(n_control + qreg_size, n_control + 2 * qreg_size - 1))
        indicator = [n_control + 2 * qreg_size - 1]

        # apply
        HRSCompare(qreg_size, n_control, val_n - val_a) | self(indicator + control + qubit_b + g)
        CtrlHRSAdder(qreg_size, val_a) | self(indicator + qubit_b + g[:2:])
        var_controlled_x(n_control) | self(control + indicator)
        CtrlHRSSubtractor(qreg_size, val_n - val_a) | self(indicator + qubit_b + g[:2:])
        var_controlled_x(n_control) | self(control + indicator)
        HRSCompare(qreg_size, n_control, val_a) | self(indicator + control + qubit_b + g)
        var_controlled_x(n_control) | self(control + indicator)


class HRSMulModRaw(CompositeGate):
    r"""
    Compute b(quantum) + x(quantum) * a(classical) mod N(classical), with one clean ancilla qubit indicator.
    The controlled qubits number of this module is range from 0 to 1.

    $$
        \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{b}\rangle_{n} \vert{indicator}\rangle
        \to
        \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{(b+x*a)%N}\rangle_{n} \vert{indicator}\rangle
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.

    Note:
        [1]: Note that this circuit works only when n > 2. So for smaller numbers, use another design.
    """

    def __init__(
        self,
        qreg_size: int,
        val_a: int,
        val_n: int,
        ctrl: bool = False,
        reverse: bool = False,
        name: str = "HRSMulModRaw"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the multiplicand.
            val_a (int): The value of the classical multiplicand.
            val_n (int): The value of the classical modulus.
            ctrl (int): Whether this module have control qubits. Defaults to False.
            reverse (bool): Whether reverse the circuit of this module.
            name (str): The name of this module. Defaults to "HRSMulModRaw".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in HRSAdderMod needs at least three qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        if reverse:
            self._mul_mod_raw_reversed(qreg_size, val_a, val_n, ctrl) | self
        else:
            self._mul_mod_raw(qreg_size, val_a, val_n, ctrl) | self

    @staticmethod
    def _mul_mod_raw(
        qreg_size: int,
        val_a: int,
        val_n: int,
        ctrl: bool
    ) -> CompositeGate:
        r"""
        Compute b(quantum) + x(quantum) * a(classical) mod N(classical),
        with target qubits b and ancilla qubit indicator.

        Args:
            qreg_size (int): The quantum register size for the multiplicand.
            val_a (int): The value of the classical multiplicand.
            val_n (int): The value of the classical modulus.
            ctrl (int): Whether this module have control qubits.
        """
        cg = CompositeGate()

        # init
        n_ctrl = 0
        if ctrl:
            n_ctrl = 1
        control = list(range(n_ctrl))
        x_list = list(range(n_ctrl, n_ctrl + qreg_size))
        b_list = list(range(n_ctrl + qreg_size, n_ctrl + 2 * qreg_size))
        indicator = [n_ctrl + 2 * qreg_size]

        a_list = []
        for i in range(qreg_size):
            a_list.append(val_a)
            val_a = (val_a * 2) % val_n

        for i in range(qreg_size):
            # borrow all the n-1 unused qubits in x
            g = x_list[:qreg_size - i - 1] + x_list[qreg_size - i:]
            HRSAdderMod(qreg_size, a_list[i], val_n, n_ctrl + 1) | cg(
                control + [x_list[qreg_size - 1 - i]] + b_list + g + indicator)

        return cg

    @staticmethod
    def _mul_mod_raw_reversed(
        qreg_size: int,
        val_a: int,
        val_n: int,
        ctrl: bool
    ) -> CompositeGate:
        """
        The reversed circuit of mul_mod_raw()

        Args:
            qreg_size (int): The quantum register size for the multiplicand.
            val_a (int): The value of the classical multiplicand.
            val_n (int): The value of the classical modulus.
            ctrl (int): Whether this module have control qubits.
        """
        cg = CompositeGate()

        # init
        n_ctrl = 0
        if ctrl:
            n_ctrl = 1
        control = list(range(n_ctrl))
        x_list = list(range(n_ctrl, n_ctrl + qreg_size))
        b_list = list(range(n_ctrl + qreg_size, n_ctrl + 2 * qreg_size))
        indicator = [n_ctrl + 2 * qreg_size]

        a_list = []
        for i in range(qreg_size):
            a_list.append(val_a)
            val_a = (val_a * 2) % val_n

        for i in range(qreg_size):
            g = x_list[:i] + x_list[i + 1:]
            HRSAdderMod(qreg_size, val_n - a_list[qreg_size - i - 1], val_n, n_ctrl + 1) | cg(
                control + [x_list[i]] + b_list + g + indicator)

        return cg


class HRSMulMod(CompositeGate):
    r"""
    Compute x(quantum) * a(classical) mod N(classical), with n dirty ancilla qubits g and
    one clean ancilla qubit indicator. The controlled qubits number of this module is range from 0 to 1.

    $$
        \vert{\text{ctrls}}\rangle \vert{x}\rangle_n \vert{g}\rangle_{n} \vert{indicator}\rangle
        \to
        \vert{\text{ctrls}}\rangle \vert{(x*a)%N}\rangle_n \vert{g}\rangle_{n} \vert{indicator}\rangle
    $$

    References:
        [1]: "Factoring using 2n+2 qubits with Toffoli based modular multiplication" by Thomas Häner,
        Martin Roetteler and Krysta M. Svore<https://arxiv.org/abs/1611.07995>.

    Note:
        [1]: Note that this circuit works only when n > 2. So for smaller numbers, use another design.
    """

    def __init__(
        self,
        qreg_size: int,
        val_a: int,
        val_n: int,
        ctrl: bool = False,
        name: str = "HRSMulMod"
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the multiplicand.
            val_a (int): The value of the classical multiplicand.
            val_n (int): The value of the classical modulus.
            ctrl (int): Whether this module have control qubits. Defaults to False.
            name (str): The name of this module. Defaults to "HRSMulMod".
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The quantum register size for the operators in HRSMulMod needs at least three qubits "
                f"but given {qreg_size}."
            )

        super().__init__(name)

        n_ctrl = 0
        if ctrl:
            n_ctrl = 1
        control = list(range(n_ctrl))
        qubit_x = list(range(n_ctrl, n_ctrl + qreg_size))
        ancilla = list(range(n_ctrl + qreg_size, n_ctrl + 2 * qreg_size))
        indicator = [n_ctrl + 2 * qreg_size]

        a_r = pow(val_a, -1, val_n)
        HRSMulModRaw(qreg_size, val_a, val_n, ctrl) | self(control + qubit_x + ancilla + indicator)

        for i in range(qreg_size):
            if ctrl:
                CSwap | self([control[0], qubit_x[i], ancilla[i]])
            else:
                Swap | self([qubit_x[i], ancilla[i]])

        HRSMulModRaw(qreg_size, a_r, val_n, ctrl, True) | self(control + qubit_x + ancilla + indicator)


class CHRSMulMod(CompositeGate):
    """ Controlled modular multiplication
        For `reg_size` is `n`:

        |control>|x>_{n}|0>_{n + 1} --> |control>|a*x mod N>_{n}|0>_{n + 1} , control == 1
        |control>|x>_{n}|0>_{n + 1} --> |control>|x>_{n}|0>_{n + 1}         , control == 0
    """

    def __init__(
        self,
        modulus: int,
        multiple: int,
        qreg_size: int,
        name: str = None
    ):
        """ Construct the modular multiplication gate

        Args:
            qreg_size (int): size of the register to hold the result of the modular multiplication.
            multiple (int): the multiple in the modular multiplication.
            modulus (int): the modulus in the modular multiplication.
            name (str): name of the gate.
        """
        if qreg_size <= 2:
            raise Exception("The numbers should be more than 2-length to use HRS circuits.")
        if int(np.log2(modulus)) + 1 > qreg_size:
            raise ValueError(f"The size of register: {qreg_size} is not enough to hold result of mod N"
                             f", which requires {int(np.log2(modulus)) + 1} qubits.")
        if np.gcd(multiple, modulus) != 1:
            raise ValueError(f"The multiple and the modulus have to be coprime, but given a={multiple}, N={modulus}.")

        super().__init__(name)
        if name is None:
            self.name = f"*{multiple} mod{modulus}"

        self._multiple = multiple
        self._modulus = modulus
        self.reg_size = qreg_size

        self.control = 0
        self.reg_x = list(range(1, qreg_size + 1))
        self.ancilla = list(range(qreg_size + 1, 2 * (qreg_size + 1)))

        self._build_gate(qreg_size, multiple, modulus) | self(self.reg_x + self.ancilla + [self.control])

        self.set_ancilla(self.ancilla)

    def exp2(self, n: int) -> CompositeGate:
        a_exp_n_reduced = self._fast_mod_exp(self._multiple, n, self._modulus)

        _gates = CompositeGate()
        self._build_gate(self.reg_size, a_exp_n_reduced, self._modulus) | _gates(
            self.reg_x + self.ancilla + [self.control]
        )
        _gates.set_ancilla(self.ancilla_qubits)
        _gates.name = f"*{self._multiple}^(2^{n}) m{self._modulus}"

        return _gates

    def _build_gate(self, n, a, N):
        """
        Compute x(quantum) * a(classical) mod N(classical), with ancilla qubits, 1-controlled.

        Args:
            n(int): length of numbers
            a(int): the constant multiplied to the quantum number
            N(int): the modulus

        Quregs:
            x(Qureg): n qubits.
            ancilla(Qureg): n qubits.
            indicator(Qubit): 1 qubit.
            control(Qubit): 1 qubit.

        Note that this circuit works only when n > 2.
        So for smaller numbers we use another design.
        """
        if n <= 2:
            raise Exception(
                "The numbers should be more than 2-length to use HRS circuits."
            )

        gate_set = CompositeGate()
        qubit_x = list(range(n))
        ancilla = list(range(n, 2 * n))
        indicator = 2 * n
        control = 2 * n + 1

        HRSMulMod(n, a, N, True) | gate_set([control] + qubit_x + ancilla + [indicator])

        return gate_set

    def _fast_mod_exp(self, base: int, n: int, N: int) -> int:
        for _ in range(n):
            base = (base * base) % N
        return base
