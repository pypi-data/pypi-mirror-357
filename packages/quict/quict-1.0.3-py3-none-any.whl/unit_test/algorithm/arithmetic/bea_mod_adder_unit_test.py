import unittest
from typing import List

from numpy.random import randint

from QuICT.algorithm.arithmetic.adder import FourierModAdder
from QuICT.core import Circuit
from QuICT.core.gate import H
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.post_circuit import decode_counts_int
from .utils.pre_circuit import circuit_init


class TestModAdder(unittest.TestCase):

    def test_non_control_correctness(self):
        qreg_size = randint(3, 7)
        modules = randint(2, 1 << qreg_size - 1)
        init_val = randint(0, modules)
        addend = randint(0, modules)

        sample_res = self._get_adder_result(qreg_size, addend, modules, init_val, 0)

        for aRes in decode_counts_int(sample_res, [qreg_size, 1]):
            out_sum, out_anc = aRes
            self.assertEqual(out_sum, (init_val + addend) % modules,
                             f"({init_val} + {addend}) % {modules} gives {out_sum}")
            self.assertEqual(out_anc, 0)

    def test_single_control_correctness(self):
        n = randint(3, 7)
        modulus = randint(2, 1 << n - 1)
        init_val = randint(0, modulus)
        addend = randint(0, modulus)

        sample_res = self._get_adder_result(n, addend, modulus, init_val, 1)

        for aRes in decode_counts_int(sample_res, [1, n, 1]):
            c, mod_add_res, anci = aRes
            self.assertEqual(mod_add_res, (init_val + c * addend) % modulus,
                             f"({init_val} + {c} * {addend}) % {modulus} gives {mod_add_res}.")
            self.assertEqual(anci, 0)

    def test_doubles_control_correctness(self):
        qreg_size = randint(3, 7)
        modules = randint(2, 1 << qreg_size - 1)
        init_val = randint(0, modules)
        addend = randint(0, modules)

        sample_res = self._get_adder_result(qreg_size, addend, modules, init_val, 2)

        for aRes in decode_counts_int(sample_res, [1, 1, qreg_size, 1]):
            out_c0, out_c1, out_sum, out_anc = aRes
            self.assertEqual(out_sum, (init_val + out_c0 * out_c1 * addend) % modules,
                             f"({init_val} + {out_c0} * {out_c1} *{addend}) % {modules} gives {out_sum}")
            self.assertEqual(out_anc, 0)

    def _get_adder_result(
        self,
        qreg_size: int,
        addend: int,
        modulus: int,
        init_val: int,
        num_control: int
    ) -> List:
        """
        Args:
            qreg_size (int): The size of the quantum register waiting to be added.
            addend (int): The integer that will be added to the qreg.
            modulus (int): The integer as modulus.
            init_val (int): The initial value of the quantum register.
            num_control (int): Indicates the number of qubits for controlling the wired adder, up to 2 qubits.
        """
        circ = Circuit(qreg_size + num_control + 1)

        if num_control >= 1:
            H | circ(0)
        if num_control == 2:
            H | circ(1)
        circuit_init(circ, list(range(num_control, num_control + qreg_size)), init_val=init_val)
        FourierModAdder(
            qreg_size=qreg_size,
            addend=addend,
            modulus=modulus,
            num_control=num_control
        ) | circ

        sv_sim = StateVectorSimulator()
        sv_sim.run(circ)
        sample_res = sv_sim.sample(1000)

        return sample_res
