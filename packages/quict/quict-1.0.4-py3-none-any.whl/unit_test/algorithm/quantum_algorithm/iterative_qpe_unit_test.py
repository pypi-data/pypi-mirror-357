import unittest
import numpy as np

from QuICT.core.gate import CompositeGate, CU1, X
from QuICT.algorithm.quantum_algorithm import IterativePhaseEstimation


class testIterativeQPE(unittest.TestCase):

    class CPhase(CompositeGate):
        def __init__(self, theta: float, name: str = None):
            self._theta = theta
            super().__init__(name)

            CU1(theta) | self([0, 1])

        def exp2(self, n: int) -> CompositeGate:
            _gates = CompositeGate()
            CU1((self._theta * (1 << n)) % (2 * np.pi)) | _gates([0, 1])

            return _gates

    def test_correctness(self):
        """ Test the iterative qpe method's correctness
        the to-be-estimated phase is a fixed-point binary decimal between 0 and 1 that is represented
        by a binary string with length `ben_len`. The iterative qpe method is expect to recover this
        phase with probability 1 for any number of shots.
        """
        bin_len = np.random.randint(4, 8)
        bin_str = "".join(str(np.random.randint(2, size=bin_len)[i]) for i in range(bin_len))
        theta = int(bin_str, base=2) / (1 << (bin_len))

        cu = self.CPhase(2 * np.pi * theta)
        state_prep = CompositeGate(gates=[X & 0])

        it_qpe_algo = IterativePhaseEstimation(
            precision_bits=bin_len,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        measure_smaple = it_qpe_algo.run(shots=100, decode_as_float=False)
        # the result is exact due to the inilization condition for theta
        self.assertEqual(len(measure_smaple), 1)
        # check the result is correct
        theta_approx_bin = list(measure_smaple)[0]
        self.assertEqual(theta_approx_bin, bin_str)


if __name__ == "__main__":
    unittest.main()
