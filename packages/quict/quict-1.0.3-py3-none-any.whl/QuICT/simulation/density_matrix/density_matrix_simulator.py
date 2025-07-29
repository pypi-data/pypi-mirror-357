from typing import Union
from collections import defaultdict
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate
from QuICT.core.noise import NoiseModel
from QuICT.core.operator import NoiseGate
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.core.utils import GateType, matrix_product_to_circuit, CircuitMatrix
from QuICT.simulation.utils import GateSimulator
from QuICT.tools.exception.core import TypeError
from QuICT.tools.exception.simulation import SampleBeforeRunError


class DensityMatrixSimulator:
    """ The Density Matrix Simulator """
    @property
    def density_matrix(self):
        return self._density_matrix

    @property
    def device(self) -> str:
        return self._gate_calculator.device

    def __init__(
        self,
        device: str = "CPU",
        precision: str = "double",
        accumulated_mode: bool = False,
        hidden_empty_qubits: bool = False,
        ignore_last_measure: bool = True,
    ):
        """
        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision, one of [single, double]. Defaults to "double".
            accumulated_mode (bool): If True, calculated density matrix with Kraus Operators in NoiseGate.
                if True, p = \\sum Ki p Ki^T.conj(). Default to be False.
            hidden_empty_qubits (bool, optional): Whether ignore the empty qubits or not, default to False.
        """
        self._device = device
        self._precision = precision
        self._gate_calculator = GateSimulator(device, precision, enable_gfunc=True)
        self._circuit_matrix_helper = CircuitMatrix(device, precision)
        self._accumulated_mode = accumulated_mode
        self._density_matrix = None
        self._quantum_machine = None
        self._hidden_empty_qubits = hidden_empty_qubits
        self._ignore_last_measure = ignore_last_measure

    def initial_circuit(self, circuit: Circuit):
        """ Initial the qubits, quantum gates and state vector by given quantum circuit. """
        self._origin_circuit = circuit
        self._circuit = circuit if self._quantum_machine is None else self._quantum_machine.transpile(
            circuit, self._accumulated_mode
        )
        self._qubits = int(circuit.width())
        self._used_qubits = self._circuit._gates.qubits
        if self._hidden_empty_qubits and self._qubits != len(self._used_qubits):
            self._qubits = len(self._circuit._gates.qubits)
            self._circuit = self._circuit.to_compositegate() & list(range(self._qubits))

    def run(
        self,
        circuit: Circuit,
        quantum_state: np.ndarray = None,
        quantum_machine_model: Union[NoiseModel, VirtualQuantumMachine] = None,
        use_previous: bool = False
    ) -> np.ndarray:
        """ Simulating the given circuit through density matrix simulator.

        Args:
            circuit (Circuit): The quantum circuit.
            density_matrix (np.ndarray): The initial density matrix.
            quantum_machine_model (NoiseModel, optional): The NoiseModel contains NoiseErrors. Defaults to None.
            use_previous (bool, optional): Using the previous state vector. Defaults to False.

        Returns:
            np.ndarray: the density matrix after simulating
        """
        # Deal with the Physical Machine Model
        self._quantum_machine = None
        if quantum_machine_model is not None:
            noise_model = quantum_machine_model if isinstance(quantum_machine_model, NoiseModel) else \
                NoiseModel(quantum_machine_info=quantum_machine_model)
            if not noise_model.is_ideal_model():
                self._quantum_machine = noise_model

        # Initial Quantum Circuit
        self.initial_circuit(circuit)

        # Initial Density Matrix
        if quantum_state is not None:
            self._gate_calculator.validate_density_matrix(quantum_state)
            self._density_matrix = self._gate_calculator.normalized_matrix(quantum_state.copy(), self._qubits)
        elif (self._density_matrix is None or not use_previous):
            if not (quantum_machine_model is None or noise_model.is_ideal_model()):
                self._density_matrix = self._gate_calculator.get_allzero_density_matrix(self._qubits)

        if quantum_machine_model is None or noise_model.is_ideal_model():
            self._run_like_sv(self._circuit)
        else:
            self._run(self._circuit)

        return self._density_matrix

    def _run_like_sv(self, circuit: Circuit):
        # Start simulator
        if not self._ignore_last_measure:
            pipeline, self._measured_q_order = circuit.flatten_gates(True), None
        else:
            pipeline, self._measured_q_order = circuit.gates_without_last_measure()

        sv = self._gate_calculator.get_allzero_state_vector(self._qubits)
        idx = 0
        while idx < len(pipeline):
            gate = pipeline[idx]
            idx += 1
            if not isinstance(gate, BasicGate):
                raise TypeError("DensityMatrixSimulation.run.circuit", "[CompositeGate, BasicGate]". type(gate))

            gate_type = gate.type
            qidxes = gate.cargs + gate.targs
            if gate_type == GateType.measure:
                result = self._gate_calculator.apply_measure_gate(
                    self._qubits - 1 - qidxes[0], sv, self._qubits
                )
                self._circuit.qubits[self._qubits - 1 - qidxes[0]].measured = int(result)
            elif gate_type == GateType.reset:
                self._gate_calculator.apply_reset_gate(
                    self._qubits - 1 - qidxes[0], sv, self._qubits
                )
            elif self.device == "GPU" and gate_type == GateType.unitary and len(qidxes) >= 3:
                self._gate_calculator.apply_large_unitary_matrix(
                    gate.get_matrix(self._gate_calculator.precision), qidxes, sv, self._qubits
                )
            else:
                self._gate_calculator.apply_gate(gate, qidxes, sv, self._qubits)

        self._density_matrix = self._gate_calculator.get_density_matrix_from_state_vector(sv)

    def _run(self, noised_circuit: Circuit):
        # Start simulator
        combined_gates = []
        if not self._ignore_last_measure:
            gate_list = noised_circuit.decomposition_gates()
        else:
            gate_list, self._measured_q_order = noised_circuit.gates_without_last_measure(True)

        for gate in gate_list:
            # Store continuous BasicGates into cgate
            if isinstance(gate, BasicGate) and gate.type not in [GateType.measure, GateType.kraus]:
                combined_gates.append(gate)
                continue

            self.apply_gates(combined_gates)
            combined_gates = []

            if gate.type == GateType.measure:
                self.apply_measure(gate.targ)
            elif isinstance(gate, NoiseGate):
                self.apply_noise(gate)
            elif gate.type == GateType.kraus:
                self.apply_kraus(gate)
            else:
                raise TypeError("DensityMatrixSimulator.run.circuit", "[BasicGate, NoiseGate]", type(gate))

        self.apply_gates(combined_gates)

    def apply_gates(self, combined_gates: list):
        r""" Simulating Circuit with BasicGates

        $$ D = M*D*M^\dagger $$

        where M is the unitary matrix of given quantum gates.

        Args:
            combined_gates (list): The list of quantum gates.
        """
        if len(combined_gates) == 0:
            return

        cir_matrix = self._circuit_matrix_helper.get_unitary_matrix(combined_gates, self._qubits)
        self._density_matrix = self._gate_calculator.dot(
            self._gate_calculator.dot(cir_matrix, self._density_matrix),
            cir_matrix.conj().T
        )

    def apply_noise(self, noise_gate: NoiseGate):
        """ Simulating NoiseGate.

        $$ D = \sum_{i \in Kraus} K_i*D*K_i^\dagger $$

        Where Kraus is the group of Kraus Matrix from the Noise Gate.

        Args:
            noise_gate (NoiseGate): The NoiseGate
        """
        gate_args = noise_gate.targs
        noised_matrix = self._gate_calculator.get_empty_density_matrix(self._qubits)
        for kraus_matrix in noise_gate.noise_matrix:
            umat = matrix_product_to_circuit(kraus_matrix, gate_args, self._qubits, self._device)
            noised_matrix += self._gate_calculator.dot(
                self._gate_calculator.dot(umat, self._density_matrix),
                umat.conj().T
            )

        self._density_matrix = noised_matrix.copy()

    def apply_kraus(self, kraus: BasicGate):
        """ Applying the damping noise's Kraus Matrix.

        Args:
            kraus (BasicGate): The Kraus Gate.
        """
        gate_args = kraus.targs
        noised_matrix = self._gate_calculator.get_empty_density_matrix(self._qubits)
        kraus_matrix = kraus.matrix
        umat = matrix_product_to_circuit(kraus_matrix, gate_args, self._qubits, self._device)

        noised_matrix += self._gate_calculator.dot(
            self._gate_calculator.dot(umat, self._density_matrix),
            umat.conj().T
        )

        self._density_matrix = noised_matrix

    def apply_measure(self, index: int):
        """ Simulating the MeasureGate.

        Args:
            index (int): The index of measured qubit.
        """
        _1, self._density_matrix = self._gate_calculator.apply_measure_gate_for_dm(
            index, self._density_matrix, self._qubits
        )
        if self._quantum_machine is not None:
            _1 = self._quantum_machine.apply_readout_error(index, int(_1))

        self._origin_circuit.qubits[index].measured = _1

    def _to_state_vector(self):
        """ get State Vector from Density Matrix. """
        state_vec = None
        cur_max_norm = 0
        for i in range(0, 1 << self._qubits):
            col_vec = self._density_matrix[:, i]
            # This norm is just the norm of the current col's common (one-of-amplitude)* factor
            norm = np.linalg.norm(col_vec)
            if norm > cur_max_norm:
                state_vec = col_vec / norm
                cur_max_norm = norm

        return state_vec

    def get_sampling_probability(self, target_qubits: list = None, extra_output: bool = False) -> dict:
        assert (self._circuit is not None), \
            SampleBeforeRunError("StateVectorSimulation sample without run any circuit.")

        target_qubits = self._regularized_target_qubits(target_qubits)
        state_vector = self._to_state_vector()
        sv_prob = self._gate_calculator.get_probability_for_state_vector(state_vector, self._qubits, target_qubits)

        if extra_output:
            normalize_prob = {}
            target_qnum = len(target_qubits) if target_qubits is not None else self._qubits
            for i in range(sv_prob.size):
                if not np.isclose(sv_prob[i], 0):
                    binary_idx = "{0:0b}".format(i).zfill(target_qnum)
                    normalize_prob[binary_idx] = float(sv_prob[i])

            return normalize_prob

        return sv_prob

    def get_noised_sampling_probability(self, sample_dict: dict):
        total_shots = np.sum(list(sample_dict.values()))
        normalized_prob = defaultdict(float)
        for key, value in sample_dict.items():
            normalized_prob[key] = value / total_shots

        return normalized_prob

    def sample(
        self,
        shots: int = 1,
        target_qubits: list = None,
        extra_output: bool = False,
        seed: int = -1
    ) -> dict:
        """ Sample the current circuit and return the sample result of measured, please call simulator.run() before.

        Args:
            shots (int): The sample times.
            target_qubits (list): The List of target sample qubits.
            extra_output (bool): Output with extra info: measured qubits (list), and samples (list)

        Returns:
            list: The list of counts of measured result.
        """
        assert (self._density_matrix is not None), \
            SampleBeforeRunError("DensityMatrixSimulator sample without run any circuit.")
        if self._quantum_machine is None:
            return self._sample_with_pure_state(shots, target_qubits, extra_output, seed=seed)

        if self._accumulated_mode:
            original_dm = self._density_matrix.copy()

        sample_qubits = self._regularized_target_qubits(target_qubits)
        if sample_qubits is None:
            sample_qubits = list(range(self._qubits))

        state_dict, sample_result = defaultdict(int), []
        for _ in range(shots):
            final_state = 0
            for m_id in sample_qubits:
                measured, self._density_matrix = self._gate_calculator.apply_measure_gate_for_dm(
                    m_id, self._density_matrix, self._qubits, seed=seed
                )
                final_state <<= 1
                final_state += int(measured)

            final_state = self._quantum_machine.apply_readout_error(sample_qubits, final_state)

            sample_result.append(final_state)
            state_dict[final_state] += 1
            if self._accumulated_mode:
                self._density_matrix = original_dm.copy()
            else:
                self._density_matrix = self._gate_calculator.get_allzero_density_matrix(self._qubits)
                noised_circuit = self._quantum_machine.transpile(self._origin_circuit, self._accumulated_mode) \
                    if self._quantum_machine is not None else self._circuit

                self._run(noised_circuit)

        if not extra_output:
            return state_dict
        else:
            normalize_res, normalize_qorder, normalize_sample = self._sample_normalize(
                state_dict, sample_result, sample_qubits
            )

            return normalize_res, normalize_qorder, normalize_sample

    def _regularized_target_qubits(self, target_qubits: list = None) -> list:
        if target_qubits is None:
            if self._ignore_last_measure and len(self._measured_q_order) > 0:
                target_qubits = self._measured_q_order
            else:
                return None

        qubit_list = list(range(self._qubits)) if not self._hidden_empty_qubits else self._used_qubits
        for tqubit in target_qubits:
            assert tqubit in qubit_list, f"The given qubit {tqubit} not in current circuit."

        if self._hidden_empty_qubits:
            target_qubits = [self._used_qubits.index(tq) for tq in target_qubits]

        return target_qubits

    def _sample_with_pure_state(
        self,
        shots: int,
        target_qubits: list = None,
        extra_output: bool = False,
        seed: int = -1
    ) -> dict:
        state_dict = defaultdict(int)
        target_qubits = self._regularized_target_qubits(target_qubits)
        state_vector = self._to_state_vector()
        sample_result = self._gate_calculator.sample_for_statevector_cdf(
            shots, self._qubits, state_vector, target_qubits, seed=seed
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
            target_qnum = self._qubits
            normalize_qorder = [f"Q{qidx}" for qidx in range(self._qubits)]
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
