"""
Optimize the given Circuit/CompositeGate by merging the adjacent gates with
the commutative relation between gates in consideration.
"""

from typing import Tuple, Union

import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import *
from QuICT.qcda.utility import OutputAligner

# Categories of combination
elimination = [
    GateType.h, GateType.x, GateType.y, GateType.z, GateType.cx, GateType.hy,
    GateType.cy, GateType.cz, GateType.ch, GateType.ccx, GateType.rccx, GateType.swap,
    GateType.ecr
]
addition = [
    GateType.u1, GateType.rx, GateType.ry, GateType.rz, GateType.phase, GateType.gphase,
    GateType.crz, GateType.cu1, GateType.fsim, GateType.rxx, GateType.ryy, GateType.rzz,
    GateType.rzx, GateType.cry
]
multiplication = [GateType.unitary]
other = [GateType.sx, GateType.sxdg, GateType.sy, GateType.sydg, GateType.s, GateType.sdg, GateType.t, GateType.tdg]
not_calculated = [GateType.sw, GateType.u2, GateType.u3, GateType.cu3]


class Node(object):
    """
    (Temporary) implementation of Directed Acyclic Graph (DAG) used in this code

    Attributes:
        gate (BasicGate): Gate represented by the node
        identity (bool): Whether the gate is identity (upon a global phase)
        predecessor (list[int]): Predecessors of the node
        reachable (bool): Whether this node needs to be compared with the new node

    TODO: Replace this part with a graph structure
    """
    def __init__(self, gate: BasicGate):
        """
        Args:
            gate (BasicGate): Gate represented by the node
        """
        self.gate = gate
        self.identity = False
        self.predecessor = set()
        self.reachable = True


class CommutativeOptimization(object):
    """
    Optimize the given Circuit/CompositeGate by merging the adjacent gates with
    the commutative relation between gates in consideration.

    During the process, several parameterization and deparameterization process could be included, as listed

    `'x'`: Rx <--> X, SX, SX_dagger

    `'y'`: Ry <--> Y, SY, SY_dagger

    `'z'`: Rz <--> Z, S, T, S_dagger, T_dagger

    Whether to parameterize or deparameterize certain kinds of gates could be specified
    by listing them in `para` and `depara`, where `['all']` stands for `['x', 'y', 'z']` for convenience.

    Examples:
        >>> from QuICT.qcda.optimization import CommutativeOptimization
        >>> CO = CommutativeOptimization()
        >>> circ_opt = CO.execute(circ)
    """
    para_rule = {
        'x': {
            GateType.x: (GateType.rx, [np.pi], np.pi / 2),
            GateType.sx: (GateType.rx, [np.pi / 2], np.pi / 4),
            GateType.sxdg: (GateType.rx, [3 * np.pi / 2], 3 * np.pi / 4),
        },
        'y': {
            GateType.y: (GateType.ry, [np.pi], np.pi / 2),
            GateType.sy: (GateType.ry, [np.pi / 2], 0),
            GateType.sydg: (GateType.ry, [3 * np.pi / 2], np.pi),
        },
        'z': {
            GateType.z: (GateType.rz, [np.pi], np.pi / 2),
            GateType.s: (GateType.rz, [np.pi / 2], np.pi / 4),
            GateType.sdg: (GateType.rz, [-np.pi / 2], -np.pi / 4),
            GateType.t: (GateType.rz, [np.pi / 4], np.pi / 8),
            GateType.tdg: (GateType.rz, [-np.pi / 4], -np.pi / 8),
        },
    }

    depara_rule = {
        # Rx
        'x': {
            (GateType.rx, 0): ([ID], 0),
            (GateType.rx, 2): ([SX], -np.pi / 4),
            (GateType.rx, 4): ([X], -np.pi / 2),
            (GateType.rx, 6): ([X, SX], -3 * np.pi / 4),
            (GateType.rx, 8): ([ID], np.pi),
            (GateType.rx, 10): ([SX], 3 * np.pi / 4),
            (GateType.rx, 12): ([X], np.pi / 2),
            (GateType.rx, 14): ([X, SX], np.pi / 4),
        },
        # Ry
        'y': {
            (GateType.ry, 0): ([ID], 0),
            (GateType.ry, 2): ([SY], 0),
            (GateType.ry, 4): ([Y], -np.pi / 2),
            (GateType.ry, 6): ([Y, SY], -np.pi / 2),
            (GateType.ry, 8): ([ID], np.pi),
            (GateType.ry, 10): ([SY], np.pi),
            (GateType.ry, 12): ([Y], np.pi / 2),
            (GateType.ry, 14): ([Y, SY], np.pi / 2),
        },
        # Rz
        'z': {
            (GateType.rz, 0): ([ID], 0),
            (GateType.rz, 1): ([T], -np.pi / 8),
            (GateType.rz, 2): ([S], -np.pi / 4),
            (GateType.rz, 3): ([S, T], -3 * np.pi / 8),
            (GateType.rz, 4): ([Z], -np.pi / 2),
            (GateType.rz, 5): ([Z, T], -5 * np.pi / 8),
            (GateType.rz, 6): ([S_dagger], 5 * np.pi / 4),
            (GateType.rz, 7): ([T_dagger], 9 * np.pi / 8),
            (GateType.rz, 8): ([ID], np.pi),
            (GateType.rz, 9): ([T], 7 * np.pi / 8),
            (GateType.rz, 10): ([S], 3 * np.pi / 4),
            (GateType.rz, 11): ([S, T], 5 * np.pi / 8),
            (GateType.rz, 12): ([Z], np.pi / 2),
            (GateType.rz, 13): ([Z, T], 3 * np.pi / 8),
            (GateType.rz, 14): ([S_dagger], np.pi / 4),
            (GateType.rz, 15): ([T_dagger], np.pi / 8),
        },
    }

    def __init__(self, para=['all'], depara=[], keep_phase=False):
        """
        Args:
            para (List[str], optional): parameterize which kinds of gates
            depara (List[str], optional): deparameterize which kinds of gates
            keep_phase (bool): whether to keep the global phase as a GPhase gate in the output
        """
        assert para == ['all'] or set(para).issubset(set(['x', 'y', 'z'])),\
            ValueError("Invalid para, should be 'all' or a subset of ['x', 'y', 'z']")
        assert depara == ['all'] or set(depara).issubset(set(['x', 'y', 'z'])),\
            ValueError("Invalid depara, should be 'all' or a subset of ['x', 'y', 'z']")
        self.para = ['x', 'y', 'z'] if para == ['all'] else para
        self.depara = ['x', 'y', 'z'] if depara == ['all'] else depara
        self.keep_phase = keep_phase

    def __repr__(self):
        return f'CommutativeOptimization(parameterization={self.para}, ' \
               f'deparameterization={self.depara})'

    @classmethod
    def parameterize(cls, gate: BasicGate, para=['x', 'y', 'z']) -> Tuple[BasicGate, float]:
        """
        In BasicGates, (X, SX, SX_dagger), (Y, SY, SY_dagger), (Z, S, Sdagger, T, Tdagger) could be
        'parameterized' to Rx, Ry, Rz respectively, which is helpful in the
        `combine` function.

        Args:
            gate (BasicGate): Gate to be transformed to its 'parameterized' version
            para (List[str], optional): parameterize which kinds of gates

        Returns:
            Tuple[BasicGate, float]: If the `gate` is listed above, its 'parameterized'
                version with the phase angle derived in the process will be returned.
                Otherwise, the `gate` itself with phase angle 0 will be returned.
        """
        for p in para:
            try:
                gate_type, gate_pargs, phase = cls.para_rule[p][gate.type]
                param_gate = gate_builder(gate_type, params=gate_pargs)
                return param_gate & gate.targ, phase
            except KeyError:
                continue
        return gate, 0

    @classmethod
    def deparameterize(cls, gate: BasicGate, depara=['x', 'y', 'z']) -> Tuple[CompositeGate, float]:
        """
        Deparameterize the parameterized gates if possible, as an inverse process of
        `parameterize` function.

        Be aware that gates like Rz(3*np.pi/4) would be transformed to S.T (which would cause more gates).

        Args:
            gate (BasicGate): Gate to be transformed to its 'deparameterized' version
            depara (List[str], optional): deparameterize which kinds of gates

        Returns:
            Tuple[CompositeGate, float]: If deparameterization process is possible, the
                'deparameterized' version of the gate with the phase angle derived in
                the process will be returned. Otherwise, the `gate` itself with phase
                angle 0 will be returned.
        """
        gates_depara = CompositeGate()
        for p in depara:
            try:
                parg = np.mod(gate.parg, 4 * np.pi) / (np.pi / 4)
                assert np.isclose(round(parg), parg)
                g_list, phase = cls.depara_rule[p][gate.type, round(parg)]
                for g in g_list:
                    gates_depara.append(g & gate.targ)
                return gates_depara, phase
            except Exception:
                continue
        gates_depara.append(gate)
        return gates_depara, 0

    @staticmethod
    def combine(gate_x: BasicGate, gate_y: BasicGate) -> BasicGate:
        """
        Combine `gate_x` and `gate_y` of the same type

        Generally, the combination could be divided into four categories:
        1. Elimination: the combined gate is ID
        2. Addition: the parameters of gates should be added
        3. Multiplication: the matrices of gates should be multiplied(i.e. UnitaryGate)
        4. Other: some special case(e.g. SS=Z) or not able to be calculated easily(e.g. U3Gate)
        In this method we would only deal with the first 3 cases, while the last case is partially
        handled by preprocessing the `parameterize` function.

        Args:
            gate_x (BasicGate): Gate to be combined
            gate_y (BasicGate): Gate to be combined

        Returns:
            BasicGate: The combined gate

        Raises:
            TypeError: If the input gates are not of the same type or unknown gate type encountered.
            ValueError: If the input gates are not operating on the same qubits in the same way
                or could not be combined directly to a gate with the same type.
        """
        assert gate_x.type == gate_y.type,\
            TypeError('commu_opt', 'Gates with same type', 'different type.')
        assert gate_x.cargs == gate_y.cargs and gate_x.targs == gate_y.targs,\
            ValueError('commu_opt', 'same control and target qubits', 'different qubits.')

        if gate_x.type in elimination:
            # IDGates operating on all qubits are the same
            return ID.copy() & gate_x.targ

        if gate_x.type in addition:
            gate = gate_x.copy()
            for id_para in range(gate_x.params):
                if gate_x.type in [GateType.u1, GateType.cu1, GateType.fsim]:
                    gate.pargs[id_para] = np.mod(gate_x.pargs[id_para] + gate_y.pargs[id_para], 2 * np.pi)
                else:
                    gate.pargs[id_para] = np.mod(gate_x.pargs[id_para] + gate_y.pargs[id_para], 4 * np.pi)
            return gate

        if gate_x.type in multiplication:
            gate = gate_x.copy()
            gate.matrix = gate_y.matrix.dot(gate_x.matrix)
            return gate

        if gate_x.type in other or gate_x.type in not_calculated:
            raise ValueError('commu_opt', 'calculated', 'not')

        raise TypeError('commu_opt', 'BasicGate', f'{gate_x.type}')

    @OutputAligner()
    def execute(self, gates: Union[Circuit, CompositeGate]) -> CompositeGate:
        """
        Optimize the given Circuit/CompositeGate by merging the adjacent gates with
        the commutative relation between gates in consideration.

        WARNING: This method is implemented for Circuit/CompositeGate with BasicGates
        only (say, ComplexGates are not supported), other gates in the Circuit/
        CompositeGate may result in an exception or unexpected output.

        FIXME: Merging gates may cause the modification of commutative relation.
        In this version only the simplest (also the most common) case, i.e. the merged
        gate is identity, is handled. More specified analysis of the DAG is needed
        to deal with other cases, which is postponed until the graph structure is completed.

        Args:
            gates (Union[Circuit, CompositeGate]): Circuit/CompositeGate to be optimized

        Returns:
            CompositeGate: The CompositeGate after optimization
        """
        opt_gates = gates.to_compositegate() if not isinstance(gates, CompositeGate) else gates
        nodes: list[Node] = []
        phase_angle = 0

        # Greedy optimization
        for gate in opt_gates.flatten_gates():
            gate: BasicGate
            # IDGate
            if gate.type in [GateType.id, GateType.measure, GateType.reset, GateType.barrier]:
                continue

            # GlobalPhaseGate
            if gate.type == GateType.gphase:
                phase_angle += gate.parg
                continue

            # Remove such as Rot(0)
            if np.allclose(
                gate.matrix,
                gate.matrix[0, 0] * np.eye(1 << gate.controls + gate.targets),
                rtol=1e-7,
                atol=1e-7,
            ):
                phase_angle += np.angle(gate.matrix[0, 0])
                continue

            # Preprocess: parameterization
            if self.para:
                gate, phase = self.parameterize(gate, self.para)
                phase_angle += phase
            new_node = Node(gate)

            # Main Procedure
            length = len(nodes)
            for prev in range(length):
                if nodes[prev].identity:
                    nodes[prev].reachable = False
                else:
                    nodes[prev].reachable = True

            combined = False
            for prev in range(length - 1, -1, -1):
                prev_node = nodes[prev]
                if prev_node.reachable:
                    prev_gate = prev_node.gate
                    # Combination of prev_gate and gate if same type
                    if (
                        prev_gate.type == gate.type and
                        prev_gate.cargs == gate.cargs and
                        prev_gate.targs == gate.targs and
                        not (gate.type in not_calculated)
                    ):
                        combined = True
                        nodes[prev].gate = self.combine(prev_gate, gate)
                        mat = nodes[prev].gate.matrix
                        if (
                            nodes[prev].gate.type == GateType.id or
                            np.allclose(
                                mat,
                                mat[0, 0] * np.eye(1 << nodes[prev].gate.controls + nodes[prev].gate.targets)
                            )
                        ):
                            nodes[prev].identity = True
                        break

                    if not prev_gate.commutative(gate):
                        for node in prev_node.predecessor:
                            nodes[node].reachable = False
                        new_node.predecessor.add(prev)
                        new_node.predecessor = new_node.predecessor.union(prev_node.predecessor)

            if not combined:
                nodes.append(new_node)

        gates_opt = CompositeGate()
        for node in nodes:
            if node.identity or node.gate.type == GateType.gphase:
                phase_angle += np.angle(node.gate.matrix[0, 0])
            elif self.depara:
                gates_depara, phase = self.deparameterize(node.gate, self.depara)
                gates_opt.extend(gates_depara)
                phase_angle += phase
            else:
                gates_opt.append(node.gate)

        phase_angle = np.mod(phase_angle.real, 2 * np.pi)
        if self.keep_phase and not np.isclose(phase_angle, 0) and not np.isclose(phase_angle, 2 * np.pi):
            with gates_opt:
                GPhase(phase_angle) & gates_opt.qubits[0]

        return gates_opt
