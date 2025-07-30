import unittest
from numpy.random import randint
from typing import List

from QuICT.algorithm.arithmetic.adder import TRIOCarryAdder
from QuICT.core.circuit import Circuit
from QuICT.core.gate import X
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int


class TestTRIOCarryAdder(unittest.TestCase):
    """ Test the quantum ripple carry adder with input carry"""

    def test_TRIOCarryAdder_unsigned(self):
        """ Test using TRIOCarryAdder gates to do unsigned addition. """

        # circuit size
        qreg_size = randint(2, 11)

        # init two addends
        a = randint(2 ** qreg_size)
        b = randint(2 ** qreg_size)
        c0 = randint(2)

        # test
        self._test_unsigned(qreg_size, a, b, c0)

    def test_TRIOCarryAdder_signed(self):
        """ Test using TRIOCarryAdder gates to do signed addition. """

        # circuit size
        qreg_size = randint(2, 11)

        # init two addends
        a = randint(-2 ** (qreg_size - 1), 2 ** (qreg_size - 1))
        b = randint(-2 ** (qreg_size - 1), 2 ** (qreg_size - 1))
        c0 = randint(2)

        # test
        # regular case
        self._test_signed(3, -1, -2, False)
        self._test_signed(3, -1, 2, True)
        self._test_signed(3, 1, -2, False)
        # overflow
        self._test_signed(3, 3, 3, False)
        # underflow
        self._test_signed(3, -4, -4, False)
        # random case
        self._test_signed(qreg_size, a, b, c0)

    def test_TRIOCarryAdder_unsigned_scale2(self):
        """ Test using TRIOCarryAdder gates to do addition with two qubit size of addend. """
        a = randint(4)
        b = randint(4)
        c0 = randint(2)

        # Test
        self._test_unsigned(2, a, b, c0)

    def test_TRIOCarryAdder_signed_scale2(self):
        """ Test using TRIOCarryAdder gates to do addition with two qubit size of addend. """
        a = randint(-2, 2)
        b = randint(-2, 2)
        c0 = randint(2)

        # Test
        self._test_signed(2, a, b, c0)

    def _test_unsigned(
        self,
        qreg_size: int,
        a: int,
        b: int,
        c0: bool
    ):
        """
            Unit test for unsigned numbers.
            Args:
                qreg_size (int): The qubits figures of two addends.
                a (int): The first addend encode into quantum register.
                b (int): The second addend encode into quantum register.
                c0 (bool): The input carry bit which must be 0 or 1.
        """
        # Construct circuit
        circuit = self._construct_adder_circuit(qreg_size, a, b, c0)

        # run and decode
        result = self._run_and_decode_result(circuit, qreg_size)
        for i in result:
            out_sum, out_a, out_c0 = i
            self.assertEqual(out_sum, a + b + c0)
            self.assertEqual(out_a, a)
            self.assertEqual(out_c0, c0)

    def _test_signed(
        self,
        qreg_size: int,
        a: int,
        b: int,
        c0: bool
    ):
        """
            Unit test for signed numbers.
            Args:
                qreg_size (int): The qubits figures of two addends.
                a (int): The first addend encode into quantum register.
                b (int): The second addend encode into quantum register.
                c0 (bool): The input carry bit which must be 0 or 1.
        """
        # Construct circuit
        circuit = self._construct_adder_circuit(qreg_size, a, b, c0)

        # run and decode
        result = self._run_and_decode_result(circuit, qreg_size, True)
        for i in result:
            out_carry, out_sum, out_a, out_c0 = i
            self.assertEqual(
                self._unsigned_to_signed(out_sum, qreg_size),
                (a + b + c0 + 2 ** (qreg_size - 1)) % (2 ** qreg_size) - 2 ** (qreg_size - 1)
            )
            self.assertEqual(self._unsigned_to_signed(out_a, qreg_size), a)
            self.assertEqual(out_c0, c0)

    def _construct_adder_circuit(
        self,
        qreg_size: int,
        a: int,
        b: int,
        c0: bool,
    ) -> Circuit:
        """
            Args:
                 qreg_size (int): The qubits figures of two addends.
                 a (int): The first addend encode into quantum register.
                 b (int): The second addend encode into quantum register.
                 c0 (bool): The input carry bit which must be 0 or 1.

            Returns:
                The circuit of the adder after init register.
        """
        add_circuit = Circuit(2 * qreg_size + 2)

        b_list = list(range(1, qreg_size + 1))
        a_list = list(range(qreg_size + 1, 2 * qreg_size + 1))
        in_carry = [2 * qreg_size + 1]

        # init register storing first addend a
        circuit_init(add_circuit, a_list, a)

        # init register storing second addend b
        circuit_init(add_circuit, b_list, b)

        # init input carry bit
        if c0:
            X | add_circuit(in_carry)

        # apply the adder with input carry
        TRIOCarryAdder(qreg_size) | add_circuit

        return add_circuit

    def _run_and_decode_result(
        self,
        circuit: Circuit,
        qreg_size: int,
        signed: bool = False
    ) -> List:
        """
            Run the circuit and decode the simulation result.

            Args:
                circuit (Circuit): the circuit prepared to run.
                qreg_size (int): size of the quantum register.
                signed (int): if True, will add one more bit for sign.

            Returns:
                The result of output partitioned by meaning.
        """
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=circuit)
        counts = sv_sim.sample(shots=1)

        if signed:
            return decode_counts_int(counts, [1, qreg_size, qreg_size, 1])
        else:
            return decode_counts_int(counts, [qreg_size + 1, qreg_size, 1])

    def _unsigned_to_signed(self, value: int, bit_len: int):
        return value - (value >> (bit_len - 1)) * (2 ** bit_len)


if __name__ == "__main__":
    unittest.main()
