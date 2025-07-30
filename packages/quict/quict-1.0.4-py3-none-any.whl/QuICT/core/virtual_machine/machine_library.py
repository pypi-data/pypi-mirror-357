import csv
import os
from QuICT.core.layout.layout import Layout
from QuICT.core.utils.gate_type import GateType
from QuICT.core.virtual_machine.instruction_set import InstructionSet
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.core.virtual_machine.virtual_machine import MachineType


def build_vqm(name: str):
    """A function building QuICT virtual quantum machine library.

    Args:
        name (str): The name of quantum machine
        For machine's name, classify is one of
            [
                CTEKOneD12 CTEKXiaoHong GoogleSycamore IoPCAS QuTechSpin2 QuTechStarmon5
                IBMHanoi IBMBrisbane IBMCairo IBMCleveland IBMCusco IBMHanoi IBMIthaca
                IBMKawasaki IBMKyiv IBMKyoto IBMNazca IBMOsaka IBMPeekskill IBMQuebec
                IBMSherbrooke IBMTorino IBMAlgiers IBMGuadalupe IBMKolkata IBMManila
                IBMMumbai IBMPerth IBMPrague IBMQuito IBMSeattle IonqHarmony SpinQ8
                QuafuScQP10 QuafuScQP18 QuafuScQP21 QuafuScQP136 QuafuDongling QuafuBaihua RigettiAnkaa2 RigettiAnkaa9Q
                OriginalKFC6130 OriginalKFC6131 OriginalWuKong
                TianXuanS1 TianJiS2 TianShuS1 TianJiM1
            ]
    """
    csv_file = os.path.join(os.path.dirname(__file__), f'quantum_machines/{name}.csv')
    csv_cs_file = os.path.join(os.path.dirname(__file__), f'quantum_machines/{name}_cs.csv')

    def read_csv_column(csv_file, column_index):
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            column_data = []

            for row in reader:
                if len(row) > column_index:
                    column_data.append(row[column_index])

        return column_data

    qubits = len(read_csv_column(csv_file, 0)[1:])
    if len(read_csv_column(csv_cs_file, 0)[1:]) > 0:
        double_gate_fidelity, coupling_strength = [], []
        for i in range(len(read_csv_column(csv_cs_file, 0)[1:])):
            double_gate_fidelity.append((
                int(read_csv_column(csv_cs_file, 0)[1:][i]),
                int(read_csv_column(csv_cs_file, 1)[1:][i]),
                float(read_csv_column(csv_cs_file, 2)[1:][i])
            ))
            coupling_strength.append((
                float(read_csv_column(csv_cs_file, 3)[1:][i]),
                float(read_csv_column(csv_cs_file, 4)[1:][i])
            ))
    else:
        double_gate_fidelity = None
        coupling_strength = None

    if name == "OriginalWuKong":
        unreachable_nodes = [5, 21, 23, 43, 51, 53, 55, 58, 59, 63, 64, 69]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    elif name == "GoogleSycamore":
        unreachable_nodes = [2, 5, 17, 35, 59, 65]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    elif name == "CTEKXiaoHong":
        unreachable_nodes = [5, 35, 47]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    elif name == "IBMOsaka":
        unreachable_nodes = [16, 106]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    elif name == "QuafuDongling":
        unreachable_nodes = [0, 1, 7, 8, 14, 15, 30, 38, 43, 47, 61, 70, 78, 84]
        unreachable_nodes += [91, 92, 93, 94, 100, 104, 105, 126, 127, 128, 129]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    elif name == "QuafuBaihua":
        unreachable_nodes = [6, 7, 8, 9, 12, 24, 31, 32, 33, 37, 40, 50, 51, 53]
        unreachable_nodes += [63, 64, 66, 74, 99, 100, 102, 103, 107, 108, 109, 110]
        unreachable_nodes += [111, 112, 113, 116, 118, 131, 134, 141, 148, 149, 150]
        layout = Layout(qubit_number=qubits, unreachable_nodes=unreachable_nodes)
    else:
        layout = Layout(qubit_number=qubits)
    layout.build_layout_by_double_gate_fidelity(double_gate_fidelity)

    qubit_fidelity = []
    for i in range(qubits):
        qubit_fidelity.append((float(read_csv_column(csv_file, 8)[1:][i]), float(read_csv_column(csv_file, 9)[1:][i])))
    preparation_fidelity = [float(i) for i in read_csv_column(csv_file, 4)[1:]]
    gate_fidelity = [float(i) for i in read_csv_column(csv_file, 3)[1:]]
    t1_coherence_time = [float(i) for i in read_csv_column(csv_file, 1)[1:]]
    t2_coherence_time = [float(i) for i in read_csv_column(csv_file, 2)[1:]]
    work_frequency = [float(i) for i in read_csv_column(csv_file, 6)[1:]]
    readout_frequency = [float(i) for i in read_csv_column(csv_file, 5)[1:]]
    gate_duration = [float(i) for i in read_csv_column(csv_file, 7)[1:]]

    if name in [
        "IBMBrisbane", "IBMCleveland", "IBMCusco", "IBMSeattle", "IBMKawasaki", "IBMKyiv",
        "IBMNazca", "IBMOsaka", "IBMQuebec", "IBMSherbrooke"
    ]:
        instruction_set = InstructionSet(GateType.ecr, [GateType.id, GateType.rz, GateType.sx, GateType.x])
    elif name in ["IoPCAS", "OriginalKFC6130", "OriginalKFC6131", "OriginalWuKong"]:
        instruction_set = InstructionSet(GateType.cz, [GateType.u3])
    elif name in ["QuafuScQP10", "QuafuScQP18", "QuafuScQP21", "QuafuScQP136", "QuafuDongling", "QuafuBaihua"]:
        instruction_set = InstructionSet(GateType.cx, [GateType.rx, GateType.rz, GateType.ry, GateType.h])
    elif name in ["RigettiAnkaa2", "RigettiAnkaa9Q"]:
        instruction_set = InstructionSet(GateType.cz, [GateType.rx, GateType.rz])
    elif name in ["TianXuanS1", "TianJiS2", "TianShuS1", "TianJiM1"]:
        instruction_set = InstructionSet(
            GateType.cz,
            [GateType.h, GateType.x, GateType.y, GateType.z, GateType.t, GateType.tdg, GateType.rz]
        )
    elif name == "CTEKOneD12":
        instruction_set = InstructionSet(GateType.cz, [GateType.x, GateType.y, GateType.rx, GateType.ry])
    elif name == "CTEKXiaoHong":
        instruction_set = InstructionSet(
            GateType.cz, [GateType.rz, GateType.sx, GateType.sxdg, GateType.sy, GateType.sydg]
        )
    elif name == "GoogleSycamore":
        instruction_set = InstructionSet(
            GateType.fsim, [GateType.sx, GateType.sy, GateType.sw, GateType.rx, GateType.ry]
        )
    elif name == "QuTechSpin2":
        instruction_set = InstructionSet(GateType.cz, [GateType.id, GateType.rx, GateType.rz])
    elif name == "QuTechStarmon5":
        instruction_set = InstructionSet(
            GateType.cz, [GateType.x, GateType.y, GateType.id, GateType.rx, GateType.ry, GateType.rz]
        )
    elif name == "IonqHarmony":
        instruction_set = InstructionSet(GateType.rxx, [GateType.rx, GateType.ry, GateType.rz])
    else:
        instruction_set = InstructionSet(GateType.cx, [GateType.id, GateType.rz, GateType.sx, GateType.x])

    if name in ["QuTechSpin2", "QuTechStarmon5"]:
        mahcine_type = MachineType.Ion_trap
    else:
        mahcine_type = MachineType.Superconductor

    vqm = VirtualQuantumMachine(
        qubits=qubits,
        instruction_set=instruction_set,
        name=name,
        machine_type=mahcine_type,
        qubit_fidelity=qubit_fidelity,
        preparation_fidelity=preparation_fidelity,
        gate_fidelity=gate_fidelity,
        t1_coherence_time=t1_coherence_time,
        t2_coherence_time=t2_coherence_time,
        layout=layout,
        double_gate_fidelity=double_gate_fidelity,
        coupling_strength=coupling_strength,
        work_frequency=work_frequency,
        readout_frequency=readout_frequency,
        gate_duration=gate_duration
    )

    return vqm
