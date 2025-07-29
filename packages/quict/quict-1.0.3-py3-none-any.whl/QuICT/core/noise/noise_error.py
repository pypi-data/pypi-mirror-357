from __future__ import annotations
from itertools import product
import numpy as np
from typing import List, Tuple

from .utils import NoiseChannel
from QuICT.core.gate import ID, X, Y, Z, Kraus, BasicGate, CompositeGate
from QuICT.tools.exception.core import (
    TypeError, ValueError, PauliNoiseUnmatchedError, DamplingNoiseMixedProbExceedError
)


class NoiseGate:
    @property
    def qubit_number(self) -> int:
        return self._gate.width()

    @property
    def qubits(self) -> list:
        return self._gate.qubits

    @property
    def gates(self) -> CompositeGate:
        return self._gate

    def __init__(self, qubits: int, gates: List[Tuple[BasicGate, List[int]]]):
        self._qubits = qubits
        self._gate = self._build_gate(gates) if isinstance(gates, list) else gates

    def _build_gate(self, gates: List):
        noise_gate = CompositeGate()
        for q_gates, q_idx in gates:
            q_gates | noise_gate(q_idx)

        return noise_gate

    def append(self, gate: BasicGate, qubit: list):
        assert isinstance(gate, BasicGate)
        gate | self._gate(qubit)

    def compose(self, other_gate: NoiseGate):
        other_gate.gates | self._gate
        self._gate.flatten()

    def tensor(self, other_gate: NoiseGate):
        target_qubits = [self.qubit_number + i for i in range(other_gate.qubit_number)]
        other_gate.gates | self._gate(target_qubits)
        self._gate.flatten()

    def copy(self):
        _ngate = NoiseGate(self.qubit_number, self._gate.copy())

        return _ngate

    def matrix(self):
        return self.gates.matrix()


class QuantumNoiseError:
    """ The based class for quantum noise error.

    Example:
        quantum_error = QuantumNoiseError([(error_matrix1, 0.4), (error_matrix2, 0.6)])

    Args:
        ops (List[Tuple(error_matrix: np.ndarray, prob: float)]): The noise error operators, the sum of
            the probabilities should be 1.
    """
    @property
    def operators(self):
        """ The noise error's matrix. """
        return self._operators

    @property
    def type(self):
        """ The type of noise error. """
        return self._type

    @type.setter
    def type(self, channel: NoiseChannel):
        assert isinstance(channel, NoiseChannel), TypeError("QuantumNoiseError.type", "NoiseChannel", type(channel))
        self._type = channel

    @property
    def qubits(self):
        """ The number of qubits. """
        return self._qubits

    def __init__(self, ops: List[Tuple[NoiseGate, float]]):
        assert isinstance(ops, list), TypeError("QuantumNoiseError.ops", "list", type(ops))

        # Initial NoiseGate and probability
        self._operators = ops
        self._qubits = self._operators[0][0].qubit_number
        self._type = NoiseChannel.unitary

    def __str__(self):
        ne_str = f"{self.type.value} with {self.qubits} qubits.\n"
        for prob, nm in enumerate(self._operators):
            ne_str += f"Noise with probability {prob}: {nm}\n"

        return ne_str

    def compose(self, other):
        """ generate composed noise error with self and other. """
        assert isinstance(other, QuantumNoiseError), TypeError(
            "QuantumNoiseError.compose", "QuantumNoiseError", type(other)
        )

        if self.qubits >= other.qubits:
            left_operator, right_operator = self.operators, other.operators
        else:
            left_operator, right_operator = other.operators, self.operators

        composed_ops = []
        for noise_gate, prob in left_operator:
            for other_noise_gate, other_prob in right_operator:
                _new_gate = noise_gate.copy()
                _new_gate.compose(other_noise_gate)
                composed_ops.append((_new_gate, prob * other_prob))

        return QuantumNoiseError(composed_ops)

    def tensor(self, other):
        """ generate tensor noise error with self and other. """
        assert isinstance(other, QuantumNoiseError), TypeError(
            "QuantumNoiseError.tensor", "QuantumNoiseError", type(other)
        )

        tensor_ops = []
        for noise_gate, prob in self.operators:
            for other_noise_gate, other_prob in other.operators:
                _new_gate = noise_gate.copy()
                _new_gate.tensor(other_noise_gate)
                tensor_ops.append((_new_gate, prob * other_prob))

        return QuantumNoiseError(tensor_ops)

    def to_matrix(self) -> list:
        """ generate kraus operator with given gate's matrix. """
        all_matrix = []
        for ngate, prob in self.operators:
            matrix = ngate.matrix()
            all_matrix.append(np.sqrt(prob) * matrix)

        return all_matrix

    def prob_mapping_operator(self, prob: float) -> CompositeGate:
        """ Return the related noise error's matrix with given probability.
        The given probability should within [0, 1].
        """
        for ngate, error_prob in self._operators:
            if prob <= error_prob:
                return ngate.gates

            prob -= error_prob

        return None


class PauliError(QuantumNoiseError):
    """ Pauli Error; Including Bit Flip and Phase Flip

    Example:
        PauliError([('i', 0.3), ('x', 0.7)])

    Args:
        ops (List[Tuple[str, float]]): The operators for pauli error.
        num_qubits (int): The number of target qubits. Defaults to 1.
    """
    _BASED_GATE = {
        'i': ID,
        'x': X,
        'y': Y,
        'z': Z
    }

    def __init__(self, ops: List[Tuple[str, float]], num_qubits: int = 1):
        if not isinstance(ops, (list, tuple)):
            raise TypeError("PauliError.ops", "[list, tuple]", type(ops))

        # Building noise error operators List[(pauli_matrix, prob)].
        operators, sum_prob = [], 0
        for op, prob in ops:
            sum_prob += prob
            if prob < 0 or prob > 1:
                raise ValueError("PauliError.ops.prob", "[0, 1]", prob)

            op = op.ljust(num_qubits, 'i')
            if len(op) > num_qubits:
                raise PauliNoiseUnmatchedError("Pauli Error get wrong input.")

            gates = []
            for idx, g in enumerate(op):
                if g not in list(self._BASED_GATE.keys()):
                    raise ValueError("PauliError.ops", "[i, x, y, z]", g)

                gates.append((self._BASED_GATE[g], [idx]))

            operators.append((NoiseGate(num_qubits, gates), prob))

        # Initial PauilError
        super().__init__(operators)
        self._origin_ops = ops
        self.type = NoiseChannel.pauil


class BitflipError(PauliError):
    """ Special Case for PauilError, with fixed Pauil Operator:
        [('x', prob), ('i', 1 - prob)]

    Args:
        prob (float): The probability to flip the qubit.
    """
    def __init__(self, prob: float):
        ops = [('i', 1 - prob), ('x', prob)]

        super().__init__(ops)


class PhaseflipError(PauliError):
    """ Special Case for PauilError, with fixed Pauil Operator:
        [('z', prob), ('i', 1 - prob)]

    Args:
        prob (float): The probability of fliping the phase.
    """
    def __init__(self, prob: float):
        ops = [('i', 1 - prob), ('z', prob)]

        super().__init__(ops)


class PhaseBitflipError(PauliError):
    """ Special Case for PauilError, with fixed Pauil Operator:
        [('y', prob), ('i', 1 - prob)]

    Args:
        prob (float): The probability of fliping the qubit and phase.
    """
    def __init__(self, prob: float):
        ops = [('i', 1 - prob), ('y', prob)]

        super().__init__(ops)


class DepolarizingError(PauliError):
    """ The Depolarizing Error

    Args:
        prob (float): The probability of depolarizing.
        num_qubits (int, optional): The number of qubits have depolarizing error. Defaults to 1.
    """
    def __init__(self, prob: float, num_qubits: int = 1):
        if not isinstance(prob, float):
            raise TypeError("DepolarizingError.prob", "float", type(prob))

        if not isinstance(num_qubits, int):
            raise TypeError("DepolarizingError.number_qubits", "int", type(prob))

        assert num_qubits >= 1, ValueError("DepolarizingError.num_qubits", ">= 1", num_qubits)
        num_ops = 4 ** num_qubits
        max_prob = num_ops / (num_ops - 1)
        if prob < 0 or prob > max_prob:
            raise ValueError("DepolarizingError.prob", f"[0, {max_prob}]", prob)

        probs = [1 - prob / max_prob] + [prob / num_ops] * (num_ops - 1)
        ops = [''.join(i) for i in product(self._BASED_GATE.keys(), repeat=num_qubits)]

        super().__init__(list(zip(ops, probs)), num_qubits)
        self.type = NoiseChannel.depolarizing


class DampingError(QuantumNoiseError):
    """ Amplitude Damping, Phase Damping and Amp-Phase Damping

        a = amp, b = phase, p = state prob \n
        A0 = sqrt(1 - p1) * [[1, 0], [0, sqrt(1 - a - b)]] \n
        A1 = sqrt(1 - p1) * [[0, sqrt(a)], [0, 0]] \n
        A2 = sqrt(1 - p1) * [[0, 0], [0, sqrt(b)]] \n
        B0 = sqrt(p1) * [[sqrt(1 - a - b), 0], [0, 1]] \n
        B1 = sqrt(p1) * [[0, 0], [sqrt(a), 0]] \n
        B2 = sqrt(p1) * [[sqrt(b), 0], [0, 0]] \n

    Args:
        amplitude_prob (float): The probability for damping amplitude.
        phase_prob (float): The probability for damping phase.
        dissipation_state (float, optional): The dissipation states. Defaults to 0.0.
    """
    def __init__(self, amplitude_prob: float, phase_prob: float, dissipation_state: float = 0.0):
        assert amplitude_prob >= 0 and amplitude_prob <= 1, ValueError(
            "DampingError.amplitude_prob", "[0, 1]", amplitude_prob
        )
        assert phase_prob >= 0 and phase_prob <= 1, ValueError("DampingError.phase_prob", "[0, 1]", phase_prob)
        assert dissipation_state >= 0 and dissipation_state <= 1, ValueError(
            "DampingError.dissipation_state", "[0, 1]", dissipation_state
        )

        if amplitude_prob + phase_prob > 1:
            raise DamplingNoiseMixedProbExceedError("the sum of amplitude and phase damping prob <= 1.")

        self.amplitude_prob = amplitude_prob
        self.phase_prob = phase_prob
        self.dissipation_state = dissipation_state

        ops = self._create_kraus_ops()
        super().__init__(ops)
        self._origin_ops = ops
        self.type = NoiseChannel.damping

    def __str__(self):
        damp_noise = f"{self.type.value} with 1 qubit\n"
        if self.amplitude_prob != 0:
            damp_noise += f"amplitude damping prob: {self.amplitude_prob} "

        if self.phase_prob != 0:
            damp_noise += f"phase damping prob: {self.phase_prob} "

        if self.dissipation_state != 0:
            damp_noise += f"prob of stable state: {self.dissipation_state}"

        return damp_noise

    def _create_kraus_ops(self):
        """ Create damping Kraus operators. """
        m0, m1 = np.sqrt(1 - self.dissipation_state), np.sqrt(self.dissipation_state)
        sqrt_amp, sqrt_phase = np.sqrt(self.amplitude_prob), np.sqrt(self.phase_prob)
        sqrt_ap = np.sqrt(1 - self.amplitude_prob - self.phase_prob)

        k0 = m0 * np.array([[1, 0], [0, sqrt_ap]], dtype=np.complex128)
        k1 = m0 * np.array([[0, sqrt_amp], [0, 0]], dtype=np.complex128)
        k2 = m0 * np.array([[0, 0], [0, sqrt_phase]], dtype=np.complex128)
        k3 = m1 * np.array([[sqrt_ap, 0], [0, 1]], dtype=np.complex128)
        k4 = m1 * np.array([[0, 0], [sqrt_amp, 0]], dtype=np.complex128)
        k5 = m1 * np.array([[sqrt_phase, 0], [0, 0]], dtype=np.complex128)
        kraus = [k0, k1, k2, k3, k4, k5]

        probs = [a * b for a, b in product(
            [1 - self.dissipation_state, self.dissipation_state],
            [1 - self.amplitude_prob - self.phase_prob, self.amplitude_prob, self.phase_prob]
        )]
        ops = []
        for idx, prob in enumerate(probs):
            if prob != 0:
                ngate = Kraus(kraus[idx])
                ops.append((NoiseGate(1, [(ngate, 0)]), prob))

        return ops

    def to_matrix(self) -> list:
        """ generate kraus operator with given gate's matrix. """
        all_matrix = []
        for ngate, _ in self.operators:
            matrix = ngate.matrix()
            all_matrix.append(matrix)

        return all_matrix
