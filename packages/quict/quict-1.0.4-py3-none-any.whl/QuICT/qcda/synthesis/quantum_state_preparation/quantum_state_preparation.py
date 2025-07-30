from typing import Union, List
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import (
    CompositeGate, DiagonalGate, GateType, GPhase, X, CX, Ry, Rz,
    H, S, S_dagger, CRy, CRz, CCX, Swap, MultiControlToffoli
)
from QuICT.core.gate.backend import MCTWithoutAux, UniformlyRotation
from QuICT.qcda.synthesis.unitary_decomposition import UnitaryDecomposition
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.tools import Logger

_logger = Logger("QuantumStatePreparation")


class QuantumStatePreparation(object):
    r"""
    For a given quantum state $|\psi\rangle$, create a CompositeGate $C$ that $|\psi\rangle = C |0\rangle$

    Choose the method between the references, designing circuit of quantum state preparation
    with uniformly gates, unitary decomposition and diagnal gates respectively

    Reference:
        [1] `Transformation of quantum states using uniformly controlled rotations`
        <https://arxiv.org/abs/quant-ph/0407010>

        [2] `Quantum-state preparation with universal gate decompositions`
        <https://arxiv.org/abs/1003.5760>

    Examples:
        >>> from QuICT.qcda.synthesis import QuantumStatePreparation
        >>> QSP = QuantumStatePreparation('uniformly_gates')
        >>> gates = QSP.execute(state_vector)

        >>> from QuICT.qcda.synthesis import QuantumStatePreparation
        >>> QSP = QuantumStatePreparation('unitary_decomposition')
        >>> gates = QSP.execute(state_vector)

    """
    _logger = _logger

    def __init__(
        self,
        method: str = 'unitary_decomposition',
        keep_phase: bool = False,
        ancilla: int = 0,
        opt: bool = True,
    ):
        """
        Args:
            method (str, optional): chosen method in
                ['uniformly_gates', 'unitary_decomposition'],
                Please note that if you select method 'unary_transformation',
                then please pass in the state_vector with all real number coefficient when using execute(),
                otherwise the method will be invalid and automatically transferred to method 'unary_diagonal_joint'.
            keep_phase (bool, optional): whether to keep the global phase as a GPhase gate in the output
            ancilla (int, optional): the number of ancillary qubits m
            opt (bool, optional): optimizer switch for 'diagonal_gates', enabled by default
        """
        assert method in [
            'uniformly_gates',
            'unitary_decomposition',
        ], ValueError('Invalid quantum state preparation method')
        self.method = method
        self.keep_phase = keep_phase
        self.ancilla = ancilla
        if self.method not in ['diagonal_gates'] and self.ancilla != 0:
            self._logger.warn(
                "Now only 'diagonal_gates' methods can make use of ancilla qubits."
            )
        self.opt = opt

    def execute(self, state_vector: np.ndarray) -> CompositeGate:
        """
        Quantum state preparation with the chosen method

        Args:
            state_vector (np.ndarray): the statevector to be prepared

        Returns:
            CompositeGate: the preparation CompositeGate
        """
        # Ref: [1] <https://arxiv.org/abs/quant-ph/0407010>
        if self.method == 'uniformly_gates':
            return self._with_uniformly_gates(state_vector)

        # Ref: [2] <https://arxiv.org/abs/1003.5760>
        if self.method == 'unitary_decomposition':
            return self._with_unitary_decomposition(state_vector)

    def _with_uniformly_gates(self, state_vector: np.ndarray) -> CompositeGate:
        """
        Quantum state preparation with uniformly gates

        Args:
            state_vector (np.ndarray): the statevector to be prepared

        Returns:
            CompositeGate: the preparation CompositeGate

        Reference:
            https://arxiv.org/abs/quant-ph/0407010
        """
        state_vector = np.array(state_vector).astype(complex)
        num_qubits = int(round(np.log2(state_vector.size)))
        assert state_vector.ndim == 1 and 1 << num_qubits == state_vector.size,\
            ValueError('Quantum state should be an array with length 2^n')

        gates = CompositeGate()
        omega = np.angle(state_vector)
        state_vector = np.abs(state_vector)
        # Now for the non-negative real state_vector
        URy = UniformlyRotation(GateType.ry)
        denominator = np.linalg.norm(state_vector)
        for k in range(num_qubits - 1, -1, -1):
            numerator = np.linalg.norm(state_vector.reshape(1 << num_qubits - k, 1 << k), axis=1)
            alpha = np.where(np.isclose(denominator, 0), 0, 2 * np.arcsin(numerator[1::2] / denominator))
            gates.extend(URy.execute(alpha))
            denominator = numerator
        # If state_vector is real and non-negative, no UniformlyRz will be needed.
        URz = UniformlyRotation(GateType.rz)
        if not np.allclose(omega, 0):
            for k in range(num_qubits):
                alpha = np.sum(omega.reshape(1 << num_qubits - k, 1 << k), axis=1)
                alpha = (alpha[1::2] - alpha[0::2]) / (1 << k)
                gates.extend(URz.execute(alpha))
            if self.keep_phase:
                gates.append(GPhase(np.average(omega)) & gates.qubits[0])

        return gates

    def _with_unitary_decomposition(self, state_vector: np.ndarray) -> CompositeGate:
        """
        Quantum state preparation with unitary decomposition

        Args:
            state_vector (np.ndarray): the statevector to be prepared

        Returns:
            CompositeGate: the preparation CompositeGate

        Reference:
            https://arxiv.org/abs/1003.5760
        """
        state_vector = np.array(state_vector).astype(complex)
        num_qubits = int(round(np.log2(state_vector.size)))
        assert state_vector.ndim == 1 and 1 << num_qubits == state_vector.size,\
            ValueError('Quantum state should be an array with length 2^n')

        first_half = num_qubits // 2 if np.mod(num_qubits, 2) == 0 else (num_qubits - 1) // 2
        last_half = num_qubits - first_half
        state_vector = state_vector.reshape(1 << first_half, 1 << last_half)
        # Schmidt decomposition
        U, d, V = np.linalg.svd(state_vector)

        gates = CompositeGate()
        # Phase 1
        gates.extend(self._with_uniformly_gates(d))
        # Phase 2
        with gates:
            for i in range(first_half):
                CX & [i, i + first_half]
        UD = UnitaryDecomposition(include_phase_gate=self.keep_phase)
        # Phase 3
        U_gates, _ = UD.execute(U)
        gates.extend(U_gates)
        # Phase 4
        if np.mod(num_qubits, 2) != 0:
            V = V[np.arange(1 << last_half).reshape(2, 1 << last_half - 1).T.flatten()]
        V_gates, _ = UD.execute(V.T)
        V_gates & list(range(first_half, num_qubits))
        gates.extend(V_gates)

        return gates
