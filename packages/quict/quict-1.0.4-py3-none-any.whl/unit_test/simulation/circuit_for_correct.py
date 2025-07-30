import numpy as np
from random import shuffle
from scipy.stats import unitary_group

from QuICT.core import Circuit
from QuICT.core.gate import (
    gate_builder, GATEINFO_MAP, Unitary, MatrixType,
    CRz, CU1, CX, FSim, Rxx, Rzz, Rzx
)


def generate_qindex(qubits, gate_args):
    # Build qindexes without any order
    qindexes = []
    qindexes.append(np.random.choice(qubits, gate_args, replace=False))

    if gate_args >= 2:
        incr_qidxes = np.sort(np.random.choice(qubits, gate_args, replace=False))
        incr_qidxes.sort()
        decr_qidxes = np.sort(np.random.choice(qubits, gate_args, replace=False))
        decr_qidxes.sort()
        # Build qindexes with incr/decre
        qindexes.append(incr_qidxes)
        qindexes.append(decr_qidxes[::-1])

    return qindexes


def generate_unitary_gate(qubits):
    matrix = unitary_group.rvs(2 ** 3)
    diag_matrix = CRz(np.pi / 2).matrix
    control_matrix = CU1(0.5).matrix
    reverse_matrix = CX.matrix
    ctrl_nor_matrix = FSim(np.pi, 1).matrix
    nor_nor_matrix = Rxx(np.pi / 2).matrix
    diag_diag_matrix = Rzz(0.5).matrix
    diag_norm_matrix = Rzx(np.pi).matrix
    unitary_list = [
        matrix, diag_matrix, reverse_matrix, control_matrix,
        nor_nor_matrix, ctrl_nor_matrix, diag_diag_matrix, diag_norm_matrix
    ]
    unitary_gate_list = []
    for umat in unitary_list:
        ugate = Unitary(umat)
        qindexes = generate_qindex(qubits, ugate.controls + ugate.targets)
        for qidxes in qindexes:
            unitary_gate_list.append(ugate.copy() & list(qidxes))

    return unitary_gate_list


def create_circuit_for_correct(qubits: int, with_unitary: bool = True):
    cir = Circuit(qubits)
    except_gates = []
    gate_list = []
    for gate_type, gate_info in GATEINFO_MAP.items():
        carg, targ, _, _, matrix_type = gate_info
        if matrix_type == MatrixType.special or gate_type in except_gates:
            continue

        real_gate = gate_builder(gate_type, random_params=True)
        qindexes = generate_qindex(qubits, carg + targ)
        for qidxes in qindexes:
            gate_list.append(real_gate.copy() & list(qidxes))

    if with_unitary:
        gate_list.extend(generate_unitary_gate(qubits))

    shuffle(gate_list)
    for gate in gate_list:
        gate | cir

    return cir
