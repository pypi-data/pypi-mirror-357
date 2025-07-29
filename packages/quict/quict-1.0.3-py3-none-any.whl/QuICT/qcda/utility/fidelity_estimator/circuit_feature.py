from typing import List

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate
from QuICT.core.utils import GateType, GATEINFO_MAP
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.qcda.utility.fidelity_estimator.circuit_path import CircuitPath


class CircuitFeature:
    def __init__(
            self,
            circ: Circuit,
            vqm: VirtualQuantumMachine,
            step: int = 1,
            mapping: List[int] = None):
        """
        Args:
            circ(Circuit): an initial circuit and can be changed. This class is used
            to extract feature of this circuit.
            vqm(VirtualQuantumMachine): this vqm should not be changed
            step(int): the step of the path in circuit to be considered
            mapping(List[int]): mapping of qubits
        Info:
            use this class to compute features of circuits
        """
        self.circ = circ
        if mapping is None:
            mapping = list(range(vqm.qubit_number))
        self.mapping = mapping
        self.depth = circ.depth()
        self.step = step
        self.circ_2d = self.get_circ_2d()
        self.vqm = vqm

    def get_circ_2d(self):
        """
        Returns:
            list(list): the 2d circuit layout
        """
        out = []
        for ii in range(1, self.depth + 1):
            out.append(self.circ.get_gates_by_depth(ii))
        return out

    def count_path(self, path: CircuitPath):
        """
        Args:
            path(CircuitPath): desired path
        Returns:
            int: the count of this path
        """
        count = 0
        for depth in range(self.depth - len(path)):
            for g in self.circ_2d[depth]:
                if path.get_gate_type(0) != g.type:
                    continue
                else:
                    # match the start gate, then check path. first parallel then next
                    next_depth = depth
                    exclude = [g]
                    next_gate = g
                    for path_depth in range(1, len(path) + 1):
                        r_type = path.get_r_type(path_depth)
                        if r_type == "next" or r_type == "next2" or r_type == "next3":
                            next_depth = next_depth + 1
                        next_gate = self._find_gate(next_gate, path.get_gate_type(path_depth),
                                                    r_type,
                                                    next_depth, exclude=exclude)
                        if next_gate is None:
                            break
                        exclude.append(next_gate)
                    else:
                        count += 1

        return count

    def _find_gate(self, this_gate: BasicGate, target_type, r_type, depth, exclude=()):
        if depth < 0 or depth > self.depth - 1:
            return None
        if GATEINFO_MAP[self.vqm.instruction_set.two_qubit_gate][0] == 0 \
                and r_type in ["next2", "next3"]:
            return None

        # map first
        affect = [self.mapping[x] for x in this_gate.cargs + this_gate.targs]
        relate = []
        if r_type == "parallel":
            for qubit in affect:
                to_add = self.vqm.double_gate_fidelity[qubit].keys()
                for item in to_add:
                    if item not in relate and self.vqm.double_gate_fidelity[qubit][item] > 0:
                        relate.append(item)
        for g in self.circ_2d[depth]:
            g: BasicGate
            if g.type == GateType.measure or g.type == GateType.barrier:
                continue
            if g.type == target_type and g not in exclude:
                if r_type == "parallel":
                    if len(set([self.mapping[x] for x in g.cargs + g.targs]) & set(affect)) == 0 and \
                            len(set([self.mapping[x] for x in g.cargs + g.targs]) & set(relate)) > 0:
                        return g
                elif r_type == "next":
                    if GATEINFO_MAP[self.vqm.instruction_set.two_qubit_gate][0] > 0:
                        if this_gate.type == self.vqm.instruction_set.two_qubit_gate \
                                and g.type != self.vqm.instruction_set.two_qubit_gate and \
                                this_gate.cargs[0] == g.targs[0]:
                            return g
                        elif this_gate.type != self.vqm.instruction_set.two_qubit_gate \
                                and g.type == self.vqm.instruction_set.two_qubit_gate and \
                                this_gate.targs[0] == g.cargs[0]:
                            return g
                        elif this_gate.type == self.vqm.instruction_set.two_qubit_gate \
                                and g.type == self.vqm.instruction_set.two_qubit_gate and \
                                ((this_gate.cargs[0] == g.targs[0] and this_gate.targs[0] != g.cargs[0]) or
                                 (this_gate.cargs[0] != g.targs[0] and this_gate.targs[0] == g.cargs[0])):
                            return g
                    else:
                        # if two qubit gates has two target, then only need intersection
                        if len(set([self.mapping[x] for x in g.cargs + g.targs]) &
                               set([self.mapping[x] for x in this_gate.cargs + this_gate.targs])) > 0:
                            return g
                elif r_type == "next2":
                    # target connect target
                    if g.targs[0] == this_gate.targs[0]:
                        return g

                elif r_type == "next3":
                    # two cx, control connect target doubly
                    if g.cargs[0] == this_gate.targs[0] and \
                            g.targs[0] == this_gate.cargs[0]:
                        return g
        return None
