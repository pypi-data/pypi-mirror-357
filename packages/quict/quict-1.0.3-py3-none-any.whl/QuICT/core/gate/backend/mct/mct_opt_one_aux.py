from typing import Union
from QuICT.core.gate import CompositeGate, ID, X, CX, CCX, RCCX, H
from ..mcrot.mcr_opt_one_aux import MCROptWithOneAux

from numpy import pi


class MCTOptWithOneAux(CompositeGate):
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
        name: str = None
    ):
        """
        Args:
            num_ctrl (int): the number of control qubit.
            name (str): name of the gate.
        """
        if num_ctrl < 0:
            raise ValueError(f"num_ctrl cannot be smaller than 0 but given {num_ctrl}.")

        super().__init__(name)

        self._ctrl_reg = list(range(num_ctrl))
        self._anci = [num_ctrl]
        self._targ = [num_ctrl + 1]

        if num_ctrl == 0:
            ID | self(self._anci)
            X | self(self._targ)
            self.set_ancilla(self._anci)
            return

        if num_ctrl == 1:
            ID | self(self._anci)
            CX | self(self._ctrl_reg + self._targ)
            self.set_ancilla(self._anci)
            return

        if num_ctrl == 2:
            ID | self(self._anci)
            CCX | self(self._ctrl_reg + self._targ)
            self.set_ancilla(self._anci)
            return

        H | self(self._targ)
        MCROptWithOneAux(
            num_ctrl=num_ctrl,
            theta=pi,
            targ_rot_mode="u1"
        ) | self(self._ctrl_reg + self._anci + self._targ)
        H | self(self._targ)

        self.set_ancilla(self._anci)
