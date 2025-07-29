import numpy as np

from QuICT.algorithm.arithmetic.adder import FourierModAdder
from QuICT.algorithm.qft import QFT, IQFT
from QuICT.core.gate import CompositeGate, CSwap
from QuICT.tools.exception.core import GateParametersAssignedError


class BEAMulMod(CompositeGate):
    r"""
    Use FourierModAdder to calculate (b+ax)%N in Fourier space that in total requires `2n + 3` qubits.

    $$
         \vert{\text{ctrl}}\rangle \vert{0}\rangle \vert{b}\rangle_{n} \vert{x}\rangle_n  \vert{\text{ancilla}}\rangle
         \to
         \vert{\text{ctrl}}\rangle \vert{(b+\text{ctrl}*a*x)%N}\rangle_{n+1}
         \vert{x}\rangle_n \vert{\text{ancilla}}\rangle
    $$

    References:
        [1]: "Circuit for Shor's algorithm using 2n+3 qubits" by Stephane Beauregard
        <http://arxiv.org/abs/quant-ph/0205095v3>.
    """

    def __init__(
        self,
        qreg_size: int,
        multiplicand: int,
        modulus: int,
        control: bool = True,
        in_fourier: bool = False,
        out_fourier: bool = False,
        name: str = None
    ):
        """
        Args:
            qreg_size (int): The quantum register size for the multiplier encoded in qubit.
            multiplicand (int): The value for the multiplicand which is given classically.
            modulus (int): The integer given as modulus.
            control (bool): Whether having qubit to control the modular multiplier.
                If true, the control qubit will be on the highest qubit.
            in_fourier (bool): If True, assuming the input register is already in Fourier spacec.
            out_fourier (bool): If True, after the addition, the qreg will be left in Fourier spacec.
            name (str): Name of the wired adder gate.
        Raises:
            GateParametersAssignedError: If `qreg_size` is smaller than 1.
        """
        if qreg_size < 1:
            raise GateParametersAssignedError(
                f"The wired Fourier adder needs at least two qubits but given {qreg_size}."
            )

        super().__init__(name)
        if name is None:
            self.name = f"BEAMulMod"

        # init qreg list
        num_control = 0
        control_list = []
        if control:
            num_control = 1
            control_list = [0]
        result_list = list(range(num_control, qreg_size + 1 + num_control))
        x_list = list(range(qreg_size + 1 + num_control, 2 * qreg_size + 1 + num_control))
        ancilla = [2 * qreg_size + 1 + num_control]

        # apply QFT
        if not in_fourier:
            QFT(qreg_size + 1) | self(result_list)

        # construct modular multiplier
        p = 1
        for i in range(qreg_size - 1, -1, -1):
            cc_fourier_mod_adder = FourierModAdder(
                qreg_size + 1,
                p * multiplicand % modulus,
                modulus,
                num_control + 1,
                True,
                True
            )
            cc_fourier_mod_adder | self(control_list + [x_list[i]] + result_list + ancilla)  # p * a % N
            p = p * 2

        if not out_fourier:
            IQFT(qreg_size + 1) | self(result_list)


class BEACUa(CompositeGate):
    """ Modular multiplication circuit for Shor's algorithm using 2n+3 qubits
        <http://arxiv.org/abs/quant-ph/0205095v3>
        For `reg_size` is `n`:

        |control>|x>_{n}|0>_{n + 2} --> |control>|a*x mod N>_{n}|0>_{n + 2} , control == 1
        |control>|x>_{n}|0>_{n + 2} --> |control>|x>_{n}|0>_{n + 2}         , control == 0
    """

    def __init__(
        self,
        modulus: int,
        multiple: int,
        qreg_size: int,
        name: str = None
    ):
        """ Construct the modular multiplication gate

        Args:
            modulus (int): the modulus in the modular multiplication.
            multiple (int): the multiple in the modular multiplication.
            qreg_size (int): size of the register to hold the result of the modular multiplication.
            name (str): name of the gate.
        """
        if int(np.log2(modulus)) + 1 > qreg_size:
            raise ValueError(f"The size of register: {qreg_size} is not enough to hold result of mod N"
                             f", which requires {int(np.log2(modulus)) + 1} qubits.")

        if np.gcd(multiple, modulus) != 1:
            raise ValueError(f"The multiple and the modulus have to be coprime, but given multiple={multiple}, "
                             f"N={modulus}.")

        super().__init__(name)
        if name is None:
            self.name = f"*{multiple} mod{modulus}"

        self._multiple = multiple
        self._modulus = modulus
        self.reg_size = qreg_size

        self.control = 0
        self.reg_x = list(range(1, qreg_size + 1))
        self.ancilla = list(range(qreg_size + 1, 2 * qreg_size + 3))

        # apply on corresponding qreg
        self._build_gate(qreg_size, multiple, modulus) | self(
            self.ancilla[: qreg_size + 1] + self.reg_x + [self.control] + [self.ancilla[qreg_size + 1]]
        )
        self.set_ancilla(self.ancilla)

    def exp2(self, n: int) -> CompositeGate:
        a_exp_n_reduced = self._fast_mod_exp(self._multiple, n, self._modulus)

        _gates = CompositeGate()
        self._build_gate(self.reg_size, a_exp_n_reduced, self._modulus) | _gates(
            self.ancilla[: self.reg_size + 1] + self.reg_x + [self.control] + [self.ancilla[self.reg_size + 1]]
        )
        _gates.set_ancilla(self.ancilla_qubits)
        _gates.name = f"*{self._multiple}^(2^{n}) m{self._modulus}"

        return _gates

    def _build_gate(self, reg_size: int, a: int, N: int) -> CompositeGate:
        """
        Args:
            reg_size (int): bits len
            a (int): least n bits used as unsigned
            N (int): least n bits used as unsigned

        Quregs:
            phib(Qureg): the qureg stores b,        length is n+1,
            x(Qureg):    the qureg stores x,        length is n,
            c(Qureg):    the qureg stores c,        length is 1,
            low(Qureg):  the clean ancillary qubit, length is 1,
        """
        gate_set = CompositeGate()
        qreg_b = list(range(reg_size + 1))
        qreg_x = list(range(reg_size + 1, 2 * reg_size + 1))
        qreg_c = [2 * reg_size + 1]
        qreg_low = [2 * reg_size + 2]

        # construct the mod(N)-multiply(a) gate
        c_mult_mod = BEAMulMod(reg_size, a, N)
        c_mult_mod | gate_set(qreg_c + qreg_b + qreg_x + qreg_low)
        for i in range(reg_size):  # n bits swapped, b[0] always 0
            CSwap | gate_set([qreg_c[0], qreg_x[i], qreg_b[i + 1]])
        # Reverse c_mult_mod(a_inv,N,x,b,c,low)
        c_mult_mod = BEAMulMod(reg_size, N - pow(a, -1, N), N)
        c_mult_mod | gate_set(qreg_c + qreg_b + qreg_x + qreg_low)

        return gate_set

    def _fast_mod_exp(self, base: int, n: int, N: int) -> int:
        for _ in range(n):
            base = (base * base) % N
        return base
