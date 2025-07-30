from typing import Optional, Dict, Union
from QuICT.core import Circuit
from QuICT.core.operator import Trigger
from QuICT.core.gate import CompositeGate, X, H, Rz, ID, Measure
from QuICT.algorithm.qft import IQFT
from QuICT.algorithm.tools import QRegManager, QubitAligner
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.tools.exception.algorithm import GetBeforeRunError
import numpy as np


class IterativePhaseEstimation:
    """ Iterative Quantum Phase Estimation

    Qubit Arrangement:
    |recycling precision_bits>
    |work_bits>
    |ancilla>

    References:
        [1]: Dobsicek, M., G. Johansson, V. S. Shumeiko, and G. Wendin. “Arbitrary Accuracy Iterative
            Phase Estimation Algorithm as a Two Qubit Benchmark.” Physical Review A 76, no. 3
            (September 19, 2007): 030306. https://doi.org/10.1103/PhysRevA.76.030306.

    """

    def __init__(
        self,
        precision_bits: int,
        work_bits: int,
        control_unitary: CompositeGate,
        work_state_prep: Optional[CompositeGate] = None
    ):
        """
        Args:
            precision_bits (int): The number of qubits for representing the phase.
            work_bits (int): The number of qubits for storing the eigenstate.
            control_unitary (CompositeGate): A controlled version of the uitary whose phase is about to
                be estimated. The control bit requires to be the highest bit.
            work_state_prep (CompositeGate): Optional eigenstate prepration gate.
        Raises:
            ValueError: If `control_unitary` is not a composite gate.
            ValueError: If `work_state_prep` is not a composite gate or its width is larger the number of
                work bits.
        """
        if not isinstance(control_unitary, CompositeGate):
            raise ValueError("Input `control_unitary` has to be a composite gate.")
        required_q_cu = max(control_unitary.qubits) - len(control_unitary.ancilla_qubits)
        if required_q_cu > work_bits:
            raise ValueError("Not enough work qubits for control unitary. "
                             f"Given {work_bits}, but the control unitary requires: {required_q_cu}.")

        if work_state_prep is not None:
            if not isinstance(work_state_prep, CompositeGate):
                raise ValueError("Input `work_state_prep` has to be a composite gate.")
            required_q_sp = max(work_state_prep.qubits) + 1 - len(work_state_prep.ancilla_qubits)
            if required_q_sp > work_bits:
                raise ValueError("Not enough work qubits for the state preparation. "
                                 f"Given {work_bits}, but the state preparation requires: {required_q_sp}.")

        self._control_unitary = control_unitary
        self._work_state_prep = work_state_prep

        # Allocate required qubits
        reg_manager = QRegManager()
        num_ancilla = max(len(control_unitary.ancilla_qubits), len(work_state_prep.ancilla_qubits))
        self._iteration = precision_bits
        self._precision_reg = reg_manager.alloc(1)
        self._work_reg = reg_manager.alloc(work_bits)
        self._ancilla_reg = reg_manager.alloc(num_ancilla)
        self._total_qubits = reg_manager.allocated

        # Get input composite gates' application indices
        gate_mapper = QubitAligner(self._work_reg, self._ancilla_reg)
        self._sp_reg = gate_mapper.getMap(self._work_state_prep)
        self._cu_reg_without_ctrl = gate_mapper.getMap(self._control_unitary, fix_top=1)

        self._circuit = None
        valid_meas_idx = [0] + [((2 * precision_bits - i + 1) * i) >> 1 for i in range(1, precision_bits)]
        self._measurement_idx = list(reversed(valid_meas_idx))
        self._total_measure_counts = {}

    @property
    def measurement_idx(self):
        return self._measurement_idx

    @property
    def total_measure_counts(self):
        return self._total_measure_counts

    def circuit(self):
        """ Build the iterative phase estimation circuit.

        Returns:
            Circuit: the iterative qpe circuit.
        """
        if self._circuit is not None:
            return self._circuit

        self._circuit = Circuit(self._total_qubits)

        if self._work_state_prep is not None:
            self._work_state_prep | self._circuit(self._sp_reg)

        ptr = 0
        for i in range(self._iteration):
            precision_pos = self._iteration - 1 - i

            H | self._circuit(self._precision_reg)
            self._control_unitary.exp2(precision_pos) | self._circuit(
                self._precision_reg + self._cu_reg_without_ctrl
            )
            H | self._circuit(self._precision_reg)

            offset = 0
            # q_if gate for q == 0 case
            cg_id = CompositeGate(gates=[ID & self._precision_reg])
            for j in range(precision_pos):
                # q_if gate for q == 1
                cg_rotation = CompositeGate(gates=[Rz(-np.pi / (2 << j)) & self._precision_reg])
                trig_targat = precision_pos - j + ((3 + i) * (j + 1)) + offset - 1
                Trigger(1, [cg_id, cg_rotation], position=trig_targat) | self._circuit(self._precision_reg)

                ptr += 1
                offset += (precision_pos - j + 1)

            if i == self._iteration - 1:
                Measure | self._circuit(self._precision_reg)
            else:
                # recycle and reset the qubit to 0 using q_if
                cg_reset = CompositeGate(gates=[X & self._precision_reg])
                Trigger(1, [cg_id, cg_reset]) | self._circuit(self._precision_reg)
                ptr += 1

        return self._circuit

    def run(
        self,
        backend=StateVectorSimulator(ignore_last_measure=False),
        shots: int = 1,
        decode_as_float: bool = True,
        cumulative: bool = True
    ) -> Union[Dict[float, int], Dict[str, int]]:
        """ Run the iterative phase estimation circuit

        Args:
            backend (Any): a backend to run the qpe circuit.
            shots (int): number of times to run the circuit.
            decode_as_float (bool): If `True`, the running result will be decoded to be the phase/(2*pi)
                which is a float between 0 and 1. If `False`, the result will be presented as bit strings.

        Returns:
            Dict[float, int] | Dict[str, int]: result get from running the qpe circuit, a (result, shot_counts) pair.
        """
        if shots < 1:
            raise ValueError(f"Shots have to be positive.")

        if self._circuit is None:
            self.circuit()

        measure_dict = {}

        for _ in range(shots):
            # get measurement results on the precision qubit
            backend.run(self._circuit)
            hist_measure = self._circuit.qubits[self._precision_reg[0]].historical_measured
            res_bin = "".join(str(hist_measure[i]) for i in self._measurement_idx)
            # reset the precision qubit measurement history
            self._circuit.qubits[self._precision_reg[0]].reset()

            # decode measurement results
            if decode_as_float:
                res_key = int(res_bin, base=2) / (1 << self._iteration)
            else:
                res_key = res_bin

            measure_dict.setdefault(res_key, 0)
            measure_dict[res_key] += 1

        if cumulative:
            for key in measure_dict:
                self._total_measure_counts.setdefault(key, 0)
                self._total_measure_counts[key] += measure_dict[key]

        return measure_dict

    def reset(self):
        self._circuit = None
        self._total_measure_counts.clear()
