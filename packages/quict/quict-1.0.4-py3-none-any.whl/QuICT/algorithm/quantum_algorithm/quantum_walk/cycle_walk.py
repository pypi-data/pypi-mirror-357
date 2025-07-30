from typing import Optional, Dict
import numpy as np

from QuICT.core.gate import CompositeGate, H
from QuICT.core import Circuit
from .shift_op import CycleShiftOp
from QuICT.algorithm.tools import QRegManager, QubitAligner
from QuICT.simulation.state_vector import StateVectorSimulator


class CycleWalk:
    """ A quantum walk on a cycle graph. Assuming each node and each direction of the coin is encoded
    as an unsigned binary integer.
    """
    def __init__(
        self,
        node_num: int,
        shift_op: Optional[CompositeGate] = None,
        coin_op: Optional[CompositeGate] = None,
        state_prep: Optional[CompositeGate] = None
    ):
        """
        Args:
            node_num (int): total number of node in the cycle graph.
            shift_op (CompositeGate | None): shift operator for the quantum walk. If not given, a default
                one, S = |x - 1><x|⊗|0><0| + |x + 1><x|⊗|1><1|, will be used.
            coin_op (CompositeGate | None): coin operator for he quantum walk. If not given, a default Hadamard
                coin will be used.
            state_prep (CompositeGate | None): quantum gate that initializes the state on the node register.
        """
        if node_num < 3:
            raise ValueError(f"node_bits can not be less than 3, but given {node_num}.")

        self._node_num = node_num
        self._node_bits = int(np.ceil(np.log2(node_num)))

        if shift_op is None:
            self._shift_op = CycleShiftOp(
                node_num=self._node_num,
                qreg_size=self._node_bits + 1,
                mode="exact",
                name="s_op"
            )
        else:
            self._shift_op = shift_op

        if coin_op is None:
            self._coin_op = CompositeGate(name="H", gates=[H & 0])
        else:
            if max(coin_op.qubits) + 1 - len(coin_op.ancilla_qubits) != 1:
                raise ValueError("Coin's application space larger than one qubit.")
            self._coin_op = coin_op

        self._state_prep = state_prep

        reg_manager = QRegManager()
        num_ancilla = reg_manager.ancilla_num([self._shift_op, self._coin_op, self._state_prep])
        self._node_reg = reg_manager.alloc(self._node_bits)
        self._coin_reg = reg_manager.alloc(1)
        self._ancilla_reg = reg_manager.alloc(num_ancilla)
        self._total_qubits = reg_manager.allocated

        self._s_actex_wo_ctrl = QubitAligner(self._node_reg, self._ancilla_reg).getMap(self._shift_op, fix_top=1)
        self._c_actex = QubitAligner(self._coin_reg, self._ancilla_reg).getMap(self._coin_op)
        if state_prep is not None:
            self._sp_actex = QubitAligner(self._node_reg, self._ancilla_reg).getMap(self._state_prep)

    def circuit(
        self,
        iteration: int
    ) -> Circuit:
        """ Given number of iteration, construct the quantum walk circuit.

        Args:
            iteration (int): Number of walk iteration.

        Returns:
            Circuit: the quantum walk circuit.
        """
        qw_circ = Circuit(self._total_qubits)

        if self._state_prep is not None:
            self._state_prep | qw_circ(self._sp_actex)

        for _ in range(iteration):
            self._coin_op | qw_circ(self._c_actex)
            self._shift_op | qw_circ(self._coin_reg + self._s_actex_wo_ctrl)

        qw_circ.ancilla_qubits = self._ancilla_reg

        return qw_circ

    def run(
        self,
        iteration: int,
        backend=StateVectorSimulator(),
        shots: int = 1
    ) -> Dict[str, int]:
        """ Run the quantum walk on the cycle graph.

        Args:
            iteration (int): Number of walk iteration.
            backend (Any): Device to run the quantum walk.
            shots (int): Number of experiments to run.

        Returns:
            Dict[str, int]: sampling result on the node register of the quantum walk circuit.
        """

        qw_circ = self.circuit(iteration=iteration)

        backend.run(qw_circ)
        sample_res = backend.sample(shots=shots, target_qubits=self._node_reg)

        res_dict = {}
        for key, val in enumerate(sample_res):
            if val != 0:
                res_dict[np.binary_repr(key, width=len(self._node_reg))] = val

        return res_dict
