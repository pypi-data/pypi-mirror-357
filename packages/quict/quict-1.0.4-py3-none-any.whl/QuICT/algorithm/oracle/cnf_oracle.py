import math
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X, CCX
from QuICT.core.gate.backend.mct.mct_linear_dirty_aux import MCTLinearHalfDirtyAux
from QuICT.core.gate.backend.mct.mct_one_aux import MCTOneAux


class CNFSATOracle:
    def __init__(self, simulator=None):
        """
        Args:
            simulator: A QuICT circuit simulator.
        """
        self.simulator = simulator
        self.mct_generator = MCTOneAux()

    def circuit(
        self, cnf_para: str, ancilla_qubits_num: int = 3, dirty_ancilla: int = 0, output_cgate: bool = True
    ) -> Circuit:
        """ Based on the given cnf formula, construct a cnf oracle that will do a bit flip on satisfiable assignments.

        Args:
            cnf_para (str | list): The path of a CNF file in dimacs format or a CNF variables: (variable_number,
                clause_number, CNF_data).
            ancilla_qubits_num (int): Number of ancilla qubits in the circuit. Needs to be greater than or equal to 3.
            dirty_ancilla (int): `0` indicates the ancilla qubits are used as clean qubits. >0 for dirty.
            output_cgate (bool): Whether return a compositegate or a circuit.
        Returns:
            Circuit | CompositeGate: the CNF oracle, a circuit or composite gate.
        """
        # check if Aux > 2
        assert ancilla_qubits_num > 2, "Need at least 3 auxiliary qubit."

        # Step 1: Read CNF File
        if isinstance(cnf_para, str):
            variable_number, clause_number, CNF_data = self.read_CNF(cnf_para)
        else:
            assert len(cnf_para) == 3
            variable_number, clause_number, CNF_data = cnf_para

        # Step 2: Construct Circuit
        self._cgate = CompositeGate()
        p = math.floor((ancilla_qubits_num + 1) / 2)
        depth = math.ceil(math.log(clause_number, p))
        target = variable_number
        if clause_number == 1:
            controls = CNF_data[1]
            controls_abs = []
            controls_X = []
            current_Aux = target + 1
            for i in range(len(controls)):
                if controls[i] < 0:
                    controls_abs.append(-controls[i] - 1)
                if controls[i] > 0:
                    controls_abs.append(controls[i] - 1)
                    controls_X.append(controls[i] - 1)
            for i in range(len(controls_X)):
                X | self._cgate(controls_X[i])
            X | self._cgate(target)
            if controls_abs != []:
                self.mct_generator.execute(len(controls_abs) + 2) | self._cgate(
                    controls_abs + [target, current_Aux]
                )

            for i in range(len(controls_X)):
                X | self._cgate(controls_X[i])
        else:
            if dirty_ancilla == 0:
                if clause_number < p + 1:
                    controls_abs = []
                    for j in range(clause_number):
                        controls_abs.append(variable_number + j + 1)
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j + 1,
                            j + 1,
                            variable_number + j + 1,
                            depth - 1,
                            depth,
                        )
                    if controls_abs != []:
                        self.mct_generator.execute(len(controls_abs) + 2) | self._cgate(
                            controls_abs + [target, target - 1]
                        )
                    else:
                        X | self._cgate(target)
                    for j in range(clause_number):
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j + 1,
                            j + 1,
                            variable_number + j + 1,
                            depth - 1,
                            depth,
                        )
                else:
                    block_len = math.ceil(clause_number / p)
                    block_number = math.ceil(clause_number / block_len)
                    controls = []

                    for j in range(block_number):
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j * block_len + 1,
                            np.minimum((j + 1) * block_len, clause_number),
                            variable_number + ancilla_qubits_num - p + 1 + j,
                            depth - 1,
                            depth,
                        )
                        controls.append(
                            variable_number + ancilla_qubits_num - p + 1 + j
                        )

                    current_Aux = variable_number + 1
                    if controls != []:
                        self.mct_generator.execute(len(controls) + 2) | self._cgate(
                            controls + [target, current_Aux]
                        )

                    for j in range(block_number):
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j * block_len + 1,
                            np.minimum((j + 1) * block_len, clause_number),
                            variable_number + ancilla_qubits_num - p + 1 + j,
                            depth - 1,
                            depth,
                        )
            else:  # dirty_ancilla =1
                if clause_number < p + 1:
                    controls_abs = []
                    for j in range(clause_number):
                        controls_abs.append(variable_number + j + 1)
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j + 1,
                            j + 1,
                            variable_number + j + 1,
                            depth - 1,
                            depth,
                        )
                    if controls_abs != []:
                        self.mct_generator.execute(len(controls_abs) + 2) | self._cgate(
                            controls_abs + [target, target - 1]
                        )

                    for j in range(clause_number):
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            j + 1,
                            j + 1,
                            variable_number + j + 1,
                            depth - 1,
                            depth,
                        )
                else:
                    if clause_number == 2:  # to do

                        CCX | self._cgate(
                            [
                                variable_number + ancilla_qubits_num - 1,
                                variable_number + ancilla_qubits_num,
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            1,
                            1,
                            variable_number + ancilla_qubits_num - 1,
                            depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [
                                variable_number + ancilla_qubits_num - 1,
                                variable_number + ancilla_qubits_num,
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            clause_number,
                            clause_number,
                            variable_number + ancilla_qubits_num,
                            depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [
                                variable_number + ancilla_qubits_num - 1,
                                variable_number + ancilla_qubits_num,
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            1,
                            1,
                            variable_number + ancilla_qubits_num - 1,
                            depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [
                                variable_number + ancilla_qubits_num - 1,
                                variable_number + ancilla_qubits_num,
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            ancilla_qubits_num,
                            clause_number,
                            clause_number,
                            variable_number + ancilla_qubits_num,
                            depth - 1,
                            depth,
                        )

                    else:
                        block_len = math.ceil(clause_number / p)
                        block_number = math.ceil(clause_number / block_len)
                        current_depth = depth
                        # even
                        if block_number == 2:
                            CCX | self._cgate(
                                [
                                    variable_number + ancilla_qubits_num - 1,
                                    variable_number + ancilla_qubits_num,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1,
                                block_len,
                                variable_number + ancilla_qubits_num - 1,
                                depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + ancilla_qubits_num - 1,
                                    variable_number + ancilla_qubits_num,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                block_len + 1,
                                clause_number,
                                variable_number + ancilla_qubits_num,
                                depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + ancilla_qubits_num - 1,
                                    variable_number + ancilla_qubits_num,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1,
                                block_len,
                                variable_number + ancilla_qubits_num - 1,
                                depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + ancilla_qubits_num - 1,
                                    variable_number + ancilla_qubits_num,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                block_len + 1,
                                clause_number,
                                variable_number + ancilla_qubits_num,
                                depth - 1,
                                depth,
                            )

                        else:  # block_number > 2
                            c = []
                            for i in range(
                                variable_number,
                                variable_number + ancilla_qubits_num + 1,
                            ):
                                if i != target:
                                    c.append(i)

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - block_number],
                                    c[ancilla_qubits_num - 2 * (block_number - 1)],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1,
                                block_len,
                                c[ancilla_qubits_num - block_number],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - block_number],
                                    c[ancilla_qubits_num - 2 * (block_number - 1)],
                                    target,
                                ]
                            )

                            # Control bit variable_ Number+Aux - (block_number-1)+2 - j
                            # put a clause, another control bit
                            # (will be the same as the previous target in this for)
                            # and the target will rise in turn
                            for j in range(1, block_number - 2):
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    ancilla_qubits_num,
                                    1 + j * block_len,
                                    (1 + j) * block_len,
                                    c[ancilla_qubits_num - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 2) * block_len,
                                (block_number - 1) * block_len,
                                c[ancilla_qubits_num - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 1) * block_len,
                                clause_number,
                                c[ancilla_qubits_num - 1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 2) * block_len,
                                (block_number - 1) * block_len,
                                c[ancilla_qubits_num - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )

                            for j in range(block_number - 3, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    ancilla_qubits_num,
                                    1 + j * block_len,
                                    (1 + j) * block_len,
                                    c[ancilla_qubits_num - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - block_number],
                                    c[ancilla_qubits_num - 2 * (block_number - 1)],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1,
                                block_len,
                                c[ancilla_qubits_num - block_number],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - block_number],
                                    c[ancilla_qubits_num - 2 * (block_number - 1)],
                                    target,
                                ]
                            )

                            # repeat
                            for j in range(1, block_number - 2):
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    ancilla_qubits_num,
                                    1 + j * block_len,
                                    (1 + j) * block_len,
                                    c[ancilla_qubits_num - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 2) * block_len,
                                (block_number - 1) * block_len,
                                c[ancilla_qubits_num - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 1) * block_len,
                                clause_number,
                                c[ancilla_qubits_num - 1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                ancilla_qubits_num,
                                1 + (block_number - 2) * block_len,
                                (block_number - 1) * block_len,
                                c[ancilla_qubits_num - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[ancilla_qubits_num - 2],
                                    c[ancilla_qubits_num - 1],
                                    c[ancilla_qubits_num - 2 - (block_number - 1)],
                                ]
                            )

                            for j in range(block_number - 3, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    ancilla_qubits_num,
                                    1 + j * block_len,
                                    (1 + j) * block_len,
                                    c[ancilla_qubits_num - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[
                                            ancilla_qubits_num
                                            - (block_number - 1)
                                            + j
                                            - 1
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            + j
                                        ],
                                        c[
                                            ancilla_qubits_num
                                            - 2 * (block_number - 1)
                                            - 1
                                            + j
                                        ],
                                    ]
                                )

        if output_cgate:
            return self._cgate
        else:
            cnf_circuit = Circuit(self._cgate.width())
            self._cgate | cnf_circuit
            return cnf_circuit

    def run(
        self, cnf_para: str, ancilla_qubits_num: int = 3, dirty_ancilla: int = 0, shots: int = 0
    ) -> int:
        """ Based on the given CNF formula, construct the phase oracle and get sampling result or statevector
        by running the oracle as a circuit.

        Args:
            cnf_para (str | list): The path of a CNF file in dimacs format or a CNF variables: (variable_number,
                clause_number, CNF_data).
            ancilla_qubits_num (int): Number of ancilla qubits in the circuit. Needs to be greater than or equal to 3.
            dirty_ancilla (int): `0` indicates the ancilla qubits are used as clean qubits. >0 for dirty.
            shots (int): Number of shots used in the sampling process. When set to `0`, the state vector instead of
                the sampling result will be returned.
        Returns:
            ndarray | List[int]: when `shots<=0`, the state-vector will be returned as an ndarray, otherwise the
                sampling result will be returned.
        """
        # Step 1: Get Circuit
        cnf_circuit = self.circuit(cnf_para, ancilla_qubits_num, dirty_ancilla, output_cgate=False)

        # Step 2: Simulator
        cnf_sv = self.simulator.run(cnf_circuit)

        # Step 3: Sample
        if shots > 0:
            cnf_sample = self.simulator.sample(shots)

            return cnf_sample
        else:
            return cnf_sv

    @staticmethod
    def read_CNF(cnf_file):
        """ Parse the input CNF file.

        Args:
            cnf_file (str): The path of the CNF file in dimacs format.
        Returns:
            (int, int, List[List[int]]): a list containing variable number, clause number and a list representing
            the CNF formula.
        """
        # file analysis
        variable_number = 0
        clause_number = 0
        CNF_data = []
        f = open(cnf_file, "r")
        for line in f.readlines():
            new = line.strip().split()
            if new[0] == "c":
                continue
            int_new = []
            if new[0] == "p":
                variable_number = int(new[2])
                clause_number = int(new[3])
            else:
                for x in new:
                    if (x != "0") and (int(x) not in int_new):
                        int_new.append(int(x))
                        if (-int(x)) in int_new:
                            int_new = []
                            break

            CNF_data.append(int_new)

        f.close()
        return variable_number, clause_number, CNF_data

    @staticmethod
    def check_solution(variable_data, variable_number, clause_number, CNF_data):
        """ Check if the CNF is satisfied with a given assignment to the variables.

        Args:
            variable_data (List[int]): A list of `0` or `1` indicating `False` or `True` assigned to each variable.
            variable_number (int): Number of variable in the CNF.
            clause_number (int): Number of clause in the CNF.
            CNF_data (List[List[int]]): A list representing the CNF formula. Can be generated by `read_CNF`.
        Returns:
            bool: is `True` if the CNF is satisfied.
        """
        cnf_result = 1
        for i in range(clause_number):
            clause_result = 0
            if CNF_data[i + 1] == []:
                clause_result = 1
            else:
                for j in range(len(CNF_data[i + 1])):
                    if CNF_data[i + 1][j] > 0:
                        clause_result = clause_result + variable_data[CNF_data[i + 1][j] - 1]
                    else:
                        if CNF_data[i + 1][j] < 0:
                            clause_result = clause_result  + (1 - variable_data[-CNF_data[i + 1][j] - 1])
                if clause_result == 0:
                    cnf_result = 0
                    break

        if cnf_result == 1:
            return True
        else:
            return False

    @classmethod
    def find_solution_count(cls, variable_number, clause_number, CNF_data):
        """ Use classical brute force method to find the number of solutions that make the CNF satisfied.

        Args:
            variable_number (int): Number of variable in the CNF.
            clause_number (int): Number of clause in the CNF.
            CNF_data (List[List[int]]): A list representing the CNF formula. Can be generated by `read_CNF`.
        Returns:
            int: number of the satisfiable solutions.
        """
        solutions = []
        for i in range(1 << variable_number):
            variable_data = bin(i)[2:].rjust(variable_number, '0')[::-1]
            variable_data = [int(x) for x in variable_data]
            if cls.check_solution(variable_data, variable_number, clause_number, CNF_data):
                solutions.append(variable_data)

        return len(solutions)

    def clause(
        self,
        CNF_data,
        variable_number: int,
        Aux: int,
        StartID: int,
        EndID: int,
        target: int,
        current_depth: int,
        depth: int,
    ):

        p = math.floor((Aux + 1) / 2)
        if StartID == EndID:  # n= variable_number + Aux + 1
            controls = CNF_data[StartID]
            controls_abs = []
            controls_X = []
            for i in range(len(controls)):
                if controls[i] < 0:
                    controls_abs.append(-controls[i] - 1)
                if controls[i] > 0:
                    controls_abs.append(controls[i] - 1)
                    controls_X.append(controls[i] - 1)
            for i in range(len(controls_X)):
                X | self._cgate(controls_X[i])
            X | self._cgate(target)

            d = set(range(variable_number + 1 + Aux))
            d.remove(target)
            for j in controls_abs:
                d.remove(j)
            d = list(d)
            if controls_abs != []:
                MCTLinearHalfDirtyAux().execute(
                    len(controls_abs), (1 + variable_number + Aux)
                ) | self._cgate(controls_abs + d + [target])

            for i in range(len(controls_X)):
                X | self._cgate(controls_X[i])
        else:  # StartID != EndID
            if (EndID - StartID) == 1:  # StartID +1 == EndID
                if ((depth - current_depth) % 2) == 1:  # odd

                    CCX | self._cgate([variable_number + 1, variable_number, target])
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        StartID,
                        StartID,
                        variable_number + 1,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate([variable_number + 1, variable_number, target])
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        EndID,
                        EndID,
                        variable_number,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate([variable_number + 1, variable_number, target])
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        StartID,
                        StartID,
                        variable_number + 1,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate([variable_number + 1, variable_number, target])
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        EndID,
                        EndID,
                        variable_number,
                        current_depth - 1,
                        depth,
                    )

                # even    target in {variable_number + ancilla_qubits_num - p + 1 + j}
                else:

                    CCX | self._cgate(
                        [variable_number + Aux - 1, variable_number + Aux, target]
                    )
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        StartID,
                        StartID,
                        variable_number + Aux - 1,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate(
                        [variable_number + Aux - 1, variable_number + Aux, target]
                    )
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        EndID,
                        EndID,
                        variable_number + Aux,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate(
                        [variable_number + Aux - 1, variable_number + Aux, target]
                    )
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        StartID,
                        StartID,
                        variable_number + Aux - 1,
                        current_depth - 1,
                        depth,
                    )

                    CCX | self._cgate(
                        [variable_number + Aux - 1, variable_number + Aux, target]
                    )
                    self.clause(
                        CNF_data,
                        variable_number,
                        Aux,
                        EndID,
                        EndID,
                        variable_number + Aux,
                        current_depth - 1,
                        depth,
                    )

            else:  # EndID - StartID > 1
                if (
                    EndID - StartID
                ) < p:  # if block_number == 1 and EndID - StartID > 1

                    c = []
                    for i in range(variable_number, variable_number + Aux + 1):
                        if i != target:
                            c.append(i)

                    if ((depth - current_depth) % 2) == 1:

                        CCX | self._cgate(
                            [c[EndID - StartID], c[2 * (EndID - StartID) - 1], target]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            StartID,
                            StartID,
                            c[EndID - StartID],
                            current_depth - 1,
                            depth,
                        )
                        CCX | self._cgate(
                            [c[EndID - StartID], c[2 * (EndID - StartID) - 1], target]
                        )

                        for j in range(1, EndID - StartID - 1):
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[(EndID - StartID) - j],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )

                            # topPhase
                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            EndID,
                            EndID,
                            c[0],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])

                        # downPhase
                        for j in range(EndID - StartID - 2, 0, -1):
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[(EndID - StartID) - j],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )

                        CCX | self._cgate(
                            [c[EndID - StartID], c[2 * (EndID - StartID) - 1], target]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            StartID,
                            StartID,
                            c[EndID - StartID],
                            current_depth - 1,
                            depth,
                        )
                        CCX | self._cgate(
                            [c[EndID - StartID], c[2 * (EndID - StartID) - 1], target]
                        )

                        # repeat....

                        # Restore each location
                        # Control bit variable_ Number+Aux - (EndID StartID)+2 - j put a clause, another control bit
                        # (will be the same as the previous target in this for) and the target will rise in turn
                        for j in range(1, EndID - StartID - 1):
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[(EndID - StartID) - j],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )

                            # topPhase
                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            EndID,
                            EndID,
                            c[0],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate([c[1], c[0], c[EndID - StartID + 1]])

                        # downPhase
                        for j in range(EndID - StartID - 2, 0, -1):
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[(EndID - StartID) - j],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[(EndID - StartID) - j],
                                    c[2 * (EndID - StartID) - 1 - j],
                                    c[2 * (EndID - StartID) - j],
                                ]
                            )

                    else:  # even
                        CCX | self._cgate(
                            [
                                c[Aux - 1 - EndID + StartID],
                                c[Aux - 2 * (EndID - StartID)],
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            StartID,
                            StartID,
                            c[Aux - 1 - EndID + StartID],
                            current_depth - 1,
                            depth,
                        )
                        CCX | self._cgate(
                            [
                                c[Aux - 1 - EndID + StartID],
                                c[Aux - 2 * (EndID - StartID)],
                                target,
                            ]
                        )

                        for j in range(1, EndID - StartID - 1):
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[Aux - (EndID - StartID) + j - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )

                            # topPhase
                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[Aux - 2],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            EndID,
                            EndID,
                            c[Aux - 1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[Aux - 2],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )

                        for j in range(EndID - StartID - 2, 0, -1):
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[Aux - (EndID - StartID) + j - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )

                        CCX | self._cgate(
                            [
                                c[Aux - 1 - EndID + StartID],
                                c[Aux - 2 * (EndID - StartID)],
                                target,
                            ]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            StartID,
                            StartID,
                            c[Aux - 1 - EndID + StartID],
                            current_depth - 1,
                            depth,
                        )
                        CCX | self._cgate(
                            [
                                c[Aux - 1 - EndID + StartID],
                                c[Aux - 2 * (EndID - StartID)],
                                target,
                            ]
                        )

                        for j in range(1, EndID - StartID - 1):
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[Aux - (EndID - StartID) + j - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )

                            # topPhase
                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[Aux - 2],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            EndID,
                            EndID,
                            c[Aux - 1],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )
                        self.clause(
                            CNF_data,
                            variable_number,
                            Aux,
                            (EndID - 1),
                            EndID - 1,
                            c[Aux - 2],
                            current_depth - 1,
                            depth,
                        )

                        CCX | self._cgate(
                            [c[Aux - 2], c[Aux - 1], c[Aux - 2 - EndID + StartID]]
                        )

                        for j in range(EndID - StartID - 2, 0, -1):
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + j,
                                StartID + j,
                                c[Aux - (EndID - StartID) + j - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - (EndID - StartID) + j - 1],
                                    c[Aux - 2 * (EndID - StartID) + j],
                                    c[Aux - 2 * (EndID - StartID) - 1 + j],
                                ]
                            )

                else:  # EndID-StartID > p-1  block number >1
                    block_len = math.ceil((EndID - StartID + 1) / p)
                    block_number = math.ceil((EndID - StartID + 1) / block_len)
                    if block_number == 2:
                        # odd  target :variable_number + ancilla_qubits_num - p + 1 + j
                        if ((depth - current_depth) % 2) == 1:

                            CCX | self._cgate(
                                [variable_number + 1, variable_number, target]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                variable_number + 1,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [variable_number + 1, variable_number, target]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + block_len,
                                EndID,
                                variable_number,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [variable_number + 1, variable_number, target]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                variable_number + 1,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [variable_number + 1, variable_number, target]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + block_len,
                                EndID,
                                variable_number,
                                current_depth - 1,
                                depth,
                            )
                        else:  # 当前偶数层

                            CCX | self._cgate(
                                [
                                    variable_number + Aux - 1,
                                    variable_number + Aux,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                variable_number + Aux - 1,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + Aux - 1,
                                    variable_number + Aux,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + block_len,
                                EndID,
                                variable_number + Aux,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + Aux - 1,
                                    variable_number + Aux,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                variable_number + Aux - 1,
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    variable_number + Aux - 1,
                                    variable_number + Aux,
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + block_len,
                                EndID,
                                variable_number + Aux,
                                current_depth - 1,
                                depth,
                            )
                    else:
                        # block number >2
                        c = []
                        for i in range(variable_number, variable_number + Aux + 1):
                            if i != target:
                                c.append(i)
                        if ((depth - current_depth) % 2) == 1:

                            CCX | self._cgate(
                                [
                                    c[block_number - 1],
                                    c[2 * (block_number - 1) - 1],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                c[block_number - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[block_number - 1],
                                    c[2 * (block_number - 1) - 1],
                                    target,
                                ]
                            )

                            # control bit variable_number + Aux - (block_number-1) + 2 -j
                            # put clause, another control bit and target accension in accordance
                            for j in range(1, block_number - 2):
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (j + 1) * block_len,
                                    c[(block_number - 1) - j],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 1) * block_len,
                                EndID,
                                c[0],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])

                            # downPhase
                            for j in range(block_number - 1 - 2, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (j + 1) * block_len,
                                    c[(block_number - 1) - j],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )

                            CCX | self._cgate(
                                [
                                    c[block_number - 1],
                                    c[2 * (block_number - 1) - 1],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID + block_len - 1,
                                c[block_number - 1],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[block_number - 1],
                                    c[2 * (block_number - 1) - 1],
                                    target,
                                ]
                            )

                            # repeat....

                            # 还原各个位置
                            # 控制位variable_number + Aux - (block_number-1) + 2 -j 放 clause
                            # 另一个 控制位(将与此for内的前一个target 相同)并和target 依次上升
                            for j in range(1, block_number - 1 - 1):
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (j + 1) * block_len,
                                    c[(block_number - 1) - j],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 1) * block_len,
                                EndID,
                                c[0],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate([c[1], c[0], c[block_number]])

                            # downPhase
                            for j in range(block_number - 1 - 2, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (j + 1) * block_len,
                                    c[(block_number - 1) - j],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[(block_number - 1) - j],
                                        c[2 * (block_number - 1) - 1 - j],
                                        c[2 * (block_number - 1) - j],
                                    ]
                                )

                        else:  # even
                            CCX | self._cgate(
                                [
                                    c[Aux - block_number],
                                    c[Aux - 2 * (block_number - 1)],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID - 1 + block_len,
                                c[Aux - block_number],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - block_number],
                                    c[Aux - 2 * (block_number - 1)],
                                    target,
                                ]
                            )

                            for j in range(1, block_number - 2):
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (1 + j) * block_len,
                                    c[Aux - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[Aux - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 1) * block_len,
                                EndID,
                                c[Aux - 1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[Aux - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )

                            for j in range(block_number - 3, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (1 + j) * block_len,
                                    c[Aux - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )

                            CCX | self._cgate(
                                [
                                    c[Aux - block_number],
                                    c[Aux - 2 * (block_number - 1)],
                                    target,
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID,
                                StartID - 1 + block_len,
                                c[Aux - block_number],
                                current_depth - 1,
                                depth,
                            )
                            CCX | self._cgate(
                                [
                                    c[Aux - block_number],
                                    c[Aux - 2 * (block_number - 1)],
                                    target,
                                ]
                            )

                            # re
                            for j in range(1, block_number - 1 - 1):
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (1 + j) * block_len,
                                    c[Aux - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )

                                # topPhase
                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[Aux - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 1) * block_len,
                                EndID,
                                c[Aux - 1],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )
                            self.clause(
                                CNF_data,
                                variable_number,
                                Aux,
                                StartID + (block_number - 2) * block_len,
                                StartID + (block_number - 1) * block_len - 1,
                                c[Aux - 2],
                                current_depth - 1,
                                depth,
                            )

                            CCX | self._cgate(
                                [
                                    c[Aux - 2],
                                    c[Aux - 1],
                                    c[Aux - 2 - (block_number - 1)],
                                ]
                            )

                            for j in range(block_number - 3, 0, -1):
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )
                                self.clause(
                                    CNF_data,
                                    variable_number,
                                    Aux,
                                    StartID + j * block_len,
                                    StartID - 1 + (1 + j) * block_len,
                                    c[Aux - (block_number - 1) + j - 1],
                                    current_depth - 1,
                                    depth,
                                )
                                CCX | self._cgate(
                                    [
                                        c[Aux - (block_number - 1) + j - 1],
                                        c[Aux - 2 * (block_number - 1) + j],
                                        c[Aux - 2 * (block_number - 1) - 1 + j],
                                    ]
                                )
