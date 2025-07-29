from __future__ import annotations
from typing import Union, List
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, BasicGate, GateType, gate_builder
from QuICT.core.utils import CircuitMatrix
from QuICT.qcda.synthesis import CartanKAKDecomposition


class ConsecutiveGateKAKDecomposition:
    """ Class for optimization the consecutive quantum gates, use KAK Decomposition. """
    __BASED_DOUBLE_GATE_LIST = ['cx', 'rxx', 'ryy', 'rzz']

    def __init__(self, based_2q_gates: Union[str, GateType] = None, threshold: int = 3, min_gate_num: int = 8):
        """
        Args:
            thredshold (int): The threshold number to defined of 2-q gates to decomposition
            based_gates (list): The target 2-qubit gate, should be one of [cx, rxx, ryy, rzz].
                if is None, use cx.
        """
        self.threshold = threshold
        self.min_gate_num = min_gate_num
        self.based_gates = self._valid_2q_gate(based_2q_gates)

        # KAK Decomposition
        self._disintegrator = CartanKAKDecomposition(target=self.based_gates)
        self._matrix_generator = CircuitMatrix()

    def _valid_2q_gate(self, based_2q_gates):
        if based_2q_gates is None:
            return 'cx'

        if isinstance(based_2q_gates, GateType):
            based_2q_gates = based_2q_gates.name

        assert based_2q_gates in self.__BASED_DOUBLE_GATE_LIST, "Based Gates must be one of [cx, rxx, ryy, rzz]."
        if based_2q_gates != 'cx':
            return 'rot'

        return based_2q_gates

    def _circuit_chunking(self, circuit: Union[Circuit, CompositeGate]):
        circuit_blocks, block_qargs = [], []
        block_per_qubits = {}
        for gate in circuit.flatten_gates():
            gate_args = gate.cargs + gate.targs
            if len(gate_args) == 1:
                if gate_args[0] in block_per_qubits.keys():
                    block_id = block_per_qubits[gate_args[0]]
                    new_gate_idx = block_qargs[block_id].index(gate_args[0])
                    circuit_blocks[block_per_qubits[gate_args[0]]].append(gate & new_gate_idx)
                else:
                    circuit_blocks.append([gate & 0])
                    block_qargs.append(gate_args)
                    block_per_qubits[gate_args[0]] = len(circuit_blocks) - 1

            elif len(gate_args) == 2:
                fst_arg_in = gate_args[0] in block_per_qubits.keys()
                sec_arg_in = gate_args[1] in block_per_qubits.keys()
                if fst_arg_in and sec_arg_in:
                    fst_block_id, sec_block_id = block_per_qubits[gate_args[0]], block_per_qubits[gate_args[1]]
                    fst_block_qarg, sec_block_qarg = block_qargs[fst_block_id], block_qargs[sec_block_id]
                    if fst_block_id == sec_block_id:
                        new_gate_idx = [block_qargs[fst_block_id].index(garg) for garg in gate_args]
                        circuit_blocks[fst_block_id].append(gate & new_gate_idx)
                        continue
                    elif len(fst_block_qarg) == 1 and len(sec_block_qarg) == 1:
                        # Gate Combination
                        fst_block = circuit_blocks[fst_block_id]
                        for block_gate in circuit_blocks[sec_block_id]:
                            fst_block.append(block_gate & 1)

                        fst_block.append(gate & [0, 1])
                        block_qargs[fst_block_id] = gate_args
                        block_per_qubits[gate_args[1]] = fst_block_id

                        circuit_blocks.pop(sec_block_id)
                        block_qargs.pop(sec_block_id)
                        for qid, bid in block_per_qubits.items():
                            if bid > sec_block_id:
                                block_per_qubits[qid] -= 1

                        continue

                elif fst_arg_in or sec_arg_in:
                    block_id = block_per_qubits[gate_args[0]] if fst_arg_in else block_per_qubits[gate_args[1]]
                    prev_block_qargs = block_qargs[block_id]
                    if len(prev_block_qargs) == 1:
                        if fst_arg_in:
                            new_gate_idx = [0, 1]
                            prev_block_qargs.append(gate_args[1])
                            block_per_qubits[gate_args[1]] = block_id
                        else:
                            new_gate_idx = [1, 0]
                            prev_block_qargs.append(gate_args[0])
                            block_per_qubits[gate_args[0]] = block_id

                        circuit_blocks[block_id].append(gate & new_gate_idx)
                        continue

                circuit_blocks.append([gate & [0, 1]])
                block_qargs.append(gate_args)
                block_per_qubits[gate_args[0]] = len(circuit_blocks) - 1
                block_per_qubits[gate_args[1]] = len(circuit_blocks) - 1
            else:
                raise ValueError("Only consider 1-q or 2-q")

        return circuit_blocks, block_qargs

    def _get_u3_gate(self, unitary):
        def _check2pi(theta, eps=1e-15):
            """ check whether theta is a multiple of 2π

            Args:
                theta(float): the angle to be checked
                eps(float): tolerate error

            Returns:
                bool: whether theta is a multiple of 2π
            """
            multiple = np.round(theta / (2 * np.pi))
            return abs(2 * np.pi * multiple - theta) < eps

        eps = 1e-6

        # u3[0, 0] is real
        z = np.exp(1j * np.angle(unitary[0, 0]))
        unitary = unitary / z

        theta = np.arccos(unitary[0, 0]).real
        sint = np.sin(theta)
        if abs(sint) >= eps:
            lamda = np.angle(unitary[0, 1] / -sint)
            phi = np.angle(unitary[1, 0] / sint)
        else:
            lamda = 0
            phi = np.angle(unitary[1, 1] / np.cos(theta))
        if _check2pi(theta, eps):
            theta = 0
        if _check2pi(lamda, eps):
            lamda = 0
        if _check2pi(phi, eps):
            phi = 0

        return gate_builder(GateType.u3, params=[theta * 2, phi, lamda])

    def _decomposition(self, block: List[BasicGate], qubit_args: list):
        # Step 1: Get block's qubit number
        qubit_num = len(qubit_args)

        # Step 2: threshold check
        if qubit_num == 2:
            num_2q_gate = 0
            for gate in block:
                if gate.controls + gate.targets == 2:
                    num_2q_gate += 1

            if num_2q_gate < self.threshold and len(block) < self.min_gate_num:
                return CompositeGate(gates=block) & qubit_args

        # Step 3: Get unitary matrix
        unitary_matrix = self._matrix_generator.get_unitary_matrix(block, qubit_num)

        # Step 4: KAK Decomposition or U3 decomposition
        if qubit_num == 2:
            decomp_gates = self._disintegrator.execute(unitary_matrix)
        else:
            decomp_gates = self._get_u3_gate(unitary_matrix)

        # Step 3: Return KAK Result
        return decomp_gates & qubit_args

    def execute(self, circuit: Union[Circuit, CompositeGate]):
        """ Decomposition all consecutive quantum gates with the same n-target qubits in circuit.
        Args:
            circuit (Circuit or CompositeGate): The target quantum circuit
        """
        # Split into Blocks
        circuit_blocks, block_qargs = self._circuit_chunking(circuit)

        # Decomposition for each blocks
        decomp_cir = Circuit(circuit.width()) if isinstance(circuit, Circuit) else CompositeGate()
        for bid, cir_block in enumerate(circuit_blocks):
            cgate = self._decomposition(cir_block, block_qargs[bid])
            cgate | decomp_cir

        decomp_cir.flatten()
        return decomp_cir
