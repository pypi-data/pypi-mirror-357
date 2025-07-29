import random
from numba import njit, prange
import numpy as np


__outward_functions = [
    "matrix_dot_vector",
    "diagonal_matrix",
    "swap_matrix",
    "reverse_matrix",
    "get_measured_probability",
    "measure_gate_apply",
    "reset_gate_apply"
]


def matrix_dot_vector(
    vec: np.ndarray,
    mat: np.ndarray,
    control_args: np.ndarray = None,
    target_args: np.ndarray = None
):
    """ Dot the quantum gate's matrix and qubits'state vector, depending on the target qubits of gate.

    Args:
        vec (np.ndarray): The state vector of qubits
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix
        control_args (np.ndarray): The control qubits of quantum gate
        target_args (np.ndarray): The target qubits of quantum gate

    Raises:
        TypeError: matrix and vector should be complex and with same precision

    Returns:
        np.ndarray: updated state vector
    """
    # Step 1: Calculate mat_bit and vec_bit
    vec_bit = int(np.log2(vec.shape[0]))
    mat_bit = int(np.log2(mat.shape[0]))
    if control_args is None and target_args is None:
        assert vec_bit == mat_bit, "matrix dot state vector should have same qubits number."
        vec = np.dot(mat, vec)
        return

    # Step 2: Get fixed index of vector by control indexes
    based_idx = 0
    if control_args is not None:
        for carg_idx in control_args:
            based_idx += 1 << carg_idx

    # Step 3: Get related index of vector by target indexes
    if target_args is None:
        raise ValueError("Cannot dot a quantum gate's matrix with no target qubit indexes.")

    arg_len = 1 << len(target_args)
    indexes = np.repeat(based_idx, arg_len)
    for idx in range(1, arg_len):
        for midx in range(mat_bit):
            if idx & (1 << midx):
                indexes[idx] += 1 << target_args[midx]

    mat_args = np.append(control_args, target_args) if control_args is not None else target_args
    sorted_args = mat_args.copy()
    sorted_args = np.sort(sorted_args)

    # Step 4: normal matrix * vec
    _matrix_dot_vector(vec, vec_bit, mat, len(mat_args), indexes, sorted_args)


@njit()
def _matrix_dot_vector(
    vec: np.ndarray,
    vec_bit: int,
    mat: np.ndarray,
    mat_bit: int,
    indexes: np.ndarray,
    sorted_args: np.ndarray
):
    repeat = 1 << (vec_bit - mat_bit)
    minus_1 = np.array([(1 << sarg) - 1 for sarg in sorted_args], dtype=np.int32)
    for i in prange(repeat):
        for sarg_idx in range(mat_bit):
            less = i & minus_1[sarg_idx]
            i = (i >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

        current_idx = indexes + i
        vec[current_idx] = np.dot(mat, vec[current_idx])


def diagonal_matrix(
    vec: np.ndarray,
    mat: np.ndarray,
    control_args: np.ndarray = None,
    target_args: np.ndarray = None,
    is_control: bool = False
):
    """ Applying the operator between diagonal matrix and state vector.

    Args:
        vec (np.ndarray): The state vector of qubits.
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix.
        control_args (np.ndarray): The control qubits of quantum gate.
        target_args (np.ndarray): The target qubits of quantum gate.
        is_control (bool): Whether the matrix type is Control or Diagonal.
    """
    # Step 1: Get diagonal value from gate_matrix
    diagonal_value = np.diag(mat)
    vec_bit = int(np.log2(vec.shape[0]))
    mat_bit = len(target_args)
    if control_args is None and target_args is None:
        assert vec_bit == mat_bit, "matrix dot state vector should have same qubits number."
        vec = np.multiply(diagonal_value, vec)
        return

    # Step 2: Get fixed index of vector by control indexes
    based_idx = 0
    for carg_idx in control_args:
        based_idx += 1 << carg_idx

    # Step 3: Get related index of vector by target indexes
    arg_len = 1 << len(target_args) if not is_control else 1
    indexes = np.repeat(based_idx, arg_len)
    if is_control:
        indexes[0] += 1 << target_args[0]
        diagonal_value = diagonal_value[-1]
    else:
        for idx in range(1, arg_len):
            for midx in range(mat_bit):
                if idx & (1 << midx):
                    indexes[idx] += 1 << target_args[midx]

    # Step 4: diagonal matrix * vec
    mat_args = np.append(control_args, target_args)
    sorted_args = mat_args.copy()
    sorted_args = np.sort(sorted_args)
    _diagonal_matrix(vec, vec_bit, diagonal_value, len(mat_args), indexes, sorted_args)


@njit()
def _diagonal_matrix(
    vec: np.ndarray,
    vec_bit: int,
    mat: np.ndarray,
    mat_bit: int,
    indexes: np.ndarray,
    sorted_args: np.ndarray
):
    repeat = 1 << (vec_bit - mat_bit)
    minus_1 = np.array([(1 << sarg) - 1 for sarg in sorted_args], dtype=np.int32)
    for i in prange(repeat):
        for sarg_idx in range(mat_bit):
            less = i & minus_1[sarg_idx]
            i = (i >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

        current_idx = indexes + i
        vec[current_idx] = np.multiply(vec[current_idx], mat)


def swap_matrix(
    vec: np.ndarray,
    mat: np.ndarray,
    control_args: np.ndarray = None,
    target_args: np.ndarray = None,
):
    """ Applying the operator between Swap Gate's matrix and state vector.

    Args:
        vec (np.ndarray): The state vector of qubits.
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix.
        control_args (np.ndarray): The control qubits of quantum gate.
        target_args (np.ndarray): The target qubits of quantum gate.
    """
    # Step 1: Deal with mat_bit == vec_bit
    valid_params = np.array([mat[-2, -3], mat[-3, -2]]) if len(target_args) > 1 else \
        np.array([mat[-2, -1], mat[-1, -2]])
    vec_bit = int(np.log2(vec.shape[0]))
    mat_bit = int(np.log2(mat.shape[0]))
    if control_args is None and target_args is None:
        assert vec_bit == mat_bit, "matrix dot state vector should have same qubits number."
        swap_idxes = [-1, -2] if len(target_args) == 1 else [-2, -3]
        temp_value = vec[swap_idxes[0]]
        vec[swap_idxes[0]] = vec[swap_idxes[1]] * valid_params[0]
        vec[swap_idxes[1]] = temp_value * valid_params[1]

        return

    # Step 2: Get fixed index of vector by control indexes
    based_index = 0
    for carg in control_args:
        based_index += 1 << carg

    # Step 3: Get related index of vector by target indexes
    swap_idxes = np.repeat(based_index, 2)
    if len(target_args) == 1:
        swap_idxes[1] += 1 << target_args[0]
    else:
        swap_idxes[0] += 1 << target_args[0]
        swap_idxes[1] += 1 << target_args[1]

    # Step 4: swap matrix * vec
    mat_args = np.append(control_args, target_args)
    sorted_args = mat_args.copy()
    sorted_args = np.sort(sorted_args)
    _swap_matrix(vec, valid_params, vec_bit, swap_idxes, sorted_args)


@njit()
def _swap_matrix(
    vec: np.ndarray,
    mat: np.ndarray,
    vec_bit: int,
    indexes: np.ndarray,
    sorted_args: np.ndarray
):
    mat_bit = len(sorted_args)
    repeat = 1 << (vec_bit - mat_bit)
    minus_1 = np.array([(1 << sarg) - 1 for sarg in sorted_args], dtype=np.int32)
    for i in prange(repeat):
        for sarg_idx in range(mat_bit):
            less = i & minus_1[sarg_idx]
            i = (i >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

        current_sidx = indexes + i
        temp_value = vec[current_sidx[0]]
        vec[current_sidx[0]] = vec[current_sidx[1]] * mat[0]
        vec[current_sidx[1]] = temp_value * mat[1]


def reverse_matrix(
    vec: np.ndarray,
    mat: np.ndarray,
    control_args: np.ndarray = None,
    target_args: np.ndarray = None,
):
    """ Applying the operator between Reverse Matrix and state vector.

    ** Do not support The Quantum Gate which has two or more target qubits.

    Args:
        vec (np.ndarray): The state vector of qubits.
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix.
        control_args (np.ndarray): The control qubits of quantum gate.
        target_args (np.ndarray): The target qubits of quantum gate.
    """
    # Step 1: Get swap matrix used value
    reverse_value = np.array([mat[-2, -1], mat[-1, -2]], dtype=vec.dtype)
    vec_bit = int(np.log2(vec.shape[0]))
    mat_bit = int(np.log2(mat.shape[0]))
    if control_args is None and target_args is None:
        assert vec_bit == mat_bit, "matrix dot state vector should have same qubits number."
        temp_value = vec[-2]
        vec[-2] = vec[-1] * reverse_value[0]
        vec[-1] = temp_value * reverse_value[1]

        return

    # Step 2: Get fixed index of vector by control indexes
    based_index = 0
    for carg in control_args:
        based_index += 1 << carg

    # Step 3: Get related index of vector by target indexes
    swap_idxes = np.repeat(based_index, 2)
    swap_idxes[1] += 1 << target_args[0]

    # Step 3: swap matrix * vec
    mat_args = np.append(control_args, target_args)
    sorted_args = mat_args.copy()
    sorted_args = np.sort(sorted_args)
    _reverse_matrix(vec, vec_bit, reverse_value, len(mat_args), swap_idxes, sorted_args)


@njit()
def _reverse_matrix(
    vec: np.ndarray,
    vec_bit: int,
    mat: np.ndarray,
    mat_bit: int,
    indexes: np.ndarray,
    sorted_args: np.ndarray
):
    repeat = 1 << (vec_bit - mat_bit)
    minus_1 = np.array([(1 << sarg) - 1 for sarg in sorted_args], dtype=np.int32)
    for i in prange(repeat):
        for sarg_idx in prange(mat_bit):
            less = i & minus_1[sarg_idx]
            i = (i >> sorted_args[sarg_idx] << (sorted_args[sarg_idx] + 1)) + less

        current_sidx = indexes + i
        temp_value = vec[current_sidx[0]]
        vec[current_sidx[0]] = vec[current_sidx[1]] * mat[0]
        vec[current_sidx[1]] = temp_value * mat[1]


@njit()
def get_measured_probability(
    index: int,
    vec: np.array
):
    """ Get the probability of measured 1.

    Args:
        index (int): The index of target qubit
        vec (np.array): The state vector of qubits
    """
    target_index = 1 << index
    vec_idx_0 = [idx for idx in range(len(vec)) if not idx & target_index]
    vec_idx_0 = np.array(vec_idx_0, dtype=np.int32)

    return np.sum(np.square(np.abs(vec[vec_idx_0])))


@njit()
def measure_gate_apply(
    index: int,
    vec: np.array,
    pauliZ: bool = False
):
    """ Measured the state vector for target qubit

    Args:
        index (int): The index of target qubit
        vec (np.array): The state vector of qubits

    Returns:
        bool: The measured result 0 or 1.
    """
    target_index = 1 << index
    vec_idx_0 = [idx for idx in range(len(vec)) if not idx & target_index]
    vec_idx_0 = np.array(vec_idx_0, dtype=np.int32)
    vec_idx_1 = [idx for idx in range(len(vec)) if idx & target_index]
    vec_idx_1 = np.array(vec_idx_1, dtype=np.int32)
    prob = np.sum(np.square(np.abs(vec[vec_idx_0])))
    if pauliZ:
        return prob

    _1 = random.random() > prob
    if _1:
        alpha = np.float64(1 / np.sqrt(1 - prob))
        vec[vec_idx_0] = np.complex128(0)
        vec[vec_idx_1] = vec[vec_idx_1] * alpha
    else:
        alpha = np.float64(1 / np.sqrt(prob))
        vec[vec_idx_0] = vec[vec_idx_0] * alpha
        vec[vec_idx_1] = np.complex128(0)

    return _1


@njit()
def reset_gate_apply(
    index: int,
    vec: np.array
):
    """ Reset the state vector for target qubit

    Args:
        index (int): The index of target qubit
        vec (np.array): The state vector of qubits
    """
    target_index = 1 << index
    vec_idx_0 = [idx for idx in range(len(vec)) if not idx & target_index]
    vec_idx_0 = np.array(vec_idx_0, dtype=np.int32)
    vec_idx_1 = [idx for idx in range(len(vec)) if idx & target_index]
    vec_idx_1 = np.array(vec_idx_1, dtype=np.int32)
    prob = np.sum(np.square(np.abs(vec[vec_idx_0])))

    alpha = np.float64(np.sqrt(prob))
    if alpha < 1e-6:
        vec[vec_idx_0] = vec[vec_idx_1]
        vec[vec_idx_1] = np.complex128(0)
    else:
        vec[vec_idx_0] = vec[vec_idx_0] / alpha
        vec[vec_idx_1] = np.complex128(0)
