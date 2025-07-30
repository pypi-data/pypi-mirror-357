import unittest
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import H, X
from .utils.pre_circuit import circuit_init
from QuICT.algorithm.quantum_algorithm.shor.arithmetic.bea import BEACUa, BEAMulMod
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.post_circuit import decode_counts_int

sv_sim = StateVectorSimulator()


class TestCtrlBeaModMulti(unittest.TestCase):

    def test_basic_correctness(self):
        modN = np.random.randint(3, 15)
        reg_size = int(np.log2(modN)) + 1
        x = np.random.randint(1, modN)
        # a and modN has to be co-prime
        a = np.random.randint(1, modN)
        while (np.gcd(a, modN) != 1):
            a = np.random.randint(1, modN)

        bea_mod_gate = BEACUa(
            modulus=modN,
            multiple=a,
            qreg_size=reg_size
        )
        circ = Circuit(2 * reg_size + 3)

        # put control bit into superposition
        H | circ(0)
        # init data register
        circuit_init(circ, list(range(1, 1 + reg_size)), x)
        bea_mod_gate | circ

        final_sv = np.round(sv_sim.run(circ))
        sv_arg_list = final_sv.nonzero()[0].tolist()
        # should be exactly two position with amplitude, corresponding to control on and off
        self.assertEqual(len(sv_arg_list), 2)
        for idx in sv_arg_list:
            # decode measurement result by blocks
            total_bin = np.binary_repr(idx, circ.width())
            ctrl_bit = int(total_bin[0])
            res_modMulti = int(total_bin[1: reg_size + 1], base=2)
            ancilla = int(total_bin[reg_size + 1:], base=2)

            # check result is correct
            if ctrl_bit == 0:
                self.assertEqual(res_modMulti, x, f"Fail on control is 0, with case: a={a}, x={x}, N={modN}")
            else:
                self.assertEqual(res_modMulti, (a * x) % modN,
                                 f"Fail on control is 1, with case: a={a}, x={x}, N={modN}")

            # check ancilla reset to 0
            self.assertEqual(ancilla, 0)

    def test_exponentiation(self):
        modN = np.random.randint(3, 15)
        reg_size = int(np.log2(modN)) + 1
        x = np.random.randint(1, modN)
        # a and modN has to be co-prime
        a = np.random.randint(1, modN)
        while (np.gcd(a, modN) != 1):
            a = np.random.randint(1, modN)

        exponent = np.random.randint(0, 8)

        bea_mod_gate = BEACUa(
            modulus=modN,
            multiple=a,
            qreg_size=reg_size
        )
        self.assertEqual(
            bea_mod_gate._fast_mod_exp(a, exponent, modN),
            pow(a, (1 << exponent), modN)
        )

        circ = Circuit(2 * reg_size + 3)

        bea_mod_exp = bea_mod_gate.exp2(exponent)
        self.assertEquals(bea_mod_gate.ancilla_qubits, bea_mod_exp.ancilla_qubits)

        # always calculate the mod multi
        X | circ(0)
        # init data register
        circuit_init(circ, list(range(1, 1 + reg_size)), x)
        bea_mod_exp | circ

        final_sv = np.round(sv_sim.run(circ), decimals=12)
        sv_arg_list = final_sv.nonzero()[0].tolist()
        # should be only one nonzero amplitude
        self.assertEqual(len(sv_arg_list), 1)
        # decode measurement result by blocks
        total_bin = np.binary_repr(sv_arg_list[0], circ.width())
        res_modExpo = int(total_bin[1: reg_size + 1], base=2)
        ancilla = int(total_bin[reg_size + 1:], base=2)

        self.assertEqual(res_modExpo, (pow(a, (1 << exponent), modN) * x) % modN,
                         f"Fail on case: {a}^(2^{exponent})*x mod{modN} with a={a}, x={x}, N={modN}.")
        # check ancilla reset to 0
        self.assertEqual(ancilla, 0)


class TestBEAMulMod(unittest.TestCase):
    """ Test the BEAMulMod arithmetic module."""

    def test_non_control_correctness(self):
        qreg_size = np.random.randint(3, 9)
        modulus = np.random.randint(2, 1 << qreg_size)
        x = np.random.randint(0, 1 << qreg_size)
        a = np.random.randint(0, modulus)
        b = np.random.randint(0, modulus)

        sample_result = self._get_multiplier_result(qreg_size, b, x, a, modulus, False)

        for aRes in decode_counts_int(sample_result, [qreg_size + 1, qreg_size, 1]):
            out_mod_mul, out_x, out_anc = aRes
            self.assertEqual(out_mod_mul, (b + a * out_x) % modulus,
                             f"({b} + {a} * {out_x}) % {modulus} gives {out_mod_mul}")
            self.assertEqual(out_anc, 0)

    def test_single_control_correctness(self):
        qreg_size = np.random.randint(3, 9)
        modulus = np.random.randint(2, 1 << qreg_size)
        x = np.random.randint(0, 1 << qreg_size)
        a = np.random.randint(0, modulus)
        b = np.random.randint(0, modulus)

        sample_result = self._get_multiplier_result(qreg_size, b, x, a, modulus, True)

        for aRes in decode_counts_int(sample_result, [1, qreg_size + 1, qreg_size, 1]):
            out_ctrl, out_mod_mul, out_x, out_anc = aRes
            self.assertEqual(out_mod_mul, (b + out_ctrl * a * out_x) % modulus,
                             f"({b} + {out_ctrl} * {a} * {out_x}) % {modulus} gives {out_mod_mul}")
            self.assertEqual(out_anc, 0)

    def test_size_and_depth(self):

        qreg_size = np.random.randint(3, 20)
        modulus = np.random.randint(2, 1 << qreg_size)
        a = np.random.randint(0, modulus)

        cg = BEAMulMod(qreg_size, a, modulus)

        self.assertEqual(cg.depth(), 18 * qreg_size ** 2 + 27 * qreg_size + 3)
        self.assertEqual(cg.size(), 2 * qreg_size ** 3 + 24 * qreg_size ** 2 + 28 * qreg_size + 2)

    def _get_multiplier_result(
        self,
        qreg_size: int,
        b: int,
        x: int,
        a: int,
        modulus: int,
        control: bool
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the multiplier encoded in qubit.
            b (int): The initial value of the target quantum register.
            x (int): The initial value of the multiplier,
            a (int): The value for the multiplicand which is given classically.
            modulus (int): The integer given as modulus.
            control (bool): Whether having qubit to control the modular multiplier.
        """
        num_control = 0
        if control:
            num_control = 1

        # init circuit
        cir = Circuit(2 * qreg_size + 2 + num_control)
        circuit_init(cir, list(range(num_control, qreg_size + 1 + num_control)), b)
        circuit_init(cir, list(range(qreg_size + 1 + num_control, 2 * qreg_size + 1 + num_control)), x)
        if control:
            H | cir(0)

        # apply multiplier
        BEAMulMod(qreg_size, a, modulus, control) | cir

        # simulation
        sv_sim = StateVectorSimulator()
        sv_sim.run(cir)
        sample_res = sv_sim.sample(1000)

        return sample_res


if __name__ == "__main__":
    unittest.main()
