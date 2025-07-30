import numpy as np
from typing import Union

from QuICT.core import Circuit
from QuICT.core.noise import NoiseModel
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.simulation.state_vector import StateVectorSimulator
from QuICT.simulation.unitary import UnitarySimulator
from QuICT.simulation.density_matrix import DensityMatrixSimulator
from QuICT.simulation.utils import Result
from QuICT.tools.exception.core import ValueError
from QuICT.tools.exception.simulation import SimulatorOptionsUnmatchedError


class Simulator:
    """ The high-level simulation class, including all QuICT simulator mode. """

    __DEVICE = ["CPU", "GPU"]
    __BACKEND = ["unitary", "state_vector", "density_matrix"]
    __PRECISION = ["single", "double"]
    __OPTIONS_DICT = {
        "state_vector": ["gpu_device_id", "sync"],
        "density_matrix": ["accumulated_mode"]
    }

    def __init__(
        self,
        device: str = "CPU",
        backend: str = "state_vector",
        precision: str = "double",
        circuit_record: bool = False,
        amplitude_record: bool = False,
        output_path: str = None,
        hidden_empty_qubits: bool = False,
        **options
    ):
        """
        Args:
            device (str): The device of the simulator. One of [CPU, GPU]
            backend (str): The backend for the simulator. One of [unitary, state_vector, density_matrix]
            precision (str): The precision of simulator, one of [single, double], default to double.
            circuit_record (bool): whether record circuit's qasm in output, default to False.
            amplitude_record (bool): whether record the amplitude of qubits, default to False.
            output_path (str): The output path for simulation result, default to None.
            **options (dict): other optional parameters for the simulator.
                state_vector: [gpu_device_id] (only for gpu)
                density_matrix: [accumulated_mode]
                unitary: None
        """
        assert device in Simulator.__DEVICE, ValueError("Simulator.device", "[CPU, GPU]", device)
        self._device = device
        assert backend in Simulator.__BACKEND, \
            ValueError("Simulator.backend", "[unitary, state_vector, density_matrix]", backend)
        self._backend = backend
        assert precision in Simulator.__PRECISION, ValueError("Simulator.precision", "[single, double]", precision)
        self._precision = precision
        self._hidden_empty_qubits = hidden_empty_qubits

        self._options = options
        if options:
            if not self._options_validation(options):
                raise SimulatorOptionsUnmatchedError(
                    f"Unmatched options arguments depending on {self._device} and {self._backend}."
                )

        # load simulator
        self._simulator = self._load_simulator()

        # Result's arguments
        self._result_recorder = Result(
            device, backend, precision, circuit_record, amplitude_record, self._options, output_path
        )

    def _options_validation(self, options: dict) -> bool:
        if self._backend == "unitary" or (self._backend == "state_vector" and self._device == "CPU"):
            return False

        default_option_list = Simulator.__OPTIONS_DICT[self._backend]
        option_keys = list(options.keys())
        for option_key in option_keys:
            if option_key not in default_option_list:
                return False

        return True

    def _load_simulator(self):
        """ Initial simulator. """
        if self._backend == "state_vector":
            simulator = StateVectorSimulator(
                self._device,
                precision=self._precision,
                hidden_empty_qubits=self._hidden_empty_qubits,
                **self._options
            )
        elif self._backend == "unitary":
            simulator = UnitarySimulator(
                device=self._device,
                precision=self._precision,
                hidden_empty_qubits=self._hidden_empty_qubits,
            )
        else:
            simulator = DensityMatrixSimulator(
                device=self._device,
                precision=self._precision,
                hidden_empty_qubits=self._hidden_empty_qubits,
                **self._options
            )

        return simulator

    def run(
        self,
        circuit: Union[Circuit, np.ndarray],
        shots: int = 1,
        quantum_state: np.ndarray = None,
        quantum_machine_model: Union[NoiseModel, VirtualQuantumMachine] = None,
        use_previous: bool = False
    ):
        """ start simulator with given circuit

        Args:
            circuit Union[Circuit, np.ndarray]: The quantum Circuit or Unitary Matrix.
            shots (int): The sample times for current Circuit.
            quantum_state (ndarray): The initial Quantum State Vector/Density Matrix.
            quantum_machine_model (Union[NoiseModel, VirtualQuantumMachine]): The model of quantum machine
            use_previous (bool, optional): Using the previous state vector. Defaults to False.

        Yields:
            [dict]: The Result Dict.
        """
        # Deal with unitary matrix as input
        if isinstance(circuit, np.ndarray) and self._backend != "unitary":
            raise SimulatorOptionsUnmatchedError(
                f"The unitary matrix input only allows in the unitary backend, not {self._backend}."
            )

        if quantum_machine_model is not None and self._backend == "unitary":
            raise SimulatorOptionsUnmatchedError(
                "The Quantum Machine Model input only allows in the Unitary Simulator backend, " +
                f"not {self._backend}."
            )

        if quantum_state is not None:
            ndim = quantum_state.ndim
            if ndim == 2 and self._backend != "density_matrix":
                raise SimulatorOptionsUnmatchedError(
                    f"The Density Matrix input only allows in the Density Matrix backend, not {self._backend}."
                )

            if ndim == 1 and self._backend == "density_matrix":
                raise SimulatorOptionsUnmatchedError(
                    f"The State Vector input only allows in the Unitary/SV backend, not {self._backend}."
                )

        if isinstance(circuit, Circuit):
            self._result_recorder.record_circuit(circuit)

        if quantum_machine_model is not None:
            amplitude = self._simulator.run(circuit, quantum_state, quantum_machine_model, use_previous)
        else:
            amplitude = self._simulator.run(circuit, quantum_state, use_previous=use_previous)

        self._result_recorder.record_amplitude(amplitude)

        sample_result = self._simulator.sample(shots)
        self._result_recorder.record_sample(sample_result)

        return self._result_recorder.__dict__()
