import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import GateType, BasicGate
from .mps_site import MPSSiteStructure


class MatrixProductStateSimulator:
    """ The Quantum Circuit Simulator with Matrix Product State. """
    @property
    def device(self) -> str:
        return self._device

    @property
    def precision(self) -> str:
        return self._precision

    def __init__(self, device: str = "CPU", precision: str = "double"):
        """ Initial MPS Simulator

        Args:
            device (str, optional): The device type, one of [CPU, GPU]. Defaults to "CPU".
            precision (str, optional): The precision type, one of [single, double]. Defaults to "double".
        """
        self._device = device
        self._precision = precision
        self._mps = MPSSiteStructure(device, precision)

    def _initial_circuit(self, circuit: Circuit):
        """ Pre-Compile Quantum Circuit. **Important** non-used function.

        Args:
            circuit (Circuit): The Quantum Circuit.
        """
        gates_per_layer = []
        depth_per_qubits = np.zeros(circuit.width(), dtype=np.int8)
        flatten_gates = circuit.flatten_gates()
        for gate, qidxes, size in flatten_gates:
            if gate.type == GateType.measure:
                raise ValueError("Not Support Middle-Measure in MPS.")

            gate_depth = np.max(depth_per_qubits[qidxes]) + 1
            if gate_depth > len(gates_per_layer):
                gates_per_layer.append([(gate, qidxes, size)])
            else:
                gates_per_layer[gate_depth - 1].append((gate, qidxes, size))

            depth_per_qubits[qidxes] = gate_depth

        return gates_per_layer

    def run(self, circuit: Circuit, quantum_state: np.ndarray = None) -> MPSSiteStructure:
        """ Start Simulator with given circuit

        Args:
            circuit (Circuit): The quantum circuits.
            quantum_state (np.ndarray, optional): The initial quantum state vector. Defaults to None.

        Returns:
            MPSSiteStructure: The Matrix Product State
        """
        qubits = circuit.width()
        self._mps.initial_mps(qubits, quantum_state)
        for gate in circuit.flatten_gates():
            if isinstance(gate, BasicGate):
                qindex = gate.cargs + gate.targs
                self._apply_basic_gate(gate, qindex)
            else:
                raise ValueError("MPS Simulation only support BasicGate currently.")

        return self._mps

    def _apply_basic_gate(self, gate: BasicGate, qindexes: list):
        """ Apply BasicGate into MPS.

        Args:
            gate (BasicGate): The quantum gate.
            qindexes (list): The qubits' indexes of quantum gate.
        """
        if len(qindexes) == 1:
            self._mps.apply_single_gate(qindexes[0], gate.matrix)
        elif len(qindexes) == 2:
            if gate.type == GateType.unitary:
                gate_matrix = gate.get_matrix(gate.precision)
            else:
                gate_matrix = gate.matrix

            self._mps.apply_double_gate(qindexes, gate_matrix)
        else:
            cgate = gate.build_gate(qindexes)
            for gate in cgate.fast_gates:
                g_idx = gate.cargs + gate.targs
                self._apply_basic_gate(gate, g_idx)

    def sample(self, shots: int):
        """ Sample the measured result from current Matrix Product State.

        Args:
            shots (int): The sample times.
        """
        assert isinstance(shots, int) and shots >= 1

        return self._mps.sample(shots)
