import unittest

from QuICT.core.gate import CompositeGate, Ry, ID
from QuICT.algorithm.quantum_algorithm.amplitude_estimation import AmplitudeEstimation
from QuICT.algorithm.oracle import StringMarkOracle

import numpy as np


class TestAmplitudeEstimation(unittest.TestCase):

    def test_exact_case_normal_qae(self):

        sp_to_be_estimated = CompositeGate()

        bin_len = np.random.randint(3, 6)
        amp_rotation_coef = np.random.randint(1, 1 << bin_len)
        theta = 2 * np.pi * amp_rotation_coef / (1 << bin_len)

        Ry(theta) | sp_to_be_estimated(0)
        ID | sp_to_be_estimated(1)

        targ_phase_flip = StringMarkOracle("10")

        test_case_info = f"test with {bin_len =}, {amp_rotation_coef =}, estimating the amplitude of |10> "\
            + f"in {np.cos(theta)}|00> + {np.sin(theta)}|10>."

        amp_estimator = AmplitudeEstimation(
            precision_bits=bin_len,
            work_bits=2,
            targ_phase_flip=targ_phase_flip,
            work_state_prep=sp_to_be_estimated,
            qpe_method="normal"
        )

        res_raw = amp_estimator.run(shots=100)

        self.assertIn(len(res_raw), [1, 2], msg="Fail on " + test_case_info)

        result_ground_truth = [amp_rotation_coef, (1 << bin_len) - amp_rotation_coef]
        for sample_res_bin in list(res_raw.keys()):
            # test exact
            self.assertIn(int(sample_res_bin, base=2), result_ground_truth, msg="Fail on " + test_case_info)
            # test decoding
            decoded = AmplitudeEstimation.decode_to_amplitude_norm(sample_res_bin)
            amp_actual = sp_to_be_estimated.matrix()[:, 0][2]
            self.assertTrue(np.allclose(decoded, amp_actual), msg=f"requires {amp_actual}, got {decoded}. ")

    def test_exact_case_iterative_qae(self):

        sp_to_be_estimated = CompositeGate()

        bin_len = np.random.randint(3, 6)
        amp_rotation_coef = np.random.randint(1, 1 << bin_len)
        theta = 2 * np.pi * amp_rotation_coef / (1 << bin_len)

        Ry(theta) | sp_to_be_estimated(0)
        ID | sp_to_be_estimated(1)

        targ_phase_flip = StringMarkOracle("10")

        test_case_info = f"Test with {bin_len =}, {amp_rotation_coef =}, estimating the amplitude of |10> "\
            + f"in {np.cos(theta)}|00> + {np.sin(theta)}|10>."

        amp_estimator = AmplitudeEstimation(
            precision_bits=bin_len,
            work_bits=2,
            targ_phase_flip=targ_phase_flip,
            work_state_prep=sp_to_be_estimated,
            qpe_method="iterative"
        )

        res_raw = amp_estimator.run(shots=100)

        self.assertIn(len(res_raw), [1, 2], msg="Fail on " + test_case_info)

        result_ground_truth = [amp_rotation_coef, (1 << bin_len) - amp_rotation_coef]
        for sample_res_bin in list(res_raw.keys()):
            self.assertIn(int(sample_res_bin, base=2), result_ground_truth, msg="Fail on " + test_case_info)
