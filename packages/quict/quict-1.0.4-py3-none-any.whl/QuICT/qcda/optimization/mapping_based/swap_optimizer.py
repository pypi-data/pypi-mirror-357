from QuICT.core import Circuit
from QuICT.core.gate import GateType, BasicGate, CX


class SwapBasedOptimizer:
    """ Optimization for swap gate and consecutive CX gate after mapping. """
    def __init__(self, only_swap: bool = True):
        """ TODO: not working for only_swap. """
        self._only_swap = only_swap
        self._last_gates_per_qubits = {}

    def execute(self, circuit: Circuit) -> Circuit:
        if circuit.count_gate_by_gatetype(GateType.swap) == 0:
            return circuit

        opt_cir = Circuit(circuit.width())
        gate_list = circuit.gates
        pointer = 0
        while pointer < len(gate_list):
            curr_gate: BasicGate = gate_list[pointer]
            curr_gate_args = curr_gate.cargs + curr_gate.targs
            if curr_gate.type not in [GateType.swap, GateType.cx] or pointer == len(gate_list) - 1:
                curr_gate | opt_cir
            else:
                for j in range(pointer + 1, len(gate_list)):
                    next_gate = gate_list[j]
                    next_gate_args = next_gate.cargs + next_gate.targs
                    in_same_qubits = sorted(curr_gate_args) == sorted(next_gate_args)
                    if (
                        curr_gate == next_gate or
                        (curr_gate.type == GateType.swap and next_gate.type == GateType.swap and in_same_qubits)
                    ):
                        gate_list.pop(j)
                        break
                    elif not curr_gate.commutative(next_gate):
                        if (
                            next_gate.type not in [GateType.cx, GateType.swap] or
                            not in_same_qubits or
                            (curr_gate.type == GateType.cx and next_gate.type == GateType.cx)
                        ):
                            curr_gate | opt_cir
                        else:
                            if curr_gate.type == GateType.swap:
                                CX | opt_cir(next_gate_args)
                                CX | opt_cir(next_gate_args[::-1])
                                gate_list.pop(j)
                            else:
                                gate_list.pop(j)
                                gate_list.insert(j, CX & curr_gate_args[::-1])
                                gate_list.insert(j + 1, CX & curr_gate_args)

                        break

                    if j == len(gate_list) - 1:
                        curr_gate | opt_cir

            pointer += 1

        return opt_cir
