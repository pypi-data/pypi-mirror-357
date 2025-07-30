from typing import Dict

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate
from ..amplitude_amplification import AmplitudeAmplification
from ..phase_estimation import PhaseEstimation, IterativePhaseEstimation
from QuICT.simulation.state_vector import StateVectorSimulator
from numpy import pi, sin

from typing import Literal

_QpeMethod = Literal["normal", "iterative"]


class AmplitudeEstimation:
    """Amplitude Estimation Method

    Reference:
        [1]: Brassard, Gilles, Peter Hoyer, Michele Mosca, and Alain Tapp. “Quantum Amplitude Amplification and
            Estimation,” 305:53-74, 2002. https://doi.org/10.1090/conm/305/05215.

    """

    _QPE_METHDOS = {"normal": PhaseEstimation, "iterative": IterativePhaseEstimation}

    def __init__(
        self,
        precision_bits: int,
        work_bits: int,
        targ_phase_flip: CompositeGate,
        work_state_prep: CompositeGate,
        qpe_method: _QpeMethod = "normal"
    ):
        r"""
        Args:
            precision_bits (int): Number of qubits for the amplitude.
            work_bits (int): Number of qubits required for the target state.
            targ_phase_flip (CompositeGate): The oracle for flipping phase of the target state whoes amplitude is
                about to be estimated.
            work_state_prep (CompositeGate): The state preparation gate that generate the state which contains the
                amplitude to be estimated.
            qpe_method (str): Quantum phase estimation implementation to be used when constructing
                the order finding circuit, choose from "normal" and "iterative".
        """
        if qpe_method not in ["normal", "iterative"]:
            raise ValueError(f"QPE method must be one of [\"normal\", \"iterative\"], but given {qpe_method}.")

        self._precision_bits = precision_bits
        self._work_bits = work_bits
        self._work_state_prep = work_state_prep

        self._amp_amplify = AmplitudeAmplification(
            work_bits=work_bits,
            targ_phase_flip=targ_phase_flip,
            work_state_prep=work_state_prep
        )

        self._qpe = self._QPE_METHDOS[qpe_method]
        self._qpe_algo = None

    def circuit(self) -> Circuit:
        """ Construct the amplitude estimation circuit.

        Return: Circuit, the amplitude estimation circuit.
        """
        if self._qpe_algo is not None:
            return self._qpe_algo.circuit()

        q_op = self._amp_amplify._iteration_op(include_phase=True)
        c_q_op = q_op.controlled()

        self._qpe_algo = self._qpe(
            precision_bits=self._precision_bits,
            work_bits=self._work_bits,
            control_unitary=c_q_op,
            work_state_prep=self._work_state_prep
        )

        return self._qpe_algo.circuit()

    def run(
        self,
        backend=StateVectorSimulator(ignore_last_measure=False),
        shots: int = 1
    ) -> Dict[str, int]:
        """ Run the amplitude estimation circuit and get the sampling result

        Args:
            backend (Any): a backend to run the qpe circuit.
            shots (int): number of times to run the circuit.

        Return: Dict[str, int]: a pair representing the sampling result in binary string with its number of count.
        """
        if self._qpe_algo is None:
            self.circuit()

        return self._qpe_algo.run(backend, shots, decode_as_float=False)

    @staticmethod
    def decode_to_amplitude_norm(bit_str: str) -> float:
        """ Decode the bit string got sampled from the circuit to norm of the disired amplitude

        Args:
            bit_str (str): the binary string got from running the amplitude estimation.

        Returns:
            float, norm of the amplitude.
        """
        angle = int(bit_str, base=2) / (1 << len(bit_str)) * pi

        return sin(angle)

    @staticmethod
    def decode_to_prob(bit_str: str) -> float:
        """ Decode the bit string got sampled from the circuit to the probability of getting the disired state.

        Args:
            bit_str (str): the binary string got from running the amplitude estimation.

        Returns:
            float, probability of getting the disired state.
        """
        angle = int(bit_str, base=2) / (1 << len(bit_str)) * pi

        return sin(angle) ** 2
