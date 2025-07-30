from typing import List, Tuple

from QuICT.core import Circuit, Hamiltonian
from QuICT.core.gate import CompositeGate, H, Rz, CX, SX


class Trotter:
    """ An Approximated Hamiltonian Evolution Method based on Trotter-Suzuki formula.

        Reference:
            [1]: Nielsen, M.A., & Chuang, I.L. (2010). Quantum Computation and Quantum Information, p.208.
    """
    def __init__(
        self,
        h: Hamiltonian
    ) -> None:

        self.sys_size = self._system_size(h)
        self.parsed_h = self._parse_hamiltonian(h, self.sys_size)

    def circuit(self, time_evol: float, num_it: int) -> Circuit:
        """ Construct the hamiltonian evolution circuit C = (e^(-itH/n))^n

        Args:
            time_evol (float): evolve time.
            num_it (int): number of iteration for the evolution.

        Return:
            Circuit: the hamiltonian evolution circuit.
        """
        def construct_transform(pauli_char: str, pre_cg: CompositeGate, index: int) -> None:
            if pauli_char not in ["I", "X", "Y", "Z"]:
                raise ValueError("Not a valid pauli operator.")

            if pauli_char == "X":
                H | pre_cg(index)
            elif pauli_char == "Y":
                SX | pre_cg(index)

        evolve_it = CompositeGate()

        for coef_pauli_pair in self.parsed_h:
            coef, pauli_str = coef_pauli_pair

            basis_transform = CompositeGate()
            cnot_cg = CompositeGate()
            core = CompositeGate()

            highest_zbasis_idx = -1

            for i in reversed(range(self.sys_size)):
                pauli_char = pauli_str[i]
                construct_transform(pauli_char, basis_transform, i)

                if pauli_char != "I":
                    if highest_zbasis_idx < 0:
                        Rz(2 * (time_evol / num_it) * coef) | core(i)
                    else:
                        cnot_cg.insert(CX & [i, highest_zbasis_idx], 0)
                    highest_zbasis_idx = i

            basis_transform | evolve_it
            cnot_cg | evolve_it
            core | evolve_it
            cnot_cg.inverse() | evolve_it
            basis_transform.inverse() | evolve_it

        evolve_it.flatten()

        trotter_circ = Circuit(self.sys_size)

        for _ in range(num_it):
            evolve_it | trotter_circ

        return trotter_circ

    def _system_size(self, h: Hamiltonian) -> int:
        """ Calculate the minimum number of qubits required for the given hamiltonian. """
        num_q = 0

        for sub_l in h.pauli_str:
            for i in range(1, len(sub_l)):
                cur_idx = int(sub_l[i][1])
                num_q = max(num_q, cur_idx + 1)

        return num_q

    def _parse_hamiltonian(self, h: Hamiltonian, sys_size: int) -> List[Tuple[float, str]]:
        """ Parse the hamiltonian. """
        parsed_h = []

        for sub_l in h.pauli_str:
            pauli_str_list = ["I"] * sys_size
            for i in range(1, len(sub_l)):
                pauli_char, idx = sub_l[i][0], int(sub_l[i][1])
                if pauli_char != "I":
                    pauli_str_list[idx] = pauli_char
            parsed_h.append((sub_l[0], "".join(pauli_str_list)))

        return parsed_h
