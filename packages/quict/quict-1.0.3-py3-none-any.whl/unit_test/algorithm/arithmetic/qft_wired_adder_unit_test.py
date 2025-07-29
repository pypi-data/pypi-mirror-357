from typing import Tuple
import unittest
import numpy as np

from QuICT.tools import Logger
from QuICT.tools.exception.core import CircuitAppendError
from QuICT.core import Circuit
from QuICT.core.gate.gate import X, H
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.algorithm.arithmetic import QFTWiredAdder
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int

logger = Logger("test_rc_adder")


class TestRCAdder(unittest.TestCase):

    def test_rc_adder_unsigned(self):
        """
            Test using the adder gate to do unsigned addition on a qreg
        """

        # regular case
        self.assertEqual(self._get_rc_adder_result(5, 3, 5), 3 + 5)
        # test for overflow
        self.assertEqual(
            self._get_rc_adder_result(5, 22, 17),
            (17 + 22) % (2**5)
        )
        # random inputs
        reg_size = 5
        a, b = np.random.randint(2**reg_size, size=2)
        self.assertEqual(
            self._get_rc_adder_result(reg_size, a, b),
            (a + b) % (2**reg_size)
        )

    def test_rc_adder_signed(self):
        """
            Test using the adder gate to do signed addition on a qreg
        """

        # regular cases
        self.assertEqual(
            self._get_rc_adder_result(5, 6, 8, signed=True),
            6 + 8
        )
        self.assertEqual(
            self._get_rc_adder_result(6, 3, -5, signed=True),
            3 - 5
        )
        self.assertEqual(
            self._get_rc_adder_result(7, -7, 2, signed=True),
            -7 + 2
        )
        self.assertEqual(
            self._get_rc_adder_result(8, -1, -3, signed=True),
            -1 - 3
        )
        # overflow
        self.assertEqual(
            self._get_rc_adder_result(5, 7, 9, signed=True),
            (7 + 9 + 2**(5 - 1)) % (2**5) - 2**(5 - 1)
        )
        # underflow
        self.assertEqual(
            self._get_rc_adder_result(5, -10, -11, signed=True),
            (-10 - 11 + 2**(5 - 1)) % (2**5) - 2**(5 - 1)
        )
        # random inputs
        reg_size = 5
        a, b = np.random.randint(low=-(2**(reg_size - 1)), high=(2**(reg_size - 1)), size=2)
        self.assertEqual(
            self._get_rc_adder_result(reg_size, a, b, signed=True),
            (a + b + 2**(reg_size - 1)) % (2**reg_size) - 2**(reg_size - 1)
        )

    def test_rc_adder_controlled_unsigned(self):
        """
            Test using the controlled adder gate to do unsigned addition on
            a qreg
        """

        # regular case
        self.assertEqual(
            self._get_rc_adder_result_controlled(5, 2, 7),
            (2, 9)
        )
        # overflow
        self.assertEqual(
            self._get_rc_adder_result_controlled(5, 23, 14),
            (23, (23 + 14) % (2**5))
        )
        # random inputs
        reg_size = 5
        a, b = np.random.randint(2**(reg_size), size=2)
        self.assertEqual(
            self._get_rc_adder_result_controlled(reg_size, a, b),
            (a, (a + b) % (2**reg_size))
        )

    def test_rc_adder_controlled_signed(self):
        """
            Test using the controlled adder gate to do signed addition on
            a qreg
        """

        # regular cases
        self.assertEqual(
            self._get_rc_adder_result_controlled(6, 2, 7, signed=True),
            (2, 9)
        )
        self.assertEqual(
            self._get_rc_adder_result_controlled(5, 3, -7, signed=True),
            (3, -4)
        )
        self.assertEqual(
            self._get_rc_adder_result_controlled(7, -7, 3, signed=True),
            (-7, -4)
        )
        self.assertEqual(
            self._get_rc_adder_result_controlled(6, -10, -9, signed=True),
            (-10, -19)
        )
        # overflow
        self.assertEqual(
            self._get_rc_adder_result_controlled(5, 8, 11, signed=True),
            (8, (8 + 11 + 2**(5 - 1)) % (2**5) - 2**(5 - 1))
        )
        # underflow
        self.assertEqual(
            self._get_rc_adder_result_controlled(6, 7, -80, signed=True),
            (7, (7 - 80 + 2**(6 - 1)) % (2**6) - 2**(6 - 1))
        )
        # random inputs
        reg_size = 5
        a, b = np.random.randint(low=-(2**(reg_size - 1)), high=(2**(reg_size - 1)), size=2)
        self.assertEqual(
            self._get_rc_adder_result_controlled(reg_size, a, b, signed=True),
            (a, (a + b + 2**(reg_size - 1)) % (2**reg_size) - 2**(reg_size - 1))
        )

    def test_doubly_controlled(self):

        reg_size = np.random.randint(3, 7)
        init_val = np.random.randint(0, 1 << reg_size)
        addend = np.random.randint(0, 1 << reg_size)

        circ = Circuit(reg_size + 2)
        H | circ(0)
        H | circ(1)

        circuit_init(circ, list(range(2, 2 + reg_size)), init_val)

        QFTWiredAdder(
            qreg_size=reg_size,
            addend=addend,
            num_control=2
        ) | circ

        sv_sim = StateVectorSimulator()

        sv_sim.run(circ)
        sample_res = sv_sim.sample(1000)

        for aRes in decode_counts_int(sample_res, partition=[1, 1, reg_size]):
            c0, c1, res_add = aRes
            self.assertEqual(res_add, (init_val + c0 * c1 * addend) % (1 << reg_size),
                                f"{init_val} + {addend} on control: {c0}{c1} gets {res_add}")

    def _get_rc_adder_result(
        self,
        qreg_size: int,
        q_x: int,
        c_y: int,
        signed: bool = False
    ) -> int:
        """
            Args:
                qreg_size (int): size of the quantum register.
                q_x (int): integer encode into quantum register.
                c_y (int): integer classically hardwired into the quantum
                circuit.
                signed (int): if True, will add one more bit for sign.

            Returns:
                "q_x + c_y" by running the adder circuit and decoding the
                result.
        """

        try:
            q_x_bin = np.binary_repr(q_x, qreg_size)
        except CircuitAppendError as e:
            logger.error(e("Not enough register size to hold q_x"))
            raise

        # Construct circuit #

        # init circuit with q_x
        adder_circ = Circuit(qreg_size)
        for i, bit in enumerate(q_x_bin):
            if '1' == bit:
                X | adder_circ([i])

        # apply rcAdder
        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=c_y
        ) | adder_circ

        # Decode #
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=adder_circ)
        # only the correct answer will have non-zero amplitude
        result = sv_sim.sample(shots=1)
        for idx_key in result:
            if result[idx_key] != 0:
                if signed:
                    return self._unsigned_to_signed(idx_key, qreg_size)
                else:
                    return idx_key

    def _get_rc_adder_result_controlled(
        self,
        qreg_size: int,
        q_x: int,
        c_y: int,
        signed: bool = False
    ) -> Tuple[int, int]:
        """
            Args:
                qreg_size (int):
                    size of the quantum register, not including the control
                    bit.
                q_x (int):
                    integer encode into quantum register.
                c_y (int):
                    integer classically hardwired into the quantum circuit.
                signed (int):
                    if True, will add one more bit for sign.
            Returns:
                return an integer tuple of size 2, index 0 contains the adder
                result when the control bit is '0', index 1 contains the adder
                result with control bit in '1'.
        """
        try:
            q_x_bin = np.binary_repr(q_x, qreg_size)
        except CircuitAppendError as e:
            logger.error(e("Not enough register size to hold q_x"))
            raise

        # Construct circuit #

        # init circuit with q_x, one more qubit for the control bit
        ctl_adder_circ = Circuit(qreg_size + 1)
        for i, bit in enumerate(q_x_bin):
            if '1' == bit:
                X | ctl_adder_circ([i + 1])

        # put the control bit into superposition
        H | ctl_adder_circ([0])

        # apply ctl-rcAdder
        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=c_y,
            num_control=1
        ) | ctl_adder_circ

        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=ctl_adder_circ)

        # Decode #
        addition_res = {}
        # the probability of only one state with non-zero amplitude is 2^(-20)
        result = sv_sim.sample(shots=20)
        for idx_key in result:
            if result[idx_key] != 0:
                ctl_bit = idx_key >> qreg_size
                # remove ctl bit to get the actual addition result
                output = ~(ctl_bit << qreg_size) & idx_key
                if signed:
                    output = self._unsigned_to_signed(output, qreg_size)

                addition_res[ctl_bit] = output

            if 2 == len(addition_res):
                break

        return addition_res[0], addition_res[1]

    def _unsigned_to_signed(self, value: int, bit_len: int):
        return value - (value >> (bit_len - 1)) * (2 ** bit_len)


if __name__ == '__main__':
    unittest.main()
