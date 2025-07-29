from typing import *
import numpy as np

from scipy.linalg import cossin
from QuICT.core import *
from QuICT.core.gate import *
from QuICT.core.gate.backend import UniformlyRotation
from .cartan_kak_decomposition import CartanKAKDecomposition
from .cartan_kak_diagonal_decomposition import CartanKAKDiagonalDecomposition
from .uniformly_ry_revision import UniformlyRyRevision
from .utility import *
from QuICT.tools import Logger


class UnitaryDecomposition(object):
    """
    Transform a general unitary matrix into CX gates and single qubit gates.

    References:
        [1] `Synthesis of Quantum Logic Circuits`
        <https://arxiv.org/abs/quant-ph/0406176>

        [2] `Constructive quantum Shannon decomposition from Cartan involutions`
        <https://arxiv.org/abs/0806.4015>

        [3] `Minimal Universal Two-qubit Quantum Circuits`
        <https://arxiv.org/abs/quant-ph/0308033>

        [4] `Optimal quantum circuits for general two-qubit gates`
        <https://arxiv.org/abs/quant-ph/0308006>

    Examples:
        1.use the method of uniformly_rotation by default
        >>> from QuICT.qcda.synthesis import UnitaryDecomposition
        >>> UD = UnitaryDecomposition()
        >>> gates, _ = UD.execute(mat)
        2.use the method of diagonal_gate
        >>> from QuICT.qcda.synthesis import UnitaryDecomposition
        >>> UD = UnitaryDecomposition(method='diagonal_gate')
        >>> gates, _ = UD.execute(mat)
    """
    _logger = Logger("UnitaryDecomposition")

    def __init__(
            self,
            method: str = 'uniformly_rotation',
            include_phase_gate: bool = False,
            recursive_basis: int = 2,
            ancilla: int = 0,
            opt: bool = False
    ):
        """
        Args:
            method (str, optional): chosen method in ['uniformly_rotation', 'diagonal_gate']
            If you choose the method of 'diagonal_gate', please pay attention to the ancilla and opt.
            include_phase_gate (bool): Whether to include a phase gate to keep synthesized gate matrix the same
                as input. If set False, the output gates might have a matrix which has a factor shift to input:
                np.allclose(<matrix_of_return_gates> * factor, <input_matrix>).
            recursive_basis (int): Terminate recursion at which level. It could be set as 1 or 2, which would stop
                recursion when matrix is 2 or 4, respectively. When set as 2, the final step is done by KAK
                decomposition. Correctness of this algorithm is never influenced by recursive_basis.
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
                "methods can decompose unitary matrix. Please choose "
                "the correct method."
            )

    def execute(self, mat: np.ndarray) -> Union[Tuple[CompositeGate, None], Tuple[CompositeGate, complex]]:
        """
        Args:
            mat (np.ndarray): Unitary matrix.

        Returns:
            Union[Tuple[CompositeGate, None], Tuple[CompositeGate, complex]]: If self.include_phase_gate==False,
            this function returns synthesized gates and a shift factor. Otherwise a tuple like (<gates>, None)
            is returned.
        """
        qubit_num = int(round(np.log2(mat.shape[0])))
        mat = mat.astype(complex)

        """
        After adding KAK diagonal optimization, inner built gates would have a
        leading diagonal gate not decomposed. If our first-level recursion is
        2-bit, using older version of KAK is OK.
        """

        if qubit_num == 2 and self.recursive_basis == 2:
            CKD = CartanKAKDecomposition()
            gates = CKD.execute(mat)
            syn_mat = gates.matrix()
            shift = shift_ratio(mat, syn_mat)
            if self.include_phase_gate:
                gates = add_factor_shift_into_phase(gates, shift)
                return gates, None
            else:
                return gates, shift

        if self.method == 'uniformly_rotation':
            gates, shift = self.inner_utrans_build_gate(
                mat=mat,
                method=self.method,
                recursive_basis=self.recursive_basis,
                keep_left_diagonal=False,
            )

        if self.method == 'diagonal_gate':
            gates, shift = self.inner_utrans_build_gate(
                mat=mat,
                method=self.method,
                recursive_basis=self.recursive_basis,
                keep_left_diagonal=False,
                use_cz_ry=False
            )

        if self.recursive_basis == 2 and self.include_phase_gate:
            gates = add_factor_shift_into_phase(gates, shift)
        if self.include_phase_gate:
            return gates, None
        else:
            return gates, shift

    def inner_utrans_build_gate(
        self,
        mat: np.ndarray,
        method: str = 'uniformly_rotation',
        recursive_basis: int = 1,
        keep_left_diagonal: bool = False,
        use_cz_ry: bool = True,
    ) -> Tuple[CompositeGate, complex]:
        mat: np.ndarray = np.array(mat)
        mat_size: int = mat.shape[0]
        qubit_num = int(round(np.log2(mat_size)))
        gates = CompositeGate()
        _kak = CartanKAKDiagonalDecomposition() if keep_left_diagonal else CartanKAKDecomposition()

        if method == 'diagonal_gate':
            use_cz_ry = False

        if qubit_num == 1:
            u = Unitary(mat) & 0
            _ret = CompositeGate(gates=[u])
            return _ret, 1.0 + 0.0j
        elif qubit_num == 2 and recursive_basis == 2:
            gates = _kak.execute(mat)
            syn_mat = gates.matrix()
            shift = shift_ratio(mat, syn_mat)
            return gates, shift

        u, angle_list, v_dagger = cossin(mat, mat_size // 2, mat_size // 2, separate=True)

        """
        Parts of following comments are from Scipy documentation
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.cossin.html)
                                   ┌                   ┐
                                   │ I  0  0 │ 0  0  0 │
        ┌           ┐   ┌         ┐│ 0  C  0 │ 0 -S  0 │┌         ┐*
        │ X11 │ X12 │   │ U1 │    ││ 0  0  0 │ 0  0 -I ││ V1 │    │
        │ ────┼──── │ = │────┼────││─────────┼─────────││────┼────│
        │ X21 │ X22 │   │    │ U2 ││ 0  0  0 │ I  0  0 ││    │ V2 │
        └           ┘   └         ┘│ 0  S  0 │ 0  C  0 │└         ┘
                                   │ 0  0  I │ 0  0  0 │
                                   └                   ┘

        Both u and v are controlled unitary operations hence can be
        decomposed into 2 (smaller) unitary operations and 1 controlled rotation.
        """

        # Dynamically import to avoid circulation.
        from .controlled_unitary import ControlledUnitaryDecomposition

        shift: complex = 1.0

        # (c,s\\s,c)
        angle_list *= 2  # Ry use its angle as theta/2
        if use_cz_ry:
            URyRevision = UniformlyRyRevision(is_cz_left=False)  # keep CZ at right side
            reversed_ry = URyRevision.execute(angle_list)
            reversed_ry & [(i + 1) % qubit_num for i in range(qubit_num)]
        else:
            if method == 'uniformly_rotation':
                URy = UniformlyRotation(GateType.ry)
                reversed_ry = URy.execute(angle_list)
                reversed_ry & [(i + 1) % qubit_num for i in range(qubit_num)]
            if method == 'diagonal_gate':
                reversed_ry, dg_list = diagonal_ury_gate(
                    angle_list,
                    self.ancilla,
                    self.opt,
                    self.include_phase_gate
                )

                real_qunum = int(np.floor(np.log2(len(angle_list)))) + 1
                ancilla_num = len(dg_list) - real_qunum

                if ancilla_num == 0:
                    reversed_ry & [(i + 1) % qubit_num for i in range(qubit_num)]
                else:
                    reversed_ry & (
                        [(i + 1) % real_qunum for i in range(real_qunum)]
                        + [qubit_num + i for i in range(ancilla_num)]
                    )

        """
        Now, gates have CZ gate(s) at it's ending part(the left side of u).
        Left gate of u is right multiplied to u in matrix view.
        If qubit_num > 2, we would have reversed_ry[-1] as a CZ affecting on (0, 1),
        while reversed_ry[-2] a CZ on (0, qubit_num - 1).
        If qubit_num == 2, there would only be one CZ affecting on (0, 1).
        """

        # u
        u1: np.ndarray = u[0]
        u2: np.ndarray = u[1]

        if use_cz_ry:
            reversed_ry.flatten()
            reversed_ry.pop()  # CZ on (0,1)
            # This CZ affects 1/4 last columns of the matrix of U, or 1/2 last columns of u2.
            _u_size = u2.shape[0]
            for i in range(_u_size // 2, _u_size):
                u2[:, i] = -u2[:, i]

            if qubit_num > 2:
                reversed_ry.flatten()
                reversed_ry.pop()  # CZ on (0, qubit_num - 1)
                # For similar reasons, this CZ only affect 2 parts of matrix of U.
                for i in range(_u_size - _u_size // 4, _u_size):
                    u1[:, i] = - u1[:, i]
                    u2[:, i] = - u2[:, i]

        CUD = ControlledUnitaryDecomposition()
        u_gates, _shift = CUD.inner_cutrans_build_gate(
            u1=u1,
            u2=u2,
            recursive_basis=recursive_basis,
            keep_left_diagonal=True,
        )
        shift *= _shift

        # v_dagger

        """
        Now, leftmost gate decompose by u is a diagonal gate on (n-2, n-1), which
        is commutable with reversed_ry. That gate is in right side of v_dagger, so
        it would be left multiplied to v_dagger.
        """
        v1_dagger = v_dagger[0]
        v2_dagger = v_dagger[1]

        if recursive_basis == 2:
            u_gates.flatten()
            forwarded_d_gate: BasicGate = u_gates.pop(0)
            forwarded_mat = forwarded_d_gate.matrix
            for i in range(0, mat_size // 2, 4):
                for k in range(4):
                    v1_dagger[i + k, :] *= forwarded_mat[k, k]
                    v2_dagger[i + k, :] *= forwarded_mat[k, k]

        v_dagger_gates, _shift = CUD.inner_cutrans_build_gate(
            u1=v1_dagger,
            u2=v2_dagger,
            recursive_basis=recursive_basis,
            keep_left_diagonal=keep_left_diagonal,
        )
        shift *= _shift

        gates = CompositeGate()
        v_dagger_gates | gates
        reversed_ry | gates
        u_gates | gates

        return gates, shift
