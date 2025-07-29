"""
the file describe transform rules that decompose SU(2) into instruction set.
"""

import numpy as np
from numpy import arccos, linalg

from QuICT.core.gate import *


def _arccos(value):
    """ calculate arccos(value)

    Args:
        value: the cos value

    Returns:
        float: the corresponding angle
    """
    if value < -1:
        value = -1
    elif value > 1:
        value = 1
    return arccos(value)


def _check2pi(theta, eps=1e-15):
    """ check whether theta is a multiple of 2π

    Args:
        theta(float): the angle to be checked
        eps(float): tolerate error

    Returns:
        bool: whether theta is a multiple of 2π
    """
    multiple = np.round(theta / (2 * np.pi))
    return abs(2 * np.pi * multiple - theta) < eps


def _check_pi(theta, eps=1e-15):
    theta_mod = theta % (2 * np.pi)

    return abs(theta_mod / np.pi - 1) < eps


def _check_half_pi_pos(theta, eps=1e-15):
    theta_mod = theta % (2 * np.pi)

    return abs(theta_mod / np.pi - 1 / 2) < eps


def _check_half_pi_neg(theta, eps=1e-15):
    theta_mod = theta % (2 * np.pi)

    return abs(theta_mod / np.pi - 3 / 2) < eps


def zyz_rule(gate):
    """ decomposition the unitary gate with 2 * 2 unitary into Rz Ry Rz sequence

    Args:
        gate(Unitary): the gate to be decomposed

    Returns:
        compositeGate: a list of compositeGate
    """
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-13

    det = linalg.det(unitary)
    beta_plus_delta = 0
    beta_dec_delta = 0
    if abs(det - 1) > eps:
        unitary[:] /= np.sqrt(det)

    if abs(unitary[0, 0]) > abs(unitary[0, 1]) > eps:
        gamma = _arccos((2 * (unitary[0, 0] * unitary[1, 1]).real - 1))
    else:
        gamma = _arccos((2 * (unitary[0, 1] * unitary[1, 0]).real + 1))
    if abs(unitary[0, 0]) > eps:
        beta_plus_delta = -np.angle(unitary[0, 0] / np.cos(gamma / 2)) * 2
    if abs(unitary[0, 1]) > eps:
        beta_dec_delta = np.angle(unitary[1, 0] / np.sin(gamma / 2)) * 2

    beta = (beta_plus_delta + beta_dec_delta) / 2
    delta = beta_plus_delta - beta
    gates = CompositeGate()
    with gates:
        # z(delta)*y(gamma)*z(beta)
        if _check2pi(gamma):
            if not _check2pi(delta + beta):
                Rz(delta + beta) & targ
        else:
            if not _check2pi(delta):
                Rz(delta) & targ
            Ry(gamma) & targ
            if not _check2pi(beta):
                Rz(beta) & targ
    return gates


def xyx_rule(gate):
    """ decomposition the unitary gate with 2 * 2 unitary into Rx Ry Rx sequence

    Args:
        gate(Unitary): the gate to be decomposed

    Returns:
        compositeGate: a list of compositeGate
    """
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-13
    unitary = np.array([
        [0.5 * (unitary[0, 0] + unitary[0, 1] + unitary[1, 0] + unitary[1, 1]),
         0.5 * (unitary[0, 0] - unitary[0, 1] + unitary[1, 0] - unitary[1, 1])],
        [0.5 * (unitary[0, 0] + unitary[0, 1] - unitary[1, 0] - unitary[1, 1]),
         0.5 * (unitary[0, 0] - unitary[0, 1] - unitary[1, 0] + unitary[1, 1])]
    ], dtype=np.complex128)
    det = linalg.det(unitary)
    beta_plus_delta = 0
    beta_dec_delta = 0
    if abs(det - 1) > eps:
        unitary[:] /= np.sqrt(det)

    if abs(unitary[0, 0]) > abs(unitary[0, 1]) > eps:
        gamma = _arccos((2 * (unitary[0, 0] * unitary[1, 1]).real - 1))
    else:
        gamma = _arccos((2 * (unitary[0, 1] * unitary[1, 0]).real + 1))
    if abs(unitary[0, 0]) > eps:
        beta_plus_delta = -np.angle(unitary[0, 0] / np.cos(gamma / 2)) * 2
    if abs(unitary[0, 1]) > eps:
        beta_dec_delta = np.angle(unitary[1, 0] / np.sin(gamma / 2)) * 2

    beta = (beta_plus_delta + beta_dec_delta) / 2
    delta = beta_plus_delta - beta
    gates = CompositeGate()
    with gates:
        # x(delta)*y(-gamma)*x(beta)
        if _check2pi(gamma):
            if not _check2pi(delta + beta):
                Rx(delta + beta) & targ
        else:
            if not _check2pi(delta):
                Rx(delta) & targ
            Ry(-gamma) & targ
            if not _check2pi(beta):
                Rx(beta) & targ
    return gates


def ibmq_rule(gate):
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-13

    det = linalg.det(unitary)
    beta_plus_delta = 0
    beta_dec_delta = 0
    if abs(det - 1) > eps:
        unitary[:] /= np.sqrt(det)

    if abs(unitary[0, 0]) > abs(unitary[0, 1]) > eps:
        gamma = _arccos((2 * (unitary[0, 0] * unitary[1, 1]).real - 1))
    else:
        gamma = _arccos((2 * (unitary[0, 1] * unitary[1, 0]).real + 1))
    if abs(unitary[0, 0]) > eps:
        beta_plus_delta = -np.angle(unitary[0, 0] / np.cos(gamma / 2)) * 2
    if abs(unitary[0, 1]) > eps:
        beta_dec_delta = np.angle(unitary[1, 0] / np.sin(gamma / 2)) * 2

    beta = (beta_plus_delta + beta_dec_delta) / 2
    delta = beta_plus_delta - beta
    gates = CompositeGate()
    with gates:
        # z(beta)*y(gamma)*z(delta)
        if _check2pi(gamma):
            # z(beta) * [sx_dag * z(gamma) * sx] * z(delta)
            # = z(beta + delta)
            if not _check2pi(delta + beta):
                Rz(np.mod(delta + beta, 2 * np.pi)) & targ
        else:
            # z(beta) * [z(pi) * sx * z(gamma - pi) * sx] * z(delta)
            # = z(beta + pi) * sx * z(gamma - pi) * sx * z(delta)
            if not _check2pi(gamma - np.pi):
                if not _check2pi(delta):
                    Rz(delta) & targ
                SX & targ
                Rz(np.mod(gamma - np.pi, 2 * np.pi)) & targ
                SX & targ
                if not _check2pi(beta + np.pi):
                    Rz(np.mod(beta + np.pi, 2 * np.pi)) & targ
            else:
                if not _check2pi(delta - beta - np.pi):
                    Rz(np.mod(delta - beta - np.pi, 2 * np.pi)) & targ
                X & targ

    return gates


def zxz_rule(gate):
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-13

    det = linalg.det(unitary)
    beta_plus_delta = 0
    beta_dec_delta = 0
    if abs(det - 1) > eps:
        unitary[:] /= np.sqrt(det)

    beta_plus_delta = 2 * np.angle(unitary[1, 1])
    beta_dec_delta = 2 * np.angle(unitary[1, 0]) + np.pi
    gamma = 2 * _arccos(np.abs(unitary[0, 0]))
    beta = (beta_plus_delta + beta_dec_delta) / 2
    delta = beta_plus_delta - beta

    gates = CompositeGate()
    with gates:
        # z(delta)*x(gamma)*z(beta)
        if _check2pi(gamma):
            if not _check2pi(delta + beta):
                Rz(delta + beta) & targ
        else:
            if not _check2pi(delta):
                Rz(delta) & targ
            Rx(gamma) & targ
            if not _check2pi(beta):
                Rz(beta) & targ
    return gates


def hrz_rule(gate):
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-13

    det = linalg.det(unitary)
    beta_plus_delta = 0
    beta_dec_delta = 0
    if abs(det - 1) > eps:
        unitary[:] /= np.sqrt(det)

    beta_plus_delta = 2 * np.angle(unitary[1, 1])
    beta_dec_delta = 2 * np.angle(unitary[1, 0]) + np.pi
    gamma = 2 * _arccos(np.abs(unitary[0, 0]))
    beta = (beta_plus_delta + beta_dec_delta) / 2
    delta = beta_plus_delta - beta

    gates = CompositeGate()
    with gates:
        # z(delta)*x(gamma)*z(beta)
        if _check2pi(gamma):
            if not _check2pi(delta + beta):
                Rz(delta + beta) & targ
        else:
            if not _check2pi(delta):
                Rz(delta) & targ
            H & targ
            Rz(gamma) & targ
            H & targ
            if not _check2pi(beta):
                Rz(beta) & targ
    return gates


def u3_rule(gate):
    unitary = gate.matrix
    targ = gate.targ
    eps = 1e-6

    # u3[0, 0] is real
    z = np.exp(1j * np.angle(unitary[0, 0]))
    unitary = unitary / z

    theta = np.arccos(unitary[0, 0]).real
    sint = np.sin(theta)
    if abs(sint) >= eps:
        lamda = np.angle(unitary[0, 1] / -sint)
        phi = np.angle(unitary[1, 0] / sint)
    else:
        lamda = 0
        phi = np.angle(unitary[1, 1] / np.cos(theta))
    if _check2pi(theta, eps):
        theta = 0
    if _check2pi(lamda, eps):
        lamda = 0
    if _check2pi(phi, eps):
        phi = 0
    g = gate_builder(GateType.u3, params=[theta * 2, phi, lamda]) & targ
    gates = CompositeGate(gates=[g])
    return gates
