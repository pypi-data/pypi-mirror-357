from typing import Optional, List
from numpy.random import randint
import unittest
from QuICT.core import Circuit
from QuICT.core.gate import H
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError

from QuICT.algorithm.arithmetic.adder import DraperAdder


class TestDraperAdder(unittest.TestCase):

    def test_single_correctness(self):
        # circuit size
        n = randint(2, 6)
        # random initialize both addends
        a = randint(2**n)
        b = randint(2**n)

        adder_circ = self._construct_adder_circuit(reg_size=n, init_reg1=a, init_reg2=b)
        decoded_counts = self._run_and_decode_adder_circuit(adder_circ, n)

        # expect exactly 1 outputs
        self.assertEqual(len(decoded_counts), 1, f"decoded_counts: {decoded_counts}")
        for count in decoded_counts:
            _, out_sum = count
            # check correctness
            self.assertEqual(out_sum, (a + b) % (1 << n))

    def test_universal_correctness(self):
        # circuit size
        n = randint(2, 6)
        # random initialize second addends
        b = randint(2**n)

        adder_circ = self._construct_adder_circuit(reg_size=n, init_reg2=b)
        decoded_counts = self._run_and_decode_adder_circuit(adder_circ, n)

        for count in decoded_counts:
            out_a, out_sum = count
            # check correctness
            self.assertEqual(out_sum, (out_a + b) % (1 << n))

    def test_invalid_input(self):
        # An invalid register size for DraperAdder
        n = randint(-1, 2)

        with self.assertRaises(GateParametersAssignedError):
            self._construct_adder_circuit(reg_size=n)

    def _construct_adder_circuit(
        self,
        reg_size: int,
        init_reg1: Optional[int] = None,
        init_reg2: Optional[int] = None
    ) -> Circuit:
        adder_circ = Circuit(2 * reg_size)

        # init first register
        if init_reg1 is None:
            for i in range(reg_size):
                H | adder_circ(i)
        else:
            circuit_init(adder_circ, range(reg_size), init_reg1)

        # init second register
        if init_reg2 is None:
            for i in range(reg_size, 2 * reg_size):
                H | adder_circ(i)
        else:
            circuit_init(adder_circ, range(reg_size, 2 * reg_size), init_reg2)

        # apply adder gate
        DraperAdder(reg_size) | adder_circ

        return adder_circ

    def _run_and_decode_adder_circuit(
        self,
        circuit: Circuit,
        reg_size: int
    ) -> List:
        """ run the circuit and decode the simulation result """
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=circuit)
        counts = sv_sim.sample(shots=2**(reg_size + 3))

        return decode_counts_int(counts, [reg_size, reg_size])


if __name__ == "__main__":
    unittest.main()
