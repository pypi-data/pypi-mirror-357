from typing import Tuple

import numpy as np


def schmidt_decompose(state_vector: np.ndarray, A_qubits: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""
    A quantum state $|\psi\rangle$ of a composite system A, B could be decomposed as
    $$
    |\psi\rangle = \sum \lambda_i |i_A\rangle |i_B\rangle,
    $$
    where $\lambda_i$ are non-negative real numbers, $\sum \lambda_i^2 = 1$,
    while $|i_A\rangle, |i_B\rangle$ are orthonormal states.
    Such decomposition is called Schmidt decomposition, the $\lambda_i$ are called Schmidt coefficients,
    the number of non-zero $\lambda_i$ is called Schmidt number,
    and $|i_A\rangle, |i_B\rangle$ are called Schmidt bases.

    In this function, we restrict $A$ and $B$ to be the first several qubits and the last several qubits respectively.

    Args:
        state_vector (np.ndarray): the state vector of the given state
        A_qubits (int): the number of the first qubits corresponding to $A$

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: $\lambda_i, |i_A\rangle, |i_B\rangle$ respectively
    """
    state_vector = np.array(state_vector)
    num_qubits = int(np.log2(state_vector.size))
    assert state_vector.ndim == 1 and 1 << num_qubits == state_vector.size,\
        ValueError('Quantum state should be an array with length 2^n')
    assert isinstance(A_qubits, int) and 0 < A_qubits and A_qubits < num_qubits,\
        ValueError('System A should have less qubits than total')
    B_qubits = num_qubits - A_qubits

    state_vector = state_vector.reshape(1 << A_qubits, 1 << B_qubits)
    U, d, V = np.linalg.svd(state_vector, full_matrices=False)
    return d, U.T, V
