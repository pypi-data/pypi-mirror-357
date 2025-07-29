from typing import Union

import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, GPhase
from QuICT.qcda.synthesis import CartanKAKDecomposition


class LocalKAKDecomposition():
    """
    Locally combine 2-qubit gates and try KAK decomposition.
    Replace the original part if 2-qubit gate count is optimized.
    """
    def __init__(self, target: str = 'cx', keep_phase=False):
        """
        Args:
            target (str, optional): the target of KAK decomposition
            keep_phase (bool, optional): whether to keep the global phase as a GPhase gate in the output
        """
        self.target = target
        self.keep_phase = keep_phase

    def execute(self, circ: Union[Circuit, CompositeGate]):
        """
        Args:
            circuit (Circuit/CompositeGate): the circuit to be locally re-synthesized

        Returns:
            CompositeGate: the equivalent compositeGate
        """
        phase = 0
        circ_kak = CompositeGate()
        kak = CartanKAKDecomposition(target=self.target)
        for gate_list in circ.gate_combination(eliminate_single=True):
            qubit = sorted(gate_list[0].cargs + gate_list[0].targs)
            gates = CompositeGate(gates=gate_list)

            if len(qubit) == 1:
                gates | circ_kak
            elif len(qubit) == 2:
                mat = gates.matrix(local=True)
                gates_kak = kak.execute(mat)
                if gates_kak.count_2qubit_gate() < gates.count_2qubit_gate():
                    if self.keep_phase:
                        mat_kak = gates_kak.matrix()
                        phase += np.angle(np.dot(mat, np.linalg.inv(mat_kak))[0, 0])
                    gates_kak | circ_kak(qubit)
                else:
                    gates | circ_kak
            else:
                raise ValueError('Invalid length of qubit in gate_combination.')

        if self.keep_phase:
            GPhase(phase) | circ_kak(circ_kak.qubits[0])

        return circ_kak
