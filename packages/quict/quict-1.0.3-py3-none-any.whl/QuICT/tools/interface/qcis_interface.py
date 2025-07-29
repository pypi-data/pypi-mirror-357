import numpy as np
from math import *

from QuICT.core import Circuit
from QuICT.core.gate import GateType, gate_builder, GATEINFO_MAP


SPECIAL_COMMAND_MAPPING = {
    # Original Quantum Gate
    "X2P": (GateType.rx, np.pi / 2),
    "X2M": (GateType.rx, -np.pi / 2),
    "Y2P": (GateType.ry, np.pi / 2),
    "Y2M": (GateType.ry, -np.pi / 2),
}

COMMAND_MAPPING = {
    # Original Quantum Gate
    "CZ": GateType.cz,
    "RZ": GateType.rz,
    "I": GateType.id,
    "B": GateType.barrier,
    "M": GateType.measure,
    # Composite Quantum Gate
    "H": GateType.h,
    "X": GateType.x,
    "Y": GateType.y,
    "S": GateType.s,
    "SD": GateType.sdg,
    "T": GateType.t,
    "TD": GateType.tdg,
    "Z": GateType.z,
    "RX": GateType.rx,
    "RY": GateType.ry,
    "RXY": GateType.rxy,
    "XY": GateType.xy,
    "XY2P": GateType.xy2p,
    "XY2M": GateType.xy2m,
}


GATETYPE_MAPPING = dict(zip(COMMAND_MAPPING.values(), COMMAND_MAPPING.keys()))


class QCISInterface:
    def __init__(self):
        self.special_gatetype = [GateType.rx, GateType.ry]
        self.special_cmd = ["X2P", "X2M", "Y2P", "Y2M"]
        self.double_qubit_cmd = ["CZ"]

    def load_circuit(self, circuit: Circuit) -> str:
        # Valid Quantum Circuit
        if not self._valid_circuit(circuit):
            raise ValueError(
                f"Failure to generate QCIS instructions, due to unsupport quantum gate inside the circuit."
            )

        # Generate QCIS String
        qcis_string = ""
        for gate in circuit.fast_gates:
            gate_type = gate.type
            # Get QCIS CMD
            if gate.type in self.special_gatetype:
                gate_parg = gate.parg
                if np.isclose(abs(gate_parg), np.pi / 2):
                    qcis_cmd = self._special_cmd_analysis(gate_type, gate_parg)
                else:
                    qcis_cmd = GATETYPE_MAPPING[gate_type]
            else:
                qcis_cmd = GATETYPE_MAPPING[gate_type]

            # Get Qubit Index
            gate_qargs = " ".join([f"Q{qid}" for qid in gate.cargs + gate.targs])

            # Combine CMD and Qubit Index
            gate_qcis = qcis_cmd + " " + gate_qargs

            # Get parameter info
            if gate.params > 0 and qcis_cmd not in self.special_cmd:
                gate_parg = " ".join([str(parg) for parg in gate.pargs])
                gate_qcis = gate_qcis + " " + gate_parg

            gate_qcis += "\n"
            qcis_string += gate_qcis

        return qcis_string

    def load_file(self, filename: str) -> Circuit:
        with open(filename) as qcis_file:
            qcis_string = qcis_file.read()

        return self._analysis_qcis_to_circuit(qcis_string)

    def load_string(self, qcis: str) -> Circuit:
        return self._analysis_qcis_to_circuit(qcis)

    def _valid_circuit(self, circuit: Circuit) -> str:
        for gate in circuit.fast_gates:
            if gate.type not in GATETYPE_MAPPING.keys():
                return False

        return True

    def _special_cmd_analysis(self, gate_type: GateType, gate_parg: float) -> str:
        if gate_type == GateType.rx:
            special_cmd = "X2P" if gate_parg > 0 else "X2M"
        elif gate_type == GateType.ry:
            special_cmd = "Y2P" if gate_parg > 0 else "Y2M"
        else:
            raise KeyError(f"Only support Rx, Ry, bug given {gate_type}.")

        return special_cmd

    def _analysis_qcis_to_circuit(self, qcis_string: str) -> Circuit:
        qcis_by_line = qcis_string.split("\n")
        gate_list, max_qubit = [], 0
        for qcis_line in qcis_by_line:
            if len(qcis_line) == 0:
                continue

            qcis_info = qcis_line.split(" ")
            # From CMD to gate_type
            qcis_cmd = qcis_info[0]
            if qcis_cmd in self.special_cmd:
                gate_type, gate_parg = SPECIAL_COMMAND_MAPPING[qcis_cmd]
            else:
                gate_type = COMMAND_MAPPING[qcis_cmd]

            # Get qubit indexes
            if qcis_cmd in self.double_qubit_cmd:
                gate_qubits = [int(qinfo[1:]) for qinfo in qcis_info[1:3]]
            else:
                gate_qubits = [int(qcis_info[1][1:])]

            # Get Parameters Info
            param_num = GATEINFO_MAP[gate_type][2]
            if qcis_cmd in self.special_cmd:
                gate = gate_builder(gate_type, params=[gate_parg])
            elif param_num > 0:
                gate_pargs = [eval(parg) for parg in qcis_info[len(gate_qubits) + 1:len(gate_qubits) + param_num + 1]]
                gate = gate_builder(gate_type, params=gate_pargs)
            else:
                gate = gate_builder(gate_type)

            # Get Gates
            gate_list.append(gate & gate_qubits)
            max_qubit = max(max_qubit, max(gate_qubits))

        circuit = Circuit(max_qubit + 1)
        for gate in gate_list:
            gate | circuit

        return circuit
