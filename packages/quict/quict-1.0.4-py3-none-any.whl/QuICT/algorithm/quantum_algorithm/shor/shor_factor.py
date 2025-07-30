import random
from math import gcd
import numpy as np
from fractions import Fraction
from typing import Tuple, Dict

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X
from QuICT.simulation.state_vector import StateVectorSimulator

from QuICT.algorithm.arithmetic.multiplier import BEACUa, CHRSMulMod
from QuICT.algorithm.quantum_algorithm.phase_estimation import PhaseEstimation, IterativePhaseEstimation

from QuICT.tools import Logger
sf_logger = Logger("Shor")

from typing import Literal

_ModMultiMethod = Literal["bea", "hrs"]
_QpeMethod = Literal["normal", "iterative"]


class ShorFactor:
    """ Shor's factoring algorithm

    References:
        [1]: "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer"
        by Peter W. Shor <https://arxiv.org/abs/quant-ph/9508027>.

        [2]: Nielsen, M.A., & Chuang, I.L. (2010). Quantum Computation and Quantum Information, p.232.

    """

    _MOD_MULTIPLIER_METHODS = {"bea": BEACUa, "hrs": CHRSMulMod}
    _QPE_METHDOS = {"normal": PhaseEstimation, "iterative": IterativePhaseEstimation}

    class SRData:
        """ For storing (s, r) pair when running order finding for multiple times. """
        def __init__(self) -> None:
            self.s_list = []
            self.r_list = []

            self.lcm_s = 1
            self.lcm_r = 1

        def is_valid(self, new_s: int, new_r: int) -> bool:
            """ Return whether the incoming s-r pair can be added. """
            return gcd(self.lcm_s, new_s) == 1 and (self.lcm_r % new_r) != 0

        def add(self, new_s: int, new_r: int) -> None:
            """ Add new (s, r) pair. """
            if not self.is_valid(new_s, new_r):
                raise ValueError(f"The (s = {new_s}, r = {new_r}) pair cannot be added. ")

            self.s_list.append(new_s)
            self.r_list.append(new_r)

            gcd_s = gcd(self.lcm_s, new_s)
            gcd_r = gcd(self.lcm_r, new_r)
            self.lcm_s = (self.lcm_s // gcd_s) * new_s
            self.lcm_r = (self.lcm_r // gcd_r) * new_r

    # add a, N here
    def __init__(
        self,
        N: int,
        *,
        c_mod_multiplier: _ModMultiMethod = "bea",
        qpe_method: _QpeMethod = "normal"
    ):
        """
        Args:
            N (int): The number to be factored.
            c_mod_multiplier (str): Modular multiplication method to be used when constructing the
                circuit for Shor's algorithm, choose from "bea" and "hrs".
            qpe_method (str): Quantum phase estimation implementation to be used when constructing
                the order finding circuit, choose from "normal" and "iterative".
        """
        try:
            self.c_mod_multi = self._MOD_MULTIPLIER_METHODS[c_mod_multiplier]
        except:
            raise ValueError(f"{c_mod_multiplier} is not a valid modular multiplication option. ",
                             f"Please choose from {self._MOD_MULTIPLIER_METHODS}.")

        try:
            self.qpe_method = self._QPE_METHDOS[qpe_method]
        except:
            raise ValueError(f"{qpe_method} is not a valid option for quantum phase estimation. ",
                             f"Please choose from {self._QPE_METHDOS}.")

        self.N = N

        self.work_bits_num = int(np.ceil(np.log2(self.N + 1)))
        self.order_bits_num = int(np.ceil(2 * np.log2(self.N + 1)))
        self._qpe_cache = {}
        self.distribution = None

    @property
    def running_data(self) -> Dict:
        """ Return historical data of all the qpe circuits that has been used by run in (base, qpe_algorithm)
            key and value pairs.
        """
        return self._qpe_cache

    def circuit(self, base: int = None) -> Circuit:
        """ Construct the order finding quantum circuit for Shor's algorithm,

        Args:
            base (int): The base for calculating the order r mod N. Has to be coprime to N.
                If not provided, will choose randomly in [2, N - 1].

        Returns:
            Circuit: An order finding circuit.
        """
        if base is None:
            base = self._rand_coprime(self.N)
        elif gcd(base, self.N) != 1:
            raise ValueError(f"The given base:{base} is not co-prime to {self.N}.")

        sf_logger.info(f"Constructing shor's order finding circuit with base={base}.")

        qpe_alg = self.qpe_method(
            precision_bits=self.order_bits_num,
            work_bits=self.work_bits_num,
            control_unitary=self.c_mod_multi(modulus=self.N, multiple=base, qreg_size=self.work_bits_num),
            work_state_prep=CompositeGate(gates=[X & 0], name="X")
        )

        return qpe_alg.circuit()

    def run(
        self,
        base: int = None,
        *,
        max_it: int = 1,
        forced_quantum_approach: bool = False,
        backend=StateVectorSimulator(ignore_last_measure=False)
    ) -> Tuple[int, int]:
        r""" Run Shor's factoring algorithm.

        Args:
            base (int, optional): The base for calculating the order r mod N. Has to be coprime to N.
                If not provided, will choose randomly in [2, N - 1].
            max_it (int, optional): The maximum number of order finding iteration.
            forced_quantum_approach (bool, optional): If true, the order finding part is forced to
                use the quantum approach.
            backend (Any, optional): Device to run the circuit.

        Returns:
            Tuple[int, int]: The two factors that multiply to N.
        """
        ## Eliminate trivial factoring cases
        c_fac1, c_fac2 = self._pre_processing(self.N)
        if c_fac1 != 0:
            return c_fac1, c_fac2

        ## Order finding for nontrivial case
        if base is None:
            base_run = random.randint(2, self.N - 1)
        else:
            base_run = base

        # classical order finding
        while True:
            gcd_bN = np.gcd(base_run, self.N)
            if gcd_bN == 1:
                break
            if not forced_quantum_approach:
                sf_logger.info(f"Shor succeed: randomly chosen base = {base_run}, "
                               f"which has common factor {gcd_bN} with N classically.")
                return gcd_bN, self.N // gcd_bN
            if base is not None:
                raise ValueError(f"The input base = {base} is not coprime to {self.N}, thus "
                                 "cannot be used in forced-quantum mode")
            base_run = random.randint(2, self.N - 1)

        # quantum order finding
        sr_pair = self.SRData()
        for _ in range(max_it):
            s, r = self._quantum_order_finding(base_run, backend)

            if r < 2:
                sf_logger.info(f"Post: s/r is close to 0, not valid for post-processing.")
                continue

            # post-processing
            if self._is_order(self.N, base_run, r):
                if r % 2 == 1:
                    sf_logger.info(f"Post: found odd order: r = {r}, for base = {base_run}. "
                                   "Changing to a new base is recommended.")
                    return 0, 0
                if self._is_trivial_order(self.N, base_run, r):
                    continue
                sf_logger.info(f"Post: Found an even order: r = {r}.")
                q_fac1, q_fac2 = self._post_processing(self.N, base_run, r)
                if q_fac1 != 0:
                    return q_fac1, q_fac2
            else:
                sf_logger.info("Fail finding a valid order in current iteration")
                if max_it > 1 and sr_pair.is_valid(s, r):
                    sf_logger.info(f"Add pair (s = {s}, r = {r}) to cumulative data.")
                    sr_pair.add(s, r)
                    q_fac1, q_fac2 = 0, 0
                    if len(sr_pair.s_list) > 1 and self._is_order(self.N, base_run, sr_pair.lcm_r):
                        sf_logger.info(f"Found order: r = {sr_pair.lcm_r}, "
                                       f"from cumulative r list: {sr_pair.r_list}.")
                        q_fac1, q_fac2 = self._post_processing(self.N, base_run, sr_pair.lcm_r)
                    if q_fac1 != 0:
                        return q_fac1, q_fac2
        sf_logger.info(f"Fail finding factor for N = {self.N} with base = { base_run}.")
        return 0, 0

    def reset(self):
        """ Clear all the historical qpe algorithm data generated from run. """
        self._qpe_cache.clear()

    def _pre_processing(self, N: int) -> Tuple[int, int]:
        """ Use classical pre-processing to rule out trivial factoring cases. """
        # 1. check if input is prime (using MillerRabin in klog(N), k is the number of rounds to run MillerRabin)
        if self._miller_rabin(N):
            sf_logger.info(f"Pre-processing:{N} does not pass miller rabin test, may be a prime number.")
            return 1, N

        # 2. If n is even, return the factor 2
        if N % 2 == 0:
            sf_logger.info(f"Pre-processing: N:{N} is even, found factor 2 classically.")
            return 2, N // 2

        # 3. Classically determine if N = p^q
        y, L = np.log2(N), int(np.ceil(np.log2(N)))
        for b in range(2, L):
            squeeze = np.power(2, y / b)
            u1, u2 = int(np.floor(squeeze)), int(np.ceil(squeeze))
            if pow(u1, b) == N:
                sf_logger.info(f"Pre-processing: N is exponential, found the only factor {u1} classically.")
                return u1, N // u1
            if pow(u2, b) == N:
                sf_logger.info(f"Pre-processing: N is exponential, found the only factor {u2} classically.")
                return u2, N // u2

        return 0, 0

    def _is_trivial_order(self, N: int, base: int, r: int) -> bool:
        """ In post processing, output whether the order is trivial. """
        if pow(base, (r >> 1), N) == N - 1:
            sf_logger.info(f"Post: found trivial solution {base}^({r}/2) = {N} - 1.")
            return True

        return False

    def _post_processing(self, N: int, base: int, r: int) -> Tuple[int, int]:
        """ Given a base and a nontrivial order, try to recover the factors. """
        # N | h^2 - 1, h = a^(r/2)
        h = pow(base, (r >> 1), N)
        f1, f2 = np.gcd(h - 1, N), np.gcd(h + 1, N)
        if f1 > 1 and f1 < N:
            sf_logger.info(f"Shor succeed: found factor {f1}, with base = {base}, r = {r}.")
            return f1, N // f1

        if f2 > 1 and f2 < N:
            sf_logger.info(f"Shor succeed: found factor {f2}, with base = {base}, r = {r}.")
            return f2, N // f2

        sf_logger.info(f"Post: can not find a factor with base = {base}, r = {r}.")

        return 0, 0

    def _quantum_order_finding(
        self,
        base: int = None,
        backend=StateVectorSimulator(ignore_last_measure=False)
    ) -> Tuple[int, int]:
        """ Run order finding subroutine with given base and backend, and use continued fraction to get (s, r) in
            approximated phase s/r.
        """
        # Construct shor's order finding quantum circuit.
        sf_logger.info(f"Quantumly determine the order of the randomly chosen base = {base}")

        if base in self._qpe_cache:
            qpe_algo = self._qpe_cache[base]
            sf_logger.info(f"Reusing previously built qpe circuit with base: {base}.")
        else:
            qpe_algo = self.qpe_method(
                precision_bits=self.order_bits_num,
                work_bits=self.work_bits_num,
                control_unitary=self.c_mod_multi(modulus=self.N, multiple=base, qreg_size=self.work_bits_num),
                work_state_prep=CompositeGate(gates=[X & 0], name="X")
            )

            self._qpe_cache[base] = qpe_algo

        res_dict = qpe_algo.run(backend=backend, shots=1, decode_as_float=False)
        res_bin = list(res_dict)[0]

        sf_logger.info(f"\tphi~ (approximately s/r) in binary form is {res_bin}")
        phi = int(res_bin, base=2) / (1 << len(res_bin))
        sf_logger.info(f"\tphi~ (approximately s/r) in decimal form is {phi}")
        frac = Fraction(phi).limit_denominator(self.N - 1)
        s = frac.numerator
        r = frac.denominator
        sf_logger.info(f"\tphi~ (approximately s/r) in fractional form is {s}/{r}")

        return s, r

    def _is_order(self, N: int, base: int, r: int):
        """ Return if `r` is an order of `base` mod `N`. """
        return pow(base, r, N) == 1

    def _rand_coprime(self, N: int) -> int:
        """ Generate a random number in [2, N-1] that is coprime to N"""

        if N < 3:
            raise ValueError(f"A random coprime to {N} does not exist.")

        a = N
        while gcd(a, N) != 1:
            a = np.random.randint(2, N)

        return a

    def _miller_rabin(self, num) -> bool:
        """ Random prime test up to N = 2^64. Return `True` when num is a prime with high probability and
            return `False` when num is a composite.
        """
        def fast_power(a, b, N):
            x = 1
            now_a = a
            while b > 0:
                if b % 2 == 1:
                    x = x * now_a % N
                now_a = now_a * now_a % N
                b >>= 1
            return x

        witness = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        if num == 1:
            return False
        t = num - 1
        k = 0
        while (t & 1) == 0:
            k += 1
            t >>= 1
        for p in witness:
            if num == p:
                return True
            a = fast_power(p, t, num)
            nxt = a
            for _ in range(k):
                nxt = (a * a) % num
                if nxt == 1 and a != 1 and a != num - 1:
                    return False
                a = nxt
            if a != 1:
                return False
        return True
