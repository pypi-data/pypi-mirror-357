from numba import njit, prange
import numpy as np

from QuICT.ops.utils import mapping_augment, find_cdf_index


@njit(parallel=True, nogil=True)
def MatrixTensorI(A, n, m):
    r""" Applying the Matrix Tensor operator to matrix A

    $$ A' = I^n \otimes A \otimes I^m $$

    Args:
        A(np.array<np.complex>): the matrix A
        n(int): the index of indentity
        m(int): the index of indentity

    Returns:
        np.array<np.complex>: the tensor result I^n ⊗ A ⊗ I^m
    """
    i_m = np.identity(m)
    row_a, col_a = A.shape
    MatrixTensor = np.zeros((n * m * row_a, n * m * col_a), dtype=A.dtype)

    for i in prange(row_a):
        for j in prange(col_a):
            temp_M = A[i, j] * i_m
            for k in range(n):
                start_row_idx = k * m * row_a + i * m
                start_col_idx = k * m * col_a + j * m
                MatrixTensor[start_row_idx:start_row_idx + m, start_col_idx:start_col_idx + m] = temp_M

    return MatrixTensor


@njit(parallel=True, nogil=True)
def MatrixPermutation(A: np.ndarray, mapping: np.ndarray, changeInput: bool = False) -> np.ndarray:
    """ permute A with mapping, inplace

    Args:
        A(np.array<np.complex>): the matrix A
        mapping(np.ndarray<int>): the qubit mapping
        changeInput(bool): whether changes in A
    """
    if not A.shape[0] == (1 << mapping.shape[0]):
        raise IndexError("Indices do not match!")

    idx_mapping = mapping_augment(mapping)

    # Do NOT perform parallel operations over row permutations!
    # They are just too spare in memory. Elements in the same column
    # are distributed with a gap as matrix row length.
    perm_mat = A[idx_mapping, :]
    for i in prange(idx_mapping.shape[0]):
        perm_mat[i] = perm_mat[i][idx_mapping]

    if changeInput:
        A[:, :] = perm_mat

    return perm_mat


@njit()
def VectorPermutation(A: np.ndarray, mapping: np.ndarray, changeInput: bool = False):
    """ permutaion A with mapping, changeInput

    Args:
        A(np.array<np.complex>): the matrix A
        mapping(np.ndarray<int>): the qubit mapping
        changeInput(bool): whether changes in A
    Returns:
        np.array<np.complex>: the result of Permutation
    """
    if not A.shape[0] == 1 << mapping.shape[0]:
        raise IndexError("Indices do not match!")

    unchanged_mapping = True
    for i in range(mapping.size):
        if mapping[i] != i:
            unchanged_mapping = False
            break

    if unchanged_mapping:
        return A

    switched_idx = mapping_augment(mapping)

    if changeInput:
        A[:] = A[switched_idx]

    return A[switched_idx]


@njit(parallel=True, nogil=True)
def tensor(A: np.ndarray, B: np.ndarray):
    """ Applying the tensor operator between A and B.

    Args:
        A(np.array<np.complex>): the matrix A
        B(np.array<np.complex>): the matrix B

    Returns:
        np.array<np.complex>: the tensor result A ⊗ B
    """
    row_a, col_a = A.shape
    row_b, col_b = B.shape
    tensor_data = np.empty((row_a * row_b, col_a * col_b), dtype=A.dtype)

    for r in prange(row_a):
        for c in prange(col_a):
            tensor_data[r * row_b:(r + 1) * row_b, c * col_b:(c + 1) * col_b] = A[r, c] * B

    return tensor_data


@njit()
def dot(A: np.ndarray, B: np.ndarray):
    """ Applying the dot operator between A and B

    Args:
        A(np.array<np.complex>): the matrix A
        B(np.array<np.complex>): the matrix B

    Returns:
        np.array<np.complex>: A * B
    """
    return np.dot(A, B)


@njit()
def multiply(A: np.ndarray, B: np.ndarray):
    """ Applying the multiply operator between A and B

    Args:
        A(np.array<np.complex>): the matrix A
        B(np.array<np.complex>): the matrix B

    Returns:
        np.array<np.complex>: A x B
    """
    return np.multiply(A, B)


@njit()
def array_combination(A: np.ndarray, qubits: int, block_qubits: int):
    """ Applying the array combination of A and block qubits

    Args:
        A(np.array<np.complex>): the state vector A
        qubits(int): the qubit number of A
        block_qubits(int): the block qubit number

    Returns:
        np.array<np.complex>: [1 << qubits - block_qubits]
    """
    task_number = 1 << (qubits - block_qubits)
    block_dim = 1 << block_qubits
    out_array = np.empty(task_number, dtype=A.dtype)

    for i in prange(task_number):
        s_idx = i * block_dim
        out_array[i] = np.abs(A[s_idx]) * np.abs(A[s_idx])
        for j in range(1, block_dim):
            out_array[i] += np.abs(A[s_idx + j]) * np.abs(A[s_idx + j])

    return out_array


@njit(nogil=True)
def sv_sampling(A: np.ndarray, shots: int, num_qubits: int, target_qubits: list = None, seed: int = -1):
    if seed != -1:
        np.random.seed(seed)

    max_prob = A[-1]
    shot_list = np.empty(shots, dtype=np.int32)

    for i in prange(shots):
        random_val = np.random.random() * max_prob
        curr_idx = find_cdf_index(A, random_val, num_qubits)

        if target_qubits is not None:
            related_idx = 0
            for tqubit in target_qubits:
                related_idx <<= 1
                if curr_idx & (1 << (num_qubits - 1 - tqubit)) > 0:
                    related_idx += 1

            curr_idx = related_idx

        shot_list[i] = curr_idx

    return shot_list


@njit(nogil=True)
def sv_sampling_for_all_qubits(A: np.ndarray, shots: int, num_qubits: int, seed: int = -1):
    if seed != -1:
        np.random.seed(seed)

    max_prob = A[-1]
    shot_list = np.empty(shots, dtype=np.int32)

    for i in prange(shots):
        random_val = np.random.random() * max_prob
        curr_idx = find_cdf_index(A, random_val, num_qubits)
        shot_list[i] = curr_idx

    return shot_list


@njit(nogil=True)
def sv_probability(A: np.ndarray, num_qubits: int, target_qubits: np.ndarray):
    prob_sv = np.square(np.abs(A))
    sum_prob_sv = np.sum(prob_sv)

    if sum_prob_sv != 1:
        prob_sv /= sum_prob_sv

    if target_qubits is not None:
        partial_prob_sv = np.zeros(1 << target_qubits.size, dtype=np.float64)
        for i in prange(prob_sv.size):
            related_idx = 0
            for tqubit in target_qubits:
                related_idx <<= 1
                if i & (1 << (num_qubits - 1 - tqubit)) > 0:
                    related_idx += 1

            partial_prob_sv[related_idx] += prob_sv[i]

        return partial_prob_sv

    return prob_sv


@njit(nogil=True)
def partial_sv_sampling_for_all_qubits(
    A: np.ndarray, state_vector: np.ndarray, shots: int, num_qubits: int, block_qubits: int, seed: int = -1
):
    if seed != -1:
        np.random.seed(seed)

    max_prob = A[-1]
    shot_list = np.empty(shots, dtype=np.int32)

    block_dim = 1 << block_qubits
    for i in prange(shots):
        random_val = np.random.random() * max_prob
        curr_idx = find_cdf_index(A, random_val, num_qubits - block_qubits)
        block_prob = np.cumsum(
            np.square(np.abs(state_vector[block_dim * curr_idx: block_dim * (curr_idx + 1)]))
        )
        block_rval = np.random.random() * block_prob[-1]
        real_idx = find_cdf_index(block_prob, block_rval, block_qubits)
        shot_list[i] = block_dim * curr_idx + real_idx

    return shot_list


@njit(nogil=True)
def partial_sv_sampling(
    A: np.ndarray, state_vector: np.ndarray,
    shots: int, num_qubits: int, block_qubits: int,
    target_qubits: list = None, seed: int = -1
):
    if seed != -1:
        np.random.seed(seed)

    max_prob = A[-1]
    shot_list = np.empty(shots, dtype=np.int32)

    block_dim = 1 << block_qubits
    for i in prange(shots):
        random_val = np.random.random() * max_prob
        curr_idx = find_cdf_index(A, random_val, num_qubits - block_qubits)

        block_prob = np.cumsum(
            np.square(np.abs(state_vector[block_dim * curr_idx: block_dim * (curr_idx + 1)]))
        )
        block_rval = np.random.random() * block_prob[-1]
        real_idx = block_dim * curr_idx + find_cdf_index(block_prob, block_rval, block_qubits)

        if target_qubits is not None:
            related_idx = 0
            for tqubit in target_qubits:
                related_idx <<= 1
                if real_idx & (1 << (num_qubits - 1 - tqubit)) > 0:
                    related_idx += 1

            real_idx = related_idx

        shot_list[i] = real_idx

    return shot_list


def matrix_dot_matrix(
    matrix_u: np.ndarray,
    matrix_g: np.ndarray,
    control_args: np.ndarray = None,
    target_args: np.ndarray = None
):
    """ Dot the quantum gate's matrix and qubits'state vector, depending on the target qubits of gate.

    Args:
        matrix_u (np.ndarray): The 2D numpy array, represent the unitary matrix / density matrix
        matrix_g (np.ndarray): The 2D numpy array, represent the quantum gate's matrix
        control_args (np.ndarray): The control qubits of quantum gate
        target_args (np.ndarray): The target qubits of quantum gate

    Raises:
        TypeError: matrix and vector should be complex and with same precision

    Returns:
        np.ndarray: updated state vector
    """
    # Step 1: Calculate mat_bit and vec_bit
    mat_bit = int(np.log2(matrix_u.shape[0]))
    if control_args is None and target_args is None:
        assert mat_bit == int(np.log2(matrix_g.shape[0])), \
            "matrix dot matrix should have same qubits number, if not assigned gate_args."
        np.dot(matrix_g, matrix_u, out=matrix_u)
        return

    # Step 2: Get fixed index of vector by control indexes
    based_idx = 0
    if control_args is not None:
        for carg_idx in control_args:
            based_idx += 1 << carg_idx

    arg_len = 1 << len(target_args)
    indexes = np.repeat(based_idx, arg_len)
    for idx in range(1, arg_len):
        for tidx in range(len(target_args)):
            if idx & (1 << tidx):
                indexes[idx] += 1 << target_args[tidx]

    gate_args = np.append(control_args, target_args) if control_args is not None else target_args
    sorted_args = gate_args.copy()
    sorted_args = np.sort(sorted_args)

    # Step 4: normal matrix * matrix
    _matrix_dot_matrix(matrix_u, mat_bit, matrix_g, len(gate_args), indexes, sorted_args)


@njit()
def _matrix_dot_matrix(
    mat_u: np.ndarray,
    mat_bit: int,
    mat_g: np.ndarray,
    gate_bit: int,
    indexes: np.ndarray,
    sorted_args: np.ndarray
):
    repeat = 1 << (mat_bit - gate_bit)
    minus_1 = np.array([(1 << sarg) - 1 for sarg in sorted_args], dtype=np.int32)
    for i in prange(repeat):
        for sarg_idx in range(gate_bit):
            less = i & minus_1[sarg_idx]
            i = (i >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

        col_idx = indexes + i
        for j in prange(repeat):
            for sarg_idx in range(gate_bit):
                less = j & minus_1[sarg_idx]
                j = (j >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

            row_idx = indexes + j
            for cidx in col_idx:
                mat_u[row_idx, cidx] = np.dot(mat_g, mat_u[row_idx, cidx])
