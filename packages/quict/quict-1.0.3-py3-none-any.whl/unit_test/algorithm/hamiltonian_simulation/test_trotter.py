from typing import List, Union
import unittest
from QuICT.algorithm.quantum_algorithm.hamiltonian_simulation import Trotter
from QuICT.core.hamiltonian import Hamiltonian
from QuICT.simulation.state_vector import StateVectorSimulator

import numpy as np

PAULI_SET = ["X", "Y", "Z", "I"]
sv_sim = StateVectorSimulator()


class TestTrotter(unittest.TestCase):

    def randH(self, sys_size: int, max_h_size: int) -> List[List[Union[float, str]]]:
        """ Given system size in terms of number of quibts and maximum number of hamiltonian terms
            return the hamiltonian list.
        """
        term_list = []
        coef_list = []
        h_collec = []

        for i in range(max_h_size):
            coef = np.random.random()
            coef_list.append(coef)

            one_term = []
            for j in range(sys_size):
                one_term.append(np.random.choice(PAULI_SET) + str(j))

            cur_pauli_str = "".join([p[0] for p in one_term])
            if cur_pauli_str not in h_collec:
                term_list.append(one_term)
                h_collec.append(cur_pauli_str)

        return term_list, coef_list

    def classical_evolve(
        self,
        h: Hamiltonian,
        t: float,
        init_statevec: Union[np.ndarray, None] = None
    ) -> np.ndarray:
        """ Classical evolve initial state under hamiltonian h for time t, using naive method. """
        num_q = 0
        for sub_l in h.pauli_str:
            for i in range(1, len(sub_l)):
                cur_idx = int(sub_l[i][1])
                num_q = max(num_q, cur_idx + 1)
        if num_q < 1:
            raise ValueError("system size cannot be empty.")

        matrix = Hamiltonian.get_hamilton_matrix(h, num_q)

        e_val, e_vec = np.linalg.eigh(matrix)

        exp_D = np.diag(np.exp(t * -1j * e_val))
        U_evolve = e_vec @ exp_D @ e_vec.T.conj()

        if init_statevec is None:
            return U_evolve[:, 0].flatten()

        return U_evolve @ init_statevec

    def test_single_term(self):
        reps = 20

        for _ in range(reps):
            sys_size = np.random.randint(3, 6)
            terms, coefs = self.randH(sys_size, 1)

            # remove "I" at end
            if terms[-1][-1][0] == "I":
                terms[-1][-1] = "Z" + terms[-1][-1][1]

            h = Hamiltonian(terms, coefs)
            hsim_trot = Trotter(h)

            t_evolve = np.random.random()
            sim_vec = sv_sim.run(hsim_trot.circuit(t_evolve, 1))
            exact_vec = self.classical_evolve(h, t_evolve)

            self.assertTrue(np.allclose(sim_vec, exact_vec, 1e-14), msg=f"Fail on case: {terms, coefs}")
