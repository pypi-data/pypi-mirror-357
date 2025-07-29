import unittest
from numpy.random import randint
from typing import List

from QuICT.algorithm.arithmetic.divider import THRestoreDivider, THNonRestDivider
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int
from QuICT.core.circuit import Circuit
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError


class TestTHRestoringDivider(unittest.TestCase):
    """ Test the quantum divider using restoring division algorithm. """

    def test_THRestoringDivider_correct(self):
        """ Test using THRestoringDivider to do divide on 2's complement positive binary. """

        # circuit size
        qreg_size = randint(3, 8)

        # init dividend
        b = randint(2 ** (qreg_size - 1))
        # init divisor
        a = randint(1, 2 ** (qreg_size - 1))

        # Construct circuit
        cir = self._construct_circuit(qreg_size, b, a)

        # run and decode
        results = self._run_and_decode(qreg_size, cir)
        for i in results:
            quotient, remainder, re_a = i
            self.assertEqual(quotient, b // a)
            self.assertEqual(remainder, b % a)
            self.assertEqual(re_a, a)

    def test_THRestoringDivider_invalid_size(self):
        """ Test using THRestoringDivider with invalid input size. """
        # circuit size
        n = randint(1, 3)

        with self.assertRaises(GateParametersAssignedError):
            self._construct_circuit(n, 0, 1)

    def _construct_circuit(
        self,
        qreg_size: int,
        b: int,
        a: int
    ) -> Circuit:
        """
            construct the divider circuit.

            Args:
                qreg_size (int): The quantum register size of dividend and divisor.
                b (int): The dividend encode into quantum register.
                a (int): The divisor encode into quantum register.

            Returns:
                The circuit of the divider after init regster.
        """
        div_circuit = Circuit(3 * qreg_size)

        b_list = list(range(qreg_size, 2 * qreg_size))
        a_list = list(range(2 * qreg_size, 3 * qreg_size))

        # init quantum register of b
        circuit_init(div_circuit, b_list, b)

        # init quantum register of a
        circuit_init(div_circuit, a_list, a)

        # apply the divider using restoring algorithm
        THRestoreDivider(qreg_size) | div_circuit

        return div_circuit

    def _run_and_decode(
        self,
        qreg_size: int,
        cir: Circuit
    ) -> List:
        """
            Run the circuit and decode the simulation result.

            Args:
                qreg_size (int): size of the quantum register.
                cir (Circuit): the circuit prepared to run.

            Returns:
                The result of output partitioned by meaning.
        """
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=cir)
        counts = sv_sim.sample(shots=1)

        return decode_counts_int(counts, [qreg_size, qreg_size, qreg_size])


class TestTHNonRestDivider(unittest.TestCase):
    """ Test the quantum divider using non-restoring division algorithm. """

    def test_THNonRestDivider_correct(self):
        """ Test using THNonRestDivider to do divide on 2's complement positive binary. """

        # circuit size
        qreg_size = randint(4, 8)

        # init dividend
        b = randint(2 ** (qreg_size - 1))
        # init divisor
        a = randint(1, 2 ** (qreg_size - 1))

        # Construct circuit
        cir = self._construct_circuit(qreg_size, b, a)

        # run and decode
        results = self._run_and_decode(qreg_size, cir)
        for i in results:
            quotient, remainder, re_a = i
            self.assertEqual(quotient, b // a)
            self.assertEqual(remainder, b % a)
            self.assertEqual(re_a, a)

    def test_THNonRestDivider_invalid_size(self):
        """ Test using THNonRestDivider with invalid input size. """
        # circuit size
        n = randint(1, 4)

        with self.assertRaises(GateParametersAssignedError):
            self._construct_circuit(n, 0, 1)

    def _construct_circuit(
        self,
        qreg_size: int,
        b: int,
        a: int
    ) -> Circuit:
        """
            construct the divider circuit.

            Args:
                qreg_size (int): The quantum register size of dividend and divisor.
                b (int): The dividend encode into quantum register.
                a (int): The divisor encode into quantum register.

            Returns:
                The circuit of the divider after init regster.
        """
        div_circuit = Circuit(3 * qreg_size - 1)

        b_list = list(range(qreg_size - 1, 2 * qreg_size - 1))
        a_list = list(range(2 * qreg_size - 1, 3 * qreg_size - 1))

        # init quantum register of b
        circuit_init(div_circuit, b_list, b)

        # init quantum register of a
        circuit_init(div_circuit, a_list, a)

        # apply the divider using restoring algorithm
        THNonRestDivider(qreg_size) | div_circuit

        return div_circuit

    def _run_and_decode(
        self,
        qreg_size: int,
        cir: Circuit
    ) -> List:
        """
            Run the circuit and decode the simulation result.

            Args:
                qreg_size (int): size of the quantum register.
                cir (Circuit): the circuit prepared to run.

            Returns:
                The result of output partitioned by meaning.
        """
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=cir)
        counts = sv_sim.sample(shots=1)

        return decode_counts_int(counts, [qreg_size, qreg_size - 1, qreg_size])


if __name__ == "__main__":
    unittest.main()
