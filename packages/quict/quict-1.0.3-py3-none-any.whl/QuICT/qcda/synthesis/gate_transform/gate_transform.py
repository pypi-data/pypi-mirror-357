from typing import Union

import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate, CompositeGate, GateType, Unitary, GPhase
from QuICT.core.virtual_machine.special_set import USTCSet
from QuICT.qcda.utility import OutputAligner
from .transform_rule import *


class GateTransform(object):
    """
    Equivalently transfrom circuit into goal instruction set

    Examples:
        >>> from QuICT.core.virtual_machine.special_set import USTCSet
        >>> from QuICT.qcda.synthesis.gate_transform import GateTransform
        >>> gt = GateTransform(USTCSet)
        >>> circ_syn = gt.execute(circ)
    """
    def __init__(self, instruction_set=USTCSet, keep_phase=False):
        """
        Args:
            instruction_set (InstructionSet): the goal instruction set
            keep_phase (bool, optional): whether to keep the global phase as a GPhase gate in the output
        """
        self.instruction_set = instruction_set
        self.keep_phase = keep_phase
        self.total_phase = 0

    @OutputAligner()
    def execute(self, circuit: Union[Circuit, CompositeGate]) -> CompositeGate:
        """
        Transform the two-qubit gate into instruction set one by one, then one-qubit gate

        Args:
            circuit (Circuit/CompositeGate): the circuit to be transformed

        Returns:
            CompositeGate: the equivalent compositeGate with goal instruction set
        """
        assert isinstance(circuit, (Circuit, CompositeGate)), TypeError("Invalid input for GateTransform")
        gates = circuit if isinstance(circuit, CompositeGate) else circuit.to_compositegate()

        gates.decomposition()
        gates.flatten()
        gates = self.two_qubit_transform(gates)
        gates = self.one_qubit_transform(gates)

        self._clean_identity_matrix(gates)

        if self.keep_phase:
            self.total_phase = np.mod(self.total_phase, 2 * np.pi)
            if not np.isclose(self.total_phase, 0) and not np.isclose(self.total_phase, 2 * np.pi):
                gates.append(GPhase(self.total_phase) & 0)

        return gates

    def _clean_identity_matrix(self, gates: CompositeGate):
        gates.flatten()
        pop_list = []
        for idx, gate in enumerate(gates.fast_gates):
            gate: BasicGate
            gate_args = gate.controls + gate.targets
            if np.allclose(gate.matrix, np.identity(1 << gate_args).astype(gate.matrix.dtype)):
                pop_list.append(idx)

        for pop_idx in pop_list[::-1]:
            gates.pop(pop_idx)

    def one_qubit_transform(self, gates: CompositeGate) -> CompositeGate:
        gates_tran = CompositeGate()
        unitaries = [np.identity(2, dtype=np.complex128) for _ in range(max(gates.qubits) + 1)]
        uni_gate_flag = [[0, None] for _ in range(max(gates.qubits) + 1)]
        single_qubit_rule = self.instruction_set.one_qubit_rule
        if isinstance(single_qubit_rule, str):
            single_qubit_rule = eval(single_qubit_rule)

        gate: BasicGate
        for gate in gates.flatten_gates():
            if gate.targets + gate.controls == 2:
                targs = gate.cargs + gate.targs
                for targ in targs:
                    if uni_gate_flag[targ][0] == 1 and uni_gate_flag[targ][1].type in self.instruction_set.gates:
                        gates_tran.append(uni_gate_flag[targ][1])
                    else:
                        gates_transformed = single_qubit_rule(Unitary(unitaries[targ].copy()) & targ)
                        if gates_transformed.width() == 0:
                            local_matrix = np.eye(2)
                        else:
                            local_matrix = gates_transformed.matrix(local=True)
                        if self.keep_phase:
                            phase = np.angle(np.dot(unitaries[targ], np.linalg.inv(local_matrix))[0][0])
                            self.total_phase += phase
                        gates_tran.extend(gates_transformed)
                    unitaries[targ] = np.identity(2, dtype=np.complex128)
                    uni_gate_flag[targ] = [0, None]
                gates_tran.append(gate)
            else:
                uni_gate_flag[gate.targ][0] += 1
                uni_gate_flag[gate.targ][1] = gate
                unitaries[gate.targ] = np.dot(gate.matrix, unitaries[gate.targ])

        for targ in range(max(gates.qubits) + 1):
            if uni_gate_flag[targ][0] == 1 and uni_gate_flag[targ][1].type in self.instruction_set.gates:
                gates_tran.append(uni_gate_flag[targ][1])
            else:
                gates_transformed = single_qubit_rule(Unitary(unitaries[targ].copy()) & targ)
                if gates_transformed.width() == 0:
                    local_matrix = np.eye(2)
                else:
                    local_matrix = gates_transformed.matrix(local=True)
                if self.keep_phase:
                    phase = np.angle(np.dot(unitaries[targ], np.linalg.inv(local_matrix))[0][0])
                    self.total_phase += phase
                gates_tran.extend(gates_transformed)
        return gates_tran

    def two_qubit_transform(self, gates: CompositeGate) -> CompositeGate:
        gates_tran = CompositeGate()
        for gate in gates:
            if gate.targets + gate.controls > 2:
                raise Exception("gate_transform only support 2-qubit and 1-qubit gate now.")
            if gate.type != self.instruction_set.two_qubit_gate and gate.targets + gate.controls == 2:
                double_qubit_rule = self.instruction_set.select_transform_rule(gate.type)

                local_gates = CompositeGate(gates=[gate])
                for source, rule in double_qubit_rule:
                    if isinstance(rule, str):
                        rule = eval(rule)
                    local_gates.flatten()
                    new_gates = CompositeGate()
                    for g in local_gates:
                        if g.type == source:
                            new_gates.extend(rule(g, self.keep_phase))
                        else:
                            new_gates.append(g)
                    local_gates = new_gates

                gates_tran.extend(local_gates)
            else:
                gates_tran.append(gate)
        return gates_tran
