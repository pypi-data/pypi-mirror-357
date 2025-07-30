from typing import Union
from collections import defaultdict
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate
from QuICT.simulation.utils import GateSimulator
from QuICT.tools.exception.core import ValueError
from QuICT.tools.exception.simulation import SampleBeforeRunError


class UnitarySimulator():
    """ Algorithms to calculate the unitary matrix of a quantum circuit, and simulate. """
    @property
    def vector(self):
        return self._vector

    @property
    def device(self):
        return self._gate_calculator.device

    def __init__(
        self,
        device: str = "CPU",
        precision: str = "double",
        hidden_empty_qubits: bool = False,
        ignore_last_measure: bool = True,
    ):
        """
        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision for the unitary matrix. Defaults to "double".
            hidden_empty_qubits (bool, optional): Whether ignore the empty qubits or not, default to False.
        """
        assert device in ["CPU", "GPU"], ValueError("UnitarySimulation.device", "[CPU, GPU]", device)
        self._device = device
        assert precision in ["single", "double"], \
            ValueError("UnitarySimulation.precision", "[single, double]", precision)
        self._precision = precision
        self._gate_calculator = GateSimulator(self._device, self._precision)
        self._vector = None
        self._hidden_empty_qubits = hidden_empty_qubits
        self._ignore_last_measure = ignore_last_measure

    def run(
        self,
        circuit: Union[np.ndarray, Circuit],
        quantum_state: np.ndarray = None,
        use_previous: bool = False
    ) -> np.ndarray:
        """ Simulation by given unitary matrix or circuit

        Args:
            circuit (Union[np.ndarray, Circuit]): The unitary matrix or the circuit for simulation
            quantum_state (ndarray): The initial quantum state vector.
            use_previous (bool, optional): whether using previous state vector. Defaults to False.

        Returns:
            np.ndarray: The state vector after simulation
        """
        # Step 1: Generate the unitary matrix of the given circuit
        if isinstance(circuit, (Circuit, CompositeGate)):
            self._qubits_num = circuit.width()
            self._used_qubits = circuit._gates.qubits
            circuit.precision = self._precision
            if self._hidden_empty_qubits and self._qubits_num != len(circuit._gates.qubits):
                self._qubits_num = len(circuit._gates.qubits)
                if isinstance(circuit, Circuit):
                    circuit = circuit.to_compositegate() & list(range(self._qubits_num))
                else:
                    circuit & list(range(self._qubits_num))

            self._unitary_matrix = circuit.matrix(self._device)
        else:
            row = circuit.shape[0]
            self._qubits_num = int(np.log2(row))
            self._unitary_matrix = self._gate_calculator.normalized_matrix(circuit, self._qubits_num)
            self._ignore_last_measure = False
            self._hidden_empty_qubits = False

        if self._ignore_last_measure:
            _, self._measured_q_order = circuit.gates_without_last_measure()

        # Step 2: Prepare the state vector
        self._original_state_vector = None
        if quantum_state is not None:
            self._vector = self._gate_calculator.dot(
                self._unitary_matrix,
                self._gate_calculator.normalized_state_vector(quantum_state, self._qubits_num)
            )
        elif not use_previous:
            self._vector = self._unitary_matrix[:, 0]

        return self._vector

    def sample(self, shots: int = 1, target_qubits: list = None, extra_output: bool = False, seed: int = -1) -> dict:
        """ Sample the measured result from current state vector, please first run simulator.run().

        Args:
            shots (int): The sample times for current state vector.
            target_qubits (list): The List of target sample qubits.
            extra_output (bool): Output with extra info: measured qubits (list), and samples (list)

        Returns:
            List[int]: The measured result list with length equal to 2 ** self._qubits
        """
        assert (self._vector is not None), \
            SampleBeforeRunError("StateVectorSimulation sample without run any circuit.")

        state_dict = defaultdict(int)
        target_qubits = self._regularized_target_qubits(target_qubits)
        sample_result = self._gate_calculator.sample_for_statevector_cdf(
            shots, self._qubits_num, self._vector, target_qubits, seed=seed
        )
        for res in sample_result:
            state_dict[res] += 1

        if not extra_output:
            return state_dict
        else:
            normalize_res, normalize_qorder, normalize_sample = self._sample_normalize(
                state_dict, sample_result, target_qubits
            )

            return normalize_res, normalize_qorder, normalize_sample

    def _sample_normalize(self, state_dict: dict, sample_per_shots: list, target_qubits: list):
        if target_qubits is None:
            target_qnum = self._qubits_num
            normalize_qorder = [f"Q{qidx}" for qidx in range(self._qubits_num)]
        else:
            target_qnum = len(target_qubits)
            normalize_qorder = [f"Q{qidx}" for qidx in target_qubits]

        # Create binary_int mapping
        b_i_mapping, normalize_res = {}, {}
        for key, val in state_dict.items():
            binary_key = "{0:0b}".format(key).zfill(target_qnum)
            normalize_res[binary_key] = val
            b_i_mapping[key] = binary_key[::-1]

        normalize_samples = [b_i_mapping[shot] for shot in sample_per_shots]

        return normalize_res, normalize_qorder, normalize_samples

    def get_sampling_probability(self, target_qubits: list = None, extra_output: bool = False) -> list:
        assert (self._vector is not None), \
            SampleBeforeRunError("StateVectorSimulation sample without run any circuit.")

        target_qubits = self._regularized_target_qubits(target_qubits)
        sv_prob = self._gate_calculator.get_probability_for_state_vector(self._vector, self._qubits_num, target_qubits)

        if extra_output:
            normalize_prob = {}
            target_qnum = len(target_qubits) if target_qubits is not None else self._qubits_num
            for i in range(sv_prob.size):
                if not np.isclose(sv_prob[i], 0):
                    binary_idx = "{0:0b}".format(i).zfill(target_qnum)
                    normalize_prob[binary_idx] = float(sv_prob[i])

            return normalize_prob

        return sv_prob

    def _regularized_target_qubits(self, target_qubits: list = None) -> list:
        if target_qubits is None:
            if self._ignore_last_measure and len(self._measured_q_order) > 0:
                target_qubits = self._measured_q_order
            else:
                return None

        qubit_list = list(range(self._qubits_num)) if not self._hidden_empty_qubits else self._used_qubits
        for tqubit in target_qubits:
            assert tqubit in qubit_list, f"The given qubit {tqubit} not in current circuit."

        if self._hidden_empty_qubits:
            target_qubits = [self._used_qubits.index(tq) for tq in target_qubits]

        return target_qubits
