from typing import Optional, Dict, Union
from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, H
from QuICT.algorithm.qft import IQFT
from QuICT.algorithm.tools import QRegManager, QubitAligner
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.tools.exception.algorithm import GetBeforeRunError
from QuICT.tools import Logger
import numpy as np


logger = Logger("QPE")


class PhaseEstimation:
    """ Quantum Phase Estimation.

    Qubit Arrangement:
    |precision_bits>
    |work_bits>
    |ancilla>

    References:
        [1]: Nielsen, M.A., & Chuang, I.L. (2010). Quantum Computation and Quantum Information, p.225.
    """
    @property
    def distribution(self) -> np.ndarray:
        if self._distribution is None:
            raise GetBeforeRunError("PhaseEstimation get distribution without running the algorithm.")

        return self._distribution

    def __init__(
        self,
        precision_bits: int,
        work_bits: int,
        control_unitary: CompositeGate,
        work_state_prep: Optional[CompositeGate] = None,
        do_swap: bool = False
    ):
        """
        Args:
            precision_bits (int): The number of qubits for representing the phase.
            work_bits (int): The number of qubits for storing the eigenstate.
            control_unitary (CompositeGate): A controlled version of the uitary whose phase is about to
                be estimated. The control bit requires to be the highest bit.
            work_state_prep (CompositeGate): Optional eigenstate prepration gate.
            do_swap (bool): If `True`, the iqft stage will include swap gates.
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

        num_ancilla = len(control_unitary.ancilla_qubits)
        self._work_state_prep = None
        if work_state_prep is not None:
            if not isinstance(work_state_prep, CompositeGate):
                raise ValueError("Input `work_state_prep` has to be a composite gate.")
            self._work_state_prep = work_state_prep
            num_ancilla = max(num_ancilla, len(work_state_prep.ancilla_qubits))
            required_q_sp = max(work_state_prep.qubits) + 1 - len(work_state_prep.ancilla_qubits)
            if required_q_sp > work_bits:
                raise ValueError("Not enough work qubits for the state preparation. "
                                 f"Given {work_bits}, but the state preparation requires: {required_q_sp}.")

        self._control_unitary = control_unitary
        self._do_swap = do_swap

        # Allocate required qubits
        reg_manager = QRegManager()
        self._precision_reg = reg_manager.alloc(precision_bits)
        self._work_reg = reg_manager.alloc(work_bits)
        self._ancilla_reg = reg_manager.alloc(num_ancilla)
        self._total_qubits = reg_manager.allocated

        # Get input composite gates' application indices
        gate_mapper = QubitAligner(self._work_reg, self._ancilla_reg)
        if work_state_prep is not None:
            self._sp_reg = gate_mapper.getMap(self._work_state_prep)
        self._cu_reg_without_ctrl = gate_mapper.getMap(self._control_unitary, fix_top=1)

        self._circuit = None
        self._distribution = None

    def circuit(self) -> Circuit:
        """ Build the quantum phase estimation circuit.

        Returns:
            Circuit: the qpe circuit.
        """
        if self._circuit is not None:
            return self._circuit

        self._circuit = Circuit(self._total_qubits)
        num_precision = len(self._precision_reg)

        if self._work_state_prep is not None:
            self._work_state_prep | self._circuit(self._sp_reg)

        for i in self._precision_reg:
            H | self._circuit(i)

        if self._do_swap:
            for i in reversed(range(num_precision)):
                ctrl_bit = self._precision_reg[i]
                self._control_unitary.exp2(num_precision - 1 - i) | self._circuit(
                    [ctrl_bit] + self._cu_reg_without_ctrl
                )
        else:
            for i in range(num_precision):
                ctrl_bit = self._precision_reg[i]
                self._control_unitary.exp2(i) | self._circuit([ctrl_bit] + self._cu_reg_without_ctrl)

        IQFT(num_precision, with_swap=self._do_swap) | self._circuit(self._precision_reg)

        return self._circuit

    def run(
        self,
        backend=StateVectorSimulator(),
        shots: int = 1,
        decode_as_float: bool = True
    ) -> Union[Dict[float, int], Dict[str, int]]:
        """ Run the quantum phase estimation circuit.

        Args:
            backend (Any): a backend to run the qpe circuit.
            shots (int): number of times to run the circuit.
            decode_as_float (bool): If `True`, the running result will be decoded to be the phase/(2*pi)
                which is a float between 0 and 1. If `False`, the result will be presented as bit strings.

        Returns:
            Dict[float, int] | Dict[str, int]: result get from running the qpe circuit.
        """
        if shots < 1:
            raise ValueError(f"Shots have to be positive.")

        if self._circuit is None:
            self.circuit()

        # run the circuit on designated backend
        if self._distribution is None:
            final_sv = backend.run(self._circuit)

            # calculate the wole distribution if backend is simulator.
            final_density_diag = (final_sv * final_sv.conj()).real
            # trace out the work and ancilla bits
            traced_diag = np.sum(
                final_density_diag.reshape(
                    (1 << len(self._precision_reg), 1 << (len(self._work_reg) + len(self._ancilla_reg)))
                ),
                axis=1
            )
            if backend.device == "GPU":
                traced_diag = traced_diag.get()
            self._distribution = traced_diag

        sample_array = np.random.choice(a=len(self._distribution), p=self._distribution, size=shots)
        unique, counts = np.unique(sample_array, return_counts=True)

        if decode_as_float:
            return dict(zip((unique / (1 << len(self._precision_reg))), counts))

        measure_dict = {}
        for i in range(len(unique)):
            key_str = np.binary_repr(unique[i], width=len(self._precision_reg))
            measure_dict[key_str] = counts[i]

        return measure_dict

    def reset(self) -> None:
        self._circuit = None
        self._distribution = None
