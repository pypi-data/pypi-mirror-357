import numpy as np

from QuICT.core.gate import BasicGate, GateMatrixGenerator, MultiControlGate
from QuICT.core.utils import GateType, MatrixType, matrix_product_to_circuit
from QuICT.ops.utils import LinAlgLoader
from QuICT.tools.exception.core import GateQubitAssignedError, ValueError
from QuICT.tools.exception.simulation import GateTypeNotImplementError, GateAlgorithmNotImplementError


THRESHOLD_QUBITS = 30
BLOCK_QUBITS = 5


class GateSimulator:
    """
    The class of simulation functions, including State Vector Creation, Density Matrix Creation, Quantum Gate's Matrix
    aggregation and Quantum Gate Algorithms.
    """
    @property
    def device(self):
        return self._device

    @property
    def precision(self):
        return self._precision

    def __init__(
        self,
        device,
        precision: str = "double",
        gpu_device_id: int = 0,
        sync: bool = True,
        enable_gfunc: bool = True
    ):
        """
        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision for the state vector, one of [single, double].
                Defaults to "double".
            gpu_device_id (int, optional): The GPU device ID. Defaults to 0.
            sync (bool, optional): Sync mode or Async mode. Defaults to True.
            enable_gfunc (bool, optional): Whether use Quantum Gate Algorithm. Defaults to True.
        """
        if device not in ["CPU", "GPU"]:
            raise ValueError("Simulation.device", "[CPU, GPU]", device)

        if precision not in ["single", "double"]:
            raise ValueError("Simulation.precision", "[single, double]", precision)

        self._device = device
        self._precision = precision
        self._dtype = np.complex128 if precision == "double" else np.complex64
        self._gpu_device_id = gpu_device_id
        self._sync = sync

        # Gate's Matrix Store
        self._gate_matrix_generator = GateMatrixGenerator()
        self._gate_matrix_info: dict = {}   # Record gate's matrix info (location, length)
        self._gates_matrix = None

        # cupy/numpy and Gate Kernel functions
        self._algorithm = LinAlgLoader(device=device, enable_gate_kernel=enable_gfunc)
        if self._device == "GPU":
            import cupy as cp

            self._array_helper = cp
            cp.cuda.runtime.setDevice(self._gpu_device_id)
        else:
            self._array_helper = np

    ####################################################################
    ############          State Vector Generator            ############
    ####################################################################
    def get_empty_state_vector(self, qubits: int):
        """ Return the empty State Vector with size equals 1 << qubits.

        Args:
            qubits (int): The number of qubits.

        Returns:
            np.ndarray: the State Vector
        """
        return self._array_helper.zeros(1 << qubits, dtype=self._dtype)

    def get_allzero_state_vector(self, qubits: int):
        """ Return the State Vector with all-zeros state and size equals 1 << qubits.

        Args:
            qubits (int): The number of qubits.

        Returns:
            np.ndarray: the State Vector
        """
        state_vector = self.get_empty_state_vector(qubits)
        state_vector[0] = self._dtype(1)

        return state_vector

    def normalized_state_vector(self, state_vector, qubits: int):
        """ Normalize the given State Vector, including the size check and type translate.

        Args:
            state_vector (np.ndarray): The given State Vector
            qubits (int): The number of qubits

        Returns:
            np.ndarray: the normalized State Vector
        """
        assert 1 << qubits == state_vector.size, "The state vector should has the same qubits with the circuit."
        if not type(state_vector) is self._array_helper.ndarray:
            state_vector = self._array_helper.array(state_vector, dtype=self._dtype)

        if state_vector.dtype != self._dtype:
            state_vector = state_vector.astype(self._dtype)

        return state_vector

    ####################################################################
    ############         Density Matrix Generator           ############
    ####################################################################
    def get_allzero_density_matrix(self, qubits: int):
        """ Return the empty Density Matrix with size equals 1 << qubits.

        Args:
            qubits (int): The number of qubits.

        Returns:
            np.ndarray: the Density Matrix
        """
        density_matrix = self._array_helper.zeros((1 << qubits, 1 << qubits), dtype=self._dtype)
        density_matrix[0, 0] = self._dtype(1)

        return density_matrix

    def get_empty_density_matrix(self, qubits: int):
        """ Return the Density Matrix with all-zeros state and size equals 1 << qubits.

        Args:
            qubits (int): The number of qubits.

        Returns:
            np.ndarray: the Density Matrix
        """
        return self._array_helper.zeros((1 << qubits, 1 << qubits), dtype=self._dtype)

    def validate_density_matrix(self, matrix) -> bool:
        """ Density Matrix Validation. """
        if not isinstance(matrix, np.ndarray):
            matrix = matrix.get()

        if not np.allclose(matrix.T.conjugate(), matrix):
            raise ValueError("The conjugate transpose of density matrix do not equal to itself.")

        eigenvalues = np.linalg.eig(matrix)[0]
        for ev in eigenvalues:
            if ev < 0 and not np.isclose(ev, 0, rtol=1e-4):
                raise ValueError("The eigenvalues of density matrix should be non-negative")

        if not np.isclose(matrix.trace(), 1, rtol=1e-4):
            raise ValueError("The sum of trace of density matrix should be 1.")

        return True

    def get_density_matrix_from_state_vector(self, state_vector):
        return self._array_helper.outer(state_vector, state_vector.conj().T)

    ####################################################################
    ############      Gate Matrix Generator & Sampling      ############
    ####################################################################
    def normalized_matrix(self, unitary_matrix, qubits: int):
        """ Normalized the Unitary Matrix

        Args:
            unitary_matrix (np.ndarray): The Unitary Matrix
            qubits (int): The number of qubits.

        Returns:
            np.ndarray: the normalized Unitary Matrix
        """
        row, col = unitary_matrix.shape
        assert 1 << qubits == row and row == col, "The unitary matrix should be square."
        if not type(unitary_matrix) is self._array_helper.ndarray:
            unitary_matrix = self._array_helper.array(unitary_matrix, dtype=self._dtype)

        if unitary_matrix.dtype != self._dtype:
            unitary_matrix = unitary_matrix.astype(self._dtype)

        return unitary_matrix

    def is_identity(self, unitary_matrix):
        """ Whether the given unitary matrix is identity matrix. """
        row = unitary_matrix.shape[0]
        if row > (1 << (THRESHOLD_QUBITS // 2)):
            return False

        identity_matrix = np.identity(row, dtype=self._dtype)
        if self.device == "GPU":
            return np.allclose(unitary_matrix.get(), identity_matrix)
        else:
            return np.allclose(unitary_matrix, identity_matrix)

    def dot(self, unitary_matrix, state_vector):
        if self.is_identity(unitary_matrix):
            return state_vector
        else:
            return self._algorithm.dot(unitary_matrix, state_vector)

    def gate_matrix_combined(self, circuit):
        """ the aggregation of Quantum Gates' matrix in the given Quantum Circuit.

        Args:
            circuit (Circuit): The Quantum Circuit.
        """
        matrix_list_for_gpu_only = []
        total_matrix_size = 0 if self._gates_matrix is None else self._gates_matrix.size
        if total_matrix_size >= (1 << 10):
            return

        for gate in circuit.flatten_gates():
            if (
                not isinstance(gate, BasicGate)
                or gate.type in [
                    GateType.measure, GateType.reset, GateType.barrier,
                    GateType.unitary, GateType.kraus, GateType.perm
                ]
                or gate.matrix_type == MatrixType.special
            ):
                continue

            gate_name = self._generate_gate_name_for_matrix_stored(gate.type, gate.pargs)
            if gate_name not in self._gate_matrix_info.keys():
                matrix = self._gate_matrix_generator.get_matrix(gate, self._precision, True)

                if self._device == "CPU":
                    self._gate_matrix_info[gate_name] = matrix
                else:
                    self._gate_matrix_info[gate_name] = (total_matrix_size, matrix.size)
                    total_matrix_size += matrix.size
                    matrix_list_for_gpu_only.append(matrix)

        if len(matrix_list_for_gpu_only) > 0:
            self._concentrate_gate_matrixs(matrix_list_for_gpu_only, total_matrix_size)

    def get_probability_for_state_vector(self, state_vector, qubits: int, target_qubits: list = None):
        if target_qubits is None:
            return self._array_helper.square(self._array_helper.abs(state_vector))

        target_qubits = self._array_helper.array(target_qubits, dtype=self._array_helper.int32)
        return self._algorithm.sv_probability(state_vector, qubits, target_qubits)

    def sample_for_statevector(self, shots: int, qubits: int, state_vector, noised: bool = False):
        measured_prob = self._array_helper.square(self._array_helper.abs(state_vector))
        if self._device == "GPU":
            measured_prob = measured_prob.get()

        if noised or not np.isclose(sum(measured_prob), 1):
            measured_prob /= sum(measured_prob)

        result = np.random.choice(
            np.arange(1 << qubits), shots, p=measured_prob
        )

        return result

    def sample_for_statevector_cdf(
        self,
        shots: int,
        qubits: int,
        state_vector,
        target_qubits: list = None,
        seed: int = -1
    ):
        if qubits >= THRESHOLD_QUBITS:
            return self.sample_for_large_statevector_cdf(shots, qubits, state_vector, target_qubits, seed=seed)

        measured_prob = self._array_helper.cumsum(
            self._array_helper.square(self._array_helper.abs(state_vector)), dtype=self._array_helper.float32
        )

        if target_qubits is None:
            result = self._algorithm.sv_sampling_for_all_qubits(measured_prob, shots, qubits, seed=seed)
        else:
            target_qubits = self._array_helper.array(target_qubits, dtype=self._array_helper.int32)
            result = self._algorithm.sv_sampling(measured_prob, shots, qubits, target_qubits, seed=seed)

        if self._device == "GPU":
            return result.get()

        return result

    def sample_for_large_statevector_cdf(
        self,
        shots: int,
        qubits: int,
        state_vector,
        target_qubits: list = None,
        seed: int = -1
    ):
        # Step 1: Sum of 1 << 5, abs & square
        partial_sv = self._algorithm.array_combination(state_vector, qubits, BLOCK_QUBITS)

        # Step 2: Find the cumsum of partial_sv
        partial_sv = self._array_helper.cumsum(partial_sv, dtype=self._array_helper.float32)

        # Step 3: Get result of partial_sv
        if target_qubits is None:
            result = self._algorithm.partial_sv_sampling_for_all_qubits(
                partial_sv, state_vector, shots, qubits, BLOCK_QUBITS, seed=seed
            )
        else:
            target_qubits = self._array_helper.array(target_qubits, dtype=self._array_helper.int32)
            result = self._algorithm.partial_sv_sampling(
                partial_sv, state_vector, shots, qubits, BLOCK_QUBITS, target_qubits, seed=seed
            )

        if self._device == "GPU":
            return result.get()

        return result

    def _generate_gate_name_for_matrix_stored(self, gate_type, gate_pargs: list = None):
        """ Generate special name [type + parameters] for store Quantum Gates' matrix. """
        gate_name = str(gate_type)

        for parg in gate_pargs:
            gate_name += f"_{parg}"

        return gate_name

    def _concentrate_gate_matrixs(self, matrix_list: list, matrix_size: int):
        gates_matrix = np.empty(matrix_size, dtype=self._dtype)
        start = 0
        for matrix in matrix_list:
            gates_matrix[start:start + matrix.size] = matrix.ravel()[:]
            start += matrix.size

        gates_matrix = self._array_helper.array(gates_matrix)
        if self._gates_matrix is None:
            self._gates_matrix = gates_matrix
        else:
            self._gates_matrix = self._array_helper.concatenate((self._gates_matrix, gates_matrix))

    def _get_gate_matrix(self, gate: BasicGate):
        """ Get Quantum Gates' Matrix.

        Args:
            gate (BasicGate): The Quantum Gate.

        Returns:
            np.ndarray/cp.ndarray: The unitary matrix of Quantum Gate.
        """
        if gate.symbol_gate:
            pargs = []
            for val in gate.symbol_pargs.values():
                pargs.append(val)
        else:
            pargs = gate.pargs
        gate_name = self._generate_gate_name_for_matrix_stored(gate.type, pargs)

        if gate_name not in self._gate_matrix_info.keys():
            matrix = self._gate_matrix_generator.get_matrix(gate, self._precision, True)
            if self._device == "GPU":
                matrix = self._array_helper.array(matrix.flatten())

            return matrix

        if self._device == "CPU":
            return self._gate_matrix_info[gate_name]
        else:
            start, interval = self._gate_matrix_info[gate_name]
            return self._gates_matrix[start:start + interval]

    def _get_gate_param_grad(self, gate: BasicGate, parg_id: int = 0):
        gtype = gate.type
        gpargs = gate.pargs
        gsymbol_pargs = gate.symbol_pargs
        gate_precision = self._precision
        matrix = self._gate_matrix_generator.grad_for_param(gtype, gpargs, gsymbol_pargs, gate_precision)[parg_id]

        if self._device == "GPU":
            matrix = self._array_helper.array(matrix)

        return matrix

    ####################################################################
    ############           Gate Kernel Functions            ############
    ####################################################################
    def apply_gate(
        self,
        gate: BasicGate,
        assigned_qubits: list,
        state_vector: np.ndarray,
        qubits: int,
        fp: bool = True,
        parg_id: int = 0,
    ):
        """ Apply the kernel function of Quantum Gate to the State Vector.

        Args:
            gate (BasicGate): the Quantum Gate
            assigned_qubits (list): The gate's qubit indexes
            state_vector (np.ndarray): The State Vector
            qubits (int): the number of qubits
        """
        gate_type = gate.type
        if gate_type in [GateType.id, GateType.barrier] or gate.is_identity():
            return

        gate_cargs = [qubits - 1 - assigned_qubits[i] for i in range(gate.controls)]
        gate_targs = [
            qubits - 1 - assigned_qubits[i]
            for i in range(gate.controls, len(assigned_qubits))
        ]

        if self._device == "CPU":
            return self._apply_gate_cpu(
                gate, gate_cargs, gate_targs, state_vector, fp, parg_id
            )
        else:
            return self._apply_gate_gpu(
                gate, gate_cargs, gate_targs, state_vector, qubits, fp, parg_id
            )

    def _apply_gate_cpu(
        self,
        gate: BasicGate,
        cargs: list,
        targs: list,
        state_vector,
        fp: bool = True,
        parg_id: int = 0,
    ):
        """ The algorithm of apply gate into State Vector in CPU."""
        matrix_type = gate.matrix_type
        if gate.type not in [GateType.unitary, GateType.rzx, GateType.ecr]:
            matrix = self._get_gate_matrix(gate) if fp else self._get_gate_param_grad(gate, parg_id)
        else:
            matrix = gate.matrix.astype(self._dtype) if self._precision == "single" else gate.matrix
            matrix = self._algorithm.MatrixPermutation(
                matrix, self._array_helper.array(range(len(targs) - 1, -1, -1)), False
            )

        control_idx = np.array(cargs, dtype=np.int64)
        target_idx = np.array(targs, dtype=np.int64)

        if matrix_type in [MatrixType.diag_diag, MatrixType.diagonal, MatrixType.control]:
            self._algorithm.diagonal_matrix(
                state_vector,
                matrix,
                control_idx,
                target_idx,
                is_control=True if matrix_type == MatrixType.control else False
            )
        elif matrix_type == MatrixType.swap:
            self._algorithm.swap_matrix(state_vector, matrix, control_idx, target_idx)
        elif matrix_type == MatrixType.reverse:
            self._algorithm.reverse_matrix(state_vector, matrix, control_idx, target_idx)
        else:
            if gate.type == GateType.rccx:
                control_idx = np.array(cargs[:1], dtype=np.int64)
                target_idx = np.array(targs + cargs[1:], dtype=np.int64)

            self._algorithm.matrix_dot_vector(
                state_vector,
                matrix,
                control_idx,
                target_idx
            )

    def _apply_gate_gpu(
        self,
        gate: BasicGate,
        cargs: list,
        targs: list,
        state_vector,
        qubits,
        fp: bool = True,
        parg_id: int = 0,
    ):
        """ The algorithm of apply gate into State Vector in GPU."""
        gate_type, matrix_type = gate.type, gate.matrix_type
        args_num = gate.controls + gate.targets
        if gate.type not in [GateType.unitary, GateType.rzx, GateType.ecr]:
            matrix = self._get_gate_matrix(gate) if fp else self._get_gate_param_grad(gate, parg_id)
        else:
            matrix = gate.matrix.astype(self._dtype) if self._precision == "single" else gate.matrix
            matrix = self._algorithm.MatrixPermutation(
                matrix, self._array_helper.array(range(len(targs) - 1, -1, -1)), gpu_out=False
            ).ravel()

        if isinstance(gate, MultiControlGate):
            if len(targs) == 1:
                self._algorithm.apply_multi_control_targ_gate(
                    state_vector, qubits, matrix, cargs, targs[0], self._sync
                )
            else:
                self._algorithm.apply_multi_control_targs_gate(
                    state_vector, qubits, matrix, cargs, targs, self._sync
                )

            return

        # [RCCX]
        if gate_type == GateType.rccx:
            self._algorithm.apply_rccxgate(
                cargs[0], targs + [cargs[1]], state_vector, qubits, self._sync
            )
        # [H, Hy, SX, SY, SW, U2, U3, Rx, Ry] 2-bits [CH, ] 2-bits[Rzx, targets, unitary]
        elif matrix_type == MatrixType.normal or matrix_type == MatrixType.diag_normal:
            self.apply_normal_matrix(
                matrix, args_num, cargs, targs, state_vector, qubits
            )
        # [Rz, Phase], 2-bits [CRz, Rzz], 3-bits [CCRz]
        elif matrix_type in [MatrixType.diagonal, MatrixType.diag_diag]:
            self.apply_diagonal_matrix(
                matrix, args_num, cargs, targs, state_vector, qubits
            )
        # [X] 2-bits [swap, iswap, iswapdg, sqiswap] 3-bits [CSWAP]
        elif matrix_type == MatrixType.swap:
            self.apply_swap_matrix(matrix, args_num, cargs, targs, state_vector, qubits)
        # [Y] 2-bits [CX, CY] 3-bits: [CCX]
        elif matrix_type == MatrixType.reverse:
            self.apply_reverse_matrix(
                matrix, args_num, cargs, targs, state_vector, qubits
            )
        # [S, sdg, Z, U1, T, tdg] # 2-bits [CZ, CU1]
        elif matrix_type == MatrixType.control:
            self.apply_control_matrix(matrix[-1].get(), args_num, cargs, targs, state_vector, qubits)
        # [FSim]
        elif matrix_type == MatrixType.ctrl_normal:
            self._algorithm.ctrl_normal_targs(
                targs, matrix, state_vector, qubits, self._sync
            )
        # [Rxx, Ryy]
        elif matrix_type == MatrixType.normal_normal:
            self._algorithm.normal_normal_targs(
                targs, matrix, state_vector, qubits, self._sync
            )
        # [Rzx]
        elif matrix_type == MatrixType.diag_normal:
            self._algorithm.diagonal_normal_targs(
                targs, matrix, state_vector, qubits, self._sync
            )
        # [Perm] TODO: replace by build_gate
        elif gate_type == GateType.perm:
            args = cargs + targs
            if len(args) == qubits:
                mapping = np.array(gate.pargs, dtype=np.int32)
            else:
                mapping = np.arange(qubits, dtype=np.int32)
                for idx, parg in enumerate(gate.pargs):
                    mapping[args[idx]] = args[parg]

            self._algorithm.VectorPermutation(
                state_vector, mapping, changeInput=True, gpu_out=False, sync=self._sync
            )
        # unsupported quantum gates
        else:
            raise GateTypeNotImplementError(
                f"Unsupported Gate Type and Matrix Type: {gate_type} {matrix_type}."
            )

    def apply_large_unitary_matrix(
        self, matrix, assigned_qubits, state_vector, qubits
    ):
        assigned_qubits = [qubits - 1 - aq for aq in assigned_qubits]
        self._algorithm.matrix_dot_vector(
            state_vector, qubits, matrix, assigned_qubits, self._sync
        )

    def apply_normal_matrix(
        self, matrix, args_num: int, cargs: list, targs: list, state_vector, qubits
    ):
        # Deal with 1-qubit normal gate e.g. H
        if args_num == 1:
            self._algorithm.normal_targ(
                targs[0], matrix, state_vector, qubits, self._sync
            )
        elif args_num == 2:  # Deal with 2-qubits control normal gate e.g. CH
            if len(cargs) == 1:
                self._algorithm.normal_ctargs(
                    cargs[0], targs[0], matrix, state_vector, qubits, self._sync
                )
            elif len(targs) == 2:  # Deal with 2-qubits unitary gate
                self._algorithm.normal_targs(
                    targs, matrix, state_vector, qubits, self._sync
                )
            else:
                raise GateQubitAssignedError(
                    "Quantum gate cannot only have control qubits."
                )

    def apply_diagonal_matrix(
        self, matrix, args_num: int, cargs: list, targs: list, state_vector, qubits
    ):
        # Deal with 1-qubit diagonal gate, e.g. Rz
        if args_num == 1:
            self._algorithm.diagonal_targ(
                targs[0], matrix, state_vector, qubits, self._sync
            )
        elif args_num == 2:  # Deal with 2-qubit diagonal gate, e.g. CRz
            if len(cargs) == 1:
                self._algorithm.diagonal_ctargs(
                    cargs[0], targs[0], matrix, state_vector, qubits, self._sync
                )
            elif len(targs) == 2:
                self._algorithm.diagonal_targs(
                    targs, matrix, state_vector, qubits, self._sync
                )
            else:
                raise GateQubitAssignedError(
                    "Quantum gate cannot only have control qubits."
                )
        else:  # [CCRz]
            self._algorithm.diagonal_more(
                cargs, targs[0], matrix, state_vector, qubits, self._sync
            )

    def apply_swap_matrix(
        self, matrix, args_num: int, cargs: list, targs: list, state_vector, qubits
    ):
        if args_num == 1:  # Deal with X Gate
            self._algorithm.swap_targ(targs[0], state_vector, qubits, self._sync)
        elif args_num == 2:  # Deal with Swap Gate
            self._algorithm.swap_targs(targs, matrix, state_vector, qubits, self._sync)
        else:  # CSwap
            self._algorithm.swap_tmore(
                targs, cargs[0], state_vector, qubits, self._sync
            )

    def apply_reverse_matrix(
        self, matrix, args_num: int, cargs: list, targs: list, state_vector, qubits
    ):
        if args_num == 1:  # Deal with 1-qubit reverse gate, e.g. Y
            self._algorithm.reverse_targ(
                targs[0], matrix, state_vector, qubits, self._sync
            )
        elif args_num == 2:   # only consider 1 control qubit + 1 target qubit
            if len(cargs) == 1:
                self._algorithm.reverse_ctargs(
                    cargs[0], targs[0], matrix, state_vector, qubits, self._sync
                )
            elif len(targs) == 2:
                self._algorithm.reverse_targs(
                    targs, matrix, state_vector, qubits, self._sync
                )
            else:
                raise GateQubitAssignedError("Quantum gate cannot only have control qubits.")
        else:   # CCX
            self._algorithm.reverse_more(
                cargs, targs[0], state_vector, qubits, self._sync
            )

    def apply_control_matrix(
        self, value, args_num: int, cargs: list, targs: list, state_vector, qubits
    ):
        if args_num == 1:    # Deal with 1-qubit control gate, e.g. S
            self._algorithm.control_targ(
                targs[0], value, state_vector, qubits, self._sync
            )
        elif args_num == 2:  # Deal with 2-qubit control gate, e.g. CZ
            self._algorithm.control_ctargs(
                cargs[0], targs[0], value, state_vector, qubits, self._sync
            )
        elif args_num == 3:  # Deal with 3-qubits control gate, e.g. CCZ
            self._algorithm.control_cctarg(
                cargs, targs[0], value, state_vector, qubits, self._sync
            )
        else:
            raise GateAlgorithmNotImplementError(
                f"Unsupportted 3-qubits+ control unitary gate."
            )

    def _apply_kraus(self, gate, targs: list, state_vector, qubits):
        targs = [qubits - 1 - targ for targ in targs]
        noise_matrix = gate.matrix
        if self._device == "CPU":
            self._algorithm.matrix_dot_vector(
                state_vector, noise_matrix, target_args=np.array(targs, dtype=np.int64)
            )
        else:
            return self._algorithm.matrix_dot_vector(
                state_vector, qubits, noise_matrix, targs, self._sync
            )

    ####################################################################
    ############           Measure/Reset Function           ############
    ####################################################################
    def apply_measure_gate(self, index: int, state_vector: np.ndarray, qubits: int) -> int:
        if self._device == "CPU":
            result = int(self._algorithm.measure_gate_apply(index, state_vector))
        else:
            prob = self._algorithm.measured_prob_calculate(
                index, state_vector, qubits, sync=self._sync
            ).get()
            result = int(self._algorithm.apply_measuregate(
                index, state_vector, qubits, prob, self._sync
            ))

        return result

    def apply_pauliZ_measure(self, index: int, state_vector: np.ndarray, qubits: int) -> float:
        if self._device == "CPU":
            prob = self._algorithm.measure_gate_apply(index, state_vector, pauliZ=True)
        else:
            prob = self._algorithm.measured_prob_calculate(
                index, state_vector, qubits, sync=self._sync
            ).get()
        expectation = float(2 * prob - 1)
        return expectation

    def apply_reset_gate(self, index: int, state_vector: np.ndarray, qubits: int):
        if self._device == "CPU":
            self._algorithm.reset_gate_apply(index, state_vector)
        else:
            prob = self._algorithm.measured_prob_calculate(
                index, state_vector, qubits, sync=self._sync
            )
            self._algorithm.apply_resetgate(
                index, state_vector, qubits, prob, self._sync
            )

    def get_measured_prob(self, index: int, state_vector: np.ndarray, qubits: int):
        if self._device == "CPU":
            return self._algorithm.get_measured_probability(index, state_vector)
        else:
            return self._algorithm.measured_prob_calculate(
                index, state_vector, qubits, sync=self._sync
            )

    def apply_measure_gate_for_dm(self, index: int, density_matrix: np.ndarray, qubits: int, seed: int = -1):
        if seed != -1:
            self._array_helper.random.seed(seed)

        P0 = self._array_helper.array([[1, 0], [0, 0]], dtype=self._dtype)
        mea_0 = matrix_product_to_circuit(P0, index, qubits, self._device)
        prob_0 = self._array_helper.matmul(mea_0, density_matrix).trace()

        _1 = np.random.random() > prob_0
        if not _1:
            U = self._array_helper.matmul(
                mea_0,
                self._array_helper.eye(1 << qubits, dtype=self._dtype) / self._array_helper.sqrt(prob_0)
            )
            density_matrix = self._algorithm.dot(self._algorithm.dot(U, density_matrix), U.conj().T)
        else:
            P1 = self._array_helper.array([[0, 0], [0, 1]], dtype=self._dtype)
            mea_1 = matrix_product_to_circuit(P1, index, qubits, self._device)

            U = self._array_helper.matmul(
                mea_1,
                self._array_helper.eye(1 << qubits, dtype=self._dtype) / self._array_helper.sqrt(1 - prob_0)
            )
            density_matrix = self._algorithm.dot(self._algorithm.dot(U, density_matrix), U.conj().T)

        return _1, density_matrix
