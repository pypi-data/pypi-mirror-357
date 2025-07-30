from typing import Tuple
import numpy as np
import scipy as sp

from QuICT.core import *
from QuICT.core.gate import *


def add_factor_shift_into_phase(gates: CompositeGate, shift: complex) -> CompositeGate:
    phase = np.angle(shift)
    if not np.isclose(phase, 0):
        phase_gate = GPhase(phase) & gates.qubits[0]
        gates.append(phase_gate)
    return gates


def quantum_shannon_decompose(
        u1: np.ndarray,
        u2: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Decompose a block diagonal even-size unitary matrix.
    block_diag(u1,u2) == block_diag(v, v) @ block_diag(d, d_dagger) @ block_diag(w, w)

    Args:
        u1 (np.ndarray): upper-left block
        u2 (np.ndarray): right-bottom block

    Returns:
        Tuple[np.ndarray,np.ndarray,np.ndarray]
    """
    s = u1 @ u2.conj().T

    d, v = sp.linalg.schur(s)
    v_dagger = v.conj().T
    d = np.sqrt(np.diag(np.diagonal(d)))
    w = d @ v_dagger @ u2

    return v, d, w


def shift_ratio(mat1: np.ndarray, mat2: np.ndarray) -> complex:
    return mat1.dot(np.linalg.inv(mat2))[0, 0]


def diagonal_ury_gate(alpha,
                      ancilla: int = 0,
                      opt: bool = False,
                      include_phase_gate: bool = False):
    """
    Args:
        qubit_num (int):the  number of qubits in the circuit
        alpha (list): the list of rotation angles
        ancilla (int): the number of ancillary qubits
        opt (bool): the switch of cnot optimizer
        include_phase_gate (bool): the switch of phase holder

    Returns:
        Tuple[CompositeGate, list]:
        gates are the diagonal equivalent of URy gates;
        qubit[:dg.width()] is the position of all qubits
    """
    gates = CompositeGate()
    # qubit_num - k - 1 = posi, Here k is from QSP method
    posi = int(np.floor(np.log2(len(alpha))))

    S_dagger | gates(posi)
    H | gates(posi)

    gate_dg, qubit_list = diagonal_urz_gate(alpha, ancilla, opt, include_phase_gate)
    gate_dg | gates

    H | gates(posi)
    S | gates(posi)

    return gates, qubit_list


def diagonal_urz_gate(alpha,
                      ancilla: int = 0,
                      opt: bool = False,
                      include_phase_gate: bool = False):
    """
    Args:
        qubit_num (int):the  number of qubits in the circuit
        alpha (list): the list of rotation angles
        ancilla (int): the number of ancillary qubits
        opt (bool): the switch of cnot optimizer
        include_phase_gate (bool): the switch of phase holder

    Returns:
        Tuple[CompositeGate, list]:
        gates are the diagonal equivalent of URz gates;
        qubit[:dg.width()] is the position of all qubits
    """

    gates = CompositeGate()
    angles = np.vstack((-alpha / 2, alpha / 2)).T.flatten()

    n = int(round(np.log2(angles.size)))
    # TODO(2023.12.22): the choice of m
    m = min((1 << n), ancilla)
    m = m - 1 if m % 2 != 0 else m
    if m != 0:
        t = int(np.floor(np.log2(m / 2)))
        if t == 0 or n - t == 0:
            m = 0
        elif int(np.floor(m / (2 * (n - t)))) <= 0:
            m = 0

    diag = DiagonalGate(n, m, opt, include_phase_gate)
    qubit = list(range(n)) + list(range(n, n + m))

    dg = diag(angles)
    dg & qubit[:dg.width()] | gates

    return gates, qubit[:dg.width()]
