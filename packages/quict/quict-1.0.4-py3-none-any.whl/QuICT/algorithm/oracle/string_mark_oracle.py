from typing import List, Union, Literal
from QuICT.core.gate import GateType, BasicGate, CompositeGate, X, H
from QuICT.core.gate.backend import MCZOneAux
_ORACLE_MODE = Literal["phase", "bitflip"]


class StringMarkOracle(CompositeGate):
    """ Construct a oracle that will flip phases on states denoted by strings.
    """
    def __init__(
        self,
        target_string: Union[str, List[str]],
        mode: _ORACLE_MODE = "phase"
    ):
        """
        Args:
            target_string (str | List[str]): a single string or a list of string that wants flip the phase on.
        """
        if len(target_string) < 1:
            raise ValueError("Target string cannot be empty.")

        super().__init__(name="O_str")

        if isinstance(target_string, str):
            target_string = [target_string]

        target_string = list(set(target_string))

        self.targ_bit_len = len(target_string[0])

        if not self._same_length(target_string, self.targ_bit_len):
            raise ValueError("Target strings must have the same length.")

        target_proc_gate: BasicGate
        total_ancilla = []
        if mode == "phase":
            target_proc_gate = X
            total_ancilla.append(self.targ_bit_len)
        else:
            target_proc_gate = H

        cg = CompositeGate()

        target_proc_gate | cg(self.targ_bit_len)

        prev_s = "1" * self.targ_bit_len
        for i in range(len(target_string)):
            cur_s = target_string[i]
            self._build_oracle_core(prev_s, cur_s) | cg
            prev_s = cur_s
        for idx, bit in enumerate(target_string[-1]):
            if bit == '0':
                X | cg(idx)

        target_proc_gate | cg(self.targ_bit_len)

        total_ancilla += MCZOneAux(self.targ_bit_len).ancilla_qubits

        h_rm_idx = []
        gate_list = cg.flatten_gates(True)
        for idx, gate in enumerate(gate_list):
            if gate.type != GateType.h:
                gate | self
                continue

            adj_h_idx = self._find_adj_h(gate_list, idx)
            if adj_h_idx > 0 and idx not in h_rm_idx:
                h_rm_idx += [idx, adj_h_idx]

            if idx not in h_rm_idx:
                gate | self

        self.set_ancilla(total_ancilla)

    def _same_length(self, string_list: List[str], s_len: int) -> bool:
        """ Check if all string are of length s_len. """
        for string in string_list:
            if len(string) != s_len:
                return False

        return True

    def _find_adj_h(self, gate_list: list[BasicGate], start_pos: int) -> int:
        wire_num = gate_list[start_pos].targ

        for search_pos in range(start_pos + 1, len(gate_list)):
            gate = gate_list[search_pos]
            ctargs = gate.cargs + gate.targs
            if len(ctargs) > 1:
                if wire_num in ctargs:
                    return -1
                else:
                    continue

            if wire_num == ctargs[0]:
                if gate.type == GateType.h:
                    return search_pos
                else:
                    return -1

        return -1

    def _build_oracle_core(self, prev_s: str, s: str) -> CompositeGate:
        """ Construct an oracle that flips phase on |s>. """
        if len(prev_s) != len(s):
            raise ValueError("String sizes do not agree.")

        s_size = len(s)

        cg = CompositeGate()
        for idx in range(s_size):
            if s[idx] != prev_s[idx]:
                X | cg(idx)

        MCZOneAux(num_ctrl=s_size) | cg

        return cg
