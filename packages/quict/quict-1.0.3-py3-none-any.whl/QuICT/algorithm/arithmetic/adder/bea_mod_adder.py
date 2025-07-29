from QuICT.core.gate import CompositeGate, X, CX
from QuICT.algorithm.arithmetic.adder import QFTWiredAdder
from QuICT.tools.exception.core import GateParametersAssignedError


class FourierModAdder(CompositeGate):
    """ Controlled modular adder, bea

    Reference:
        [1]: "Circuit for Shor's algorithm using 2n+3 qubits": http://arxiv.org/abs/quant-ph/0205095v3
    """

    def __init__(
        self,
        qreg_size: int,
        addend: int,
        modulus: int,
        num_control: int = 0,
        in_fourier: bool = False,
        out_fourier: bool = False,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Size of the quantum register waiting to be added. Needs to be greater than or equal to 2.
            addend (int): The integer that will be added to the qreg.
            modulus (int): The integer as modulus.
            num_control (int): Indicates the number of qubits for controlling the wired adder, up to 2 qubits.
                If not 0, the control bits will be on the highest bits.
            in_fourier (bool): If True, assuming the input register is already in ry-qft basis.
            out_fourier (bool): If True, after the addition, the qreg will be left in ry-qft basis.
            name (str): Name of the wired adder gate.

        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 2.
        """
        if qreg_size < 2:
            raise GateParametersAssignedError(
                f"The wired Fourier modular adder needs at least two qubits but given {qreg_size}."
            )
        if num_control < 0 or num_control > 2:
            raise ValueError("Number of control qubits not supported. Should be in the range: [0, 2].")

        super().__init__(name)

        self._ctrl_reg = list(range(num_control))
        self._data_reg = list(range(num_control, qreg_size + num_control))
        self._anci_reg = [qreg_size + num_control]

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=addend,
            num_control=num_control,
            in_fourier=in_fourier,
            out_fourier=True
        ) | self(self._ctrl_reg + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=-modulus,
            in_fourier=True
        ) | self(self._data_reg)

        CX | self([self._data_reg[0], self._anci_reg[0]])

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=modulus,
            num_control=1,
            out_fourier=True
        ) | self(self._anci_reg[:1] + self._data_reg)

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=-addend,
            num_control=num_control,
            in_fourier=True
        ) | self(self._ctrl_reg + self._data_reg)

        X | self(self._data_reg[0])
        CX | self([self._data_reg[0], self._anci_reg[0]])
        X | self(self._data_reg[0])

        QFTWiredAdder(
            qreg_size=qreg_size,
            addend=addend,
            num_control=num_control,
            in_fourier=False,
            out_fourier=out_fourier
        ) | self(self._ctrl_reg + self._data_reg)

        self.set_ancilla(self._ancilla_qubits)
