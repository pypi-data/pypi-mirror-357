from enum import Enum
from typing import Union
import numpy as np

from .id_generator import unique_id_generator
from .gate_type import GateType
from .circuit_gate import CircuitGates


class CircuitBased(object):
    """ Based Class for Circuit and Composite Gate. """

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name is None:
            self._name = "QC_" + unique_id_generator()
        else:
            self._name = name

    @property
    def precision(self) -> str:
        return self._precision

    @precision.setter
    def precision(self, precision: str):
        assert precision in ['single', 'double'], ValueError("Wrong precision. Should be one of [single, double]")
        self._precision = precision

    @property
    def gates(self):
        """ Return the list of BasicGate/CompositeGate/Operator in the current circuit. \n
        *Warning*: this is slowly due to the copy of gates, you can use self.fast_gates to
        get list of tuple(gate, qubit_indexes, size) for further using.
        """
        return self._gates.gates()

    @property
    def fast_gates(self):
        """ Return the list of tuple(gate, qubit_indexes, size) in the current circuit. """
        return self._gates.gates(no_copy=True)

    def __init__(self, name: str, qubits: int = 0, precision: str = "double"):
        """
        Args:
            name (str): The name of current Quantum Circuit
        """
        self.name = name
        self.precision = precision

        self._gates = CircuitGates()    # List[Union[BasicGate, CompositeGate]]
        self._qubits = qubits
        self._pointer = None

    ####################################################################
    ############         Circuit's Gates Function           ############
    ####################################################################
    def decomposition_gates(self, no_copy: bool = False) -> list:
        """ Decomposition the CompositeGate or BasicGate which has build_gate function.

        Returns:
            list: The list of BasicGate
        """
        return self._gates.decomposition(no_copy)

    def flatten_gates(self, no_copy: bool = False) -> list:
        """ Get the list of Quantum Gates, flat all the CompositeGate in Circuit. """
        return self._gates.flatten(no_copy)

    def gates_without_last_measure(self, decomposition: bool = False) -> tuple:
        gates_no_measure = self._gates.flatten() if not decomposition else self._gates.decomposition()
        remained_qubits = self._gates.qubits
        measured_q_order = []
        for gid in range(len(gates_no_measure) - 1, -1, -1):
            gate = gates_no_measure[gid]
            gate_args = gate.cargs + gate.targs
            if len(set(gate_args) & set(remained_qubits)) > 0:
                if not hasattr(gate, "type"):
                    continue

                if gate.type == GateType.measure:
                    measured_q_order.append(gate_args[0])
                    gates_no_measure.pop(gid)

                for garg in gate_args:
                    if garg in remained_qubits:
                        remained_qubits.remove(garg)

                if len(remained_qubits) == 0:
                    break

        return gates_no_measure, measured_q_order

    def decomposition(self):
        """ Decomposition the CompositeGate and BasicGate in current Circuit. """
        self._gates.decomposition(no_copy=True, self_change=True)

    def flatten(self):
        """ Flat all CompositeGate in current Circuit. """
        self._gates.flatten(no_copy=True, self_change=True)

    def gate_combination(self, eliminate_single: bool = False):
        """ Combination all consecutive single-qubit gate / bi-qubits gate in the circuit.
        It will flat all CompositeGate here.
        """
        return self._gates.combination(eliminate_single)

    def get_gates_by_depth(self, depth: int) -> list:
        """ Get the list of Quantum Gates in target qubits and depth.

        Args:
            depth (int): The target depth.
        """
        target_qubits = self._gates.qubits
        if depth == -1:
            return self._gates.find_last_layer_gates(target_qubits, all_contains=True)

        return self._gates.get_target_gates(target_qubits, depth, no_copy=False)

    def pop(self, index: int = -1):
        """ Pop the BasicGate/Operator/CompositeGate from current Quantum Circuit.

        Args:
            index (int, optional): The target gate's index. Defaults to 0.
        """
        return self._gates.pop(index)

    def pop_by_position(self, qubits: list, depth: int):
        """ Pop the BasicGate/Operator/CompositeGate from current Quantum Circuit with
        given qubits and depth.

        Args:
            qubits (list): The indexes of qubits.
            depth (int): The target depth.
        """
        return self._gates.pop_by_position(qubits, depth)

    def insert(self, gate, index: int):
        """ insert a Quantum Gate into current Circuit with given index.

        Args:
            gate (Union[BasicGate, CompositeGate]): The quantum gate want to insert.
            index (int): The index of gate list.
        """
        if type(gate).__name__ == "CompositeGate" and gate.size() == 0:
            return

        assert isinstance(index, int) and index >= 0

        self._gates.insert(gate.copy(), index)

    def insert_by_position(self, gate, qubits: list = None, depth: int = -1):
        """ Insert a Quantum Gate into current Circuit with given qubits and depth, it will
        cause the gate list to be flatten due to the insert gate into CompositeGate.

        Args:
            gate (Union[BasicGate, CompositeGate]): The quantum gate want to insert
            qubits (list[int]): The target qubit indexes.
            depth (int): The index of insert position.
        """
        if type(gate).__name__ == "CompositeGate" and gate.size() == 0:
            return

        if qubits is None:
            qubits = gate.qubits if type(gate).__name__ == "CompositeGate" else gate.cargs + gate.targs
            gate = gate.copy()
        else:
            gate = gate.copy() & qubits

        if len(qubits) == 0:
            raise ValueError("Gate need qubit indexes to insert into Composite Gate.")

        self._qubit_indexes_validation(qubits)
        self._gates.insert(gate, depth)

    ####################################################################
    ############           Circuit's Properties             ############
    ####################################################################
    def size(self) -> int:
        """ the number of BasicGate/Operator in the Circuit.

        Returns:
            int: the number of gates in circuit
        """
        return self._gates.size

    def gate_length(self) -> int:
        """ The number of CompositeGate and BasicGate in Circuit. """
        return self._gates.length

    def count_2qubit_gate(self) -> int:
        """ The number of the two qubit gates in the Circuit/CompositeGate

        Returns:
            int: the number of the two qubit gates
        """
        return self._gates.biq_gates_count

    def count_1qubit_gate(self) -> int:
        """ The number of the one qubit gates in the Circuit/CompositeGate

        Returns:
            int: the number of the one qubit gates
        """
        return self._gates.siq_gates_count

    def count_gate_by_gatetype(self, gate_type: GateType) -> int:
        """ The number of the target Quantum Gate in the Circuit/CompositeGate

        Args:
            gateType(GateType): the type of gates to be count

        Returns:
            int: the number of the gates
        """
        return self._gates.gates_count_by_type(gate_type)

    def get_all_gatetype(self) -> list:
        """ Return all gate's type in current circuit. """
        return self._gates.gatetype_list

    def __str__(self):
        circuit_info = {
            "name": self.name,
            "width": self.width(),
            "size": self.size(),
            "depth": self.depth(),
            "1-qubit gates": self.count_1qubit_gate(),
            "2-qubit gates": self.count_2qubit_gate(),
        }

        return str(circuit_info)

    ####################################################################
    ############      Trainable Circuit's Properties        ############
    ####################################################################
    def count_training_gate(self):
        """ The number of the trainable gates in the Circuit/CompositeGate

        Returns:
            int: the number of the trainable gates
        """
        return self._gates.training_gates_count

    def count_variables(self):
        """ The number of the variables in the Circuit/CompositeGate.

        Returns:
            int: The number of variables.
        """
        return self._gates.variables_count

    def free_symbols(self):
        """ The symbols in the Circuit/CompositeGate.

        Returns:
            list: The symbols list.
        """
        return self._gates.free_symbols

    def symbol_pargs(self):
        """ Returns the symbols in the Circuit/CompositeGate and their corresponding values.

        Returns:
            dict: Symbols with corresponding values.
        """
        return self._gates.symbol_pargs

    def assigned_value(self):
        """ Whether all symbols in the Circuit/CompositeGate are assigned values.

        Returns:
            bool: If True, all symbols in the Circuit/CompositeGate are assigned values.
        """
        for gate in self.fast_gates:
            if not gate.assigned_value:
                return False
        return True

    def init_pargs(self, symbols: list, values: Union[list, np.ndarray]):
        """ Initialize the trainable parameters of the Circuit/CompositeGate.

        Args:
            symbols (list): The symbols that needs to be assigned values.
            values (Union[list, np.ndarray]): The values to be assigned.
        """
        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(values, (list, np.ndarray)):
            values = [values]
        assert set(symbols).issubset(set(self.free_symbols())), "The symbols must belong to free symbols."
        self._gates.init_pargs(symbols, values)

    ####################################################################
    ############           Circuit's Utilities              ############
    ####################################################################
    def _qubit_indexes_validation(self, indexes: list):
        """ Validate the qubit indexes.

        Args:
            indexes (list): The given qubit indexes.
        """
        # Indexes' type check
        if not isinstance(indexes, list):
            raise TypeError(
                f"Qubit indexes should be one of int/list[int]/Qubit/Qureg not {type(indexes)}."
            )
        for idx in indexes:
            assert idx >= 0 and isinstance(idx, (int, np.int32, np.int64)), \
                "The qubit indexes should be integer and greater than zero."

        # Repeat indexes check
        if len(indexes) != len(set(indexes)):
            raise ValueError(
                "The qubit indexes cannot contain the repeatted index."
            )

        # Qubit's indexes max/min limitation check
        min_idx, max_idx = min(indexes), max(indexes)
        if min_idx < 0:
            raise ValueError("The qubit indexes should >= 0.")

        if self._qubits != 0:
            assert max_idx < self.width(), ValueError("The max of qubit indexes cannot exceed the width of Circuit.")
            assert len(indexes) <= self.width(), \
                ValueError("The number of qubit index cannot exceed the width of Circuit.")

    def qasm(self, output_file: str = None):
        """ The qasm of current CompositeGate/Circuit. The Operator will be ignore.

        Args:
            output_file (str): The output qasm file's name or path

        Returns:
            str: The string of Circuit/CompositeGate's qasm.
        """
        # Header
        qreg = self.width() if type(self).__name__ == "Circuit" else max(self.qubits) + 1
        creg = min(self.count_gate_by_gatetype(GateType.measure), qreg)
        if creg == 0:
            creg = qreg

        qasm_string = 'OPENQASM 2.0;\ninclude "qelib1.inc";\n'
        qasm_string += f"qreg q[{qreg}];\n"
        qasm_string += f"creg c[{creg}];\n"

        # Body [gates]
        cbits = 0
        for gate in self.flatten_gates(no_copy=True):
            targs = gate.cargs + gate.targs
            if gate.qasm_name == "measure":
                qasm_string += f"measure q[{targs[0]}] -> c[{cbits}];\n"
                cbits += 1
                cbits = cbits % creg
            elif gate.qasm_name == "unitary":
                str_args = [f"q[{arg}]" for arg in targs]
                qasm_string += f"{gate.name} " + ', '.join(str_args) + ";\n"
            else:
                qasm_string += gate.qasm(targs)

        if output_file is not None:
            with open(output_file, "w+") as of:
                of.write(qasm_string)

        return qasm_string

    def qcis(self, output_file: str = None):
        """ generate the qcis of current CompositeGate/Circuit.
        WARNING: Only support the instruction set of QCIS.

        Args:
            output_file (str): The output qcis file's name or path

        Returns:
            str: The string of Circuit/CompositeGate's qcis.
        """
        qcis_string = ""
        # Body [gates]
        for gate in self.flatten_gates(no_copy=True):
            targs = gate.cargs + gate.targs
            if gate.qasm_name == "measure":
                qcis_string += f"M Q{targs[0]}\n"
            elif gate.qasm_name == "rx":
                if np.isclose(gate.parg, np.pi / 2):
                    qcis_string += f"X2P Q{targs[0]}\n"
                elif np.isclose(gate.parg, -np.pi / 2):
                    qcis_string += f"X2M Q{targs[0]}\n"
                else:
                    qcis_string += f"RX Q{targs[0]} {gate.parg}\n"
            elif gate.qasm_name == "ry":
                if np.isclose(gate.parg, np.pi / 2):
                    qcis_string += f"Y2P Q{targs[0]}\n"
                elif np.isclose(gate.parg, -np.pi / 2):
                    qcis_string += f"Y2M Q{targs[0]}\n"
                else:
                    qcis_string += f"RY Q{targs[0]} {gate.parg}\n"
            elif gate.qasm_name == "sdg":
                qcis_string += f"SD Q{targs[0]}\n"
            elif gate.qasm_name == "tdg":
                qcis_string += f"TD Q{targs[0]}\n"
            else:
                gate_qcis = gate.qasm_name.upper()
                qubit_string = ' '.join([f"Q{qarg}" for qarg in targs])
                if gate.params == 0:
                    qcis_string += f"{gate_qcis} {qubit_string}\n"
                else:
                    param_string = ' '.join([str(parg) for parg in gate.pargs])
                    qcis_string += f"{gate_qcis} {qubit_string} {param_string}\n"

        qcis_string = qcis_string[:-1]
        if output_file is not None:
            with open(output_file, "w+") as of:
                of.write(qcis_string)

        return qcis_string

    def draw(
        self,
        method: str = 'matp_auto',
        filename: str = None,
        flatten: bool = False,
        hidden_empty_qubits: bool = True
    ):
        """Draw the figure of circuit.

        Args:
            method(str): the method to draw the circuit
                matp_inline: Show the figure interactively but do not save it to file.
                matp_file: Save the figure to file but do not show it interactively.
                matp_auto: Automatically select inline or file mode according to matplotlib backend.
                matp_silent: Return the drawn figure without saving or showing.
                command : command
            filename(str): the output filename without file extensions, default to None.
                If filename is None, it will using matlibplot.show() except matlibplot.backend
                is agg, it will output jpg file named circuit's name.
            flatten(bool): Whether draw the Circuit with CompositeGate or Decomposite it.
            hidden_empty_qubits(bool): Whether hidden the empty qubits in the circuit's graph.

        Returns:
            If method is 'matp_silent', a matplotlib Figure is returned. Note that that figure is created in matplotlib
            Object Oriented interface, which means it must be display with IPython.display.

        Examples:
            >>> from IPython.display import display
            >>> circ = Circuit(5)
            >>> circ.random_append()
            >>> silent_fig = circ.draw(method="matp_silent")
            >>> display(silent_fig)

            >>> from IPython.display import display
            >>> compositegate = CompositeGate()
            >>> cx_gate=CX & [1,3]
            >>> u2_gate= U2(1, 0)
            >>> H| compositegate(1)
            >>> cx_gate | compositegate
            >>> u2_gate | compositegate(1)
            >>> silent_fig = compositegate.draw(method="matp_silent")
            >>> display(silent_fig)
        """
        from QuICT.tools.drawer import PhotoDrawer, TextDrawing
        import matplotlib

        if method.startswith('matp'):
            if filename is not None:
                if '.' not in filename:
                    filename += '.jpg'

            photo_drawer = PhotoDrawer()
            if method == 'matp_auto':
                save_file = matplotlib.get_backend() == 'agg'
                show_inline = matplotlib.get_backend() != 'agg'
            elif method == 'matp_file':
                save_file = True
                show_inline = False
            elif method == 'matp_inline':
                save_file = False
                show_inline = True
            elif method == 'matp_silent':
                save_file = False
                show_inline = False
            else:
                raise ValueError(
                    "Circuit.draw.matp_method", "[matp_auto, matp_file, matp_inline, matp_silent]", method
                )

            silent = (not show_inline) and (not save_file)
            photo_drawer.run(
                circuit=self, filename=filename, save_file=save_file,
                flatten=flatten, hidden_empty_qubits=hidden_empty_qubits
            )

            if show_inline:
                from IPython.display import display
                display(photo_drawer.figure)
            elif silent:
                return photo_drawer.figure

        elif method == 'command':
            gates = self.flatten_gates() if flatten else self.gates
            qregs = self.qubits if not hidden_empty_qubits else self._gates.qubits
            text_drawer = TextDrawing(qregs, gates, hidden_empty_qubits=hidden_empty_qubits)
            if filename is None:
                print(text_drawer.single_string())
                return
            elif '.' not in filename:
                filename += '.txt'

            text_drawer.dump(filename)
        else:
            raise ValueError(
                "Circuit.draw.method", "[matp_auto, matp_file, matp_inline, matp_silent, command]", method
            )


class CircuitMode(Enum):
    Clifford = "Clifford"
    CliffordRz = "CliffordRz"
    Arithmetic = "Arithmetic"
    Misc = "Misc"
