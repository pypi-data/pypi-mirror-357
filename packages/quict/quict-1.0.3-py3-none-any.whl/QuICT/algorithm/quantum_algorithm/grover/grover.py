from typing import Optional, Union, List, Callable, Dict, Tuple
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, Measure
from QuICT.algorithm.quantum_algorithm.amplitude_amplification import AmplitudeAmplification
from QuICT.simulation.state_vector import StateVectorSimulator

from QuICT.tools import Logger
logger = Logger("Grover")

ALPHA = 1.5


class Grover:
    """ Grover's algorithm for solving unstructured search problem.

    References:
        [1]: Nielsen, M.A., & Chuang, I.L. (2010). Quantum Computation and Quantum Information, p.248.

        [2]: Brassard, Gilles, Peter Hoyer, Michele Mosca, and Alain Tapp. “Quantum Amplitude Amplification
          and Estimation,” 305:53-74, 2002. https://doi.org/10.1090/conm/305/05215.
    """

    def __init__(
        self,
        targ_bit_len: int,
        oracle: CompositeGate
    ):
        """
        Args:
            targ_bit_len (int): Length of the target bit string(s).
            oracle (CompositeGate): The oracle that flip the targets' phase.
        """
        if max(oracle.qubits) < targ_bit_len - 1:
            raise ValueError("Oracle's application space smaller than search space.")

        self.targ_bit_len = targ_bit_len
        self.oracle = oracle
        self.amp_alg = AmplitudeAmplification(work_bits=self.targ_bit_len, targ_phase_flip=self.oracle)

    def circuit(
        self,
        iteration: int,
        include_measure: bool = False
    ) -> Circuit:
        """ Grover search for f with custom oracle

        Args:
            iteration (int): Number of grover iteration in the circuit.
            include_measure (bool): When set to `True` the, output will have measurement gates on working qubits.
        Returns:
            Circuit: The grover search circuit.
        """

        amp_circ = self.amp_alg.circuit(iteration=iteration)

        if include_measure:
            for i in range(self.targ_bit_len):
                Measure | amp_circ(i)

        return amp_circ

    def run(
        self,
        n_solution: int,
        backend=StateVectorSimulator(),
        shots: int = 1
    ) -> Dict[str, int]:
        """ With given number of solutions, construct the grover circuit and run.

        Args:
            n_solution (int): Number of solution.
            backend (Any): Device to run the quantum algorithm.
            shots (int): Number of experiments to run.
        """

        it_opt = self._grover_it_num(self.targ_bit_len, n_solution)
        logger.info(f"Building grover circuit with optimal iteration num: {it_opt}.")

        return self.amp_alg.run(iteration=it_opt, backend=backend, shots=shots)

    def run_iterative(
        self,
        solution_checker: Callable[[str], bool],
        backend=StateVectorSimulator()
    ) -> Union[Tuple[str, int], None]:
        """ Run the grover search via a gradually-shrink-search-space strategy. Use this method if the
            number of solution is unknown.

        Args:
            solution_checker (Callable[[str], bool]): A callable that given a string as input, output
                if it's a valid solution.
            backend (Any): Device to run the quantum algorithm.
        """
        n_sol_init = 1 << self.targ_bit_len
        while n_sol_init > 0:
            # get current grover iteration number
            it_num = self._grover_it_num(self.targ_bit_len, n_sol_init)
            logger.info(f"Trying with number of solution : {n_sol_init} with grover iteration = {it_num}.")
            # run qaa
            res_dict = self.amp_alg.run(iteration=it_num, backend=backend, shots=1)
            for key in res_dict:
                if solution_checker(key):
                    logger.info(f"Successfully found solution: {key}.")
                    return key, it_num
            # update next guess
            n_sol_init = int(n_sol_init / ALPHA)
        logger.info(f"Fail finding target with grover.")

        return None

    def _grover_it_num(self, target_bit: int, n_solution: int) -> int:
        """ Given bit length of the search space and number of solution,
            calculate the optimal grover iteration.
        """
        theta_a = np.arcsin(np.sqrt(n_solution / (1 << target_bit)))
        return int(np.pi / (4 * theta_a))
