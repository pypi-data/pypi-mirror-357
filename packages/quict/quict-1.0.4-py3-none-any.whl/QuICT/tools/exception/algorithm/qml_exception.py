from QuICT.tools.exception import QuICTException


class TypeError(QuICTException):
    """Type Error in QML Module."""

    def __init__(self, locate: str, require: str, given: str):
        msg = f"{locate}'s type should be {require}, but given {given}."
        super().__init__(3001, msg)


class ValueError(QuICTException):
    """Value Error in QML Module."""

    def __init__(self, locate: str, require: str, given: str):
        msg = f"{locate}'s value should be {require}, but given {given}."
        super().__init__(3002, msg)


class HamiltonianError(QuICTException):
    """Hamiltonian Error."""

    def __init__(self, msg: str = None):
        super().__init__(3003, msg)


class AnsatzError(QuICTException):
    """Ansatz Error."""

    def __init__(self, msg: str = None):
        super().__init__(3004, msg)


class EncodingError(QuICTException):
    """Encoding Error."""

    def __init__(self, msg: str = None):
        super().__init__(3005, msg)


class ModelError(QuICTException):
    """Model Error."""

    def __init__(self, msg: str = None):
        super().__init__(3006, msg)


class DatasetError(QuICTException):
    """Dataset Error."""

    def __init__(self, msg: str = None):
        super().__init__(3007, msg)


class ModelRestoreError(QuICTException):
    """Model Restore Operator Error."""

    def __init__(self, msg: str = None):
        super().__init__(3008, msg)


class DeviceError(QuICTException):
    """Device Error."""

    def __init__(self):
        super().__init__(3009, "Simulator and differentiator must use the same device.")


class PrecisionError(QuICTException):
    """Precision Error."""

    def __init__(self):
        super().__init__(
            3010, "Simulator and differentiator must use the same precision."
        )


class FermionOperatorError(QuICTException):
    """FermionOperator Error."""

    def __init__(self, msg: str = None):
        super().__init__(3011, msg)


class BackPropagationError(QuICTException):
    """Back-propagation Error."""

    def __init__(self, msg: str = None):
        super().__init__(3012, msg)
