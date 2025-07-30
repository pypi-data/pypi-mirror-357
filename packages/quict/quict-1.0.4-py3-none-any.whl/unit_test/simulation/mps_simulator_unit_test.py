import os
import unittest
import numpy as np

from QuICT.core import Circuit
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.simulation.matrix_product_state import MatrixProductStateSimulator
from .circuit_for_correct import create_circuit_for_correct


@unittest.skipUnless(os.environ.get("test_with_gpu", False), "require GPU")
class TestGPUMPSSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('GPU MPS simulator unit test begin!')
        cls.qubit_interval = list(range(5, 10))
        cls.size_coeff = 10
        cls.times = 10

        cls.mps_single = MatrixProductStateSimulator(device="GPU", precision="single")
        cls.mps_double = MatrixProductStateSimulator(device="GPU", precision="double")

        cls.sv_single = StateVectorSimulator(device="GPU", precision="single")
        cls.sv_double = StateVectorSimulator(device="GPU", precision="double")

    @classmethod
    def tearDownClass(cls):
        print('GPU MPS simulator unit test finished!')

    def test_correction(self):
        qubit = np.random.choice(self.qubit_interval)
        validate_circuit = create_circuit_for_correct(int(qubit))

        sv_result_double = self.sv_double.run(validate_circuit)
        mps_result_double = self.mps_double.run(validate_circuit).to_statevector()

        assert np.allclose(sv_result_double.get(), mps_result_double.get(), atol=1e-5)

    def test_simulation(self):
        for _ in range(10):
            qubit = np.random.choice(self.qubit_interval)
            cir = Circuit(int(qubit))
            cir.random_append(self.size_coeff * qubit)

            sv_result_single = self.sv_single.run(cir)
            sv_result_double = self.sv_double.run(cir)

            mps_result_single = self.mps_single.run(cir).to_statevector()
            mps_result_double = self.mps_double.run(cir).to_statevector()

            assert np.allclose(sv_result_single.get(), mps_result_single.get(), atol=1e-5)
            assert np.allclose(sv_result_double.get(), mps_result_double.get(), atol=1e-5)

    def test_sample(self):
        qubit = np.random.choice(self.qubit_interval)
        cir = Circuit(int(qubit))
        cir.random_append(self.size_coeff * qubit)

        _ = self.mps_single.run(cir).to_statevector()
        _ = self.mps_double.run(cir).to_statevector()

        sample_single = self.mps_single.sample(1000)
        sample_double = self.mps_double.sample(1000)
        assert sum(sample_double) == 1000 and sum(sample_single) == 1000


class TestCPUMPSSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('CPU MPS simulator unit test begin!')
        cls.qubit_interval = list(range(5, 10))
        cls.size_coeff = 10
        cls.times = 10

        cls.mps_single = MatrixProductStateSimulator(device="CPU", precision="single")
        cls.mps_double = MatrixProductStateSimulator(device="CPU", precision="double")

        cls.sv_single = StateVectorSimulator(device="CPU", precision="single")
        cls.sv_double = StateVectorSimulator(device="CPU", precision="double")

    @classmethod
    def tearDownClass(cls):
        print('CPU MPS simulator unit test finished!')

    def test_correction(self):
        qubit = np.random.choice(self.qubit_interval)
        validate_circuit = create_circuit_for_correct(int(qubit))

        sv_result_single = self.sv_single.run(validate_circuit)
        sv_result_double = self.sv_double.run(validate_circuit)

        mps_result_single = self.mps_single.run(validate_circuit).to_statevector()
        mps_result_double = self.mps_double.run(validate_circuit).to_statevector()

        assert np.allclose(sv_result_single, mps_result_single, atol=1e-5)
        assert np.allclose(sv_result_double, mps_result_double, atol=1e-5)

    def test_simulation(self):
        for _ in range(10):
            qubit = np.random.choice(self.qubit_interval)
            cir = Circuit(int(qubit))
            cir.random_append(self.size_coeff * qubit)

            sv_result_single = self.sv_single.run(cir)
            sv_result_double = self.sv_double.run(cir)

            mps_result_single = self.mps_single.run(cir).to_statevector()
            mps_result_double = self.mps_double.run(cir).to_statevector()

            assert np.allclose(sv_result_single, mps_result_single, atol=1e-5)
            assert np.allclose(sv_result_double, mps_result_double, atol=1e-5)

    def test_sample(self):
        qubit = np.random.choice(self.qubit_interval)
        cir = Circuit(int(qubit))
        cir.random_append(self.size_coeff * qubit)

        _ = self.mps_single.run(cir).to_statevector()
        _ = self.mps_double.run(cir).to_statevector()

        sample_single = self.mps_single.sample(1000)
        sample_double = self.mps_double.sample(1000)
        assert sum(sample_double) == 1000 and sum(sample_single) == 1000
