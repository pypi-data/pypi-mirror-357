import unittest
import numpy as np

from QuICT.core import Circuit
from QuICT.core.gate import H, X
from .utils.pre_circuit import circuit_init
from QuICT.algorithm.quantum_algorithm.shor.arithmetic.hrs import CHRSMulMod
from QuICT.simulation.state_vector import StateVectorSimulator
sv_sim = StateVectorSimulator()


class TestCtrlHRSModMulti(unittest.TestCase):

    def test_basic_correctness(self):
        modN = np.random.randint(5, 15)
        reg_size = int(np.log2(modN)) + 1
        x = np.random.randint(1, modN)
        # a and modN has to be co-prime
        a = np.random.randint(1, modN)
        while(np.gcd(a, modN) != 1):
            a = np.random.randint(1, modN)

        hrs_mod_gate = CHRSMulMod(
            modulus=modN,
            multiple=a,
            qreg_size=reg_size
        )
        circ = Circuit(2 * reg_size + 2)

        # put control bit into superposition
        H | circ(0)
        # init data register
        circuit_init(circ, list(range(1, 1 + reg_size)), x)
        hrs_mod_gate | circ

        final_sv = np.round(sv_sim.run(circ))
        sv_arg_list = final_sv.nonzero()[0].tolist()
        # should be exactly two position with amplitude, corresponding to control on and off
        self.assertEqual(len(sv_arg_list), 2)
        for idx in sv_arg_list:
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
        modN = np.random.randint(5, 15)
        reg_size = int(np.log2(modN)) + 1
        x = np.random.randint(1, modN)
        # a and modN has to be co-prime
        a = np.random.randint(1, modN)
        while(np.gcd(a, modN) != 1):
            a = np.random.randint(1, modN)

        exponent = np.random.randint(0, 8)

        hrs_mod_gate = CHRSMulMod(
            modulus=modN,
            multiple=a,
            qreg_size=reg_size
        )
        self.assertEqual(
            hrs_mod_gate._fast_mod_exp(a, exponent, modN),
            pow(a, (1 << exponent), modN)
        )

        circ = Circuit(2 * reg_size + 2)
        hrs_mod_exp = hrs_mod_gate.exp2(exponent)
        self.assertEquals(hrs_mod_gate.ancilla_qubits, hrs_mod_exp.ancilla_qubits)

        # always calculate the mod multi
        X | circ(0)
        # init data register
        circuit_init(circ, list(range(1, 1 + reg_size)), x)
        hrs_mod_exp | circ

        final_sv = np.round(sv_sim.run(circ))
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


if __name__ == "__main__":
    unittest.main()
