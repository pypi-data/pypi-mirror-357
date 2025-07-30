import numpy as np

from QuICT.core.gate import *
from QuICT.qcda.synthesis.unitary_decomposition import CartanKAKDecomposition

# This file describes necessary transform rules between 2-qubit gates.
# The neccessity is decided by the categories defined in QuICT/core/virtual_machine/instruction_set.py
# Modify that file before trying to add more rules.


# Rules between categories
def cx2rzz_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    if keep_phase:
        GPhase(-np.pi / 4) & targs[0] | gates
    H & targs[1] | gates
    Rz(-np.pi / 2) & targs[0] | gates
    Rz(-np.pi / 2) & targs[1] | gates
    Rzz(np.pi / 2) & targs | gates
    H & targs[1] | gates
    return gates


def rzz2cx_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    CX & targs | gates
    Rz(theta) & targs[1] | gates
    CX & targs | gates
    return gates


def cx2fsim_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[1] | gates
    FSim(0, np.pi) & targs | gates
    H & targs[1] | gates
    return gates


def fsim2cx_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    kak = CartanKAKDecomposition(target='cx')
    gates = kak.execute(gate.matrix)
    gates & targs
    if keep_phase:
        phase = np.angle(gates.matrix()[0, 0])
        GPhase(-phase) & targs[0] | gates
    return gates


def rzz2fsim_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    theta = gate.pargs[0]
    gates = CompositeGate()
    if keep_phase:
        GPhase(theta / 2) & targs[0] | gates
    Rz(theta) & targs[0] | gates
    Rz(theta) & targs[1] | gates
    FSim(0, 2 * theta) & targs | gates
    return gates


def fsim2rzz_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    kak = CartanKAKDecomposition(target='rot')
    rot_gates = kak.execute(gate.matrix)
    gates = CompositeGate()
    for g in rot_gates:
        if g.type == GateType.rxx:
            gates.extend(rxx2rzz_rule(g, keep_phase=keep_phase))
        elif g.type == GateType.ryy:
            gates.extend(ryy2rzz_rule(g, keep_phase=keep_phase))
        else:
            gates.append(g)
    gates & targs
    if keep_phase:
        phase = np.angle(gates.matrix()[0, 0])
        GPhase(-phase) & targs[0] | gates
    return gates


# Rules within CX category


def cx2cy_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    S & targs[1] | gates
    CY & targs | gates
    S_dagger & targs[1] | gates
    return gates


def cy2cx_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    S_dagger & targs[1] | gates
    CX & [targs[0], targs[1]] | gates
    S & targs[1] | gates
    return gates


def cx2cz_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[1] | gates
    CZ & targs | gates
    H & targs[1] | gates
    return gates


def cz2cx_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[1] | gates
    CX & [targs[0], targs[1]] | gates
    H & targs[1] | gates
    return gates


def cx2ch_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    T & targs[1] | gates
    Rx(np.pi / 2) & targs[1] | gates
    CH & targs | gates
    Rx(-np.pi / 2) & targs[1] | gates
    T_dagger & targs[1] | gates
    return gates


def ch2cx_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rx(-np.pi / 2) & targs[1] | gates
    T_dagger & targs[1] | gates
    CX & targs | gates
    T & targs[1] | gates
    Rx(np.pi / 2) & targs[1] | gates
    return gates


def cx2ecr_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()

    Rz(np.pi / 2) & targs[0] | gates
    X & targs[0] | gates
    SX & targs[1] | gates
    ECR & targs | gates
    return gates


def ecr2cx_rule(gate, keep_phase=True):
    targs = gate.cargs + gate.targs
    gates = CompositeGate()

    X & targs[0] | gates
    Rz(-np.pi / 2) & targs[0] | gates
    SX_dagger & targs[1] | gates
    CX & targs | gates
    return gates


# Rules within Rzz category


def rzz2crz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rz(theta) & targs[1] | gates
    CRz(-2 * theta) & targs | gates
    return gates


def crz2rzz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rz(theta / 2) & targs[1] | gates
    Rzz(-theta / 2) & targs | gates
    return gates


def rzz2cry_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rz(theta) & targs[1] | gates
    Rx(-np.pi / 2) & targs[1] | gates
    CRy(-2 * theta) & targs | gates
    Rx(np.pi / 2) & targs[1] | gates
    return gates


def cry2rzz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rx(np.pi / 2) & targs[1] | gates
    Rz(theta / 2) & targs[1] | gates
    Rzz(-theta / 2) & targs | gates
    Rx(-np.pi / 2) & targs[1] | gates
    return gates


def rzz2rxx_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[0] | gates
    H & targs[1] | gates
    Rxx(theta) & targs | gates
    H & targs[0] | gates
    H & targs[1] | gates
    return gates


def rxx2rzz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[0] | gates
    H & targs[1] | gates
    Rzz(theta) & targs | gates
    H & targs[1] | gates
    H & targs[0] | gates
    return gates


def rzz2ryy_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rx(-np.pi / 2) & targs[0] | gates
    Rx(-np.pi / 2) & targs[1] | gates
    Ryy(theta) & targs | gates
    Rx(np.pi / 2) & targs[1] | gates
    Rx(np.pi / 2) & targs[0] | gates
    return gates


def ryy2rzz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    Rx(np.pi / 2) & targs[0] | gates
    Rx(np.pi / 2) & targs[1] | gates
    Rzz(theta) & targs | gates
    Rx(-np.pi / 2) & targs[1] | gates
    Rx(-np.pi / 2) & targs[0] | gates
    return gates


def rzz2rzx_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[1] | gates
    Rzx(theta) & targs | gates
    H & targs[1] | gates
    return gates


def rzx2rzz_rule(gate, keep_phase=True):
    theta = gate.pargs[0]
    targs = gate.cargs + gate.targs
    gates = CompositeGate()
    H & targs[1] | gates
    Rzz(theta) & targs | gates
    H & targs[1] | gates
    return gates
