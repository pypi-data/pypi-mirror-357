from typing import List
import unittest
import numpy as np

from QuICT.core.gate import BasicGate, CompositeGate, X, CU1, CX, CCRz
from QuICT.algorithm.quantum_algorithm import PhaseEstimation


class TestPhaseEstimation(unittest.TestCase):
    # A controlled unitary with exp2() overloaded
    class CPhase(CompositeGate):
        def __init__(self, theta: float, name: str = None):
            self._theta = theta
            super().__init__(name)

            CU1(theta) | self([0, 1])

        def exp2(self, n: int) -> CompositeGate:
            _gates = CompositeGate()
            CU1((self._theta * (1 << n)) % (2 * np.pi)) | _gates([0, 1])

            return _gates

    class CRzWithOneAncilla(CompositeGate):
        def __init__(self, theta: float, name: str = None):
            self._theta = theta
            super().__init__(name)

            X | self(2)
            CCRz(theta) | self([0, 1, 2])
            X | self(2)
            self.set_ancilla([2])

        def exp2(self, n: int) -> CompositeGate:
            _gates = CompositeGate()
            X | _gates(2)
            CCRz((self._theta * (1 << n)) % (4 * np.pi)) | _gates([0, 1, 2])
            X | _gates(2)
            _gates.set_ancilla(self.ancilla_qubits)

            return _gates

    class CRzWithTwoAncilla(CompositeGate):
        def __init__(self, theta: float, name: str = None):
            self._theta = theta
            super().__init__(name)

            X | self(3)
            CX | self([3, 2])
            CCRz(theta) | self([0, 1, 2])
            CX | self([3, 2])
            X | self(3)
            self.set_ancilla([2, 3])

        def exp2(self, n: int) -> CompositeGate:
            _gates = CompositeGate()
            X | _gates(3)
            CX | _gates([3, 2])
            CCRz((self._theta * (1 << n)) % (4 * np.pi)) | _gates([0, 1, 2])
            CX | _gates([3, 2])
            X | _gates(3)
            _gates.set_ancilla(self.ancilla_qubits)

            return _gates

    def test_cu_with_default_exp(self):
        """ Test correctness of qpe for a controled unitary with default exp2() method. """
        # initialize the phase to be estimated, the unitary and the eigenstate.
        theta = np.random.rand()
        # a controlled unitary without customized exp() method
        cu = CompositeGate(gates=[CU1(2 * np.pi * theta) & [0, 1]])
        # |1> is u1's eigen-state, u1(alpha)|1> = e^{i * alpha}|1>
        state_prep = CompositeGate(gates=[X & 0])

        bit_precision = np.random.randint(4, 8)
        qpe_algo = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        qpe_algo.run()
        # deteministically get the estimated phase
        approx_theta = np.argmax(qpe_algo.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(theta, approx_theta, delta=(1 / (1 << bit_precision)))

        ## test the swap gates in iqft does not change the results in precision bits
        qpe_algo_with_swap = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep,
            do_swap=True
        )

        qpe_algo_with_swap.run()
        approx_theta_with_swap = np.argmax(qpe_algo_with_swap.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(approx_theta, approx_theta_with_swap, delta=1e-12)

    def test_cu_with_customized_exp(self):
        """ Test correctness of qpe for a c_u with customized exp2() method. """
        theta = np.random.rand()
        # use the customized control unitary
        cu = self.CPhase(2 * np.pi * theta)
        state_prep = CompositeGate(gates=[X & 0])
        bit_precision = np.random.randint(4, 8)
        qpe_algo = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        qpe_algo.run()
        approx_theta = np.argmax(qpe_algo.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(theta, approx_theta, delta=(1 / (1 << bit_precision)))

    def test_state_prep_with_ancilla(self):
        """ Test correctness of qpe when state prep's using ancilla bits. """
        # construct U|0>|0> = |1>|0> with nontrivial use of a clean ancilla qubit
        state_prep = CompositeGate()
        X | state_prep(1)
        CX | state_prep([1, 0])
        X | state_prep(1)
        # set ancilla index for it to be recognized by the qpe algorithm
        state_prep.set_ancilla([1])

        theta = np.random.rand()
        cu = self.CPhase(2 * np.pi * theta)
        bit_precision = np.random.randint(4, 8)
        qpe_algo = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        qpe_algo.run()
        approx_theta = np.argmax(qpe_algo.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(theta, approx_theta, delta=(1 / (1 << bit_precision)))

    def test_control_unitary_with_ancilla(self):
        # state preparation use no ancilla
        state_prep = CompositeGate(gates=[X & 0])

        theta = np.random.rand()
        # control unitary use one ancilla
        cu = self.CRzWithOneAncilla(4 * np.pi * theta)
        bit_precision = np.random.randint(4, 8)
        qpe_algo = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        qpe_algo.run()
        approx_theta = np.argmax(qpe_algo.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(theta, approx_theta, delta=(1 / (1 << bit_precision)))

    def test_cu_state_prep_different_ancilla(self):
        # state preparation use one ancilla qubit
        state_prep = CompositeGate()
        X | state_prep(1)
        CX | state_prep([1, 0])
        X | state_prep(1)
        state_prep.set_ancilla([1])

        theta = np.random.rand()
        # control unitary use two ancilla qubits
        cu = self.CRzWithTwoAncilla(4 * np.pi * theta)
        bit_precision = np.random.randint(4, 8)
        qpe_algo = PhaseEstimation(
            precision_bits=bit_precision,
            work_bits=1,
            control_unitary=cu,
            work_state_prep=state_prep
        )

        qpe_algo.run()
        approx_theta = np.argmax(qpe_algo.distribution) / (1 << bit_precision)
        self.assertAlmostEqual(theta, approx_theta, delta=(1 / (1 << bit_precision)))


if __name__ == "__main__":
    unittest.main()
