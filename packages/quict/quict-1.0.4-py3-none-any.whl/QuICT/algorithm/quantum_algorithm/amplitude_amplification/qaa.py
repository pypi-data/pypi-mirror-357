from typing import Optional, Dict
from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X, H, CX, CCX, GPhase
from QuICT.core.gate.backend import MCZOneAux
from QuICT.algorithm.tools import QRegManager, QubitAligner
from QuICT.simulation.state_vector import StateVectorSimulator

from QuICT.tools.logger import Logger
import numpy as np


class AmplitudeAmplification:
    """ Quantum Amplitude Amplificaiton.

    Qubit Arrangement:
    |work_bits>
    |ancilla>

    References:
        [1]: Brassard, Gilles, Peter Hoyer, Michele Mosca, and Alain Tapp. “Quantum Amplitude Amplification
          and Estimation,” 305:53-74, 2002. https://doi.org/10.1090/conm/305/05215.
    """

    def __init__(
        self,
        work_bits: int,
        targ_phase_flip: CompositeGate,
        work_state_prep: Optional[CompositeGate] = None,
        zero_phase_flip: Optional[CompositeGate] = None
    ) -> None:
        r"""
        Args:
            work_bits (int): The number of qubits required for the quantum state, in which the amplitude is
                about to be amplified.
            targ_phase_flip (CompositeGate): The oracle for flipping targets phases: I - 2\sum_x{|x><x|}.
            work_state_prep (CompositeGate | None): Optional initial state preparation gate. A default euqally
                superposition gate, $H^{\otimes n}$, will be used if not provided.
            zero_phase_flip (CompositeGate | None): Optional flip-around-zero-state gate: I - 2|0><0|. Will use
                a default method if not provided.
        """
        if work_bits < 2:
            raise ValueError(f"work_bits can not be less than 2, but given {work_bits}.")

        self._work_bits = work_bits
        self._oracle = targ_phase_flip

        if work_state_prep is None:
            self._work_state_prep = self._default_state_prep(work_bits)
        else:
            self._work_state_prep = work_state_prep

        if zero_phase_flip is None:
            self._zero_phase_flip = self._default_phase_flip(work_bits)
        else:
            self._zero_phase_flip = zero_phase_flip

        # Allocate qubits
        reg_manager = QRegManager()
        num_ancilla = reg_manager.ancilla_num(
            [self._oracle, self._work_state_prep, self._zero_phase_flip]
        )
        self._work_reg = reg_manager.alloc(work_bits)
        self._ancilla_reg = reg_manager.alloc(num_ancilla)
        self._total_qubits = reg_manager.allocated

        # Get input composite gates' application indices
        gate_mapper = QubitAligner(self._work_reg, self._ancilla_reg)
        self._o_reg = gate_mapper.getMap(self._oracle)
        self._sp_reg = gate_mapper.getMap(self._work_state_prep)
        self._zFlip_reg = gate_mapper.getMap(self._zero_phase_flip)

    def circuit(
        self,
        iteration: int,
        include_phase: bool = False
    ) -> Circuit:
        """ Construct the quantum amplitude amplification circuit
        Args:
            iteration (int): Number of times to apply the amplify operator Q in the circuit.
            include_phase (bool): When set to `True`, the circuit will include the global -1 phase
                in Q = -A * S_0 * A^(-1) * O.

        Returns:
            Circuit: the QAA circuit.
        """
        qaa_circ = Circuit(self._total_qubits)

        self._work_state_prep | qaa_circ(self._sp_reg)

        Q_it = self._iteration_op(include_phase)
        for _ in range(iteration):
            Q_it | qaa_circ

        return qaa_circ

    def run(
        self,
        iteration: int,
        include_phase: bool = False,
        backend=StateVectorSimulator(),
        shots: int = 1
    ) -> Dict[str, int]:
        """ Construct and run the quantum amplitude amplification circuit.
        Args:
            iteration (int): Number of times to apply the amplify operator Q in the circuit.
            include_phase (bool): When set to `True`, the circuit will include the global -1 phase
                in Q = -A * S_0 * A^(-1) * O.
            backend (Any): A device to run the qaa circuit.
            shots (int): Number of runs for the circuit.
        """
        qaa_circ = self.circuit(iteration, include_phase)

        final_sv = backend.run(qaa_circ)
        final_density_diag = (final_sv * final_sv.conj()).real
        traced_diag = np.sum(
            final_density_diag.reshape(
                (1 << len(self._work_reg), 1 << len(self._ancilla_reg))
            ),
            axis=1
        )

        if backend.device == "GPU":
            traced_diag = traced_diag.get()

        sample_array = np.random.choice(a=len(traced_diag), p=traced_diag, size=shots)
        unique, counts = np.unique(sample_array, return_counts=True)

        measure_dict = {}
        for i in range(len(unique)):
            key_str = np.binary_repr(unique[i], width=len(self._work_reg))
            measure_dict[key_str] = counts[i]

        return measure_dict

    def _iteration_op(self, include_phase: bool = False) -> CompositeGate:
        """ Build Iteration operator Q = A * S_0 * A^(-1) * O """
        cg = CompositeGate(name="Q")

        if include_phase:
            GPhase(np.pi) | cg(0)
        self._oracle | cg(self._o_reg)
        self._work_state_prep.inverse() | cg(self._sp_reg)
        self._zero_phase_flip | cg(self._zFlip_reg)
        self._work_state_prep | cg(self._sp_reg)

        cg.set_ancilla(self._ancilla_reg)

        return cg

    def _default_state_prep(self, reg_size: int) -> CompositeGate:
        """ Default state preparation gate when work_state_prep is not provided. """
        if reg_size < 1:
            raise ValueError(f"Register size has to be positive but given: {reg_size}.")

        cg = CompositeGate(name="A")

        for i in range(reg_size):
            H | cg(i)

        return cg

    def _default_phase_flip(self, reg_size: int) -> CompositeGate:
        """ Default phase flip gate when zero_phase_flip is not provided. """
        if reg_size < 2:
            raise ValueError(f"Register size has to be positive but given: {reg_size}.")

        cg = CompositeGate(name="S_0")

        for i in range(reg_size):
            X | cg(i)

        MCZOneAux(reg_size - 1) | cg

        for i in range(reg_size):
            X | cg(i)

        if reg_size > 3:
            cg.set_ancilla([reg_size])

        return cg
