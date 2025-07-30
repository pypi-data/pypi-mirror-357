from typing import List
from QuICT.core.gate import CompositeGate


class QubitAligner:
    """ Align CompositeGate's working qubits and ancilla qubits with some given quantum registers
        given as two lists representing the work_bits register and the ancilla register.
    """
    def __init__(self, work_bits: List[int], ancilla_bits: List[int]) -> None:
        self._check_valid_reg(work_bits, ancilla_bits)
        self._work_bits = work_bits
        self._ancilla_bits = ancilla_bits

    def getMap(self, cg: CompositeGate, fix_top: int = 0, leave_fix_empty: bool = True) -> List[int]:
        """ Given a composite, calculate the desired application indices that will align
        the composite's ancilla qubits with given ancilla_bits list.

        Args:
            cg (CompositeGate): the composite waiting to be aligned. Make sure its ancilla qubits
                is set as desired by using `.set_ancilla()` method.
            fix_top (int): the number of qubits from the top that wanted to be fixed and not remapped to
                neither work_bits nor ancilla_bits list.
            leave_fix_empty (bool): If `True`, the indices of the fix top qubits will not be in the result.
                If `False`, the indices of the fix top qubits will be set to `-1`.

        Returns:
            List[int]: the remapped indices. In the [work_bits_indices, ancilla_indices] order.
        """
        required_width = max(cg.qubits) + 1
        work_bits_req = required_width - len(cg.ancilla_qubits) - fix_top
        if len(cg.ancilla_qubits) > len(self._ancilla_bits):
            raise ValueError("Not enough ancilla bits for the input composite gate. "
                             f"Given {len(self._ancilla_bits)} but the gate requires {len(cg.ancilla_qubits)}.")
        if work_bits_req > len(self._work_bits):
            raise ValueError("Not enough work qubits for the input composite gate. "
                             f"Given {len(self._work_bits)} but the gate requires {work_bits_req}.")
        for i in list(range(fix_top)):
            if i in cg.ancilla_qubits:
                raise ValueError(f"Cannot set {i}th qubits to be fixed for it appears in composite gate's "
                                 f"ancilla_qubits list: {cg.ancilla_qubits}.")

        # iterate both register from top to bottom
        it_ancilla = 0
        it_work = len(self._work_bits) - work_bits_req
        final_map = []
        for i in range(fix_top, required_width):
            if i in cg.ancilla_qubits:
                idx = self._ancilla_bits[it_ancilla]
                it_ancilla += 1
            else:
                idx = self._work_bits[it_work]
                it_work += 1
            final_map.append(idx)

        if leave_fix_empty:
            return final_map

        return [-1] * fix_top + final_map

    def _check_valid_reg(self, work_bits: List[int], ancilla_bits: List[int]) -> None:
        for i in work_bits:
            if i in ancilla_bits:
                raise ValueError(f"Two registers cannot overlap. Index {i} in work bits also appears in ancilla bits.")
