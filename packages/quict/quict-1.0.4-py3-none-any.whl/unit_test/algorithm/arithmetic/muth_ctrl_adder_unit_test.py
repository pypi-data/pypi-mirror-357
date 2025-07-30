from typing import Optional, List
from numpy.random import randint
import unittest
from QuICT.core import Circuit
from QuICT.core.gate import H, X
from QuICT.simulation.state_vector import StateVectorSimulator
from .utils.pre_circuit import circuit_init
from .utils.post_circuit import decode_counts_int
from QuICT.tools.exception.core.gate_exception import GateParametersAssignedError
from QuICT.algorithm.arithmetic.adder import MuThCtrlAdder


class TestMuThCtrlAdder(unittest.TestCase):
    def test_single_correctness(self):
        # circuit size
        n = randint(2, 6)
        # random initialize both addends
        a = randint(2**n)
        b = randint(2**n)

        ctrl_adder_circ = self._construct_cAdder_circuit(reg_size=n, init_reg1=a, init_reg2=b)
        decoded_counts = self._run_and_decode_adder_circuit(ctrl_adder_circ, n)

        # expect exactly 2 outputs
        self.assertEqual(len(decoded_counts), 2, f"decoded_counts: {decoded_counts}")
        for count in decoded_counts:
            ctrl_bit, _, output_sum, ancilla = count
            # check correctness
            self.assertEqual(output_sum, ctrl_bit * a + b)
            # check ancilla reset to 0
            self.assertEqual(ancilla, 0)

    def test_universal_correctness(self):
        # circuit size
        n = randint(2, 6)
        # random initialize second addends
        b = randint(2**n)

        ctrl_adder_circ = self._construct_cAdder_circuit(reg_size=n, init_reg2=b)
        decoded_counts = self._run_and_decode_adder_circuit(ctrl_adder_circ, n)

        for count in decoded_counts:
            ctrl_bit, input_a, output_sum, ancilla = count
            # check correctness
            self.assertEqual(output_sum, ctrl_bit * input_a + b,
                             f"ctrl: {ctrl_bit}, reg_a: {input_a}, reg_b: {b}, out_sum: {output_sum}"
                             )
            # check ancilla reset to 0
            self.assertEqual(ancilla, 0)

    def test_invalid_input(self):
        # An invalid register size for MuThCtrlAdder
        n = randint(-1, 2)

        with self.assertRaises(GateParametersAssignedError):
            self._construct_cAdder_circuit(reg_size=n)

    def _construct_cAdder_circuit(
        self,
        reg_size: int,
        ctrl_bit: Optional[bool] = None,
        init_reg1: Optional[int] = None,
        init_reg2: Optional[int] = None
    ) -> Circuit:
        """ contruct control adder circuit """
        cAdder_circ = Circuit(2 * reg_size + 3)

        # init control bit
        if ctrl_bit is None:
            H | cAdder_circ(0)
        elif ctrl_bit:
            X | cAdder_circ(0)

        # init first register
        if init_reg1 is None:
            for i in range(1, 1 + reg_size):
                H | cAdder_circ(i)
        else:
            circuit_init(cAdder_circ, range(1, 1 + reg_size), init_reg1)

        # init second register
        if init_reg2 is None:
            for i in range(reg_size + 2, 2 * reg_size + 2):
                H | cAdder_circ(i)
        else:
            circuit_init(cAdder_circ, range(reg_size + 2, 2 * reg_size + 2), init_reg2)

        # apply control adder gate
        MuThCtrlAdder(reg_size) | cAdder_circ

        return cAdder_circ

    def _run_and_decode_adder_circuit(
        self,
        circuit: Circuit,
        reg_size: int
    ) -> List:
        """ run the circuit and decode the simulation result """
        sv_sim = StateVectorSimulator()
        sv_sim.run(circuit=circuit)
        counts = sv_sim.sample(shots=2**(reg_size + 3))

        return decode_counts_int(counts, [1, reg_size, reg_size + 1, 1])


if __name__ == "__main__":
    unittest.main()
