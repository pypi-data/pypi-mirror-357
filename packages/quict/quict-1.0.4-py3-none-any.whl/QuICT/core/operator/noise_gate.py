from __future__ import annotations

from ._operator import Operator


class NoiseGate(Operator):
    """
    The quantum gate with noise error.
    """
    @property
    def noise_matrix(self) -> list:
        """ The noised gate matrix. """
        return self._noise_matrix

    @property
    def qasm_name(self) -> str:
        return self._gate.qasm_name

    def qasm(self, targs) -> str:
        return self._gate.qasm(targs)

    @property
    def type(self) -> str:
        return self._gate.type

    @property
    def targets(self) -> int:
        return self._gate.targets

    @property
    def controls(self) -> int:
        return self._gate.controls

    @property
    def variables(self) -> int:
        return self._gate.variables

    def __init__(self, gate, noise):
        """
        Args:
            gate (BasicGate): The quantum gate.
            error (QuantumNoiseError): The noise error.
        """
        self._gate = gate
        self._noise = noise
        args_num = gate.controls + gate.targets
        gate_name = gate.type.name
        super().__init__(args_num, name=f"ng_{gate_name}")
        self._noise_matrix = noise.to_matrix()
        self._precision = gate.precision

    def copy(self):
        _ngate = NoiseGate(self._gate, self._noise)

        if len(self.targs) > 0:
            _ngate.targs = self._targs

        return _ngate
