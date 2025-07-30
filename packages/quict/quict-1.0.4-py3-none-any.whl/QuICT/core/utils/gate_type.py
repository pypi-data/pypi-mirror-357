from enum import Enum
import numpy as np


class GateType(Enum):
    h = "H gate"
    hy = "Self-inverse gate"
    s = "S gate"
    sdg = "The conjugate transpose of Phase gate"
    x = "Pauli-X gate"
    y = "Pauli-Y gate"
    z = "Pauli-Z gate"
    sx = "sqrt(X) gate"
    sxdg = "The conjugate transpose of sqrt(X) gate"
    sy = "sqrt(Y) gate"
    sydg = "The conjugate transpose of sqrt(Y) gate"
    sw = "sqrt(W) gate"
    id = "Identity gate"
    u1 = "U1 gate"
    u2 = "U2 gate"
    u3 = "U3 gate"
    rx = "Rx gate"
    ry = "Ry gate"
    rz = "Rz gate"
    t = "T gate"
    tdg = "The conjugate transpose of T gate"
    phase = "Phase gate"
    gphase = "Global Phase gate"

    # QCIS Gate
    rxy = "RXY gate"
    xy = "XY gate"
    xy2p = "XY2P gate"
    xy2m = "XY2M gate"

    # 2-q gates
    cz = "controlled-Z gate"
    cx = "controlled-X gate"
    cy = "controlled-Y gate"
    ch = "controlled-Hadamard gate"
    cry = "controlled-Ry gate"
    crz = "controlled-Rz gate"
    cu1 = "controlled-U1 gate"
    cu3 = "controlled-U3 gate"
    fsim = "fSim gate"
    ecr = "ECR gate"
    rxx = "Rxx gate"
    ryy = "Ryy gate"
    rzz = "Rzz gate"
    rzx = "Rzx gate"
    swap = "Swap gate"
    cswap = "cswap gate"
    iswap = "iswap gate"
    iswapdg = "The conjugate transpose of iswap gate"
    sqiswap = "square root of iswap gate"
    ccx = "Toffoli gate"
    ccz = "Multi-Control Z Gate"
    ccrz = "CCRz gate"
    rccx = "simplified Toffoli gate, or Margolus gate"

    # Special gate below
    measure = "Measure gate"
    measurex = "Pauli X Measure gate"
    measurey = "Pauli Y Measure gate"
    reset = "Reset gate"
    barrier = "Barrier gate"
    unitary = "Unitary gate"
    kraus = "Kraus Gate, only for Noised Circuit"
    multi_control = "Multi_Control Gate"

    # no qasm represent below
    perm = "Permutation gate"
    perm_fx = "Perm-Fx gate"


class MatrixType(Enum):
    r""" Different Type of quantum gates' matrix

    - normal: based type of matrix

        Single Qubit:

        $$ \begin{bmatrix}
        v_{00} & v_{01} \\
        v_{10} & v_{11} \\
        \end{bmatrix}
        $$

        Bi-Qubits (1 control + 1 target):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & v_{00} & v_{01} \\
        0 & 0 & v_{10} & v_{11} \\
        \end{bmatrix}
        $$

    - diagonal: diagonal matrix

        Single Qubit:

        $$ \begin{bmatrix}
        v_{00} & 0 \\
        0 & v_{11} \\
        \end{bmatrix}
        $$

        Bi-Qubits (1 control + 1 target):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & v_{00} & 0 \\
        0 & 0 & 0 & v_{11} \\
        \end{bmatrix}
        $$

        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        v_{00} & 0 & 0 & 0 \\
        0 & v_{11} & 0 & 0 \\
        0 & 0 & v_{22} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        $$

        Tri-Qubits (2 controls + 1 target):

        $$
        \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & v_{00} & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & v_{11} \\
        \end{bmatrix}
        $$

    - control: control diagonal matrix

        Single Qubit:

        $$ \begin{bmatrix}
        1 & 0 \\
        0 & v_{00} \\
        \end{bmatrix}
        $$

        Bi-Qubits (1 control + 1 target):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 0 & 0 & v_{00} \\
        \end{bmatrix}
        $$

    - swap: swap quantum gates' matrix

        Single Qubit:

        $$ \begin{bmatrix}
        0 & 1 \\
        1 & 0 \\
        \end{bmatrix}
        $$

        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 1 \\
        \end{bmatrix}
        $$

        Tri-Qubits (1 controls + 2 targets):

        $$
        \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        \end{bmatrix}
        $$

    - reverse; reverse matrix

        Single Qubit:

        $$ \begin{bmatrix}
        0 & v_{01} \\
        v_{10} & 0 \\
        \end{bmatrix}
        $$

        Bi-Qubits (1 control + 1 target):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 0 & v_{01} \\
        0 & 0 & v_{10} & 0 \\
        \end{bmatrix}
        $$

        Tri-Qubits (2 controls + 1 target):

        $$
        \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & v_{01} \\
        0 & 0 & 0 & 0 & 0 & 0 & v_{10} & 0 \\
        \end{bmatrix}
        $$

    - special: no matrix Gate, such as $Measure, Reset, Barrier, Perm$

    - diag_diag: 2-qubits diagonal matrix [TODO: Remove in open_test]

        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        v_{00} & 0 & 0 & 0 \\
        0 & v_{11} & 0 & 0 \\
        0 & 0 & v_{22} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        $$

    - ctrl_normal: control-normal mixed quantum gate's matrix
        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & v_{00} & v_{01} & 0 \\
        0 & v_{10} & v_{11} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        $$

    - normal-normal: normal-normal mixed quantum gate's matrix
        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        v_{00} & 0 & 0 & v_{03} \\
        0 & v_{11} & v_{12} & 0 \\
        0 & v_{21} & v_{22} & 0 \\
        v_{30} & 0 & 0 & v_{33} \\
        \end{bmatrix}
        $$

    - diagonal-normal: diagonal-normal mixed quantum gate's matrix
        Bi-Qubits (2 targets):

        $$ \begin{bmatrix}
        v_{00} & v_{01} & 0 & 0 \\
        v_{10} & v_{11} & 0 & 0 \\
        0 & 0 & v_{22} & v_{23} \\
        0 & 0 & v_{32} & v_{33} \\
        \end{bmatrix}
        $$

    """
    identity = "identity matrix"
    normal = "normal matrix"
    diagonal = "diagonal matrix"
    control = "control matrix"
    swap = "swap matrix"
    reverse = "reverse matrix"
    special = "special matrix"
    diag_diag = "diagonal * diagonal"
    ctrl_normal = "control * matrix"
    normal_normal = "normal * normal"
    diag_normal = "diagonal * normal"


# Mapping: GateType: (controls, targets, parameters, type, matrix_type)
GATEINFO_MAP = {
    GateType.h: (0, 1, 0, GateType.h, MatrixType.normal),
    GateType.hy: (0, 1, 0, GateType.hy, MatrixType.normal),
    GateType.s: (0, 1, 0, GateType.s, MatrixType.control),
    GateType.sdg: (0, 1, 0, GateType.sdg, MatrixType.control),
    GateType.x: (0, 1, 0, GateType.x, MatrixType.swap),
    GateType.y: (0, 1, 0, GateType.y, MatrixType.reverse),
    GateType.z: (0, 1, 0, GateType.z, MatrixType.control),
    GateType.sx: (0, 1, 0, GateType.sx, MatrixType.normal),
    GateType.sxdg: (0, 1, 0, GateType.sxdg, MatrixType.normal),
    GateType.sy: (0, 1, 0, GateType.sy, MatrixType.normal),
    GateType.sydg: (0, 1, 0, GateType.sydg, MatrixType.normal),
    GateType.sw: (0, 1, 0, GateType.sw, MatrixType.normal),
    GateType.id: (0, 1, 0, GateType.id, MatrixType.identity),
    GateType.u1: (0, 1, 1, GateType.u1, MatrixType.control),
    GateType.u2: (0, 1, 2, GateType.u2, MatrixType.normal),
    GateType.u3: (0, 1, 3, GateType.u3, MatrixType.normal),
    GateType.rx: (0, 1, 1, GateType.rx, MatrixType.normal),
    GateType.ry: (0, 1, 1, GateType.ry, MatrixType.normal),
    GateType.rz: (0, 1, 1, GateType.rz, MatrixType.diagonal),
    GateType.t: (0, 1, 0, GateType.t, MatrixType.control),
    GateType.tdg: (0, 1, 0, GateType.tdg, MatrixType.control),
    GateType.phase: (0, 1, 1, GateType.phase, MatrixType.control),
    GateType.gphase: (0, 1, 1, GateType.gphase, MatrixType.diagonal),
    GateType.rxy: (0, 1, 2, GateType.rxy, MatrixType.normal),
    GateType.xy: (0, 1, 1, GateType.xy, MatrixType.reverse),
    GateType.xy2p: (0, 1, 1, GateType.xy2p, MatrixType.normal),
    GateType.xy2m: (0, 1, 1, GateType.xy2m, MatrixType.normal),
    GateType.cz: (1, 1, 0, GateType.cz, MatrixType.control),
    GateType.cx: (1, 1, 0, GateType.cx, MatrixType.reverse),
    GateType.cy: (1, 1, 0, GateType.cy, MatrixType.reverse),
    GateType.ch: (1, 1, 0, GateType.ch, MatrixType.normal),
    GateType.cry: (1, 1, 1, GateType.cry, MatrixType.normal),
    GateType.crz: (1, 1, 1, GateType.crz, MatrixType.diagonal),
    GateType.cu1: (1, 1, 1, GateType.cu1, MatrixType.control),
    GateType.cu3: (1, 1, 3, GateType.cu3, MatrixType.normal),
    GateType.fsim: (0, 2, 2, GateType.fsim, MatrixType.ctrl_normal),
    GateType.ecr: (0, 2, 0, GateType.ecr, MatrixType.normal),
    GateType.rxx: (0, 2, 1, GateType.rxx, MatrixType.normal_normal),
    GateType.ryy: (0, 2, 1, GateType.ryy, MatrixType.normal_normal),
    GateType.rzz: (0, 2, 1, GateType.rzz, MatrixType.diag_diag),
    GateType.rzx: (0, 2, 1, GateType.rzx, MatrixType.diag_normal),
    GateType.measure: (0, 1, 0, GateType.measure, MatrixType.special),
    GateType.measurex: (0, 1, 0, GateType.measurex, MatrixType.special),
    GateType.measurey: (0, 1, 0, GateType.measurey, MatrixType.special),
    GateType.reset: (0, 1, 0, GateType.reset, MatrixType.special),
    GateType.barrier: (0, 1, 0, GateType.barrier, MatrixType.special),
    GateType.swap: (0, 2, 0, GateType.swap, MatrixType.swap),
    GateType.iswap: (0, 2, 0, GateType.iswap, MatrixType.swap),
    GateType.iswapdg: (0, 2, 0, GateType.iswapdg, MatrixType.swap),
    GateType.sqiswap: (0, 2, 0, GateType.sqiswap, MatrixType.ctrl_normal),
    GateType.ccx: (2, 1, 0, GateType.ccx, MatrixType.reverse),
    GateType.ccz: (2, 1, 0, GateType.ccz, MatrixType.control),
    GateType.ccrz: (2, 1, 1, GateType.ccrz, MatrixType.diagonal),
    GateType.cswap: (1, 2, 0, GateType.cswap, MatrixType.swap),
    GateType.rccx: (2, 1, 0, GateType.rccx, MatrixType.normal),     # TODO: rccx matrix type can update
}

GATE_TO_CGATE = {
    GateType.h: (GateType.ch, None),
    GateType.x: (GateType.cx, None),
    GateType.y: (GateType.cy, None),
    GateType.z: (GateType.cz, None),
    GateType.u1: (GateType.cu1, None),
    GateType.u3: (GateType.cu3, None),
    GateType.phase: (GateType.cu1, None),
    GateType.ry: (GateType.cry, None),
    GateType.rz: (GateType.crz, None),
    GateType.s: (GateType.cu1, [np.pi / 2]),
    GateType.sdg: (GateType.cu1, [-np.pi / 2]),
    GateType.t: (GateType.cu1, [np.pi / 4]),
    GateType.tdg: (GateType.cu1, [-np.pi / 4]),
    GateType.cx: (GateType.ccx, None),
    GateType.cz: (GateType.ccz, None),
    GateType.crz: (GateType.ccrz, None),
    GateType.swap: (GateType.cswap, None)
}


# Mapping: GateType: default_parameters
GATE_ARGS_MAP = {
    GateType.u1: [np.pi / 2],
    GateType.u2: [np.pi / 2, np.pi / 2],
    GateType.u3: [0, 0, np.pi / 2],
    GateType.rx: [np.pi / 2],
    GateType.ry: [np.pi / 2],
    GateType.rz: [np.pi / 2],
    GateType.phase: [0],
    GateType.gphase: [0],
    # QCIS support
    GateType.rxy: [0, np.pi / 2],
    GateType.xy: [np.pi / 2],
    GateType.xy2p: [np.pi / 2],
    GateType.xy2m: [np.pi / 2],

    GateType.cry: [np.pi / 2],
    GateType.crz: [np.pi / 2],
    GateType.cu1: [np.pi / 2],
    GateType.cu3: [np.pi / 2, 0, 0],
    GateType.fsim: [np.pi / 2, 0],
    GateType.rxx: [0],
    GateType.ryy: [np.pi / 2],
    GateType.rzz: [np.pi / 2],
    GateType.rzx: [np.pi / 2],
    GateType.ccrz: [0],
}


PAULI_GATE_SET = [GateType.x, GateType.y, GateType.z, GateType.id]
DIAGONAL_GATE_SET = [
    GateType.rz, GateType.gphase, GateType.crz, GateType.ccrz, GateType.rzz, GateType.rzx
]
SINGLE_QUBIT_GATE_SET = [
    GateType.x, GateType.y, GateType.z, GateType.u1, GateType.u2, GateType.u3, GateType.tdg,
    GateType.sdg, GateType.h, GateType.hy, GateType.s, GateType.sx, GateType.sxdg, GateType.sydg,
    GateType.sy, GateType.sw, GateType.t, GateType.rx, GateType.ry, GateType.rz, GateType.id,
    GateType.phase, GateType.gphase, GateType.xy, GateType.rxy, GateType.xy2m, GateType.xy2p,
    GateType.measure, GateType.reset, GateType.barrier, GateType.measurex, GateType.measurey
]
CLIFFORD_GATE_SET = [
    GateType.x, GateType.y, GateType.z, GateType.h, GateType.s, GateType.sdg, GateType.cx
]
