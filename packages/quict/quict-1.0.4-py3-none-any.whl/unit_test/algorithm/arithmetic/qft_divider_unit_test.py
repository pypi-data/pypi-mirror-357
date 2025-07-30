import unittest
from typing import List

from numpy import binary_repr
from numpy.random import randint, choice

from QuICT.algorithm import QFT, IQFT
from QuICT.algorithm.arithmetic.divider.qft_divider import QFTDivider, SUBModule, CtrlADDModule, CtrlAddSubModule
from QuICT.core import Circuit
from QuICT.core.gate import X
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.tools.exception.core import GateParametersAssignedError
from unit_test.algorithm.arithmetic.utils.post_circuit import decode_counts_int
from unit_test.algorithm.arithmetic.utils.pre_circuit import circuit_init


class TestSUBModule(unittest.TestCase):
    """
    Test the subtraction module used in the QFTDivider.
    """

    def test_sub_module(self):
        """Test the module functionality correctness."""
        # init circuit size
        qreg_size = randint(2, 8)

        # init minuend and subtrahend
        a = randint(2 ** (qreg_size - 1))
        b = randint(2 ** (qreg_size - 1))

        # construct the circuit
        cir = self._construct_the_circuit(qreg_size, a, b)

        # simulation
        sim = StateVectorSimulator()
        sim.run(cir)
        counts = sim.sample(10)

        # decode
        result = decode_counts_int(counts, [qreg_size, qreg_size])
        for i in result:
            out_difference, out_b = i
            out_difference = out_difference - (out_difference >> (qreg_size - 1)) * 2 ** qreg_size
            self.assertEqual(out_difference, a - b)
            self.assertEqual(out_b, b)

    def _construct_the_circuit(
            self,
            qreg_size: int,
            a: int,
            b: int
    ) -> Circuit:
        """
            Construct the subtraction module.

            Args:
                qreg_size (int): The register size for minuend and subtrahend.
                a (int): The minuend encoded into quantum register.
                b (int): The subtrahend encoded into quantum register

            Returns:
                The circuit of this module after initialization.
        """
        mod = Circuit(2 * qreg_size)
        a_list = list(range(qreg_size))
        b_list = list(range(qreg_size, 2 * qreg_size))

        # init the minuend and subtrahend
        circuit_init(mod, a_list, a)
        circuit_init(mod, b_list, b)

        # apply the module
        QFT(qreg_size) | mod(a_list)
        SUBModule(qreg_size) | mod
        IQFT(qreg_size) | mod(a_list)

        return mod


class TestCtrlADDModule(unittest.TestCase):
    """
    Test the control addition module used in the QFTDivider.
    """

    def test_ctrl_add_module(self):
        """Test the module functionality correctness."""
        # init circuit size
        qreg_size = randint(2, 8)

        # init minuend and subtrahend
        a = randint(2 ** (qreg_size - 1))
        b = randint(2 ** (qreg_size - 1))
        ctrl = choice([0, 1])

        # construct the circuit
        cir = self._construct_the_circuit(qreg_size, a, b, ctrl)

        # simulation
        sim = StateVectorSimulator()
        sim.run(cir)
        counts = sim.sample(10)

        # decode
        result = decode_counts_int(counts, [1, qreg_size, qreg_size])
        for i in result:
            _, out_sum, out_b = i
            self.assertEqual(out_sum, a + b * ctrl)
            self.assertEqual(out_b, b)

    def _construct_the_circuit(
            self,
            qreg_size: int,
            a: int,
            b: int,
            ctrl: int
    ) -> Circuit:
        """
            Construct the control addition modul.

            Args:
                qreg_size (int): The register size for two addends.
                a (int): The first addend encoded into quantum register.
                b (int): The second addend encoded into quantum register.
                ctrl (int): The control qubit value.

            Returns:
                The circuit of the module after initialization.
        """
        add = Circuit(2 * qreg_size + 1)
        a_list = list(range(1, qreg_size + 1))
        b_list = list(range(qreg_size + 1, 2 * qreg_size + 1))

        # init addends
        if ctrl:
            X | add([0])
        circuit_init(add, a_list, a)
        circuit_init(add, b_list, b)

        # apply the module
        QFT(qreg_size) | add(a_list)
        CtrlADDModule(qreg_size) | add
        IQFT(qreg_size) | add(a_list)

        return add


class TestCtrlAddSubModule(unittest.TestCase):
    """Test the control adder-subtractor module used in QFTDivider."""

    def test_ctrl_add_sub_module(self):
        """Test the module functionality correctness."""
        # init circuit size
        qreg_size = randint(2, 11)

        # init operands
        a = randint(2 ** qreg_size)
        b = randint(2 ** (qreg_size - 1))
        ctrl = choice([0, 1])

        # construct the circuit
        cir = self._construct_the_circuit(qreg_size, a, b, ctrl)

        # simulation
        sim = StateVectorSimulator()
        sim.run(cir)
        counts = sim.sample(100)

        # decode
        sim_result = decode_counts_int(counts, [1, qreg_size, qreg_size])
        real_result = binary_repr(a + ((-1) ** ctrl) * b, width=qreg_size + 1)
        real_result = int(real_result[1::], base=2)
        for i in sim_result:
            out_ctrl, out_result, out_b = i
            self.assertEqual(out_ctrl, ctrl)
            self.assertEqual(out_result, real_result)
            self.assertEqual(out_b, b)

    def _construct_the_circuit(
            self,
            qreg_size: int,
            a: int,
            b: int,
            ctrl: int
    ) -> Circuit:
        """
            Construct the control adder-subtractor module.

            Args:
                qreg_size (int): The register size for the two addends.
                a (int): The first addend encoded into quantum register.
                b (int): The second addend encoded into quantum register.
                ctrl (int): The control qubit.

            Returns:
                The circuit of the module after initialization.
        """
        mod = Circuit(2 * qreg_size + 1)
        a_list = list(range(1, qreg_size + 1))
        b_list = list(range(qreg_size + 1, 2 * qreg_size + 1))

        # init addends
        if ctrl:
            X | mod([0])
        circuit_init(mod, a_list, a)
        circuit_init(mod, b_list, b)

        # apply the module
        QFT(qreg_size) | mod(a_list)
        CtrlAddSubModule(qreg_size) | mod
        IQFT(qreg_size) | mod(a_list)

        return mod


class TestQFTDivider(unittest.TestCase):
    """Test the divider using non-restoring algorithm based on QFT."""

    def test_unsigned_integer(self):
        """Test using the divider to do unsigned division with non-zero divisor."""
        # init circuit size
        qreg_size = randint(3, 10)

        # init dividend and divisor
        a = randint(2 ** qreg_size)
        b = randint(1, 2 ** (qreg_size - 1))

        # init the cirucit
        divider = self._construct_the_circuit(qreg_size, a, b)

        # simulate and decode
        result = self._run_and_decode(divider, qreg_size)
        for i in result:
            out_quotient, out_remainder, out_b = i
            self.assertEqual(out_quotient, a // b)
            self.assertEqual(out_remainder, a % b)
            self.assertEqual(out_b, b)

    def test_zero_case(self):
        """Test using the divider with divisor equal to zero."""
        # init circuit size
        qreg_size = randint(3, 8)

        # init the dividend and divisor
        a = randint(2 ** qreg_size)
        b = 0

        # init the circuit
        divider = self._construct_the_circuit(qreg_size, a, b)

        # simulation and decode
        result = self._run_and_decode(divider, qreg_size)
        for i in result:
            out_quotient, out_remainder, out_b = i
            self.assertEqual(out_quotient, 2 ** qreg_size - 1 - (a >> qreg_size - 1))
            self.assertEqual(out_remainder, a - ((a >> qreg_size - 1) << qreg_size - 1))
            self.assertEqual(out_b, b)

    def test_size_and_depth(self):
        """Test the size and depth of the divider."""
        # init circuit size
        qreg_size = randint(3, 18)

        # construct the divider
        divider = QFTDivider(qreg_size)

        # test the size
        self.assertEqual(
            divider.size(),
            3 * (qreg_size ** 3) + 5 * (qreg_size ** 2) - 4 * qreg_size
        )
        self.assertEqual(
            divider.depth(),
            2 * (qreg_size ** 3) + 5 * (qreg_size ** 2) - 2 * qreg_size - 2
        )

    def test_QFTDivider_invalid_size(self):
        """ Test using QFTDivider with invalid input size. """
        # circuit size
        qreg_size = randint(1, 3)

        with self.assertRaises(GateParametersAssignedError):
            self._construct_the_circuit(qreg_size, 0, 1)

    def _construct_the_circuit(
            self,
            qreg_size: int,
            dividend: int,
            divisor: int
    ) -> Circuit:
        """
            Construct the divider circuit.

            Args:
                qreg_size (int) The register size for the dividend and divisor.
                dividend (int): The dividend encoded into quantum register.
                divisor (int): The divisor encoded into quantum register.

            Returns:
                The circuit of the divider after initialization.
        """
        divider = Circuit(3 * qreg_size - 1)
        dd_list = list(range(qreg_size - 1, 2 * qreg_size - 1))
        ds_list = list(range(2 * qreg_size - 1, 3 * qreg_size - 1))

        # init the circuit
        circuit_init(divider, dd_list, dividend)
        circuit_init(divider, ds_list, divisor)

        # apply the divider
        QFTDivider(qreg_size) | divider

        return divider

    def _run_and_decode(
            self,
            cir: Circuit,
            qreg_size: int
    ) -> List:
        """
            Run the circuit and decode the simulation result.

            Args:
                cir (Circuit): The circuit prepared to simulate.
                qreg_size (int): The register size for dividend and divisor.

            Returns:
                The result of simulation which is partitioned by the meaning.
        """
        sim = StateVectorSimulator()
        sim.run(cir)
        counts = sim.sample(100)

        return decode_counts_int(counts, [qreg_size, qreg_size - 1, qreg_size])


if __name__ == "__main__":
    unittest.main()
