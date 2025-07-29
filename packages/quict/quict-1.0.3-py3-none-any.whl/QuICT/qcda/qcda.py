"""
Class for customizing the whole process of synthesis, optimization and mapping
"""

from typing import List, Union, Tuple

from QuICT.core import Circuit, Layout
from QuICT.core.gate import CompositeGate
from QuICT.core.virtual_machine import InstructionSet, VirtualQuantumMachine
from QuICT.core.utils import GateType, CLIFFORD_GATE_SET
from QuICT.qcda.synthesis import GateTransform, LocalKAKDecomposition
from QuICT.qcda.optimization import CommutativeOptimization, CliffordRzOptimization, SymbolicCliffordOptimization
from QuICT.qcda.optimization.cnot_without_ancilla import CnotWithoutAncilla
from QuICT.qcda.mapping import SABREMapping, VF2Mapping
from QuICT.tools import Logger


logger = Logger("QCDA")


class QCDA(object):
    """Customize the process of synthesis, optimization and mapping

    In this class, we meant to provide the users with a direct path to design the
    process by which they could transform a unitary matrix to a quantum circuit
    and/or optimize a quantum circuit.
    """

    def __init__(self, process: List = None):
        """Initialize a QCDA process

        A QCDA process is defined by a list of synthesis, optimization and mapping.
        Experienced users could customize the process for certain purposes.

        Args:
            process (list, optional): A customized list of Synthesis, Optimization and Mapping
        """
        self.process = []
        if process is not None:
            self.process = process

    def add_method(self, method=None):
        """Adding a specific method to the process

        Args:
            method: Some QCDA method
        """
        self.process.append(method)

    def add_gate_transform(self, target_instruction: InstructionSet = None, keep_phase: bool = False):
        """Add GateTransform for some target InstructionSet

        GateTransform would transform the gates in the original Circuit/CompositeGate to a certain InstructionSet.

        Args:
            target_instruction (InstructionSet): The target InstructionSet
            keep_phase (bool): whether to keep the global phase as a GPhase gate in the output
        """
        assert target_instruction is not None, ValueError("No InstructionSet provided for Synthesis")
        self.add_method(GateTransform(target_instruction, keep_phase=keep_phase))

    def add_default_optimization(self, level: str = "light", keep_phase: bool = False):
        """Generate the default optimization process

        The default optimization process contains the CommutativeOptimization.

        Args:
            level (str, optional): Optimizing level. Support `light`, `heavy` level.
            keep_phase (bool, optional): whether to keep the global phase as a GPhase gate in the output
        """

        self.add_method(CommutativeOptimization(keep_phase=keep_phase))
        self.add_method(CliffordRzOptimization(level=level, keep_phase=keep_phase))

    def add_mapping(self, layout: Layout = None, method: str = "sabre"):
        """Generate the default mapping process

        The default mapping process contains the Mapping

        Args:
            layout (Layout): Topology of the target physical device
            method (str, optional): used mapping method in ['sabre', 'vf2']
        """
        assert layout is not None, ValueError("No Layout provided for Mapping")
        assert method in ["sabre", "vf2"], ValueError("Invalid mapping method")
        mapping_dict = {
            "sabre": SABREMapping(layout),
            "vf2": VF2Mapping(layout),
        }
        self.add_method(mapping_dict[method])

    def compile(self, circuit: Union[Circuit, CompositeGate]) -> Union[Circuit, CompositeGate]:
        """Compile the circuit with the given process

        Args:
            circuit (Union[Circuit, CompositeGate]): the target CompositeGate or Circuit

        Returns:
            Union[Circuit, CompositeGate]: the resulting CompositeGate or Circuit
        """
        logger.info("QCDA Now processing GateDecomposition.")
        circuit.decomposition()
        circuit.flatten()
        for process in self.process:
            logger.info(f"QCDA Now processing {process.__class__.__name__}.")
            circuit = process.execute(circuit)

        return circuit

    def auto_compile(
        self, circuit: Circuit, quantum_machine_info: VirtualQuantumMachine, keep_phase=False
    ) -> Tuple[Circuit, List[int], List[int]]:
        """Auto-Compile the circuit with the given quantum machine info. Normally follow the steps:

        1. Optimization
        2. Mapping
        3. Local KAK Decomposition
        4. Gate Transform
        5. Optimization

        Args:
            circuit (CompositeGate/Circuit): the target CompositeGate or Circuit
            quantum_machine_info (VirtualQuantumMachine): the information about target quantum machine.
            keep_phase (bool): whether to keep the global phase as a GPhase gate in the output

        Return:
            compiled_circuit (CompositeGate/Circuit): The compiled CompositeGate or Circuit.
            logic2phy (List[int]): The mapping of logical qubits to physical qubits.
            phy2logic (List[int]): The mapping of physical qubits to logical qubits at the end of circuit.
        """
        qm_iset = quantum_machine_info.instruction_set
        qm_layout = quantum_machine_info.layout
        qm_process = []
        # Step 1: optimization algorithm for common circuit
        circuit.decomposition()
        circuit.flatten()
        if circuit.count_gate_by_gatetype(GateType.cx) == circuit.size():
            qm_process.append(CnotWithoutAncilla())
        else:
            gate_types = circuit.get_all_gatetype()
            qm_process.append(self._choice_opt_algorithm(gate_types))

        # Step 2: Mapping if layout is not all-connected
        if qm_layout is not None:
            mapping = SABREMapping(qm_layout, initial_iterations=10, swap_iterations=10)
            qm_process.append(mapping)

        if qm_iset is not None:
            # Step 3: Local KAK Decomposition
            if qm_iset.two_qubit_gate in [GateType.rxx, GateType.ryy, GateType.rzz]:
                qm_process.append(LocalKAKDecomposition(target="rot", keep_phase=keep_phase))
            else:
                qm_process.append(LocalKAKDecomposition(target="cx", keep_phase=keep_phase))

            # Step 4: Gate Transform by the given instruction set
            qm_process.append(GateTransform(qm_iset, keep_phase=keep_phase))

        # Step 5: Start the auto QCDA process:
        logger.info("QCDA Now processing GateDecomposition.")
        for process in qm_process:
            logger.info(f"QCDA Now processing {process.__class__.__name__}.")
            circuit = process.execute(circuit)

        # Step 6: Depending on the special instruction set gate, choice best optimization algorithm.
        if qm_iset is not None or qm_layout is not None:
            post_opt_process = self._choice_opt_algorithm(circuit.get_all_gatetype(), keep_phase=keep_phase)
            logger.info(f"QCDA Now processing {post_opt_process.__class__.__name__}.")
            circuit = post_opt_process.execute(circuit)

        logic2phy = mapping.logic2phy if qm_layout is not None else None
        phy2logic = mapping.phy2logic if qm_layout is not None else None

        return circuit, logic2phy, phy2logic

    def _choice_opt_algorithm(self, gate_types: list, keep_phase=False):
        clifford_only, extra_rz = True, False
        for gtype in gate_types:
            if gtype in (GateType.rz, GateType.ccx, GateType.ccz, GateType.t, GateType.tdg):
                extra_rz = True
            elif gtype not in CLIFFORD_GATE_SET:
                clifford_only = False
                break

        if clifford_only:
            return CliffordRzOptimization(keep_phase=keep_phase) if extra_rz else SymbolicCliffordOptimization()
        else:
            depara_list = []
            if (GateType.x in gate_types or GateType.sx in gate_types) and GateType.rx not in gate_types:
                depara_list.append("x")
            if (GateType.y in gate_types or GateType.sy in gate_types) and GateType.ry not in gate_types:
                depara_list.append("y")
            if (
                GateType.z in gate_types
                or GateType.s in gate_types
                or GateType.t in gate_types
                or GateType.sdg in gate_types
                or GateType.tdg in gate_types
            ) and GateType.rz not in gate_types:
                depara_list.append("z")
            return CommutativeOptimization(depara=depara_list, keep_phase=keep_phase)
