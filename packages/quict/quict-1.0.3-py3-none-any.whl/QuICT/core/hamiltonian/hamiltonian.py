import re

import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import *
from QuICT.tools.exception.algorithm import HamiltonianError
from QuICT.tools.exception.core import TypeError

_PAULI_OPERATOR_PRODUCTS = {
    ("I", "I"): (1.0, "I"),
    ("I", "X"): (1.0, "X"),
    ("X", "I"): (1.0, "X"),
    ("I", "Y"): (1.0, "Y"),
    ("Y", "I"): (1.0, "Y"),
    ("I", "Z"): (1.0, "Z"),
    ("Z", "I"): (1.0, "Z"),
    ("X", "X"): (1.0, "I"),
    ("Y", "Y"): (1.0, "I"),
    ("Z", "Z"): (1.0, "I"),
    ("X", "Y"): (1.0j, "Z"),
    ("X", "Z"): (-1.0j, "Y"),
    ("Y", "X"): (-1.0j, "Z"),
    ("Y", "Z"): (1.0j, "X"),
    ("Z", "X"): (1.0j, "Y"),
    ("Z", "Y"): (-1.0j, "X"),
}


class Hamiltonian:
    """The Hamiltonian class.

    Note:
        Coefficients are required. And each Pauli Gate should act on different qubit.

        Some examples are like this:

        [[0.4, 'Y0', 'X1', 'Z2', 'I5'], [0.6]]
        [[1, 'X0', 'I5'], [-3, 'Y3'], [0.01, 'Z5', 'Y0']]

    Args:
        pauli_terms (list): A list of pauli terms in the Hamiltonian.
        coefficients (list): A list of coefficients of each pauli term in the Hamiltonian.

    Examples:
        >>> from QuICT.algorithm.quantum_machine_learning.utils import Hamiltonian
        >>> ham = Hamiltonian([["Y0", "X1"], []], [0.4, 0.6])
        >>> ham
        [0.6]
        [0.4, 'Y0', 'X1']
        >>> ham_matrix = ham.get_hamilton_matrix(2)
        >>> ham_matrix
        [[0.6+0.j  0. +0.j  0. +0.j  0. -0.4j]
        [0. +0.j  0.6+0.j  0. -0.4j 0. +0.j ]
        [0. +0.j  0. +0.4j 0.6+0.j  0. +0.j ]
        [0. +0.4j 0. +0.j  0. +0.j  0.6+0.j ]]
    """

    @property
    def pauli_str(self):
        """The pauli string of the Hamiltonian, i.e. [[0.4, 'Y0', 'X1'], [0.6]]."""
        return self._pauli_str

    @property
    def operators(self):
        """The pauli operators of the Hamiltonian, i.e. {'X1 Y0': 0.4, '': 0.6}"""
        return self._operators

    @property
    def coefficients(self):
        """The coefficient of each term in the Hamiltonian, i.e. [0.4, 0.6]."""
        return self._coefficients

    def __init__(self, pauli_terms: list, coefficients: list):
        """Instantiate the Hamiltonian class instance with pauli terms and coefficients."""
        assert len(pauli_terms) == len(coefficients), HamiltonianError(
            "The number of pauli terms and coefficients shoule be same."
        )
        self._operators = self._get_operator_dict(pauli_terms, coefficients)
        self._del_zeros()
        self._coefficients = list(self._operators.values())
        self._pauli_str = self._get_pauli_str()

    @classmethod
    def from_pauli_str(cls, pauli_str: list):
        """Instantiate the Hamiltonian class instance with a Pauli string.

        Args:
            pauli_str (list): A list of Hamiltonian information.
        """
        pauli_terms = []
        coefficients = []
        for pauli_operator in pauli_str:
            coefficients.append(pauli_operator[0])
            pauli_terms.append(pauli_operator[1:])
        return cls(pauli_terms, coefficients)

    def __getitem__(self, indexes):
        """Get slice according to the indexes."""
        pauli_str = []
        if isinstance(indexes, int):
            indexes = [indexes]
        for idx in indexes:
            pauli_str.append(self.pauli_str[idx])
        return Hamiltonian(pauli_str)

    def __repr__(self):
        """Return a sorted pauli string of the Hamiltonian."""
        ham_str = ""
        pauli_str = sorted(self._pauli_str, key=lambda factor: factor[1:])
        for factor in pauli_str:
            ham_str += str(factor) + "\n"
        return ham_str[:-1]

    def __eq__(self, other):
        """Determine whether two Hamiltonians are the same."""
        assert isinstance(other, Hamiltonian), TypeError(
            "Hamiltonian.__eq__.other", "Hamiltonian", type(other)
        )
        if len(self.pauli_str) != len(other.pauli_str):
            return False
        for op1, op2 in zip(self.pauli_str, other.pauli_str):
            if abs(op1[0] - op1[0]) > 1e-8:
                return False
            if op1[1:] != op2[1:]:
                return False
        return True

    def __add__(self, other):
        """Concatenate two Pauli Strings."""
        assert isinstance(other, Hamiltonian), TypeError(
            "Hamiltonian.__add__.other", "Hamiltonian", type(other)
        )
        return Hamiltonian.from_pauli_str(self.pauli_str + other.pauli_str)

    def __sub__(self, other):
        """Concatenate two Pauli strings after the coefficients of the subtrahend term become the opposite."""
        return self.__add__(other.__mul__(-1))

    def __mul__(self, multiplier):
        """Number multiplication operation for coefficients or multiplication between Hamiltonians."""
        if isinstance(multiplier, numbers.Number):
            pauli_terms = list(self.operators.keys())
            coefficients = [coeff * multiplier for coeff in self.coefficients]
            return Hamiltonian(pauli_terms, coefficients)
        elif isinstance(multiplier, Hamiltonian):
            new_operators = dict()
            for left_term, left_coeff in self.operators.items():
                for right_term, right_coeff in multiplier.operators.items():
                    new_coeff = left_coeff * right_coeff
                    if not left_term or not right_term:
                        new_term = left_term + right_term
                    else:
                        new_term = left_term + " " + right_term
                        new_term, new_coeff = self._simplify(new_term, new_coeff)

                    # Update result dict.
                    if new_term in new_operators:
                        new_operators[new_term] += new_coeff
                    else:
                        new_operators[new_term] = new_coeff
            return Hamiltonian(list(new_operators.keys()), list(new_operators.values()))
        else:
            raise TypeError(
                "Hamiltonian.__mul__.multiplier",
                "[numbers.Number, Hamiltonian]",
                type(multiplier),
            )

    def get_hamilton_matrix(self, n_qubits):
        """Construct a matrix form of the Hamiltonian.

        Args:
            n_qubits (int): The number of qubits.

        Returns:
            np.array: The Hamiltonian matrix.
        """
        hamilton_matrix = np.zeros((1 << n_qubits, 1 << n_qubits), dtype=np.complex128)
        hamilton_circuits = self.construct_hamilton_circuit(n_qubits)
        for coeff, circuit in zip(self._coefficients, hamilton_circuits):
            hamilton_matrix += coeff * circuit.matrix()

        return hamilton_matrix

    def construct_hamilton_circuit(self, n_qubits):
        """Construct a circuit form of the Hamiltonian.

        Args:
            n_qubits (int): The number of qubits.

        Returns:
            list<Circuit>: A list of circuits corresponding to the Hamiltonian.
        """
        hamilton_circuits = []
        gate_dict = {"X": X, "Y": Y, "Z": Z}
        for term in self._operators.keys():
            circuit = Circuit(n_qubits)
            if term == "":
                hamilton_circuits.append(circuit)
                continue
            pauli_gates = [gate for gate in re.sub("[0-9]", "", term).split(" ")]
            qubit_indexes = [
                int(index) for index in re.sub("[a-zA-Z]", "", term).split(" ")
            ]
            for qid, gate in zip(qubit_indexes, pauli_gates):
                if gate not in gate_dict.keys():
                    raise HamiltonianError("Invalid Pauli gate.")
                gate_dict[gate] | circuit(qid)
            hamilton_circuits.append(circuit)
        return hamilton_circuits

    def _get_operator_dict(self, pauli_terms, coefficients):
        coefficients = np.array(coefficients)
        operator_dict = {}
        n_terms = len(pauli_terms)
        for i in range(n_terms):
            if not pauli_terms[i]:
                if "" in operator_dict.keys():
                    operator_dict[""] += coefficients[i]
                else:
                    operator_dict[""] = coefficients[i]
                continue
            if isinstance(pauli_terms[i], str):
                pauli_terms[i] = pauli_terms[i].split(" ")
            self._pauli_term_validation(pauli_terms[i])
            term = sorted(self._remove_I(pauli_terms[i]))
            term = " ".join(term)
            if term in operator_dict.keys():
                operator_dict[term] += coefficients[i]
            else:
                operator_dict[term] = coefficients[i]
        return operator_dict

    def _pauli_term_validation(self, pauli_term):
        indexes = []
        for pauli_gate in pauli_term:
            pauli_gate = pauli_gate.upper()
            if (
                pauli_gate[0] not in ["X", "Y", "Z", "I"]
                or not pauli_gate[1:].isdigit()
            ):
                raise HamiltonianError(
                    "The Pauli gate should be in the format of Pauli gate + qubit index. e.g. Z0, I5, Y3."
                )
            indexes.append(int(pauli_gate[1:]))

        if len(indexes) != len(set(indexes)):
            raise HamiltonianError("Each Pauli Gate should act on different qubit.")

    def _remove_I(self, pauli_term):
        for pauli_gate in pauli_term[::-1]:
            if "I" in pauli_gate:
                pauli_term.remove(pauli_gate)
        return pauli_term

    def _get_pauli_str(self):
        assert self.operators, HamiltonianError(
            "The Hamiltonian operator shoule not be empty."
        )
        pauli_str = []
        for term, coefficient in self.operators.items():
            pauli_operator = [coefficient]
            if term:
                for op in term.split(" "):
                    pauli_operator.append(op)
            pauli_operator[1:] = sorted(
                pauli_operator[1:], key=lambda factor: factor[1]
            )
            pauli_str.append(pauli_operator)
        pauli_str.sort()
        return pauli_str

    def _simplify(self, term, coefficient):
        if not term:
            return term, coefficient
        term = sorted(term.split(" "), key=lambda factor: factor[1:])

        new_term = []
        left_factor = term[0]
        for right_factor in term[1:]:
            left_action = left_factor[0]
            left_index = left_factor[1:]
            right_action = right_factor[0]
            right_index = right_factor[1:]

            if left_index == right_index:
                new_coeff, new_action = _PAULI_OPERATOR_PRODUCTS[
                    left_action, right_action
                ]
                left_factor = new_action + str(left_index)
                coefficient *= new_coeff
            else:
                if left_action != "I":
                    new_term.append(left_factor)
                left_factor = right_factor

        if left_factor[1] != "I":
            new_term.append(left_factor)
        new_term = " ".join(new_term)
        return new_term, coefficient

    def _del_zeros(self):
        for term in list(self._operators.keys()):
            if term and abs(self._operators[term]) < 1e-8:
                del self._operators[term]
        if not self._operators:
            self._operators[""] = 0
