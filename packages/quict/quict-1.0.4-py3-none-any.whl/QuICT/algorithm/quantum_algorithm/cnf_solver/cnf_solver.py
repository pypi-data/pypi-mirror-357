from typing import Dict, Union, Tuple
from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X, H
from ..grover import Grover
from QuICT.algorithm.oracle import CNFSATOracle
from QuICT.simulation.state_vector import StateVectorSimulator


class CNFSolver:
    """ A solver for CNF satisfiability problem by using grover's search algorithm. """

    def __init__(self, cnf_file: str):
        """
        Args:
            cnf_file (str): Path to the cnf dimacs file.
        """
        self._file_path = cnf_file
        self._circuit = None

        self._var_num, self._cl_num, self._cnf_data = CNFSATOracle.read_CNF(cnf_file)

        self._grover = Grover(
            targ_bit_len=self._var_num,
            oracle=self._cnf_phase_oracle(self._var_num, self._cl_num, self._cnf_data)
        )

    def _cnf_phase_oracle(self, v_num: int, c_num: int, cnf_data: list) -> CompositeGate:
        oracle = CompositeGate()

        X | oracle(v_num)
        H | oracle(v_num)
        CNFSATOracle().circuit([v_num, c_num, cnf_data]) | oracle
        H | oracle(v_num)
        X | oracle(v_num)

        oracle.set_ancilla(list(range(v_num, max(oracle.qubits) + 1)))

        return oracle

    def circuit(self, iteration: int) -> Circuit:
        """ Construct grover search circuit for cnf-sat problem.

        Args:
            iteration (int): number of cnf oracle query in the circuit.

        Returns: Circuit, the quantum circuit for cnf-sat problem with given iteration.
        """
        return self._grover.circuit(iteration)

    def run(
        self,
        n_solution: int,
        backend=StateVectorSimulator(),
        shots: int = 1
    ) -> Dict[str, int]:
        """ Given number of solution, run cnf solver with the optimal grover iteration.

        Args:
            n_solution: number of solutions for the cnf-sat problem.
            backend (Any): Device to run the quantum algorithm.
            shots (int): Number of experiments to run.

        Returns: Dict[str, int], a dictionary in which the key-value pairs are sample strings, denoting cnf
            variable assignments, with their number of times been sampled.
        """
        return self._grover.run(n_solution, backend, shots)

    def run_iterative(self, backend=StateVectorSimulator()) -> Union[Tuple[str, int], None]:
        """ Search by iterative grover without knowning the number of satisfiable solutions.

        Args:
            backend (Any): Device to run the quantum algorithm.

        Returns: Tuple[str, int] | None, when success, the satisfying assignment and the number of
            oracle calls been used are returned.
        """

        return self._grover.run_iterative(self.check_solution, backend)

    def check_solution(self, assignment: str) -> bool:
        """ Check if the given assignment is a satisfying assignment for the cnf.

        Args:
            assignment: the variable assignments to be tested.

        Returns: bool, whether or not the cnf is satisfied.
        """

        return CNFSATOracle.check_solution([int(i) for i in assignment], self._var_num, self._cl_num, self._cnf_data)
