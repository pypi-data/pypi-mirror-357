from typing import List
import numpy as np

from QuICT.core.gate import CompositeGate, Ry, Rz, U1, CRy, CRz, CU1


class MCRWithoutAux(CompositeGate):
    """ A Multi control rotation gate.

    References:
        `Linear-Depth Quantum Circuits for n-qubit Toffoli gates with no Ancilla`
        <https://arxiv.org/abs/1303.3557>
    """
    def __init__(
        self,
        num_ctrl: int,
        theta: float,
        targ_rot_mode: str = "ry",
        ctrl_rot_mode: str = "ry",
        reset_ctrl: bool = True,
        name: str = None
    ):
        """ Construct a multi-controlled rotation gate currently support ry and rz to be controlled.

        Args:
            num_ctrl (int): the number of control bit.
            theta (float): the angle for the rotation.
            targ_rot_mode (str): rotation gate to be applied on the target qubit.
            ctrl_rot_mode (str): rotation gate to be applied on the contrl qubit.
            reset_ctrl (bool): If `True` the control bits will be reset to original states after the
                target rotation is applied.
        """
        if num_ctrl < 0:
            raise ValueError(f"num_ctrl requires to be non-negative but given {num_ctrl}")
        targ_rot_map = {"ry": CRy, "rz": CRz, "u1": CU1}
        ctrl_rot_map = {"ry": CRy}
        if targ_rot_mode not in targ_rot_map:
            raise ValueError(f"targ_rot_mode requires to be in {list(targ_rot_map.keys())} but given {targ_rot_mode}")
        if ctrl_rot_mode not in ctrl_rot_map:
            raise ValueError(f"ctrl_rot_mode requires to be in {list(ctrl_rot_map.keys())} but given {ctrl_rot_mode}")

        # ctrl_rot = self._crx
        R_targ = targ_rot_map[targ_rot_mode]
        R_ctrl = ctrl_rot_map[ctrl_rot_mode]

        super().__init__(name)
        if num_ctrl == 0:
            if targ_rot_mode == "ry":
                Ry(theta) | self(0)
            elif targ_rot_mode == "rz":
                Rz(theta) | self(0)
            elif targ_rot_mode == "u1":
                U1(theta) | self(0)
            return

        if num_ctrl == 1:
            R_targ(theta) | self([0, 1])
            return

        for ctrl in reversed(range(1, num_ctrl)):
            R_targ(theta / (1 << (num_ctrl - ctrl))) | self([ctrl, num_ctrl])
            for targ in range(num_ctrl - 1, ctrl, -1):
                R_ctrl(np.pi / (1 << (targ - ctrl))) | self([ctrl, targ])

        R_targ(theta / (1 << (num_ctrl - 1))) | self([0, num_ctrl])
        for targ in range(num_ctrl - 1, 0, -1):
            R_ctrl(np.pi / (1 << (targ - 1))) | self([0, targ])

        for ctrl in range(1, num_ctrl):
            for targ in range(ctrl + 1, num_ctrl):
                R_ctrl(-np.pi / (1 << (targ - ctrl))) | self([ctrl, targ])
            R_targ(-theta / (1 << (num_ctrl - ctrl))) | self([ctrl, num_ctrl])

        if not reset_ctrl:
            return

        for ctrl in reversed(range(1, num_ctrl)):
            for targ in range(num_ctrl - 1, ctrl, -1):
                R_ctrl(np.pi / (1 << (targ - ctrl))) | self([ctrl, targ])

        for targ in range(num_ctrl - 1, 0, -1):
            R_ctrl(-np.pi / (1 << (targ - 1))) | self([0, targ])

        for ctrl in range(1, num_ctrl):
            for targ in range(ctrl + 1, num_ctrl):
                R_ctrl(-np.pi / (1 << (targ - ctrl))) | self([ctrl, targ])
