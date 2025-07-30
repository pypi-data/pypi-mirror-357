import numpy as np
from typing import Union
from collections import defaultdict

from QuICT.ops.utils import LinAlgLoader


class QubitTensor:
    """ The tensor data structure for qubit in MPS simulation. """
    @property
    def tensor_data(self) -> np.ndarray:
        return self._tensor_data

    @tensor_data.setter
    def tensor_data(self, data):
        self._tensor_data = data

    @property
    def ldim(self) -> int:
        """ Return the left dimension. """
        return self._tensor_data.shape[0]

    @property
    def dim(self) -> int:
        """ Return the qubit dimension. """
        return self._tensor_data.shape[1]

    @property
    def rdim(self) -> int:
        """ Return the right dimension. """
        return self._tensor_data.shape[2]

    def __init__(self, state: np.ndarray):
        """
        Args:
            state (np.ndarray): The Tensor data of qubit.
        """
        self._tensor_data = state


class Normalize:
    @property
    def matrix_data(self) -> np.ndarray:
        return self._matrix_data

    @matrix_data.setter
    def matrix_data(self, data):
        self._matrix_data = data

    @property
    def ldim(self) -> int:
        return self._matrix_data.shape[0]

    @property
    def rdim(self) -> int:
        return self._matrix_data.shape[0]

    def __init__(self, norm_coeff: np.ndarray):
        self._matrix_data = norm_coeff


class MPSSiteStructure:
    """ The Structure of Matrix Product State.

    Q0 -- O -- Q1 -- O -- ... -- O -- Qn-1 -- O -- Qn
     |         |                        |           |
     U         U          ...           ----  U  ----
     |         |                        |           |
    Q0`-- O -- Q1`-- O -- ... -- O -- Qn-1`-- O` -- Qn`
    """
    __SWAP_MATRIX = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=np.complex128)

    @property
    def qubits(self) -> int:
        return self._qubits

    def __init__(
        self,
        device: str = "CPU",
        precision: str = "double"
    ):
        """ Initial the MPSSiteStructure Class

        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision type, one of [single, double]. Defaults to "double".
        """
        # based properties
        assert device in ["CPU", "GPU"]
        self._device = device
        assert precision in ["double", "single"]
        self._precision = precision
        self._dtype = np.complex128 if self._precision == "double" else np.complex64
        self._qubits = 0

        # matrix product state structure
        self._product_state = []
        self._norms = []
        self._groups = []   # List of the interval of entangle states, e.g. [(0, 3), (5, 7)]

        # algorithm Module
        self._linear_algorithm = LinAlgLoader(device=device)
        if self._device == "GPU":
            import cupy as cp

            self._array_helper = cp
        else:
            self._array_helper = np

    def initial_mps(self, qubits: int, quantum_state: Union[str, np.ndarray] = None):
        """ Generate the initial state for MPS by given quantum state or default state.

        Args:
            qubits (int): The number of qubits.
            quantum_state (Union[str, np.ndarray], optional): The initial quantum state. Defaults to None.
        """
        self._qubits = qubits
        if quantum_state is not None:
            # TODO: add special quantum state like GHZ or ... later
            if not isinstance(quantum_state, str):
                quantum_state = self._array_helper.array(quantum_state)
                self._quantum_state_schmidt_decomposition(quantum_state)
        else:
            self._product_state = [QubitTensor(self._initial_qtensor()) for _ in range(self._qubits)]
            self._norms = [Normalize(self._initial_normalize())for _ in range(1, self._qubits)] if qubits > 1 else []
            self._groups = []

    def _initial_qtensor(self):
        return self._array_helper.array([1, 0], dtype=self._dtype).reshape(1, 2, 1)

    def _initial_normalize(self):
        return self._array_helper.array([1, ], dtype=self._dtype)

    def _quantum_state_schmidt_decomposition(self, quantum_state: np.ndarray) -> list:
        """ Generate the Matrix Product State from the given quantum state by the Schmidt Decomposition

        Args:
            quantum_state (np.ndarray): The given quantum state

        Returns:
            list: The MPS list
        """
        assert len(quantum_state.shape) == 1
        quantum_state = quantum_state.reshape(1, -1)
        self._product_state = []
        self._norms = []
        if self._qubits == 1:
            self._product_state.append(QubitTensor(quantum_state.reshape(1, 2, 1)))
            return

        for _ in range(self.qubits - 1):
            ldim = quantum_state.shape[0]
            quantum_state = quantum_state.reshape(2 * ldim, -1)

            U, S, VT = self._array_helper.linalg.svd(quantum_state, full_matrices=False)
            self._product_state.append(QubitTensor(U.reshape(ldim, 2, -1)))
            self._norms.append(Normalize(S))
            quantum_state = VT

        self._product_state.append(QubitTensor(VT.reshape(-1, 2, 1)))
        self._groups = [0, self._qubits - 1]

    def _update_groups(self):
        self._groups = []
        start = 0
        for idx, norm in enumerate(self._norms):
            if norm.ldim == 1:
                self._groups.append([start, idx])
                start = idx + 1
            elif idx == self._qubits - 2:
                self._groups.append([start, idx + 1])

    def _check_groups(self, index: int):
        for start, end in self._groups:
            if start <= index and end >= index:
                return [start, end]

        return index

    ### Gate Related Functions ###
    def apply_single_gate(self, qubit_index: int, gate_matrix: np.ndarray):
        """ Apply single gate into MPS

        Args:
            qubit_index (int): The index of qubit
            gate_matrix (np.ndarray): The matrix of the quantum gate
        """
        assert qubit_index < self.qubits
        target_qubit = self._product_state[qubit_index]
        target_qubit.tensor_data = self._array_helper.tensordot(
            target_qubit.tensor_data, self._array_helper.array(gate_matrix, dtype=self._dtype), [[1], [1]]
        ).transpose([0, 2, 1])

    def apply_double_gate(self, qubit_indexes: list, gate_matrix: np.ndarray):
        """ Apply bi-qubits quantum gate into MPS.

        Args:
            qubit_indexes (list): The list of qubits' indexes
            gate_matrix (np.ndarray): The matrix of the quantum gate
            inverse (bool, optional): Need Extra inverse? only for CRx and Unitary. Defaults to False.
        """
        q0, q1 = qubit_indexes
        if abs(q0 - q1) == 1:
            # Apply consecutive bi-qubits gate
            self._apply_consecutive_double_gate(qubit_indexes, gate_matrix)
        else:
            # Apply swap gate for un-consecutive bi-qubits gate
            min_q = min(qubit_indexes)
            max_q = max(qubit_indexes)
            for i in range(min_q, max_q - 1):
                self._apply_consecutive_double_gate([i, i + 1], self.__SWAP_MATRIX)

            qubit_indexes = [max_q, max_q - 1] if q0 > q1 else [max_q - 1, max_q]
            self._apply_consecutive_double_gate(qubit_indexes, gate_matrix)
            for i in range(max_q - 1, min_q, -1):
                self._apply_consecutive_double_gate([i - 1, i], self.__SWAP_MATRIX)

        self._update_groups()

    def _apply_consecutive_double_gate(self, qubit_indexes: list, gate_matrix: np.ndarray):
        """ Apply bi-qubits quantum gate with consecutive qubits' indexes into MPS.

        Args:
            qubit_indexes (list): The list of qubits' indexes
            gate_matrix (np.ndarray): The matrix of the quantum gate
            inverse (bool, optional): Need Extra inverse? only for CRx and Unitary.. Defaults to False.
        """
        if qubit_indexes[0] > qubit_indexes[1]:
            qubit_indexes.sort()
            gate_matrix = self._linear_algorithm.MatrixPermutation(gate_matrix, np.array([1, 0]))

        # Only support consecutive qubits gate
        qubit0 = self._product_state[qubit_indexes[0]]
        qubit1 = self._product_state[qubit_indexes[1]]
        norm = self._norms[qubit_indexes[0]]

        # Combined two qubits together
        q0_data = qubit0.tensor_data
        q1_data = qubit1.tensor_data
        q0_ldim, q1_rdim = q0_data.shape[0], q1_data.shape[2]
        bi_qubits_comb = self._array_helper.tensordot(
            self._array_helper.tensordot(q0_data, self._array_helper.diag(norm.matrix_data), [2, 0]),
            q1_data,
            [2, 0]
        )
        bi_qubits_comb = bi_qubits_comb.reshape([q0_ldim, -1, q1_rdim])

        # Apply two qubit gate
        bi_qubits_comb = self._array_helper.tensordot(
            bi_qubits_comb,
            self._array_helper.array(gate_matrix, dtype=self._dtype),
            [[1], [1]]
        ).transpose([0, 2, 1])
        # schmidt decomposition
        bi_qubits_comb = bi_qubits_comb.reshape(q0_ldim * 2, -1)
        U, S, VT = self._array_helper.linalg.svd(bi_qubits_comb, full_matrices=False)

        # Put back to Qi, Ni, Qi+1
        qubit0.tensor_data = U.reshape(q0_ldim, 2, -1)
        qubit1.tensor_data = VT.reshape(-1, 2, q1_rdim)
        norm.matrix_data = S

    ### Measure Gate Related ###
    # TODO: Support Later
    def apply_measure_gate(self, qubit_indexes: list):
        internal_groups = defaultdict(list)
        for qidx in qubit_indexes:
            group_idx = self._check_groups(qidx)
            if isinstance(group_idx, int):
                self._apply_mgate(qidx)
            else:
                if len(internal_groups[group_idx[0]]) == 0:
                    internal_groups[group_idx[0]].append(group_idx[1])

                internal_groups[group_idx[0]].append(qidx)

        for key, value in internal_groups.items():
            self._apply_mgate([key] + value)

    def _apply_mgate(self, qubit_indexes: Union[list, int]):
        if isinstance(qubit_indexes, int):
            target_site = self._product_state[qubit_indexes]
            result = self._measured_from_state_vector(target_site.tensor_data, 1)
            self._measured_back_for_individual_shot(result, qubit_indexes)
        else:
            interval = qubit_indexes[:2]
            qidxes = qubit_indexes[2:]
            statevector = self.to_statevector(interval)
            result = self._measured_from_state_vector(statevector, interval[1] - interval[0] + 1)

            self._measured_back_for_group(result, interval, qidxes)

    def _measured_from_state_vector(self, state_vector: np.ndarray, qubits: int):
        state_vector = state_vector.flatten('C')
        measured_prob = self._array_helper.square(self._array_helper.abs(state_vector))
        if self._device == "GPU":
            measured_prob = measured_prob.get()

        result = np.random.choice(
            np.arange(1 << qubits),
            p=measured_prob
        )

        return result

    def _measured_back_for_individual_shot(self, result: int, qubit_index: int):
        result_array = [0, 1] if result == 1 else [1, 0]
        self._product_state[qubit_index] = QubitTensor(
            self._array_helper.array(result_array, dtype=self._dtype).reshape(1, 2, 1)
        )

    def _measured_back_for_group(self, result: int, group: list, qubit_indexes: Union[list, int]):
        # TODO: currently only
        pass

    def single_amplitude_calculate(self, state_index: int):
        """ Calculate single amplitude for current MPS.

        Args:
            state_index (int): The index of quantum state which want to be calculate.
        """
        assert state_index < (1 << self._qubits)
        # Index divided by qubits per each circuit blocks
        bit_index = "{0:0b}".format(state_index)
        bit_index = bit_index.zfill(self._qubits)
        # bit_index = [bit_index[i] for i in range(0, self._qubits, 1)]

        q0_state = int(bit_index[0], 2)
        single_state = self._product_state[0].tensor_data[:, q0_state, :]
        for i in range(1, self._qubits):
            # multiply the norm
            single_state = np.einsum('ij,j->ij', single_state, self._norms[i - 1].matrix_data)

            # choice qubits' state
            qmps = self._product_state[i]
            q_state = int(bit_index[i], 2)
            target_value = qmps.tensor_data[:, q_state, :]
            single_state = np.einsum('ij,jk->ik', single_state, target_value)

        return single_state.flatten()

    def to_statevector(self, interval: list = None) -> np.ndarray:
        """ Transfer MPS into State Vector. WARNING: it will generate an vector with size 2**n, where n is the
         number of qubits.

        Returns:
            np.ndarray: The state vector from MPS
        """
        if not interval:
            start, end = 0, self.qubits
        else:
            assert len(interval) == 2
            start, end = interval

        state_vector = self._product_state[start].tensor_data
        for i in range(start + 1, end):
            state_vector = self._array_helper.tensordot(
                state_vector, self._array_helper.diag(self._norms[i - 1].matrix_data), [[-1], [0]]
            )
            state_vector = self._array_helper.tensordot(state_vector, self._product_state[i].tensor_data, [[-1], [0]])
            ldim, rdim = state_vector.shape[0], state_vector.shape[-1]
            state_vector = state_vector.reshape([ldim, -1, rdim])

        return state_vector.flatten('C')

    def sample(self, shots: int):
        """ Sample the measured result from current Matrix Product State.

        Args:
            shots (int): The sample times.
        """
        # Get State Vector
        state_vector = self.to_statevector()
        state_list = [0] * (1 << self._qubits)

        # Sample from State Vector
        measured_prob = self._array_helper.square(self._array_helper.abs(state_vector))
        if self._device == "GPU":
            measured_prob = measured_prob.get()

        sample_result = np.random.choice(
            np.arange(1 << self._qubits), shots, p=measured_prob
        )
        for res in sample_result:
            state_list[res] += 1

        return state_list
