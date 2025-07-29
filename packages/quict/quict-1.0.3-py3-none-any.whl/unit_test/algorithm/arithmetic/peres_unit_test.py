from numpy import binary_repr, round
import unittest
from QuICT.core import Circuit
from QuICT.core.gate import X
from QuICT.simulation.state_vector import StateVectorSimulator
sv_sim = StateVectorSimulator()

from QuICT.algorithm.arithmetic.adder.utils.hl_Peres import HLPeres


class TestPeresGate(unittest.TestCase):

    def test_correctness(self):

        for i in range(8):
            c, b, a = binary_repr(i, 3)

            circ = Circuit(3)
            for idx, val in enumerate([c, b, a]):
                if val == "1":
                    X | circ(idx)
            HLPeres() | circ

            vec = round(sv_sim.run(circ), decimals=14)

            # result is deterministic
            self.assertEqual(len(vec.nonzero()[0]), 1)

            res0, res1, res2 = binary_repr(vec.nonzero()[0][0], 3)
            res0, res1, res2 = int(res0), int(res1), int(res2)
            c, b, a = int(c), int(b), int(a)
            # check the result according to definition
            self.assertEqual(res0, (a & b) ^ c, f"res0 is not correct for input state: {c}{b}{a}")
            self.assertEqual(res1, a ^ b, f"res1 is not correct for input state: {c}{b}{a}")
            self.assertEqual(res2, a, f"res0 is not correct for input state: {c}{b}{a}")
