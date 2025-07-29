from enum import Enum
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import GateType, gate_builder, BasicGate


CONTROL_GATE_MAPPING = {
    GateType.cz: GateType.z,
    GateType.cx: GateType.x,
    GateType.cy: GateType.y,
    GateType.ch: GateType.h,
    GateType.cry: GateType.ry,
    GateType.crz: GateType.rz,
    GateType.cu1: GateType.u1,
    GateType.cu3: GateType.u3,
    GateType.ccx: GateType.x,
    GateType.ccz: GateType.z,
    GateType.ccrz: GateType.rz,
    GateType.cswap: GateType.swap,
    GateType.rccx: GateType.x,
}


class QuantumStateBasedOptimization:
    def __init__(self):
        self._curr_quantum_state = []   # List[QubitState] to store the qubit state at current time.
        self._exchange_gate = [GateType.x, GateType.y]
        self._keep_state_gate = [GateType.z, GateType.s, GateType.sdg]
        self._swap_state_gate = [GateType.swap]

    def execute(self, circuit: Circuit, initial_quantum_state: list = None, final_quantum_state: np.ndarray = None):
        if initial_quantum_state is None:
            self._curr_quantum_state = [0] * circuit.width()
        else:
            self._curr_quantum_state = initial_quantum_state

        opt_circuit = Circuit(circuit.width())
        for gate in circuit.flatten_gates(False):
            gate: BasicGate
            if gate.controls >= 1:
                opt_gate, merge_ = self.optimized_with_control_gate(gate)
                if opt_gate is not None:
                    gate = opt_gate
                elif not merge_:
                    gate | opt_circuit
                    continue
                else:
                    continue

            gate_type = gate.type
            if gate_type in self._exchange_gate:
                if self._curr_quantum_state[gate.targ] != 2:
                    self._curr_quantum_state[gate.targ] = self._curr_quantum_state[gate.targ] ^ 1
            elif gate_type in self._swap_state_gate:
                temp_state = self._curr_quantum_state[gate.targs[0]]
                self._curr_quantum_state[gate.targs[0]] = self._curr_quantum_state[gate.targs[1]]
                self._curr_quantum_state[gate.targs[1]] = temp_state
            elif gate_type not in self._keep_state_gate:
                for targ in gate.targs:
                    self._curr_quantum_state[targ] = 2

            gate | opt_circuit(gate.targs)

        return opt_circuit

    def optimized_with_control_gate(self, gate):
        all_control = True
        mixed_state = False
        for carg in gate.cargs:
            if self._curr_quantum_state[carg] == 2:
                mixed_state = True
                break
            elif self._curr_quantum_state[carg] == 0:
                all_control = False

        if mixed_state:
            return None, False
        elif not all_control:
            return None, True

        target_gate_type = CONTROL_GATE_MAPPING[gate.type]
        target_gate = gate_builder(target_gate_type) if gate.params == 0 else \
            gate_builder(target_gate_type, params=gate.pargs)

        return target_gate & gate.targs, True
