from typing import Union
from collections import defaultdict
import numpy as np

from QuICT.core import Circuit, Hamiltonian
from QuICT.core.gate import BasicGate, CompositeGate, H, Rz, Perm
from QuICT.core.noise import NoiseModel
from QuICT.core.operator import Trigger
from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.simulation.utils import GateSimulator
from QuICT.tools.exception.core import TypeError
from QuICT.tools.exception.simulation import SampleBeforeRunError


class StateVectorSimulator:
    """ The simulator for qubits' vector state. """
    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, vec):
        self._vector = self._gate_calculator.normalized_state_vector(vec, self._qubits)

    @property
    def device(self) -> str:
        return self._gate_calculator.device

    @property
    def device_id(self) -> int:
        return self._gate_calculator._gpu_device_id

    @property
    def precision(self) -> Union[np.complex64, np.complex128]:
        return self._gate_calculator._dtype

    def __init__(
        self,
        device: str = "CPU",
        precision: str = "double",
        gpu_device_id: int = 0,
        sync: bool = True,
        hidden_empty_qubits: bool = False,
        ignore_last_measure: bool = True,
    ):
        """
        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision for the state vector, one of [single, double].
                Defaults to "double".
            gpu_device_id (int, optional): The GPU device ID. Defaults to 0.
            sync (bool, optional): Sync mode or Async mode. Defaults to True.
            hidden_empty_qubits (bool, optional): Whether ignore the empty qubits or not, default to False.
        """
        self._gate_calculator = GateSimulator(device, precision, gpu_device_id, sync)
        self._quantum_machine = None
        self._hidden_empty_qubits = hidden_empty_qubits
        self._ignore_last_measure = ignore_last_measure

    def initial_circuit(self, circuit: Circuit):
        """ Initial the qubits, quantum gates and state vector by given quantum circuit. """
        self._origin_circuit = circuit
        self._circuit = circuit if self._quantum_machine is None else self._quantum_machine.transpile(circuit)
        self._qubits = int(circuit.width()) if isinstance(circuit, Circuit) else max(circuit.qubits) + 1
        self._used_qubits = circuit._gates.qubits
        if self._hidden_empty_qubits and self._qubits != len(self._used_qubits):
            self._qubits = len(circuit._gates.qubits)
            if isinstance(circuit, Circuit):
                circuit = circuit.to_compositegate() & list(range(self._qubits))
            else:
                circuit = circuit.copy() & list(range(self._qubits))

        if not self._ignore_last_measure:
            self._pipeline, self._measured_q_order = circuit.gates, None
        else:
            self._pipeline, self._measured_q_order = circuit.gates_without_last_measure()

        self._gate_calculator.gate_matrix_combined(self._circuit)

    def initial_state_vector(self, all_zeros: bool = False):
        """ Initial qubits' vector states. """
        if not all_zeros:
            self._vector = self._gate_calculator.get_allzero_state_vector(self._qubits)
        else:
            self._vector = self._gate_calculator.get_empty_state_vector(self._qubits)

    def run(
        self,
        circuit: Circuit,
        quantum_state: np.ndarray = None,
        quantum_machine_model: Union[NoiseModel, VirtualQuantumMachine] = None,
        use_previous: bool = False
    ) -> np.ndarray:
        """ start simulator with given circuit

        Args:
            circuit (Circuit): The quantum circuits.
            quantum_state (ndarray): The initial quantum state vector.
            quantum_machine_model (Union[NoiseModel, VirtualQuantumMachine]): The model of quantum machine
            use_previous (bool, optional): Using the previous state vector. Defaults to False.

        Returns:
            Union[cp.array, np.array]: The state vector.
        """
        # Deal with the Physical Machine Model
        self._quantum_machine = None
        if quantum_machine_model is not None:
            noise_model = quantum_machine_model if isinstance(quantum_machine_model, NoiseModel) else \
                NoiseModel(quantum_machine_info=quantum_machine_model)
            if not noise_model.is_ideal_model():
                self._quantum_machine = noise_model

        # Initial Quantum Circuit and State Vector
        self.initial_circuit(circuit)
        self._original_state_vector = None
        if quantum_state is not None:
            self._vector = self._gate_calculator.normalized_state_vector(quantum_state.copy(), self._qubits)
            if self._quantum_machine is not None:
                self._original_state_vector = quantum_state.copy()
        elif not use_previous:
            self.initial_state_vector()

        # Apply gates one by one
        self._run()
        return self.vector

    def get_expectations(self, circuit, hamiltonians, quantum_state: np.ndarray = None):
        """ Run the simulator to get expectations.

        Args:
            circuit (Circuit): The quantum circuits.
            hamiltonians (Hamiltonian): The hamiltonians for calculating expectations.
            quantum_state (ndarray, optional): The initial quantum state vector. Defaults to None.

        Returns:
            Union[float, np.ndarray]: The expectations.
            Union[cp.array, np.array]: The state vector.
        """
        hamiltonians = self._check_hamiltonians(hamiltonians)
        expectations = []
        state_vector = self.run(circuit, quantum_state)
        for hamiltonian in hamiltonians:
            ham_circuit_list = hamiltonian.construct_hamilton_circuit(circuit.width())
            coefficients = hamiltonian.coefficients
            grad_vector = self._gate_calculator.get_empty_state_vector(circuit.width())
            for coeff, ham_circuit in zip(coefficients, ham_circuit_list):
                grad_vec = self.run(ham_circuit, state_vector)
                grad_vector += coeff * grad_vec
            expectation = (
                (state_vector.conj() @ grad_vector).real
                if self.device == "CPU"
                else (state_vector.conj() @ grad_vector).real.get()
            )
            expectations.append(expectation)

        return np.array(expectations)

    def _check_hamiltonians(self, hams):
        if isinstance(hams, Hamiltonian):
            hams = [hams]
        if isinstance(hams, list):
            for ham in hams:
                assert isinstance(ham, Hamiltonian), TypeError(
                    "StateVectorSimulator._check_hamiltonians.ham",
                    "Hamiltonian",
                    type(ham),
                )
        else:
            raise TypeError(
                "StateVectorSimulation._check_hamiltonians.hams",
                "[Hamiltonian, List[Hamiltonian]]".type(hams),
            )
        return hams

    def _run(self):
        idx = 0
        while idx < len(self._pipeline):
            gate = self._pipeline[idx]
            idx += 1
            if isinstance(gate, CompositeGate):
                self._apply_compositegate(gate)
            elif isinstance(gate, BasicGate):
                if gate.type == GateType.perm:
                    self._apply_perm_gate(gate)
                else:
                    self._apply_gate(gate)
            elif isinstance(gate, Trigger):
                self._apply_trigger(gate, idx)
            else:
                raise TypeError("StateVectorSimulation.run.circuit", "[CompositeGate, BasicGate, Trigger]". type(gate))

    def _apply_gate(self, gate: BasicGate):
        """ Depending on the given quantum gate, apply the target algorithm to calculate the state vector.

        Args:
            gate (Gate): the quantum gate in the circuit.
        """
        gate_type = gate.type
        qidxes = gate.cargs + gate.targs
        if gate_type == GateType.measure:
            self._apply_measure_gate(self._qubits - 1 - qidxes[0])
        elif gate_type == GateType.measurex:
            self._gate_calculator.apply_gate(H, qidxes, self._vector, self._qubits)
            self._apply_measure_gate(self._qubits - 1 - qidxes[0])
        elif gate_type == GateType.measurey:
            self._gate_calculator.apply_gate(Rz(-np.pi / 2), qidxes, self._vector, self._qubits)
            self._gate_calculator.apply_gate(H, qidxes, self._vector, self._qubits)
            self._apply_measure_gate(self._qubits - 1 - qidxes[0])
        elif gate_type == GateType.reset:
            self._apply_reset_gate(self._qubits - 1 - qidxes[0])
        elif self.device == "GPU" and gate_type in [GateType.unitary] and len(qidxes) >= 3:
            self._gate_calculator.apply_large_unitary_matrix(
                gate.get_matrix(self._gate_calculator.precision), qidxes, self._vector, self._qubits
            )
        elif gate_type == GateType.kraus:
            self._gate_calculator._apply_kraus(gate, qidxes, self._vector, self._qubits)
        else:
            self._gate_calculator.apply_gate(gate, qidxes, self._vector, self._qubits)

    def _apply_perm_gate(self, gate: Perm):
        perm_list = np.array(gate.pargs)
        self._gate_calculator._algorithm.VectorPermutation(self._vector, perm_list, changeInput=True)

    def _apply_compositegate(self, gate: CompositeGate):
        """ Depending on the given quantum gate, apply the target algorithm to calculate the state vector.

        Args:
            gate (Gate): the quantum gate in the circuit.
        """
        for cgate in gate.gates:
            if isinstance(cgate, CompositeGate):
                self._apply_compositegate(cgate)
            else:
                self._apply_gate(cgate)

    def _apply_trigger(self, op: Trigger, current_idx: int) -> CompositeGate:
        """ Deal with the Operator <Trigger>.

        Args:
            op (Trigger): The operator Trigger
            current_idx (int): the index of Trigger in Circuit
        """
        qidxes = []
        for targ in op.targs:
            index = self._qubits - 1 - targ
            self._apply_measure_gate(index)
            qidxes.append(targ)

        mapping_cgate = op.mapping(int(self._circuit[qidxes]))
        if isinstance(mapping_cgate, CompositeGate):
            if op.position is not None:
                position = op.position + current_idx if isinstance(op.position, int) else \
                    [pos + current_idx for pos in op.position]
            else:
                position = current_idx

            if isinstance(position, int):
                assert position >= current_idx, "The trigger's position must after itself."
                self._pipeline = self._pipeline[:position] + mapping_cgate.gates + \
                    self._pipeline[position:]
            else:
                for pos in position[::-1]:
                    assert pos >= current_idx, "The trigger's position must after itself."
                    self._pipeline = self._pipeline[:pos] + mapping_cgate.gates + self._pipeline[pos:]

    def _apply_measure_gate(self, qidx):
        result = self._gate_calculator.apply_measure_gate(qidx, self._vector, self._qubits)
        if self._quantum_machine is not None:
            result = self._quantum_machine.apply_readout_error(qidx, result)

        self._circuit.qubits[self._qubits - 1 - qidx].measured = int(result)

    def _set_measured_prob(self, qidx) -> float:
        prob = self._gate_calculator.get_measured_prob(qidx, self._vector, self._qubits)
        self._circuit.qubits[qidx].probability = prob

        return prob

    def _apply_reset_gate(self, qidx):
        self._gate_calculator.apply_reset_gate(qidx, self._vector, self._qubits)

    def _apply_pauliZ_measure(self, qidxes: list, vector):
        results = []
        for qidx in qidxes:
            result = self._gate_calculator.apply_pauliZ_measure(self._qubits - 1 - qidx, vector, self._qubits)
            results.append(result)
        return np.array(results)

    def _apply_multiply(self, value: Union[float, np.complex64]):
        """ Deal with Operator <Multiply>

        Args:
            value (Union[float, complex]): The multiply value apply to state vector.
        """
        from QuICT.ops.gate_kernel.multigpu import float_multiply, complex_multiply

        default_parameters = (self._vector, self._qubits, self._gate_calculator._sync)
        if isinstance(value, float):
            float_multiply(value, *default_parameters)
        else:
            complex_multiply(value, *default_parameters)

    def get_measured_prob(self, index: int, all_measured: bool = False):
        """ Return the probability of measured qubit with given index to be 1

        Args:
            index (int): The given qubit index
            all_measured (bool): Calculate measured probability with all state vector,
                only using with Multi-Node Simulation.
        """
        from QuICT.ops.gate_kernel.gpu import measured_prob_calculate

        return measured_prob_calculate(
            index,
            self._vector,
            self._qubits,
            all_measured=all_measured,
            sync=self._gate_calculator._sync
        )

    def apply_specialgate(self, index: int, type: GateType, prob: float = None):
        """ Apply Measure/Reset gate in to simulator

        Args:
            index (int): The given qubit index
            type (GateType): the gate type of special gate
            prob (float): The given probability of measured the target qubit into 1

        Returns:
            [float]: The target qubit's measured value or reset value, <0 or <1
        """
        from QuICT.ops.gate_kernel.gpu import apply_measuregate, apply_resetgate
        if type == GateType.measure:
            result = int(apply_measuregate(
                index,
                self._vector,
                self._qubits,
                prob,
                self._gate_calculator._sync
            ))
            self._circuit.qubits[self._qubits - 1 - index].measured = result
        elif type == GateType.reset:
            result = apply_resetgate(
                index,
                self._vector,
                self._qubits,
                prob,
                self._gate_calculator._sync
            )

        return result

    def apply_zeros(self):
        """ Set state vector to be zero. """
        self._vector = self._gate_calculator._array_helper.zeros_like(self.vector)

    def get_sampling_probability(self, target_qubits: list = None, extra_output: bool = False) -> dict:
        assert (self._circuit is not None), \
            SampleBeforeRunError("StateVectorSimulation sample without run any circuit.")

        target_qubits = self._regularized_target_qubits(target_qubits)
        sv_prob = self._gate_calculator.get_probability_for_state_vector(self._vector, self._qubits, target_qubits)

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

    def sample(self, shots: int = 1, target_qubits: list = None, extra_output: bool = False, seed: int = -1) -> dict:
        """ Sample the measured result from current state vector, please first run simulator.run().

        Args:
            shots (int): The sample times for current state vector.
            target_qubits (list): The List of target sample qubits.
            extra_output (bool): Output with extra info: measured qubits (list), and samples (list)

        Returns:
            List[int]: The measured result list with length equal to 2 ** self._qubits
        """
        assert (self._circuit is not None), \
            SampleBeforeRunError("StateVectorSimulation sample without run any circuit.")
        target_qubits = self._regularized_target_qubits(target_qubits)
        if self._quantum_machine is not None:
            state_dict, sample_result = self._sample_with_noise(shots, target_qubits, extra_output, seed)
        else:
            state_dict = defaultdict(int)
            sample_result = self._gate_calculator.sample_for_statevector_cdf(
                shots, self._qubits, self._vector, target_qubits, seed=seed
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

    def _sample_with_noise(
        self,
        shots: int,
        target_qubits: list = None,
        extra_output: bool = False,
        seed: int = -1
    ) -> dict:
        total_qubits = list(range(self._qubits))
        target_qubits = self._regularized_target_qubits(target_qubits)

        state_dict, sample_result = defaultdict(int), []
        for _ in range(0, shots):
            final_state = self._gate_calculator.sample_for_statevector_cdf(
                1, self._qubits, self._vector, seed=seed
            )

            # Apply readout noise
            for fstate in final_state:
                fstate = self._quantum_machine.apply_readout_error(total_qubits, fstate)
                state_dict[fstate] += 1
                sample_result.append(fstate)

            # Re-generate noised circuit and initial state vector
            self._vector = self._gate_calculator.get_allzero_state_vector(self._qubits) \
                if self._original_state_vector is None else self._original_state_vector.copy()
            noised_circuit = self._quantum_machine.transpile(self._origin_circuit)
            self._pipeline = noised_circuit.gates
            self._gate_calculator.gate_matrix_combined(noised_circuit)
            self._run()

        if target_qubits is not None:
            state_dict, sample_result = self._partial_sample(state_dict, sample_result, target_qubits)

        if not extra_output:
            return state_dict, sample_result
        else:
            normalize_res, normalize_qorder, normalize_sample = self._sample_normalize(
                state_dict, sample_result, target_qubits
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

    def _partial_sample(self, state_dict: dict, sample_result: list, target_qubits: list) -> dict:
        qubit_list = list(range(self._qubits)) if not self._hidden_empty_qubits else self._used_qubits
        for tqubit in target_qubits:
            assert tqubit in qubit_list, f"The given qubit {tqubit} not in current circuit."

        if self._hidden_empty_qubits:
            target_qubits = [self._used_qubits.index(tq) for tq in target_qubits]

        new_sv, sample_mapping = defaultdict(int), defaultdict(int)
        for key, value in state_dict.items():
            new_key = self._extend_index(key, target_qubits)
            new_sv[new_key] += value
            sample_mapping[key] = new_key

        new_sample = [sample_mapping[s] for s in sample_result]
        return new_sv, new_sample

    def _extend_index(self, index, target_indexes):
        str_idx = "{0:0b}".format(index)
        str_idx = str_idx.zfill(self._qubits)

        new_idx = 0
        for qidx in target_indexes:
            new_idx <<= 1
            if str_idx[qidx] == "1":
                new_idx += 1

        return new_idx
