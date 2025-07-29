"""
Synthesize a Clifford circuit unidirectionally or bidirectionally
"""

import copy
import random
import multiprocessing as mp
from typing import Tuple, Union

import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate, CompositeGate, GateType
from QuICT.qcda.synthesis.gate_transform.transform_rule import cy2cx_rule, cz2cx_rule
from QuICT.qcda.utility import PauliOperator, OutputAligner


class CliffordUnidirectionalSynthesizer(object):
    r"""
    Construct $L_1, …, L_n$ such that $C = L_1 … L_j C_j$, where $C_j$ acts trivially on the first $j$ qubits.
    By induction the original Clifford circuit $C$ is synthesized.

    Reference:
        `Clifford Circuit Optimization with Templates and Symbolic Pauli Gates`
        <https://arxiv.org/abs/2105.02291>

    Examples:
        >>> from QuICT.qcda.synthesis.clifford.clifford_synthesizer import CliffordUnidirectionalSynthesizer
        >>> CUS = CliffordUnidirectionalSynthesizer()
        >>> circ_syn = CUS.execute(circ)
    """
    def __init__(self, strategy: str = 'greedy'):
        """
        Args:
            strategy (str, optional): strategy of choosing qubit for each step, in ['greedy', 'random']
        """
        assert strategy in ['greedy', 'random'],\
            ValueError('strategy of choosing qubit could only be "greedy" or "random"')
        self.strategy = strategy

    @OutputAligner()
    def execute(self, gates: Union[Circuit, CompositeGate]) -> CompositeGate:
        """
        Synthesize the Clifford circuit

        Args:
            gates (Circuit/CompositeGate): the Clifford Circuit/CompositeGate to be synthesized

        Returns:
            CompositeGate: the synthesized Clifford CompositeGate
        """
        gates = CompositeGate(gates=gates.gates)
        width = max(gates.qubits) + 1
        gates_deco = CompositeGate()
        for gate in gates.flatten_gates():
            gate: BasicGate
            if gate.is_clifford():
                gates_deco.append(gate)
            elif gate.type == GateType.cz:
                gates_deco.extend(cz2cx_rule(gate))
            elif gate.type == GateType.cy:
                gates_deco.extend(cy2cx_rule(gate))
            else:
                raise TypeError("Only Clifford gates allowed.")
        gates = gates_deco

        def gates_next(gates: CompositeGate, disentangler: CompositeGate):
            gates_next = disentangler.inverse()
            gates_next.extend(gates)
            return gates_next

        gates_syn = CompositeGate()
        not_disentangled = list(range(width))
        if self.strategy == 'greedy':
            while not_disentangled:
                cnot_min = np.inf
                disentangler_min = None
                qubit_min = None
                for qubit in not_disentangled:
                    disentangler = self.disentangle_one_qubit(gates, width, qubit)
                    if disentangler.count_2qubit_gate() < cnot_min:
                        cnot_min = disentangler.count_2qubit_gate()
                        disentangler_min = disentangler
                        qubit_min = qubit
                gates_syn.extend(disentangler_min)
                gates = gates_next(gates, disentangler_min)
                not_disentangled.remove(qubit_min)
        else:
            while not_disentangled:
                qubit = random.choice(not_disentangled)
                disentangler = self.disentangle_one_qubit(gates, width, qubit)
                gates_syn.extend(disentangler)
                gates = gates_next(gates, disentangler)
                not_disentangled.remove(qubit)

        return gates_syn

    @staticmethod
    def disentangle_one_qubit(gates: CompositeGate, width: int, target: int) -> CompositeGate:
        r"""
        Disentangle the target qubit from gates, i.e. for CompositeGate $C$, give the CompositeGate $L$
        such that $L^{-1} C$ acts trivially on the target qubit.

        Args:
            gates (CompositeGate): the CompositeGate to be disentangled
            width (int): the width of the operators
            target (int): the target qubit to be disentangled from gates

        Returns:
            CompositeGate: the disentangler
        """
        # Create X_j, Z_j
        pauli_x = PauliOperator([GateType.id for _ in range(width)])
        pauli_z = PauliOperator([GateType.id for _ in range(width)])
        pauli_x.operator[target] = GateType.x
        pauli_z.operator[target] = GateType.z

        # Compute C X_j C^-1 and C Z_j C^-1
        for gate in gates.inverse().flatten_gates():
            pauli_x.conjugate_act(gate)
            pauli_z.conjugate_act(gate)

        return PauliOperator.disentangler(pauli_x, pauli_z, target)


class CliffordBidirectionalSynthesizer(object):
    r"""
    Construct $L_1, …, L_n, R_1, …, R_n$ such that $C = L_1 … L_j C_j R_j … R_1$,  where $C_j$ acts trivially
    on the first $j$ qubits.
    By induction the original Clifford circuit $C$ is synthesized.

    Reference:
        `Clifford Circuit Optimization with Templates and Symbolic Pauli Gates`
        <https://arxiv.org/abs/2105.02291>

    Examples:
        >>> from QuICT.qcda.synthesis.clifford.clifford_synthesizer import CliffordBidirectionalSynthesizer
        >>> CBS = CliffordBidirectionalSynthesizer()
        >>> circ_syn = CBS.execute(circ)
    """
    def __init__(
            self,
            qubit_strategy: str = 'greedy',
            pauli_strategy: str = 'random',
            shots: int = 1,
            multiprocess: bool = False,
            process: int = 4,
            chunksize: int = 64,
    ):
        """
        Args:
            qubit_strategy (str, optional): strategy of choosing qubit for each step, in ['greedy', 'random']
            pauli_strategy (str, optional): strategy of choosing PauliOperator for each step, in ['greedy', 'random']
            shots (int, optional): if pauli_strategy is random, shots of random
            multiprocess (bool, optional): whether to use the multiprocessing acceleration
            process (int, optional): the number of processes in a pool
            chunksize (int, optional): iteration dealt with in a process
        """
        assert qubit_strategy in ['greedy', 'random'],\
            ValueError('strategy of choosing qubit could only be "greedy" or "random"')
        assert pauli_strategy in ['brute_force', 'random'],\
            ValueError('strategy of choosing PauliOperator could only be "brute_force" or "random"')
        self.qubit_strategy = qubit_strategy
        self.pauli_strategy = pauli_strategy
        self.shots = shots
        self.multiprocess = multiprocess
        self.process = process
        self.chunksize = chunksize

    @OutputAligner()
    def execute(self, gates: Union[Circuit, CompositeGate]) -> CompositeGate:
        """
        Synthesize the Clifford circuit

        Args:
            gates (Circuit/CompositeGate): the Clifford Circuit/CompositeGate to be synthesized

        Returns:
            CompositeGate: the synthesized Clifford CompositeGate
        """
        if isinstance(gates, Circuit):
            gates = gates.to_compositegate()
        width = max(gates.qubits) + 1
        gates_deco = CompositeGate()
        for gate in gates.flatten_gates():
            gate: BasicGate
            if gate.is_clifford():
                gates_deco.append(gate)
            elif gate.type == GateType.cz:
                gates_deco.extend(cz2cx_rule(gate))
            elif gate.type == GateType.cy:
                gates_deco.extend(cy2cx_rule(gate))
            else:
                raise TypeError("Only Clifford gates allowed.")
        gates = gates_deco

        def gates_next(gates: CompositeGate, left: CompositeGate, right: CompositeGate):
            gates_next = left.inverse()
            gates_next.extend(gates)
            gates_next.extend(right)
            return gates_next

        gates_left = CompositeGate()
        gates_right = CompositeGate()
        not_disentangled = list(range(width))

        if self.qubit_strategy == 'greedy':
            while not_disentangled:
                cnot_min = np.inf
                left_min = None
                right_min = None
                qubit_min = None
                for qubit in not_disentangled:
                    cnot_cnt, left, right = self._minimum_over_pauli(gates, width, qubit, not_disentangled)
                    if cnot_cnt < cnot_min:
                        cnot_min = cnot_cnt
                        left_min = left
                        right_min = right
                        qubit_min = qubit
                gates_left.extend(left_min)
                gates_right.insert(right_min.inverse(), 0)
                gates = gates_next(gates, left_min, right_min)
                not_disentangled.remove(qubit_min)
        else:
            while not_disentangled:
                qubit = random.choice(not_disentangled)
                _, left, right = self._minimum_over_pauli(gates, width, qubit, not_disentangled)
                gates_left.extend(left)
                gates_right.insert(right.inverse(), 0)
                gates = gates_next(gates, left, right)
                not_disentangled.remove(qubit)

        gates_left.extend(gates_right)
        return gates_left

    @staticmethod
    def _insert_identity(p: PauliOperator, width: int, not_disentangled: list):
        # Operators on the disentangled qubits must be I
        for i in range(width):
            if i not in not_disentangled:
                p.operator.insert(i, GateType.id)

    @classmethod
    def _brute_force_iterator(cls, gates: CompositeGate, width: int, qubit: int, not_disentangled: list):
        for p1 in PauliOperator.iterator(len(not_disentangled)):
            cls._insert_identity(p1, width, not_disentangled)
            for p2 in PauliOperator.iterator(len(not_disentangled)):
                cls._insert_identity(p2, width, not_disentangled)
                # Only anti-commutative pairs
                if p1.commute(p2):
                    continue
                yield gates, qubit, p1, p2

    @classmethod
    def _random_iterator(cls, gates: CompositeGate, width: int, qubit: int, not_disentangled: list, shots: int):
        for _ in range(shots):
            p1, p2 = PauliOperator.random_anti_commutative_pair(len(not_disentangled))
            cls._insert_identity(p1, width, not_disentangled)
            cls._insert_identity(p2, width, not_disentangled)
            yield gates, qubit, p1, p2

    def _minimum_over_pauli(self, gates: CompositeGate, width: int, qubit: int, not_disentangled: list):
        cnot_min = np.inf
        left_min = None
        right_min = None
        if self.pauli_strategy == 'brute_force':
            iterator = self._brute_force_iterator(gates, width, qubit, not_disentangled)
        if self.pauli_strategy == 'random':
            iterator = self._random_iterator(gates, width, qubit, not_disentangled, self.shots)
        if self.multiprocess:
            pool = mp.Pool(self.process)
            result = pool.starmap_async(self.disentangle_one_qubit,
                                        iterable=iterator,
                                        chunksize=self.chunksize)
            for left, right in result.get():
                if left.count_2qubit_gate() + right.count_2qubit_gate() < cnot_min:
                    cnot_min = left.count_2qubit_gate() + right.count_2qubit_gate()
                    left_min = left
                    right_min = right
            pool.close()
            pool.join()
        else:
            for gates, qubit, p1, p2 in iterator:
                left, right = self.disentangle_one_qubit(gates, qubit, p1, p2)
                if left.count_2qubit_gate() + right.count_2qubit_gate() < cnot_min:
                    cnot_min = left.count_2qubit_gate() + right.count_2qubit_gate()
                    left_min = left
                    right_min = right
        return cnot_min, left_min, right_min

    @staticmethod
    def disentangle_one_qubit(
        gates: CompositeGate,
        target: int,
        p1: PauliOperator,
        p2: PauliOperator
    ) -> Tuple[CompositeGate, CompositeGate]:
        r"""
        Disentangle the target qubit from gates, i.e. for CompositeGate $C$, give the CompositeGate $L, R$
        such that $L^{-1} C R^{-1}$ acts trivially on the target qubit.

        Args:
            gates (CompositeGate): the CompositeGate to be disentangled
            target (int): the target qubit to be disentangled from gates
            p1 (PauliOperator): PauliOperator $P$
            p2 (PauliOperator): PauliOperator $P'$

        Returns:
            Tuple[CompositeGate, CompositeGate]: the left and right disentangler
        """
        # Using the notation in the paper
        o1 = copy.deepcopy(p1)
        o2 = copy.deepcopy(p2)

        # Compute C P C^-1 and C P' C^-1
        for gate in gates.inverse().flatten_gates():
            o1.conjugate_act(gate)
            o2.conjugate_act(gate)

        return PauliOperator.disentangler(o1, o2, target), PauliOperator.disentangler(p1, p2, target)
