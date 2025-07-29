from typing import Union
from QuICT.core.gate import CompositeGate, ID, X, CX, RCCX, H, Ry, CRy, Rz, CRz, U1, CU1
from .mcr_without_aux import MCRWithoutAux

from numpy import pi


class MCROptWithOneAux(CompositeGate):
    """ A logn depth multi-control toffoli using one clean ancilla

        |ctrl>_n
        |anci>_1
        |targ>_1

        References:
            [1]: Nie, Junhong, Wei Zi, and Xiaoming Sun. “Quantum Circuit for Multi-Qubit Toffoli Gate with Optimal
                Resource.” arXiv, February 7, 2024. http://arxiv.org/abs/2402.05053.
    """
    def __init__(
        self,
        num_ctrl: int,
        theta: float,
        targ_rot_mode: str = "ry",
        name: str = None
    ):
        """
        Args:
            num_ctrl (int): the number of control qubit.
            name (str): name of the gate.
        """
        if num_ctrl < 0:
            raise ValueError(f"num_ctrl cannot be smaller than 0 but given {num_ctrl}.")

        targ_rot_map = {"ry": CRy, "rz": CRz, "u1": CU1}
        if targ_rot_mode not in targ_rot_map:
            raise ValueError(f"targ_rot_mode requires to be in {list(targ_rot_map.keys())} but given {targ_rot_mode}")

        R_targ = targ_rot_map[targ_rot_mode]

        super().__init__(name)

        self._ctrl_reg = list(range(num_ctrl))
        self._anci = [num_ctrl]
        self._targ = [num_ctrl + 1]

        if num_ctrl == 0:
            ID | self(self._anci)
            if targ_rot_mode == "ry":
                Ry(theta) | self(self._targ)
            elif targ_rot_mode == "rz":
                Rz(theta) | self(self._targ)
            elif targ_rot_mode == "u1":
                U1(theta) | self(self._targ)
            self.set_ancilla(self._anci)
            return

        if num_ctrl > 0 and num_ctrl < 5:
            ID | self(self._anci)
            MCRWithoutAux(
                num_ctrl=num_ctrl,
                theta=theta,
                targ_rot_mode=targ_rot_mode
            ) | self(self._ctrl_reg + self._targ)
            self.set_ancilla(self._anci)
            return

        rest_num_ctrl = num_ctrl - 4
        len_first = (rest_num_ctrl + 1) // 2
        len_second = rest_num_ctrl - len_first

        c_rest_first = list(range(4, 4 + len_first))
        c_rest_second = list(range(4 + len_first, 4 + len_first + len_second))

        # step 1. O(1) part for the recursion
        self._cnx(ctrl=4) | self(self._ctrl_reg[:4] + self._anci)

        # step 2. divide into half recursivly
        upper_left = self._build_left(num_ctrl=len_first)
        lower_left = self._build_left(num_ctrl=len_second)

        ul_targ_anci = [[], []]
        ll_targ_anci = [[], []]
        if upper_left is not None:
            ul_targ_anci[0].append(0)
            if len(upper_left.ancilla_qubits) > 0:
                ul_targ_anci[1].append(1)
        if lower_left is not None:
            ll_targ_anci[0].append(2)
            if len(lower_left.ancilla_qubits) > 0:
                ll_targ_anci[1].append(3)

        for i in ul_targ_anci + ll_targ_anci:
            if len(i) > 0:
                X | self(*i)

        if upper_left is not None:
            upper_left | self(c_rest_first + ul_targ_anci[1] + ul_targ_anci[0])
        if lower_left is not None:
            lower_left | self(c_rest_second + ll_targ_anci[1] + ll_targ_anci[0])

        #  step 3. Cn-Rot(theta) on the target
        mid_num_ctrl = len(ul_targ_anci[0] + ll_targ_anci[0])

        MCRWithoutAux(
            num_ctrl=mid_num_ctrl + 1,
            theta=theta,
            targ_rot_mode=targ_rot_mode
        ) | self(ul_targ_anci[0] + ll_targ_anci[0] + self._anci + self._targ)

        # step 4. reset control qubits for step 2
        if lower_left is not None:
            lower_left.inverse() | self(c_rest_second + ll_targ_anci[1] + ll_targ_anci[0])
        if upper_left is not None:
            upper_left.inverse() | self(c_rest_first + ul_targ_anci[1] + ul_targ_anci[0])

        for i in ul_targ_anci + ll_targ_anci:
            if len(i) > 0:
                X | self(*i)

        # step 5. reset the ancilla qubit for step 1
        self._cnx(ctrl=4) | self(self._ctrl_reg[:4] + self._anci)

        self.set_ancilla(self._anci)

    def _cnx(self, ctrl: int, reset: bool = True) -> CompositeGate:
        """ O(1) of the recursion depend on this. """
        cg = CompositeGate(f"c{ctrl}x")
        H | cg(ctrl)
        MCRWithoutAux(num_ctrl=ctrl, theta=pi, targ_rot_mode="u1", reset_ctrl=reset) | cg
        H | cg(ctrl)

        return cg

    def _build_left(
        self,
        num_ctrl
    ) -> Union[CompositeGate, None]:
        cg = CompositeGate()

        if num_ctrl == 0:
            return None
        if num_ctrl == 1:
            CX | cg([0, 1])
            return cg
        if num_ctrl == 2:
            RCCX | cg([0, 1, 2])
            return cg
        if num_ctrl in [3, 4]:
            self._cnx(num_ctrl, reset=False) | cg(list(range(num_ctrl + 1)))
            return cg

        base_c = list(range(4))

        rest_num_ctrl = num_ctrl - 4
        len_first = (rest_num_ctrl + 1) // 2
        len_second = rest_num_ctrl - len_first

        c_rest_first = list(range(4, 4 + len_first))
        c_rest_second = list(range(4 + len_first, 4 + len_first + len_second))

        anci = [num_ctrl]
        targ = [num_ctrl + 1]

        # step 1.
        self._cnx(ctrl=4) | cg(base_c + anci)

        # step 2.
        upper_left = self._build_left(num_ctrl=len_first)
        lower_left = self._build_left(num_ctrl=len_second)

        ul_targ_anci = [[], []]
        ll_targ_anci = [[], []]
        if upper_left is not None:
            ul_targ_anci[0].append(0)
            if len(upper_left.ancilla_qubits) > 0:
                ul_targ_anci[1].append(1)
        if lower_left is not None:
            ll_targ_anci[0].append(2)
            if len(lower_left.ancilla_qubits) > 0:
                ll_targ_anci[1].append(3)

        for i in ul_targ_anci + ll_targ_anci:
            if len(i) > 0:
                X | cg(*i)

        if upper_left is not None:
            upper_left | cg(c_rest_first + ul_targ_anci[1] + ul_targ_anci[0])
        if lower_left is not None:
            lower_left | cg(c_rest_second + ll_targ_anci[1] + ll_targ_anci[0])

        #  step 3.
        mid_num_ctrl = len(ul_targ_anci[0] + ll_targ_anci[0])

        self._cnx(ctrl=mid_num_ctrl + 1) | cg(ul_targ_anci[0] + ll_targ_anci[0] + anci + targ)

        cg.set_ancilla(anci)

        return cg
