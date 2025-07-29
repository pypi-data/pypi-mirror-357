from collections import deque
from typing import List

import numpy as np

from QuICT.core import Circuit
from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import VirtualQuantumMachine


class SimpleFidelityEstimator:
    """
    A simple fidelity estimator that multiplies fidelity of gates in the circuit.
    """

    def __init__(self, vqm: VirtualQuantumMachine):
        """
        Args:
            vqm(VirtualQuantumMachine): target quantum machine.
        """
        self._vqm = vqm

    def _get_shortest_path(self, u, v):
        """
        Compute shortest path between two qubits in topology.
        """
        prev = {u: -1}
        que = deque([u])
        while len(que) > 0 and v not in prev:
            cur = que.popleft()
            for nxt in self._vqm.double_gate_fidelity[cur]:
                if nxt not in prev:
                    prev[nxt] = cur
                    que.append(nxt)
                if nxt == v:
                    break

        if v not in prev:
            return []

        ret = []
        while v != u:
            ret.append([prev[v], v])
            v = prev[v]
        return ret[::-1]

    def estimate_fidelity(
        self, cir: Circuit, mapping: List[int] = None, readout: bool = True, instruction_set: bool = True
    ):
        """
        Estimate fidelity of the circuit.

        Args:
            cir(Circuit): target circuit
            mapping(List[int]): Mapping of the circuit. Identity if None.
            readout(bool): whether to consider readout error, default is True
            instruction_set(bool): whether to consider instruction set, default is True

        Returns:
            float: fidelity of the circuit
        """
        cir.flatten()
        if mapping is None:
            mapping = list(range(self._vqm.qubit_number))

        fidelity = 1.0
        for gate in cir.gates:
            if instruction_set and (
                gate.type not in self._vqm.instruction_set.gates and
                gate.type not in [GateType.measure, GateType.barrier, GateType.reset]
            ):
                return 0.0
            if gate.controls + gate.targets == 2:
                if self._vqm.qubit_fidelity is None:
                    continue
                q1, q2 = mapping[(gate.cargs + gate.targs)[0]], mapping[(gate.cargs + gate.targs)[1]]
                if q2 not in self._vqm.double_gate_fidelity[q1]:
                    path = self._get_shortest_path(q1, q2)
                    for u, v in path:
                        cs = self._vqm.double_gate_fidelity[u][v]
                        fidelity *= cs**3
                else:
                    fidelity *= self._vqm.double_gate_fidelity[q1][q2]
            elif gate.controls + gate.targets == 1:
                qid = mapping[gate.targ]
                if gate.type in [GateType.barrier, GateType.reset]:
                    continue

                if gate.type in [GateType.measure, GateType.barrier, GateType.reset] and readout and self._vqm.qubit_fidelity is not None:
                    fidelity *= np.average(self._vqm.qubit_fidelity[qid])
                    continue
                if self._vqm.gate_fidelity is None:
                    continue
                if isinstance(self._vqm.gate_fidelity[qid], dict):
                    if gate.type in self._vqm.gate_fidelity[qid]:
                        fidelity *= self._vqm.gate_fidelity[qid][gate.type]
                else:
                    fidelity *= self._vqm.gate_fidelity[qid]
            else:
                return 0.0

        return fidelity
