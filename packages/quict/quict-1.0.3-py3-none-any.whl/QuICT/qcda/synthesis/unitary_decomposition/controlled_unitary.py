from typing import *
import numpy as np

from QuICT.core import *
from QuICT.core.gate import *
from QuICT.core.gate.backend import UniformlyRotation
from .utility import *
from QuICT.tools import Logger


class ControlledUnitaryDecomposition(object):
    _logger = Logger("ControlledUnitaryDecomposition")

    def __init__(self,
                 include_phase_gate: bool = True,
                 recursive_basis: int = 2,
                 method: str = 'uniformly_rotation',
                 ancilla: int = 0,
                 opt: bool = False):
        """
        Args:
            include_phase_gate (bool): Whether to include a phase gate to keep synthesized gate matrix the same
                as input. If set False, the output gates might have a matrix which has a factor shift to input:
                np.allclose(<matrix_of_return_gates> * factor, <input_matrix>).
            recursive_basis (int): Terminate recursion at which level. It could be set as 1 or 2, which would stop
                recursion when matrix is 2 or 4, respectively. When set as 2, the final step is done by KAK
                decomposition.
                Correctness of this algorithm is never influenced by recursive_basis.
            method (str, optional): chosen method in ['uniformly_rotation', 'diagonal_gate']
            If you choose the method of 'diagonal_gate', please pay attention to the ancilla and opt.
            ancilla (int):the number of ancillary qubits when the method is 'diagonal_gate'
            opt (bool): the switch of cnot optimizer when the method is 'diagonal_gate'
        """

        self.include_phase_gate = include_phase_gate
        self.recursive_basis = recursive_basis
        self.method = method
        self.ancilla = ancilla
        self.opt = opt
        if self.method not in ['uniformly_rotation', 'diagonal_gate']:
            self._logger.warn(
                "Only 'uniformly_rotation' and 'diagonal_gate' "
                "methods can decompose controlled unitary matrix. "
                "Please choose the correct method."
            )

    def execute(
            self,
            u1: np.ndarray,
            u2: np.ndarray
    ) -> Union[Tuple[CompositeGate, None], Tuple[CompositeGate, complex]]:
        """
        Transform a controlled-unitary matrix into CX gates and single qubit gates.
        A controlled-unitary is a block-diagonal unitary. Parameter u1 and u2 are
        the block diagonals.

        Args:
            u1 (np.ndarray): Upper-left block diagonal.
            u2 (np.ndarray): bottom-right block diagonal.

        Returns:
            Union[Tuple[CompositeGate, None], Tuple[CompositeGate, complex]]: If self.inlclude_phase_gate==False,
                this function returns synthesized gates and a shift factor. Otherwise a tuple like (<gates>, None)
                is returned.
        """
        gates, shift = self.inner_cutrans_build_gate(u1, u2, self.recursive_basis, method=self.method)
        if self.include_phase_gate:
            gates = add_factor_shift_into_phase(gates, shift)
            return gates, None
        else:
            return gates, shift

    def _i_tensor_unitary(
        self,
        u: np.ndarray,
        recursive_basis: int,
        keep_left_diagonal: bool = False,
    ) -> Tuple[CompositeGate, complex]:
        """
        Transform (I_{2x2} tensor U) into gates. The 1st bit
        is under the identity transform.

        Args:
            u (np.ndarray): A unitary matrix.

        Returns:
            Tuple[CompositeGate, complex]: Synthesized gates and a phase factor.
        """

        gates: CompositeGate
        shift: complex
        # Dynamically import to avoid circulation.
        from .unitary_decomposition import UnitaryDecomposition
        UD = UnitaryDecomposition()
        gates, shift = UD.inner_utrans_build_gate(
            mat=u,
            recursive_basis=recursive_basis,
            keep_left_diagonal=keep_left_diagonal
        )
        new_qubits = [q + 1 for q in gates.qubits]
        gates & new_qubits

        return gates, shift

    def inner_cutrans_build_gate(
        self,
        u1: np.ndarray,
        u2: np.ndarray,
        recursive_basis: int = 2,
        keep_left_diagonal: bool = False,
        method: str = 'uniformly_rotation',
    ) -> Tuple[CompositeGate, complex]:
        """
        Build gates from parameterized model without mapping

        Returns:
            Tuple[CompositeGate, complex]: Synthesized gates and factor shift.
        """
        qubit_num = 1 + int(round(np.log2(u1.shape[0])))
        v, d, w = quantum_shannon_decompose(u1, u2)
        shift: complex = 1.0

        # diag(u1, u2) == diag(v, v) @ diag(d, d_dagger) @ diag(w, w)
        # diag(v, v)
        v_gates, _shift = self._i_tensor_unitary(v, recursive_basis, keep_left_diagonal=True)
        shift *= _shift

        # diag(d, d_dagger)
        angle_list = []
        for i in range(d.shape[0]):
            s = d[i, i]
            theta = -2 * np.log(s) / 1j
            angle_list.append(theta)

        angle_list = np.array(angle_list)
        if method == 'uniformly_rotation':
            URz = UniformlyRotation(GateType.rz)
            reversed_rz = URz.execute(angle_list)
            reversed_rz & [(i + 1) % qubit_num for i in range(qubit_num)]

        if method == 'diagonal_gate':
            reversed_rz, dg_list = diagonal_urz_gate(angle_list,
                                                     self.ancilla,
                                                     self.opt,
                                                     self.include_phase_gate)

            real_qunum = int(np.floor(np.log2(len(angle_list)))) + 1
            ancilla_num = len(dg_list) - real_qunum

            if ancilla_num == 0:
                reversed_rz & [(i + 1) % qubit_num for i in range(qubit_num)]
            else:
                reversed_rz & (
                    [(i + 1) % real_qunum for i in range(real_qunum)]
                    + [qubit_num + i for i in range(ancilla_num)]
                )

        # diag(w, w)
        if recursive_basis == 2:
            v_gates.flatten()
            forwarded_d_gate: BasicGate = v_gates.pop(0)
            forwarded_mat = forwarded_d_gate.matrix
            for i in range(0, w.shape[0], 4):
                for k in range(4):
                    w[i + k, :] *= forwarded_mat[k, k]

        w_gates, _shift = self._i_tensor_unitary(w, recursive_basis, keep_left_diagonal=keep_left_diagonal)
        shift *= _shift

        gates = CompositeGate()
        w_gates | gates
        reversed_rz | gates
        v_gates | gates

        return gates, shift
