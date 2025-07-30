from typing import Optional, List
from numpy.random import randint
import unittest
from QuICT.core import Circuit
from QuICT.core.gate import H, X
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError
from QuICT.algorithm.arithmetic.multiplier import MuThMultiplier


class TestMuThMultiplier(unittest.TestCase):
    def test_single_correctness(self):
        # circuit size
        n = randint(2, 5)
        m = 7 - n

        a = randint(2**n)
        b = randint(2**m)

        multi_circ = self._construct_multi_cric(reg_size1=n, reg_size2=m, init_reg1=a, init_reg2=b)
        decoded_counts = self._run_and_decode(multi_circ, reg_size1=n, reg_size2=m)

        self.assertEqual(len(decoded_counts), 1, f"decoded_counts: {decoded_counts}")
        for count in decoded_counts:
            input_a, input_b, output_axb, ancilla = count
            # check correctness
            self.assertEqual(output_axb, a * b, f"{input_a} * {input_b} != {output_axb}")
            # check ancilla reset to 0
            self.assertEqual(ancilla, 0)

    def test_universal_correctness(self):
        n = randint(2, 5)
        m = 7 - n

        multi_circ = self._construct_multi_cric(reg_size1=n, reg_size2=m)
        decoded_counts = self._run_and_decode(multi_circ, reg_size1=n, reg_size2=m)

        for count in decoded_counts:
            input_a, input_b, output_axb, ancilla = count
            # check correctness
            self.assertEqual(output_axb, input_a * input_b, f"{input_a} * {input_b} != {output_axb}")
            # check ancilla reset to 0
            self.assertEqual(ancilla, 0)

    def test_invalid_param(self):
        # first register not valid
        n = randint(-1, 2)
        m = randint(2, 5)

        with self.assertRaises(GateParametersAssignedError):
            MuThMultiplier(n, m)

        # second register not valid
        n = randint(2, 5)
        m = randint(-1, 2)
        with self.assertRaises(GateParametersAssignedError):
            MuThMultiplier(n, m)

    def _construct_multi_cric(
        self,
        reg_size1: int,
        reg_size2: int,
        init_reg1: Optional[int] = None,
        init_reg2: Optional[int] = None,
    ) -> Circuit:
        """ cosntruct multiplier circuit """
        multi_circ = Circuit(2 * (reg_size1 + reg_size2) + 1)

        # first register
        if init_reg1 is None:
            for i in range(reg_size1):
                H | multi_circ(i)
        else:
            circuit_init(multi_circ, range(reg_size1), init_reg1)

        # second register
        if init_reg2 is None:
            for i in range(reg_size1, reg_size1 + reg_size2):
                H | multi_circ(i)
        else:
            circuit_init(multi_circ, range(reg_size1, reg_size1 + reg_size2), init_reg2)

        # apply multiplier
        MuThMultiplier(reg_size1, reg_size2) | multi_circ

        return multi_circ

    def _run_and_decode(
        self,
        circuit: Circuit,
        reg_size1: int,
        reg_size2: int
    ) -> List:
        """ run multiplier circuit and decode the simulation result"""
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=circuit)
        counts = sv_sim.sample(shots=2**(reg_size1 + reg_size2 + 2))

        return decode_counts_int(counts, [reg_size1, reg_size2, reg_size1 + reg_size2, 1])


if __name__ == "__main__":
    unittest.main()
