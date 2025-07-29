from typing import Union

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate
import numpy as np


def cnot_f2_matrix(circuit: Union[Circuit, CompositeGate]) -> np.ndarray:
    n = circuit.width()
    mat = np.eye(n, dtype=np.int64)
    for cnot_gate in circuit.fast_gates:
        c = cnot_gate.carg
        t = cnot_gate.targ
        mat[t] += mat[c]
    mat[:, :] &= 1
    return mat


def cnot_eq(a: Union[Circuit, CompositeGate], b: Union[Circuit, CompositeGate]) -> bool:
    if a.width() != b.width():
        return False
    ma, mb = cnot_f2_matrix(a), cnot_f2_matrix(b)
    return np.all(ma == mb)
