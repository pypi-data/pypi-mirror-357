from QuICT.core.gate import CompositeGate, X, CX
from QuICT.algorithm.arithmetic.adder import QFTWiredAdder


class Comparator(CompositeGate):
    """
    In "lt" (less than) mode:
        U(c)|x>|0> --> |x>|x < c>
    In "ge" (greater than or equal) mode:
        U(c)|x>|0> --> |x>|x >= c>
    """

    def __init__(
        self,
        qreg_size: int,
        const: int,
        in_fourier: bool = False,
        out_fourier: bool = False,
        mode: str = "lt",
        name: str = None
    ):
        """
        Args:
            qreg_size (int): Size of the quantum register.
            const (int): The integer to be compared with, given classically.
            name (str): Name of the gate.
        """
        if mode not in ["lt", "ge"]:
            raise ValueError("Not a valid mode, pealse choose from: \"lt\", \"ge\"}.")
        # TODO: check `qreg_size` can hold `const` as a signed int
        super().__init__(name)

        self._data_reg = list(range(qreg_size))
        self._sign_reg = [qreg_size]

        QFTWiredAdder(qreg_size, -const, in_fourier=in_fourier) | self(self._data_reg)
        if mode == "ge":
            X | self(self._data_reg[0])
        CX | self([self._data_reg[0], self._sign_reg[0]])
        if mode == "ge":
            X | self(self._data_reg[0])
        QFTWiredAdder(qreg_size, const, out_fourier=out_fourier) | self(self._data_reg)
