from typing import Union, List, Dict
from enum import Enum

from QuICT.core import Qureg, Layout
from QuICT.tools.exception.core import TypeError

from .instruction_set import InstructionSet


class MachineType(Enum):
    Superconductor = "Superconductor Chip"
    Ion_trap = "Ion trap Chip"


class VirtualQuantumMachine:
    """ The Class store the information about Quantum Machine. """
    @property
    def qubit_number(self) -> int:
        """ Return the number of qubits. """
        return len(self._qubits)

    @property
    def qubits(self) -> Qureg:
        """ Return the Qureg of current Machine. """
        return self._qubits

    @qubits.setter
    def qubits(self, qubits: Qureg):
        assert isinstance(qubits, Qureg)
        self._qubits = qubits

    @property
    def instruction_set(self) -> InstructionSet:
        """ Return the instruction set of current Machine. """
        return self._instruction_set

    @instruction_set.setter
    def instruction_set(self, ins: InstructionSet):
        assert ins is None or isinstance(ins, InstructionSet), \
            TypeError("VirtualQuantumMachine.instruction_set", "InstructionSet", f"{type(ins)}")
        self._instruction_set = ins

    @property
    def layout(self) -> Layout:
        """ Return the layout of current Machine. """
        return self._layout

    @layout.setter
    def layout(self, layout: Layout):
        assert isinstance(layout, Layout), TypeError("VirtualQuantumMachine.layout", "Layout", f"{type(layout)}")
        assert layout.qubit_number == self.qubit_number
        self._layout = layout

    @property
    def qubit_fidelity(self) -> list:
        """ Return the fidelity of each qubits. """
        return self._qubits.fidelity

    @qubit_fidelity.setter
    def qubit_fidelity(self, qf: list):
        if self._unreach_nodes is not None and len(qf) < self.qubit_number:
            qf = self._fill_unreach_point(qf)
        self._qubits.set_fidelity(qf)

    @property
    def preparation_fidelity(self) -> list:
        """ Return the fidelity of each qubits. """
        return self._qubits.preparation_fidelity

    @preparation_fidelity.setter
    def preparation_fidelity(self, qsp: list):
        if self._unreach_nodes is not None and len(qsp) < self.qubit_number:
            qsp = self._fill_unreach_point(qsp)

        self._qubits.set_preparation_fidelity(qsp)

    @property
    def t1_times(self) -> list:
        """ Return the t1 coherence strength of each qubits. """
        return self._qubits.T1

    @t1_times.setter
    def t1_times(self, t1: list):
        if self._unreach_nodes is not None and len(t1) < self.qubit_number:
            t1 = self._fill_unreach_point(t1)

        self._qubits.set_t1_time(t1)

    @property
    def t2_times(self) -> list:
        return self._qubits.T2

    @t2_times.setter
    def t2_times(self, t2: list):
        if self._unreach_nodes is not None and len(t2) < self.qubit_number:
            t2 = self._fill_unreach_point(t2)

        self._qubits.set_t2_time(t2)

    @property
    def double_gate_fidelity(self) -> dict:
        return self._layout.double_gate_fidelity

    @double_gate_fidelity.setter
    def double_gate_fidelity(self, gf: list):
        self._layout.set_double_gate_fidelity(gf)

    @property
    def coupling_strength(self) -> list:
        return self._coupling_strength

    @coupling_strength.setter
    def coupling_strength(self, cs: list):
        assert isinstance(cs, List)
        self._coupling_strength = cs

    @property
    def gate_fidelity(self) -> dict:
        return self._qubits.gate_fidelity

    @gate_fidelity.setter
    def gate_fidelity(self, gf):
        if self._instruction_set is not None and isinstance(gf, dict):
            for gtype in gf.keys():
                if gtype not in self._instruction_set.gates:
                    raise ValueError(f"The gate type {gtype} from GateFidelity is not in current instruction set.")

        if isinstance(gf, list) and self._unreach_nodes is not None and len(gf) < self.qubit_number:
            gf = self._fill_unreach_point(gf)

        self._qubits.set_gate_fidelity(gf)

    @property
    def work_frequency(self) -> List:
        return self._qubits.work_frequency

    @work_frequency.setter
    def work_frequency(self, wf: List):
        if self._unreach_nodes is not None and len(wf) < self.qubit_number:
            wf = self._fill_unreach_point(wf)

        self._qubits.set_work_frequency(wf)

    @property
    def readout_frequency(self) -> List:
        return self._qubits.readout_frequency

    @readout_frequency.setter
    def readout_frequency(self, rf: List):
        if self._unreach_nodes is not None and len(rf) < self.qubit_number:
            rf = self._fill_unreach_point(rf)

        self._qubits.set_readout_frequency(rf)

    @property
    def gate_duration(self) -> List:
        return self._qubits.gate_duration

    @gate_duration.setter
    def gate_duration(self, gd: List):
        if self._unreach_nodes is not None and len(gd) < self.qubit_number:
            gd = self._fill_unreach_point(gd)

        self._qubits.set_gate_duration(gd)

    def __init__(
        self,
        qubits: Union[int, Qureg],
        instruction_set: InstructionSet = None,
        name: str = None,
        machine_type: MachineType = None,
        qubit_fidelity: List[float] = None,
        preparation_fidelity: List[float] = None,
        gate_fidelity: Union[float, Dict] = None,
        t1_coherence_time: List[float] = None,
        t2_coherence_time: List[float] = None,
        double_gate_fidelity: List[tuple] = None,
        coupling_strength: List[tuple] = None,
        layout: Layout = None,
        work_frequency: Union[float, list] = None,
        readout_frequency: Union[float, list] = None,
        gate_duration: Union[float, list] = None,
    ):
        """
        Args:
            qubits (Union[int, Qureg]): The qubit number or the Qureg which is the list of Qubit.
            instruction_set (InstructionSet): The set of quantum gates which Quantum Machine supports.
            name (str): The name of quantum machine.
            qubit_fidelity (list, optional): The readout fidelity for each qubit. Defaults to None.
            preparation_fidelity (list, optional): The state preparation fidelity for each qubit. Defaults to None.
            gate_fidelity (Union[float, dict], optional): The fidelity for single qubit quantum gate. Defaults to None.
            t1_coherence_time (list, optional): The t1 coherence time for each qubit. Defaults to None.
            t2_coherence_time (list, optional): The t2 coherence time for each qubit. Defaults to None.
            double_gate_fidelity (list, optional): The fidelity for double qubit quantum gate. Defaults to None.
            coupling_strength (list, optional): The coupling strength between the qubits. Defaults to None.
            layout (Layout, optional): The description of physical topology of Quantum Machine. Defaults to None.
            work_frequency (Union[float, list]): The frequency when each qubit works in current Quantum Machine.
            readout_frequency (Union[float, list]): The frequency when measured qubits in current Quantum Machine.
            gate_duration (Union[float, list]): The amount of time that a Quantum Gate operators on a Quantum State.

        Raises:
            TypeError: The wrong type about input.
        """
        self.name = name if name is not None else "Quantum_Machine"
        self.machine_type = machine_type if machine_type is not None else MachineType.Superconductor

        # Describe the qubits of Quantum Machine
        if isinstance(qubits, int):
            self._qubits = Qureg(qubits)
        elif isinstance(qubits, Qureg):
            self._qubits = qubits
        else:
            raise TypeError("VirtualQuantumMachine.qubits", "one of [int, Qureg]", f"{type(qubits)}")

        # Describe the layout of Quantum Machine
        self._layout = None
        if layout is not None:
            self.layout = layout
            self._unreach_nodes = layout.unreachable_nodes

        # Describe the gate set of Quantum Machine
        self._instruction_set = None
        if instruction_set is not None:
            self.instruction_set = instruction_set

        if qubit_fidelity is not None:
            self.qubit_fidelity = qubit_fidelity

        if preparation_fidelity is not None:
            self.preparation_fidelity = preparation_fidelity

        if t1_coherence_time is not None:
            self.t1_times = t1_coherence_time

        if t2_coherence_time is not None:
            self.t2_times = t2_coherence_time

        if double_gate_fidelity is not None:
            self.double_gate_fidelity = double_gate_fidelity

        if coupling_strength is not None:
            self.coupling_strength = coupling_strength

        if gate_fidelity is not None:
            self.gate_fidelity = gate_fidelity

        if work_frequency is not None:
            self.work_frequency = work_frequency

        if readout_frequency is not None:
            self.readout_frequency = readout_frequency

        if gate_duration is not None:
            self.gate_duration = gate_duration

    def _fill_unreach_point(self, target_list: list):
        self._unreach_nodes.sort()
        for node in self._unreach_nodes:
            target_list.insert(node, 0.0)

        if len(target_list) > self.qubit_number:
            target_list = target_list[:self.qubit_number]

        return target_list

    def __str__(self):
        return f"Virtual Quantum Machine {self.name}, with {self.qubit_number} qubits."

    def show_layout(self):
        from QuICT.tools.display import layout_graph_drawer

        layout_graph_drawer(self.name, self.layout)
