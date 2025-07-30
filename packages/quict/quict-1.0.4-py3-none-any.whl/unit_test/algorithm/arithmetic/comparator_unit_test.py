import unittest
from QuICT.core import Circuit
from QuICT.core.gate import H
from QuICT.algorithm.arithmetic.basic import Comparator
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.post_circuit import decode_counts_int
import numpy as np


class TestComparator(unittest.TestCase):

    def test_less_than(self):
        n = np.random.randint(4, 7)
        comp_targ = np.random.randint(0, 1 << (n - 1))

        circ = Circuit(n + 1)
        for i in range(n - 1):
            H | circ(i + 1)

        Comparator(
            qreg_size=n,
            const=comp_targ,
            mode="lt"
        ) | circ

        sv_sim = StateVectorSimulator()
        sv_sim.run(circ)
        sample_res = sv_sim.sample(shots=1000)
        print(f"target: {comp_targ}")

        for aRes in decode_counts_int(sample_res, [1, n - 1, 1]):
            sign, input_val, res_lt = aRes
            self.assertEqual(res_lt, input_val < comp_targ)
            self.assertEqual(sign, 0)

    def test_greater_equal(self):
        n = np.random.randint(4, 7)
        comp_targ = np.random.randint(0, 1 << (n - 1))

        circ = Circuit(n + 1)
        for i in range(n - 1):
            H | circ(i + 1)

        Comparator(
            qreg_size=n,
            const=comp_targ,
            mode="ge"
        ) | circ

        sv_sim = StateVectorSimulator()
        sv_sim.run(circ)
        sample_res = sv_sim.sample(shots=1000)
        print(f"target: {comp_targ}")

        for aRes in decode_counts_int(sample_res, [1, n - 1, 1]):
            sign, input_val, res_lt = aRes
            self.assertEqual(res_lt, input_val >= comp_targ)
            self.assertEqual(sign, 0)
