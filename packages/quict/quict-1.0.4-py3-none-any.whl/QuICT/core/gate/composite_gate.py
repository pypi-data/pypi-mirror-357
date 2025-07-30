from __future__ import annotations

from typing import Union, List
import numpy as np

from QuICT.core.gate import BasicGate
from QuICT.core.utils import CircuitBased, CircuitMatrix, CGATE_LIST, CGATE_HOLD, GATEINFO_MAP
from QuICT.tools.exception.core import CompositeGateAppendError, TypeError, GateQubitAssignedError


class CompositeGate(CircuitBased):
    """ Implement a group of gate """
    @property
    def qubits(self) -> list:
        return self._gates.qubits

    @property
    def ancilla_qubits(self) -> list:
        return self._ancilla_qubits

    def __init__(
        self,
        name: str = None,
        gates: List[BasicGate, CompositeGate] = None,
        precision: str = "double"
    ):
        """
        Args:
            name (str, optional): the name of the composite gate. Defaults to None.
            gates (List[BasicGate, CompositeGate], optional): gates within this composite gate. Defaults to None.
        """
        super().__init__(name, precision=precision)
        if gates is not None:
            for gate in gates:
                if isinstance(gate, CompositeGate):
                    self.extend(gate)
                else:
                    self.append(gate)
        self._ancilla_qubits = []

    def clean(self):
        """ Remove all quantum gates in current Circuit. """
        self._gates.reset()
        self._pointer = None

    def width(self):
        """ The number of qubits in CompositeGate.

        Returns:
            int: the number of qubits in circuit
        """
        return len(self.qubits)

    def depth(self):
        """ The depth of the circuit.

        Returns:
            int: the depth
        """
        return self._gates.depth(max(self.qubits) + 1)

    ####################################################################
    ############          CompositeGate Context             ############
    ####################################################################
    def __enter__(self):
        global CGATE_LIST
        CGATE_LIST.append(self)
        CGATE_HOLD[self._name] = False

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print(f"{exc_type}: {exc_value}")
        if exc_type is not None:
            raise Exception(exc_value)

        global CGATE_LIST
        CGATE_LIST.remove(self)
        CGATE_HOLD.pop(self.name)

        return True

    ####################################################################
    ############        CompositeGate Qureg Mapping         ############
    ####################################################################
    def __call__(self, indexes: Union[list, int]):
        if isinstance(indexes, int):
            indexes = [indexes]

        self._qubit_indexes_validation(indexes)
        self._pointer = indexes
        return self

    def __and__(self, targets: Union[int, list]):
        """ assign indexes for the composite gates

        Args:
            targets ([int/list[int]]): qubit describe
        """
        if isinstance(targets, int):
            targets = [targets]

        self._qubit_indexes_validation(targets)
        context_hold = False
        if CGATE_LIST:
            target_cgate = CGATE_LIST[-1]
            global CGATE_HOLD
            if not CGATE_HOLD[target_cgate.name]:
                CGATE_HOLD[target_cgate.name] = True
                context_hold = True

        self._gates.remap(targets)

        if CGATE_LIST:
            if context_hold:
                target_cgate.extend(self)
                CGATE_HOLD[target_cgate.name] = False

        return self

    ####################################################################
    ############            CompositeGate Build             ############
    ####################################################################
    def __or__(self, targets):
        """ deal the operator '|'

        Use the syntax "CompositeGate | circuit", "CompositeGate | CompositeGate"
        to add the gate of gateSet into the circuit

        Note that the order of qubits is that control bits first
        and target bits followed.

        Args:
            targets: the targets the gate acts on, it can have the following form,
                1) Circuit
                2) CompositeGate
        Raise:
            TypeError: the type of other is wrong
        """
        try:
            targets.extend(self)
        except Exception as e:
            raise CompositeGateAppendError(f"Failure to append current CompositeGate, due to {e}.")

    def __xor__(self, targets):
        """deal the operator '^'

        Use the syntax "gateSet ^ circuit", "gateSet ^ gateSet"
        to add the gate of gateSet's inverse into the circuit

        Note that the order of qubits is that control bits first
        and target bits followed.

        Args:
            targets: the targets the gate acts on, it can have the following form,
                1) Circuit
                2) CompositeGate
        Raise:
            TypeError: the type of other is wrong
        """
        try:
            targets.extend(self.inverse())
        except Exception as e:
            raise CompositeGateAppendError(f"Failure to append the inverse of current CompositeGate, due to {e}.")

    def __getitem__(self, item):
        """ get gates from this composite gate

        Args:
            item (int/slice): slice passed in.

        Return:
            [BasicGates]: the gates
        """
        gate = self._gates.gate_list[item]

        return gate.copy()

    def extend(self, gates: CompositeGate):
        """ Add a CompositeGate to current CompositeGate.

        Args:
            gates (CompositeGate): The given CompositeGate
        """
        if gates.size() == 0:
            return

        if self._pointer is not None:
            gate_args = gates.width()
            assert gate_args <= len(self._pointer), GateQubitAssignedError(
                f"{gates.name} need at least {gate_args} indexes, but given {len(self._pointer)}"
            )
            if gate_args == len(self._pointer):
                gate_qidxes = self._pointer[:]
            else:
                gate_qidxes = [self._pointer[qidx] for qidx in gates.qubits]

            copy_gates = gates.copy() & gate_qidxes
        else:
            self._qubit_indexes_validation(gates.qubits)
            copy_gates = gates.copy()

        self._gates.extend(copy_gates)
        self._pointer = None

    def append(self, gate: BasicGate):
        """ Add a quantum gate to current CompositeGate.

        Args:
            gate (BasicGate): The quantum gate need to append
        """
        if type(gate).__name__ in ["Multiply", "DataSwitch", "DeviceTrigger", "SpecialGate"]:
            self._gates.append(gate)
            return

        if not isinstance(gate, BasicGate):
            raise TypeError("CompositeGate.append", "BasicGate", type(gate))

        if self._pointer is not None:
            gate_args = gate.controls + gate.targets
            assert len(self._pointer) == gate_args, \
                GateQubitAssignedError(f"{gate.type} need {gate_args} indexes, but given {len(self._pointer)}")

            qubit_index = self._pointer[:]
            copy_gate = gate.copy() & qubit_index
        else:
            qubit_index = gate.cargs + gate.targs
            if not qubit_index:
                raise GateQubitAssignedError(f"{gate.type} need qubit indexes to add into Composite Gate.")

            self._qubit_indexes_validation(qubit_index)
            copy_gate = gate.copy()

        self._gates.append(copy_gate)
        self._pointer = None

    def split(self, qubits: list = None, depth: Union[int, list] = None, rescale: bool = True):
        """ Split the CompositeGate by qubits or depth.

        Args:
            qubits (List): The qubit indexes for one of split CompositeGate.
            depth (Union[int, List]): The split depth for current CompositeGate, support split by different
            depth for different qubits.
        """
        left_gates, right_gates = self._gates.split(qubits, depth)
        left_cgate, right_cgate = CompositeGate(gates=left_gates), CompositeGate(gates=right_gates)
        if rescale:
            left_cgate & list(range(left_cgate.width()))
            right_cgate & list(range(right_cgate.width()))

        return left_cgate, right_cgate

    ####################################################################
    ############            CompositeGate Utils             ############
    ####################################################################
    def inverse(self) -> CompositeGate:
        # Refactoring later
        """ the inverse of CompositeGate

        Returns:
            CompositeGate: the inverse of the gateSet
        """
        _gates = CompositeGate(name=f"inv({self.name})")
        for gate in self.gates[::-1]:
            gate.inverse() | _gates

        return _gates

    def copy(self) -> CompositeGate:
        """ Copy current CompositeGate. """
        _gates = CompositeGate(gates=self.gates)
        _gates.name = self.name

        return _gates

    def matrix(self, device: str = "CPU", local: bool = False, expand_gate: bool = True) -> np.ndarray:
        """ matrix of these gates

        Args:
            device (str, optional): The device type for generate circuit's matrix, one of [CPU, GPU]. Defaults to "CPU".
            local (bool): whether consider only about the occupied qubits or not
            expand_gate (bool, optional): whether or not expand each gate to the full system size when calculating
                circuit's matrix. Default to `True`.

        Returns:
            np.ndarray: the matrix of the gates
        """
        assert device in ["CPU", "GPU"]
        circuit_matrix = CircuitMatrix(device, self._precision)
        if self.size() != self.count_1qubit_gate() + self.count_2qubit_gate():
            based_gates = self.decomposition_gates()
        else:
            based_gates = self.flatten_gates()

        if not local:
            matrix_width = max(self.qubits) + 1
        else:
            matrix_width, based_qubits = self.width(), self.qubits
            for gate in based_gates:
                new_qidx = [based_qubits.index(q) for q in gate.cargs + gate.targs]
                gate & new_qidx

        if not expand_gate:
            return circuit_matrix.get_unitary_matrix_non_expand(based_gates, matrix_width)

        return circuit_matrix.get_unitary_matrix(based_gates, matrix_width)

    def exp2(self, n: int) -> CompositeGate:
        """ Get a Composite that applys current Composite gate 2^n times

        Args:
            n (int): The exponent.

        Returns:
            CompositeGate: a gate that apply the original gate 2^n times.
        """
        if n < 0:
            raise ValueError("The exponent can't be smaller than 0.")

        _gates = CompositeGate(f"{self.name}^(2^{n})")

        for _ in range(1 << n):
            for gate in self.gates:
                gate | _gates

        _gates.set_ancilla(self.ancilla_qubits)
        return _gates

    def controlled(self) -> CompositeGate:
        from QuICT.core.gate import MultiControlGate, GateType

        _gates = CompositeGate(f"c-{self.name}")

        for g in self.decomposition_gates(True):
            ctargs = g.cargs + g.targs
            if g.type == GateType.id:
                BasicGate(
                    *GATEINFO_MAP[GateType.id],
                    is_original_gate=True
                ) | _gates(0)
            elif g.type == GateType.gphase:
                BasicGate(
                    *GATEINFO_MAP[GateType.phase],
                    pargs=g.pargs,
                    is_original_gate=True
                ) | _gates(0)
            else:
                MultiControlGate(
                    controls=1,
                    gate_type=g.type,
                    params=g.pargs
                ).build_gate() | _gates([0] + (np.array(ctargs, dtype=int) + 1).tolist())

        _gates.flatten()

        if len(self.ancilla_qubits) > 0:
            _gates.set_ancilla((np.array(self.ancilla_qubits) + 1).tolist())

        return _gates

    def set_ancilla(self, ancilla_qubits: List[int]) -> None:
        """ Set ancilla qubits' indices.

        Args:
            ancilla_qubits (List[int]): list of indices indicating the ancilla qubits.
        """
        if len(ancilla_qubits) < 1:
            return
        self._qubit_indexes_validation(ancilla_qubits)
        if max(ancilla_qubits) > max(self.qubits):
            raise ValueError(f"Ancilla index {max(ancilla_qubits)} is outside the composite "
                             f"gate's current application range. Which is {max(self.qubits)}")
        self._ancilla_qubits = ancilla_qubits

    def peel(self, level: int = -1) -> CompositeGate:
        """ Partially flatten the composite gates inside current composite.

        Args:
            level (int): maximum level to flatten the composite gates. `lelve = -1` means
                the composite gates will be fully flattened.

        Returns:
            CompositeGate: a partially flattened composite gate.
        """
        if self._gates is None:
            return self

        _cg_peeled = CompositeGate(precision=self.precision)

        _cg_peeled._gates = self._gates.flatten_by_level(level=level)

        return _cg_peeled
