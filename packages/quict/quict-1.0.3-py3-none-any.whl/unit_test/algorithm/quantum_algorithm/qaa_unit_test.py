import unittest

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X, H
from QuICT.core.gate.backend import MCTOneAux
from QuICT.algorithm.quantum_algorithm import AmplitudeAmplification
from QuICT.simulation.state_vector import StateVectorSimulator
sv_sim = StateVectorSimulator()
import numpy as np


class TestAmplitudeAmplification(unittest.TestCase):
    AMP_THRESH = 1e-12
    MIN_INIT_OVERLAP = 1e-3

    def test_check_amplified_magnitude(self):
        """ Check correctness with respect to:

            Brassard, Gilles, Peter Hoyer, Michele Mosca, and Alain Tapp. “Quantum Amplitude Amplification
            and Estimation,” 305:53-74, 2002. https://doi.org/10.1090/conm/305/05215.

        """
        target = self._rand_bin_str(3, 8)
        targ_size = len(target)
        print(f"\nTarget init to: {target}. ")

        oracle = self._grover_oracle_with_ancilla(target)

        # Init the amplification algorithm
        amp_algo = AmplitudeAmplification(
            work_bits=targ_size,
            targ_phase_flip=oracle
        )

        # theta_a in eq (5), assuming default state preparation: H^n
        theta_a = np.arcsin(np.exp2(-targ_size / 2))
        # Randomly initialize number of iteration
        it_opt = int(np.pi / (4 * theta_a))
        # Init iteration to include both under & over rotation cases.
        it = np.random.randint(1, 1.75 * it_opt)
        print(f"Iteration init to: {it}. ")

        amp_circ = amp_algo.circuit(iteration=it)
        # Run simulation
        final_sv = sv_sim.run(amp_circ)
        reduced_sv = self._trace_ancilla(final_sv, targ_size)
        reduced_sv_mag = np.linalg.norm(reduced_sv.reshape(-1, 1), axis=1)
        amplified_state = np.argmax(reduced_sv_mag)

        # Check the desired state get amplified
        self.assertEqual(int(target, base=2), amplified_state)
        amplified_amp = np.linalg.norm(reduced_sv[amplified_state])
        # By eq (8)
        desired_amp = np.sin((2 * it + 1) * theta_a)
        print(f"Desired amplitude: {desired_amp}. ")
        self.assertAlmostEqual(amplified_amp, desired_amp, delta=self.AMP_THRESH,
                               msg=f"target actual amp = {amplified_amp} with desired amp = {desired_amp}.")

        return

    def test_arbitrary_state_prep(self):
        target = self._rand_bin_str(3, 8)
        targ_size = len(target)
        print(f"\nTarget init to: {target}. ")

        # initialize a random state_prep unitary with sufficiently large
        # overlap with the target state.
        initial_overlap = 0.0
        while(initial_overlap < self.MIN_INIT_OVERLAP):
            state_prep = Circuit(targ_size)
            state_prep.random_append(targ_size * 8)
            initial_overlap = np.linalg.norm(state_prep.matrix()[int(target, base=2), 0])

        oracle = self._grover_oracle_with_ancilla(target)
        sp_cg = state_prep.to_compositegate()

        amp_algo = AmplitudeAmplification(
            work_bits=targ_size,
            targ_phase_flip=oracle,
            work_state_prep=sp_cg
        )

        theta_a = np.arcsin(initial_overlap)
        it_opt = int(np.pi / (4 * theta_a))
        print(f"it opt:{it_opt}")
        it = np.random.randint(1, 1.75 * it_opt)
        print(f"Iteration init to: {it}. ")

        amp_circ = amp_algo.circuit(iteration=it)
        # Run simulation
        final_sv = sv_sim.run(amp_circ)
        reduced_sv = self._trace_ancilla(final_sv, targ_size)
        reduced_sv_mag = np.linalg.norm(reduced_sv.reshape(-1, 1), axis=1)

        # self.assertEqual(int(target, base=2), amplified_state)
        target_amp = reduced_sv_mag[int(target, base=2)]
        desired_amp = np.sin((2 * it + 1) * theta_a)
        print(f"Desired amplitude: {desired_amp}. ")
        self.assertAlmostEqual(target_amp, desired_amp, delta=self.AMP_THRESH,
                               msg=f"target actual amp = {target_amp} with desired amp = {desired_amp}.")

        return

    def _grover_oracle_with_ancilla(self, target: str) -> CompositeGate:
        """ An oracel as composite gate that will flip the phase of |target>.
            Using 2 ancilla qubits.
        """
        s_size = len(target)

        cg = CompositeGate(name="O")
        for idx, bit in enumerate(target):
            if bit == '0':
                X | cg(idx)

        X | cg(s_size)
        H | cg(s_size)
        MCTOneAux().execute(s_size + 2) | cg
        H | cg(s_size)
        X | cg(s_size)

        for idx, bit in enumerate(target):
            if bit == '0':
                X | cg(idx)

        cg.set_ancilla([s_size, s_size + 1])

        return cg

    def _rand_bin_str(self, lo: int, hi: int):
        """ Generate a random binary string with random length in [lo, hi). """
        targ_len = np.random.randint(lo, hi)

        return "".join([str(np.random.randint(2)) for _ in range(targ_len)])

    def _trace_ancilla(
        self,
        vec: np.ndarray,
        work_num: int = -1,
        anc_num: int = -1
    ) -> np.ndarray:
        """ Only apply when the ancilla space is separable. """
        dim1, dim2 = -1, -1
        if work_num > 0:
            dim1 = 1 << work_num
        if anc_num > 0:
            dim2 = 1 << anc_num

        return np.sum(np.reshape(vec, (dim1, dim2)), axis=1)


if __name__ == "__main__":
    unittest.main()
