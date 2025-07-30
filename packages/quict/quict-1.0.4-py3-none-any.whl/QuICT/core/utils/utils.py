from typing import Union
import numpy as np


CGATE_LIST = []
CGATE_HOLD = {}


def matrix_product_to_circuit(
    gate_matrix: np.ndarray,
    gate_args: Union[int, list],
    qubits: int,
    device: str = "CPU"
):
    """ Expand gate matrix with the number of qubits

    Args:
        gate_matrix (np.ndarray): The gate's matrix.
        gate_args Union[int, list]: The gate's qubit indexes.
        qubits (int): The qubits' number
        device(str, optional): Generate matrix in GPU or not. Default to CPU.

    Returns:
        np.array: the expanded gate's 2-D matrix
    """
    if isinstance(gate_args, int):
        gate_args = [gate_args]

    n = 1 << qubits
    xor = n - 1
    new_values = np.zeros((n, n), dtype=gate_matrix.dtype)
    assert gate_matrix.shape == (1 << len(gate_args), 1 << len(gate_args))
    for arg in gate_args:
        assert arg >= 0 and arg < qubits and isinstance(arg, int)

    datas = np.zeros(n, dtype=int)
    for i in range(n):
        nowi = 0
        for t_idx, targ in enumerate(gate_args):
            assert targ >= 0 and targ < qubits
            k = qubits - 1 - targ
            if (1 << k) & i != 0:
                nowi += (1 << (len(gate_args) - 1 - t_idx))

        datas[i] = nowi

    for i in gate_args:
        xor = xor ^ (1 << (qubits - 1 - i))

    for i in range(n):
        nowi = datas[i]
        for j in range(n):
            if (i & xor) == (j & xor):
                nowj = datas[j]
                new_values[i][j] = gate_matrix[nowi][nowj]

    if device == "GPU":
        import cupy as cp
        new_values = cp.array(new_values)

    return new_values
