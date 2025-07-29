from __future__ import annotations
from collections import defaultdict
from typing import Union
import numpy as np
from .gate_type import GateType


class CircuitGates:
    @property
    def size(self) -> int:
        """ The number of Quantum Gate. """
        return self._size

    @property
    def qubits(self) -> list:
        """ The list of qubit indexes, which is sorted. """
        return sorted(self._gate_qubits_count.keys())

    @property
    def length(self) -> int:
        """ The number of [BasicGate / CompositeGate]. """
        return len(self.gate_list)

    @property
    def siq_gates_count(self) -> int:
        """ The number of single-qubit quantum gate. """
        return self._siq_gates_count

    @property
    def biq_gates_count(self) -> int:
        """ The number of 2-qubits quantum gates. """
        return self._biq_gates_count

    @property
    def gate_qubits_count(self) -> dict:
        """ The number of quantum gate with target gate type. """
        return self._gate_qubits_count

    def gates_count_by_type(self, gate_type: GateType) -> int:
        """ The number of quantum gate with target gate type. """
        return self._gate_type_count[gate_type]

    @property
    def gatetype_list(self) -> list:
        return list(self._gate_type_count.keys())

    @property
    def training_gates_count(self) -> int:
        """ The number of trainable gates. """
        return self._training_gates_count

    @property
    def variables_count(self) -> int:
        """ The number of variables. """
        return self._variables_count

    @property
    def free_symbols(self) -> list:
        """ The list of symbols. """
        return self._free_symbols

    @property
    def symbol_pargs(self) -> dict:
        """ The symbols with corresponding values. """
        return self._symbol_pargs

    def __init__(self, gates: list = None):
        self._initial_property()
        self.gate_list = []
        if gates is not None:
            self._prebuild(gates)

    ####################################################################
    ############              Gate's Utilities              ############
    ####################################################################
    def _initial_property(self):
        self._size = 0
        self._biq_gates_count = 0
        self._siq_gates_count = 0
        self._training_gates_count = 0
        self._variables_count = 0
        self._gate_type_count = defaultdict(int)
        self._gate_qubits_count = defaultdict(int)
        self._symbol_pargs = dict()
        self._free_symbols = []

    def _prebuild(self, gates: list):
        for gate in gates:
            if type(gate).__name__ == "CompositeGate":
                self._analysis_compositegate(gate)
            elif type(gate).__name__ != "Trigger":
                self._analysis_gate(gate)

            self.gate_list.append(gate)

    def gates(self, no_copy: bool = False):
        """ Return all gates in current CircuitGates. """
        if no_copy:
            return self.gate_list

        return [gate.copy() for gate in self.gate_list]

    def depth(self, size: int):
        """ Return the depth of current"""
        depth = np.zeros(size, dtype=int)
        for gate in self.flatten(True, False):
            if type(gate).__name__ == "Trigger":
                continue

            targs = gate.cargs + gate.targs
            depth[targs] = np.max(depth[targs]) + 1

        return np.max(depth)

    def get_target_gates(self, qubits: list, depth: int, no_copy: bool = True) -> list:
        """ Return the BasicGate with target qubits and depth.

        Args:
            qubits (list): The indexes of qubits
            depth (int): The target depth
            no_copy (bool): Whether copy target gate.
        """
        based_depth = np.zeros(max(qubits) + 1, dtype=int)
        set_qubits = set(qubits)
        previous_gates = []
        for gate in self.flatten(no_copy, False):
            if type(gate).__name__ == "Trigger":
                continue

            targs = gate.cargs + gate.targs
            based_depth[targs] = np.max(based_depth[targs]) + 1
            gate_depth, set_targs = based_depth[targs[0]], set(targs)
            depth_condition = gate_depth >= depth if no_copy else gate_depth == depth
            if depth_condition:
                interact_args = set_targs & set_qubits
                if len(interact_args) > 0:
                    previous_gates.append(gate)
                    set_qubits = set_qubits ^ interact_args
            if len(set_qubits) == 0:
                break
        return previous_gates

    def remap(self, qubits: list):
        """ Remapping the gates's qubit indexes. """
        assert len(qubits) == len(self.qubits)
        for gate in self.gate_list:
            if type(gate).__name__ == "CompositeGate":
                gate_args = gate.qubits
            else:
                gate_args = gate.cargs + gate.targs

            new_qidx = [qubits[self.qubits.index(q)] for q in gate_args]
            gate & new_qidx

        new_qubits_count = defaultdict(int)
        for idx, old_q in enumerate(self.qubits):
            new_qubits_count[qubits[idx]] = self._gate_qubits_count[old_q]

        self._gate_qubits_count = new_qubits_count.copy()

    def reset(self):
        """ Clean the gates in Circuit. """
        self.gate_list = []
        self._initial_property()

    def copy(self):
        """ Copy the quantum gates relationship in current Circuit. """
        return CircuitGates(self.gates(False))

    def flatten_by_level(self, level: int = -1) -> CircuitGates:
        """ Flatten gates in the circuit by level of decomposition. """
        def decomp_gate_list(gate_list: list, level: int = -1) -> list:
            decomp_gates = []
            for gate in gate_list:
                if type(gate).__name__ == "CompositeGate":
                    if level < 0:
                        temp_gate = gate.copy() & gate.qubits
                        decomp_gates += decomp_gate_list(temp_gate._gates.gate_list)
                    elif level == 0:
                        decomp_gates.append(gate)
                    else:
                        temp_gate = gate.copy() & gate.qubits
                        decomp_gates += decomp_gate_list(temp_gate._gates.gate_list, level - 1)
                else:
                    decomp_gates.append(gate)
            return decomp_gates

        return CircuitGates(gates=decomp_gate_list(self.gate_list, level))

    def flatten(self, no_copy: bool = False, self_change: bool = False):
        """ Get the list of Quantum Gates, flat all the CompositeGate in Circuit. """
        new_gates = []
        for gate in self.gate_list:
            if type(gate).__name__ == "CompositeGate":
                new_gates.extend(gate.flatten_gates(no_copy))
            else:
                if not no_copy:
                    new_gates.append(gate.copy())
                else:
                    new_gates.append(gate)

        if self_change:
            self.gate_list = new_gates
        else:
            return new_gates

    def decomposition(self, no_copy: bool = False, self_change: bool = False):
        """ Decomposition the CompositeGate or BasicGate which has build_gate function. """
        new_gates = []
        for gate in self.flatten(no_copy):
            if type(gate).__name__ in ["BasicGate", "Unitary", "MultiControlGate"]:
                decom_gate = gate.build_gate()
                if decom_gate is None:
                    if no_copy:
                        new_gates.append(gate)
                    else:
                        new_gates.append(gate.copy())
                else:
                    new_gates.extend(decom_gate.flatten_gates(True))
                    if self_change:
                        self.gate_analysis(gate, minus=-1)
                        self.gate_analysis(decom_gate, minus=1)
            elif type(gate).__name__ in ["NoiseGate", "Trigger", "Kraus"]:
                new_gates.append(gate)

        if self_change:
            self.gate_list = new_gates
        else:
            return new_gates

    def combination(self, eliminate_single: bool = False):
        new_comb_gates = []
        gate_qubits_mapping = defaultdict(list)    # Tuple(qubits): gate list index
        for gate in self.flatten(True, False):
            gate_args = gate.cargs + gate.targs
            gate_args = tuple(sorted(gate_args))
            if gate_args in gate_qubits_mapping.keys():
                gate_qubits_mapping[gate_args].append(gate)
            else:
                mapping_index, set_gargs = [], set(gate_args)
                for key in gate_qubits_mapping.keys():
                    interact_idx = set_gargs & set(key)
                    if len(interact_idx) > 0:
                        mapping_index.append(key)
                        set_gargs = set_gargs ^ interact_idx

                    if len(set_gargs) == 0:
                        break

                if eliminate_single and len(mapping_index) == 1 and len(gate_args) == 1:
                    gate_qubits_mapping[mapping_index[0]].append(gate)
                else:
                    gate_qubits_mapping[gate_args].append(gate)
                    for map_idx in mapping_index:
                        new_comb_gates.append(gate_qubits_mapping.pop(map_idx))

        new_comb_gates.extend(gate_qubits_mapping.values())
        return new_comb_gates

    def init_pargs(self, symbols: list, values: Union[list, np.ndarray]):
        """ Initialize the trainable parameters.

        Args:
            symbols (list): The symbols that needs to be assigned values.
            values (Union[list, np.ndarray]): The values to be assigned.
        """
        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(values, (list, np.ndarray)):
            values = [values]
        for gate in self.gate_list:
            if type(gate).__name__ not in ["Trigger", "NoiseGate", "Unitary", "Perm"]:
                if type(gate).__name__ == "CompositeGate":
                    gate.init_pargs(symbols, values)
                    self._symbol_pargs.update(gate.symbol_pargs())
                else:
                    if gate.symbol_gate:
                        gate.init_pargs(symbols, values)
                        for symbol, value in zip(symbols, values):
                            self._symbol_pargs[symbol] = value

    def gate_analysis(self, gate, minus: int = 1):
        """ Update Circuit property by add/pop quantum gate. """
        if type(gate).__name__ == "CompositeGate":
            self._analysis_compositegate(gate, minus)
        elif type(gate).__name__ not in ["Trigger", "Multiply", "DataSwitch", "DeviceTrigger", "SpecialGate"]:
            if type(gate).__name__ == "NoiseGate":
                self._analysis_gate(gate._gate, minus)
            else:
                self._analysis_gate(gate, minus)

    def _analysis_gate(self, gate, minus: int = 1):
        # Qubits update
        gate_qargs = gate.cargs + gate.targs
        for qidx in gate_qargs:
            self._gate_qubits_count[qidx] += minus
            if minus == -1 and self._gate_qubits_count[qidx] == 0:
                del self._gate_qubits_count[qidx]

        # Gates count update
        self._size += minus
        if gate.controls + gate.targets == 1:
            self._siq_gates_count += minus
        elif gate.controls + gate.targets == 2:
            self._biq_gates_count += minus
        if gate.variables > 0 and gate.required_grad:
            self._training_gates_count += minus
            self._variables_count += minus * gate.variables

        self._gate_type_count[gate.type] += minus
        if self._gate_type_count[gate.type] == 0:
            del self._gate_type_count[gate.type]
        self._symbol_pargs.update(gate.symbol_pargs)
        self._free_symbols += [
            symbol for symbol in gate.free_symbols if symbol not in self._free_symbols
        ]

    def _analysis_compositegate(self, cgate, minus: int = 1):
        # Qubits info update
        for key, value in cgate._gates._gate_qubits_count.items():
            self._gate_qubits_count[key] += value * minus
            if minus == -1 and self._gate_qubits_count[key] == 0:
                del self._gate_qubits_count[key]

        # Gates count update
        self._size += cgate.size() * minus
        self._biq_gates_count += cgate.count_2qubit_gate() * minus
        self._siq_gates_count += cgate.count_1qubit_gate() * minus
        self._training_gates_count += cgate.count_training_gate() * minus
        self._variables_count += cgate.count_variables() * minus
        for key, value in cgate._gates._gate_type_count.items():
            self._gate_type_count[key] += value * minus
        self._symbol_pargs.update(cgate.symbol_pargs())
        self._free_symbols += [
            symbol for symbol in cgate.free_symbols() if symbol not in self._free_symbols
        ]

    ####################################################################
    ############               Gate's Build                 ############
    ####################################################################
    def append(self, gate):
        """ Add a quantum gate to Circuit's gate mapping.

        Args:
            gate (BasicGate, Operator): The quantum gate.
            qidxes (list): The qubit indexes.
        """
        self.gate_analysis(gate)
        self.gate_list.append(gate)

    def extend(self, gates):
        """ Add a CompositeGate to Circuit's gate mapping.

        Args:
            gates (CompositeGate): The CompositeGate.
            qidxes (list): The qubit indexes.
        """
        # Update gate properties
        self.gate_analysis(gates)
        self.gate_list.append(gates)

    def insert_by_position(self, gate, depth: int = -1):
        """ Insert a BasicGate / CompositeGate.

        Args:
            gate (BasicGate): The quantum gate.
            depth (int): the target depth.
        """
        self.gate_analysis(gate)
        if depth == -1:
            self.gate_list.append(gate)
            return
        elif depth <= 1:
            self.gate_list.insert(0, gate)
            return

        qubits = gate.qubits if type(gate).__name__ == "CompositeGate" else gate.cargs + gate.targs
        previous_gate = self.get_target_gates(qubits, depth)
        if len(previous_gate) == 0:
            self.gate_list.append(gate)
            return

        self.flatten(True, True)
        insert_idx = len(self.gate_list)
        for pgate in previous_gate:
            insert_idx = min(self.gate_list.index(pgate), insert_idx)

        self.gate_list.insert(insert_idx, gate)

    def insert(self, gate, index: int):
        """ Insert the BasicGate/CompositeGate into gate_list with given index. """
        qubits = gate.qubits if type(gate).__name__ == "CompositeGate" else gate.cargs + gate.targs
        if len(qubits) == 0:
            raise ValueError(f"The insert gate must be assigned before insert.")
        self.gate_analysis(gate)
        self.gate_list.insert(index, gate)

    def pop(self, index: int = None):
        """ Pop the gate with target index. """
        pop_gate = self.gate_list.pop(index)
        self.gate_analysis(pop_gate, -1)

        return pop_gate

    def pop_by_position(self, qubits: list, depth: int = -1):
        """ Pop the gate with target qubits and depth.

        Args:
            qubits (list): The target qubit indexes.
            depth (int): The target depth.
        """
        if depth == -1:
            pop_gate = self.find_last_layer_gates(qubits)
            assert len(pop_gate)
        else:
            pop_gate = self.get_target_gates(qubits, depth)

        for pgate in pop_gate:
            self.gate_analysis(pgate, -1)
            self.gate_list.remove(pgate)

    def find_last_layer_gates(self, qubits: list, all_contains: bool = False):
        """ Return the last layer gates with given qubits.

        Args:
            qubits (list): The indexes of qubits.
            all_contains (bool): Whether the gate is in the last layer exactly.
        """
        target_gates, rest_qubits = [], qubits[:]
        for gate in self.flatten(True, False)[::-1]:
            if type(gate).__name__ == "Trigger":
                continue

            if all_contains:
                gate_args_set = set(gate.cargs + gate.targs)
                if len(gate_args_set) == len(gate_args_set & set(rest_qubits)):
                    target_gates.append(gate.copy())
                    rest_qubits = [idx for idx in rest_qubits if idx not in gate_args_set]
            else:
                is_target = False
                for targ in gate.cargs + gate.targs:
                    if targ in rest_qubits:
                        is_target = True
                        rest_qubits.remove(targ)

                if is_target:
                    target_gates.append(gate.copy())

            if len(rest_qubits) == 0:
                break

        return target_gates

    ####################################################################
    ############               Gate's Split                 ############
    ####################################################################
    def split(self, qubits: list = None, depth: Union[int, list] = None, width: int = None):
        """ Split the Circuit/CompositeGate by qubits or depth.

        Args:
            qubits (List): The qubit indexes for one of split CompositeGate.
            depth (Union[int, List]): The split depth for current CompositeGate, support split by different
            depth for different qubits.
            width (int): The width of current Circuit/CompositeGate.
        """
        if qubits is None and depth is None:
            raise KeyError("Split must assign at least one of qubits and depth.")
        elif qubits is not None and depth is not None:
            raise KeyError("Split only allow split either qubits or depth each time. ")

        if qubits is not None:
            return self.split_by_qubits(qubits)
        else:
            if width is None:
                width = len(self.qubits)

            if isinstance(depth, int):
                depth = [depth] * width

            assert len(depth) == width
            return self.split_by_depth(depth)

    def split_by_qubits(self, qubits: list):
        """ Split Circuit/CompositeGate by qubits. """
        left_gates, right_gates = [], []
        for gate in self.gate_list:
            qidxes = gate.qubits if type(gate).__name__ == "CompositeGate" else gate.cargs + gate.targs
            interact_id = set(qidxes) & set(qubits)
            if len(interact_id) == len(qidxes):
                left_gates.append(gate.copy())
            elif len(interact_id) == 0:
                right_gates.append(gate.copy())
            else:
                raise KeyError("Cannot split Circuit due to qubits conflict.")

        return left_gates, right_gates

    def split_by_depth(self, depth: list):
        """ Split Circuit/CompositeGate by depth. """
        based_depth = np.zeros(len(depth), dtype=int)
        left, right = [], []
        for gate in self.flatten(True, False):
            if type(gate).__name__ == "Trigger":
                continue

            targs = gate.cargs + gate.targs
            based_depth[targs] = np.max(based_depth[targs]) + 1

            left_inside, right_inside = False, False
            for targ in targs:
                if based_depth[targ] <= depth[self.qubits.index(targ)]:
                    left_inside = True
                else:
                    right_inside = True

            if left_inside & right_inside:
                raise ValueError(f"Failure to split current circuit, due to {targs}.")

            if left_inside:
                left.append(gate)
            else:
                right.append(gate)

        return left, right
