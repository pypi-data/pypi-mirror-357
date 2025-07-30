from typing import List, Union
from QuICT.core.gate import CompositeGate


class QRegManager:
    """ Quantum register allocator"""
    def __init__(self) -> None:
        self.allocated = 0

    def alloc(self, num_q: int) -> List[int]:
        """ Allocate designated number of qubits and return the newly allocated register as a list.

        Args:
            num_q (int): Number of qubits to allocate.

        Returns:
            List[int]: List of indices for the newly allocated qubits.
        """
        reg_list = list(range(self.allocated, self.allocated + num_q))
        self.allocated += num_q

        return reg_list

    @classmethod
    def ancilla_num(cls, gate_list: List[Union[CompositeGate, None]]) -> int:
        """ Calculate the total ancilla qubits needed for a collection of CompositeGates.

        Args:
            gate_list (List[Composite | None]): A collection of CompositeGates (possibly has None in the list).

        Returns:
            int: The least number of ancilla qubits required to meet the usage for all the composite gates
                in the list.
        """
        max_ancilla = 0
        for gate in gate_list:
            if gate is not None:
                if isinstance(gate, CompositeGate):
                    if len(gate.ancilla_qubits) > max_ancilla:
                        max_ancilla = len(gate.ancilla_qubits)
                else:
                    raise TypeError(f"Invalid type: {type(gate).__name__} in gate list.")

        return max_ancilla
