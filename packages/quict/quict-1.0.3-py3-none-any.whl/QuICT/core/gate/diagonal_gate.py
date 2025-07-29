from typing import List, Iterable, Tuple, Set
import numpy as np
from QuICT.core.gate import CompositeGate, CX, U1, GPhase
from QuICT.tools import Logger

_logger = Logger("DiagonalGate")


class DiagonalGate(object):
    """
    Diagonal gate

    Reference:
        https://arxiv.org/abs/2108.06150
    """
    _logger = _logger

    def __init__(self, target: int, aux: int = 0, opt: bool = True, keep_phase: bool = True):
        """
        Args:
            target (int): number of target qubits
            aux (int, optional): number of auxiliary qubits
            opt (bool): optimizer switch, enabled by default
            keep_phase (bool): global phase switch
        """
        self.target = target
        if np.mod(aux, 2) != 0:
            self._logger.warn(
                'Algorithm serves for even number of auxiliary qubits. One auxiliary qubit is dropped.'
            )
            aux = aux - 1
        self.aux = aux
        self.opt = opt
        self.keep_phase = keep_phase
        self.count_no_aux = [0] * (1 << self.target)
        if self.opt:
            from QuICT.qcda.optimization.cnot_without_ancilla import CnotWithoutAncilla
            self._cnot_optimizer = CnotWithoutAncilla()

    def __call__(self, theta: List[float]) -> CompositeGate:
        """
        Args:
            theta (List[float]): list of (2 ** target) angles of rotation in the diagonal gate

        Returns:
            CompositeGate: diagonal gate
        """
        assert len(theta) == 1 << self.target, \
            ValueError('Incorrect number of angles')
        if self.aux == 0:
            self.count_no_aux = [0] * (1 << self.target)
            return self.no_aux_qubit(self.target, theta)
        else:
            return self.with_aux_qubit(theta)

    def no_aux_qubit(self, n: int, theta: List[float]) -> CompositeGate:
        """
        Args:
            n (int): number of qubits in the diagonal gate
            theta (List[float]): list of (2 ** target) angles of rotation in the diagonal gate

        Returns:
            CompositeGate: diagonal gate without auxiliary qubit
        """
        # nmax is the final size of the diagonal gate
        # nmax can keep the size of theta the same as s of alpha_s
        nmax = self.target
        gates = CompositeGate()
        r_t = int(np.floor(n / 2))
        r_c = n - r_t

        if n == 1:
            s_int = 1 << (nmax - 1)

            if self.count_no_aux[s_int] == 0:
                self.count_no_aux[s_int] += 1
                phase_c0 = self.alpha_s(theta, s_int, nmax)
                U1(phase_c0) | gates(0)

            # Global phase
            if self.keep_phase:
                gates.append(GPhase(theta[0]) & 0)

            return gates

        T, ell = self.construct_T(r_t)
        F = self.disjoint_families_F(r_c, r_t)

        # Implement the G_k, k = 1,...,ell
        # All operations are implemented one target bit at a loop
        for i in range(r_t):
            for k in range(ell):
                # Stage 1
                st = T[k][i]
                cnot_s1 = CompositeGate()
                for j in range(r_t):
                    if st[j] == '1' and i != j:
                        CX & [r_c + j, r_c + i] | cnot_s1

                if cnot_s1.size() != 0 and self.opt:
                    cnot_s1 = self._cnot_optimizer.execute(cnot_s1).to_compositegate()
                cnot_s1 | gates

                # Stage 2: Gray Path Stage
                # Phase 1
                s = '0' * r_c + T[k][i]
                if s in F[k]:
                    if len(s) < nmax:
                        s = s + '0' * (nmax - len(s))
                    s_int = int(s, 2)

                    if self.count_no_aux[s_int] == 0:
                        self.count_no_aux[s_int] += 1
                        phase_c1 = self.alpha_s(theta, s_int, nmax)
                        U1(phase_c1) | gates(r_c + i)

                # Phase p
                for p in range(1, 1 << r_c):
                    # Step p.1
                    # give the c^(i) gray code cycle
                    c = self.lucal_gray_code(i, r_c)
                    cnot_p1 = CompositeGate()
                    for index in range(r_c):
                        if c[p - 1][index] != c[p][index]:
                            CX & [index, i + r_c] | cnot_p1
                            break

                    if cnot_p1.size() != 0 and self.opt:
                        cnot_p1 = self._cnot_optimizer.execute(cnot_p1).to_compositegate()
                    cnot_p1 | gates

                    # Step p.2
                    sp = c[p] + T[k][i]
                    if sp in F[k]:
                        if len(sp) < nmax:
                            sp = sp + '0' * (nmax - len(sp))
                        sp_int = int(sp, 2)

                        if self.count_no_aux[sp_int] == 0:
                            self.count_no_aux[sp_int] += 1
                            phase_cp = self.alpha_s(theta, sp_int, nmax)
                            U1(phase_cp) | gates(r_c + i)

                # Phase 2^r_c + 1
                cnot_rc = CompositeGate()
                for index in range(r_c):
                    if c[0][index] != c[2 ** r_c - 1][index]:
                        CX & [index, i + r_c] | cnot_rc
                        break

                if cnot_rc.size() != 0 and self.opt:
                    cnot_rc = self._cnot_optimizer.execute(cnot_rc).to_compositegate()
                cnot_rc | gates

                cnot_la = CompositeGate()
                st = T[k][i]
                for j in range(r_t - 1, -1, -1):
                    if st[j] == '1' and i != j:
                        CX & [r_c + j, r_c + i] | cnot_la

                if cnot_la.size() != 0 and self.opt:
                    cnot_la = self._cnot_optimizer.execute(cnot_la).to_compositegate()
                cnot_la | gates

        # implement the r_c-qubit diagonal unitary matrix recursively.
        self.no_aux_qubit(r_c, theta) | gates

        return gates

    def with_aux_qubit(self, theta: List[float]) -> CompositeGate:
        """
        Args:
            theta (List[float]): list of (2 ** target) angles of rotation in the diagonal gate

        Returns:
            CompositeGate: diagonal gate with auxiliary qubit at the end of qubits
        """
        # Pay attention:All arrays and qubit is 0 as the starting point,
        # but begins with 1 in the paper.
        n = self.target
        m = self.aux
        gates = CompositeGate()

        # Stage 1: Prefix Copy
        t = int(np.floor(np.log2(m / 2)))
        copies = int(np.floor(m / (2 * t)))
        # the round of the copy process
        r = int(np.floor(np.log2(copies + 1)))

        # define a cnot gate set
        cnot_s1 = CompositeGate()

        # Consider the parallelism of the copy process.
        for i in range(1, r + 1):
            for j in range(t):
                CX & [j, n + (2 ** (i - 1) - 1) * t + j] | cnot_s1
            for j in range((2 ** (i - 1) - 1) * t):
                CX & [n + j, n + j + (2 ** (i - 1)) * t] | cnot_s1
        if 2 ** r - 1 < copies:
            rest = copies - 2 ** r + 1
            for j in range(t):
                CX & [j, n + (2 ** r - 1) * t + j] | cnot_s1
            if rest != 1:
                for j in range((rest - 1) * t):
                    CX & [n + j, n + (2 ** r) * t + j] | cnot_s1

        # Stage 2: Gray Initial
        ell = 2 ** t
        ini_star = n + int(m / 2)
        # To ensure parallelism, the group number of the control bit is given.
        visit1 = [0 for _ in range(n)]
        s = self.partitioned_gray_code(n, t)
        # 1.implement U1
        for j in range(1, 1 + ell):
            st = s[j - 1][0]
            for i in range(len(st)):
                if st[i] == '1':
                    CX & [n + t * (visit1[i] % copies) + i, ini_star + j - 1] | cnot_s1
                    visit1[i] += 1

        # We use the optimization for cnot gates

        if cnot_s1.size() != 0 and self.opt:
            cnot_s1 = self._cnot_optimizer.execute(cnot_s1).to_compositegate()
        cnot_s1 | gates

        # 2.implement R1
        for j in range(1, 1 + ell):
            sj1_int = int(s[j - 1][0], 2)
            phase = self.alpha_s(theta, sj1_int, n)
            U1(phase) | gates(ini_star + j - 1)

        # Stage 3:Suffix Copy
        cnot_s3 = CompositeGate()
        # 1.U^{\dagger}_{copy,1}
        if 2 ** r - 1 < copies:
            rest = copies - 2 ** r + 1
            if rest != 1:
                for j in range((rest - 1) * t - 1, -1, -1):
                    CX & [n + j, n + (2 ** r) * t + j] | cnot_s3

            for j in range(t - 1, -1, -1):
                CX & [j, n + (2 ** r - 1) * t + j] | cnot_s3

        for i in range(r, 0, -1):
            for j in range((2 ** (i - 1) - 1) * t - 1, -1, -1):
                CX & [n + j, n + j + (2 ** (i - 1)) * t] | cnot_s3

            for j in range(t - 1, -1, -1):
                CX & [j, n + (2 ** (i - 1) - 1) * t + j] | cnot_s3

        # 2.U_{copy,2}
        copies3 = int(np.floor(m / (2 * (n - t))))
        r3 = int(np.floor(np.log2(copies3 + 1)))
        for i in range(1, r3 + 1):
            for j in range(t, n):
                CX & [j, n + (2 ** (i - 1) - 1) * (n - t) + j - t] | cnot_s3
            for j in range((2 ** (i - 1) - 1) * (n - t)):
                CX & [n + j, n + j + (2 ** (i - 1)) * (n - t)] | cnot_s3
        if 2 ** r3 - 1 < copies3:
            rest = copies3 - 2 ** r3 + 1
            for j in range(t, n):
                CX & [j, n + (2 ** r3 - 1) * (n - t) + j - t] | cnot_s3
            if rest != 1:
                for j in range((rest - 1) * (n - t)):
                    CX & [n + j, n + (2 ** r3) * (n - t) + j] | cnot_s3

        # Optimization for cnot gates
        if cnot_s3.size() != 0 and self.opt:
            cnot_s3 = self._cnot_optimizer.execute(cnot_s3).to_compositegate()
        cnot_s3 | gates

        # Stage 4: Gray Path
        num_phases = int((2 ** n) / ell)
        path_star = n + int(m / 2)
        for k in range(2, num_phases + 1):
            visit2 = [0 for _ in range(n)]
            # Step k.1: U_k
            for j in range(1, ell + 1):
                s = self.partitioned_gray_code(n, t)
                s1 = s[j - 1][k - 2]
                s2 = s[j - 1][k - 1]

                for i in range(len(s1)):
                    if s1[i] != s2[i]:
                        CX & [n + i - t + (n - t) * (visit2[i] % copies3), path_star + j - 1] | gates
                        visit2[i] += 1

            # Step k.2: R_k
            for j in range(1, ell + 1):
                s = self.partitioned_gray_code(n, t)
                sjk_int = int(s[j - 1][k - 1], 2)
                phase_k = self.alpha_s(theta, sjk_int, n)
                U1(phase_k) | gates(j - 1 + path_star)

        # Stage 5:Inverse
        cnot_s5 = CompositeGate()
        # clear the CNOT gates in Stage 4:Gray Path Stage k.1 U1
        visit3 = [0 for _ in range(n)]
        for j in range(1, ell + 1):
            s = self.partitioned_gray_code(n, t)
            s2 = s[j - 1][num_phases - 1]

            for i in range(len(s2)):
                if s2[i] != '0':
                    if i >= t:
                        copies3 = int(np.floor(m / (2 * (n - t))))
                        CX & [n + i - t + (n - t) * (visit3[i] % copies3), path_star + j - 1] | cnot_s5
                        visit3[i] += 1

        # clear the copy process in Stage 3
        # (Write the copy process in reverse order)
        if 2 ** r3 - 1 < copies3:
            rest = copies3 - 2 ** r3 + 1
            if rest != 1:
                for j in range((rest - 1) * (n - t) - 1, -1, -1):
                    CX & [n + j, n + (2 ** r3) * (n - t) + j] | cnot_s5
            for j in range(n - 1, t - 1, -1):
                CX & [j, n + (2 ** r3 - 1) * (n - t) + j - t] | cnot_s5
        for i in range(r3, 0, -1):
            for j in range((2 ** (i - 1) - 1) * (n - t) - 1, -1, -1):
                CX & [n + j, n + j + (2 ** (i - 1)) * (n - t)] | cnot_s5
            for j in range(n - 1, t - 1, -1):
                CX & [j, n + (2 ** (i - 1) - 1) * (n - t) + j - t] | cnot_s5

        # clear the Stage 1:copy prefix
        t = int(np.floor(np.log2(m / 2)))
        copies = int(np.floor(m / (2 * t)))
        r = int(np.floor(np.log2(copies + 1)))
        for i in range(1, r + 1):
            for j in range(t):
                CX & [j, n + (2 ** (i - 1) - 1) * t + j] | cnot_s5
            for j in range((2 ** (i - 1) - 1) * t):
                CX & [n + j, n + j + (2 ** (i - 1)) * t] | cnot_s5
        if 2 ** r - 1 < copies:
            rest = copies - 2 ** r + 1
            for j in range(t):
                CX & [j, n + (2 ** r - 1) * t + j] | cnot_s5
            if rest != 1:
                for j in range((rest - 1) * t):
                    CX & [n + j, n + (2 ** r) * t + j] | cnot_s5

        # clear the Stage 2:U1
        visit4 = [0 for _ in range(n)]
        s = self.partitioned_gray_code(n, t)
        for j in range(1, 1 + ell):
            st = s[j - 1][0]
            for i in range(len(st)):
                if st[i] == '1':
                    CX & [n + t * (visit4[i] % copies) + i, ini_star + j - 1] | cnot_s5
                    visit4[i] += 1

        # clear the Stage 1:prefix copy
        # (Write the copy process in reverse order)
        if 2 ** r - 1 < copies:
            rest = copies - 2 ** r + 1
            if rest != 1:
                for j in range((rest - 1) * t - 1, -1, -1):
                    CX & [n + j, n + (2 ** r) * t + j] | cnot_s5
            for j in range(t - 1, -1, -1):
                CX & [j, n + (2 ** r - 1) * t + j] | cnot_s5
        for i in range(r, 0, -1):
            for j in range((2 ** (i - 1) - 1) * t - 1, -1, -1):
                CX & [n + j, n + j + (2 ** (i - 1)) * t] | cnot_s5

            for j in range(t - 1, -1, -1):
                CX & [j, n + (2 ** (i - 1) - 1) * t + j] | cnot_s5

        # Optimization for cnot gates
        if cnot_s5.size() != 0 and self.opt:
            cnot_s5 = self._cnot_optimizer.execute(cnot_s5).to_compositegate()
        cnot_s5 | gates

        # Global phase
        if self.keep_phase:
            gates.append(GPhase(theta[0]) & 0)
        return gates

    @staticmethod
    def lucal_gray_code(k: int, n: int) -> List[str]:
        """
        Generate the (k, n)-Gray code defined in and following Lemma 7

        Args:
            k (int): start the circular modification from the k-th binary code
            n (int): the length of binary code, that is, the length of Gray code would be 2^n

        Returns:
            List[str]: the (k, n)-Gray code
        """
        def flip(bit):
            if bit == '1':
                return '0'
            if bit == '0':
                return '1'
            raise ValueError('Invalid bit found in gray code generation.')

        def zeta(x):
            """
            For integer x, zeta(x) = max{k: 2^k | x}
            """
            x_bin = np.binary_repr(x)
            return len(x_bin) - len(x_bin.strip('0'))

        gray_code = ['0' for _ in range(n)]
        result = [''.join(gray_code)]
        for i in range(1, 1 << n):
            bit = np.mod(zeta(i) + k, n)
            gray_code[bit] = flip(gray_code[bit])
            result.append(''.join(gray_code))

        return result

    @classmethod
    def partitioned_gray_code(cls, n: int, t: int) -> List[List[str]]:
        """
        Lemma 15 by the construction in Appendix E

        Args:
            n (int): length of 0-1 string to be partitioned
            t (int): length of the shared prefix of each row

        Returns:
            List[List[str]]: partitioned gray code
        """
        s = [[] for _ in range(1 << t)]
        for j in range(1 << t):
            prefix = np.binary_repr(j, width=t)[::-1]
            for suffix in cls.lucal_gray_code(np.mod(j, n - t), n - t):
                s[j].append(prefix + suffix)
        return s

    @staticmethod
    def binary_inner_prod(s: int, x: int, width: int) -> int:
        """
        Calculate the binary inner product of s_bin and x_bin, where s_bin and x_bin
        are binary representation of s and x respectively of width n

        Args:
            s (int): s in <s, x>
            x (int): x in <s, x>
            width (int): the width of s_bin and x_bin

        Returns:
            int: the binary inner product of s and x
        """
        s_bin = np.array(list(np.binary_repr(s, width=width)), dtype=int)
        x_bin = np.array(list(np.binary_repr(x, width=width)), dtype=int)
        return np.mod(np.dot(s_bin, x_bin), 2)

    @classmethod
    def alpha_s(cls, theta: List[float], s: int, n: int) -> float:
        r"""
        Solve Equation 6
        $\sum_s \alpha_s <s, x> = \theta(x)$

        Args:
            theta (List[float]): phase angles of the diagonal gate
            s (int): key of the solution component
            n (int): number of qubits in the diagonal gate

        Returns:
            float: $\alpha_s$ in Equation 6
        """
        A = np.zeros(1 << n)
        for x in range(1, 1 << n):
            A[x] = cls.binary_inner_prod(s, x, width=n)
        # A_inv = 2^(1-n) (2A - J)
        # A_inv = (2 * A[1:] - 1) / (1 << (n - 1))
        # As size should be matched, we change the code
        A_inv = (2 * A - 1) / (1 << (n - 1))
        return np.dot(A_inv, theta)

    @classmethod
    def phase_shift(cls, theta: List[float], seq: Iterable = None, aux: int = None) -> CompositeGate:
        r"""
        Implement the phase shift
        $|x\rangle -> \exp(i \theta(x)) |x\rangle$
        by solving Equation 6
        $\sum_s \alpha_s <s, x> = \theta(x)$

        Args:
            theta (List[float]): phase angles of the diagonal gate
            seq (Iterable, optional): sequence of s application, numerical order if not assigned
            aux (int, optional): key of auxiliary qubit (if exists)

        Returns:
            CompositeGate: CompositeGate of the diagonal gate
        """
        n = int(np.floor(np.log2(len(theta))))
        if seq is None:
            seq = range(1, 1 << n)
        else:
            assert sorted(list(seq)) == list(range(1, 1 << n)),\
                ValueError('Invalid sequence of s in phase_shift')
        if aux is not None:
            assert aux >= n, \
                ValueError('Invalid auxiliary qubit in phase_shift.')
        # theta(0) = 0
        global_phase = theta[0]
        theta = theta - global_phase

        gates = CompositeGate()
        GPhase(global_phase) & 0 | gates
        # Calculate A_inv row by row (i.e., for different s)
        for s in seq:
            alpha = cls.alpha_s(theta, s, n)
            if aux is not None:
                gates.extend(cls.phase_shift_s(s, n, alpha, aux=aux))
            else:
                gates.extend(cls.phase_shift_s(s, n, alpha, j=0))
        return gates

    @classmethod
    def phase_shift_s(cls, s: int, n: int, alpha: float, aux: int = None, j: int = None) -> CompositeGate:
        r"""
        Implement the phase shift for a certain s defined in Equation 5 as Figure 8
        $|x\rangle -> \exp(i \alpha_s <s, x>) |x\rangle$

        Args:
            s (int): whose binary representation stands for the 0-1 string s
            n (int): the number of qubits in $|x\rangle$
            alpha (float): $\alpha_s$ in the equation
            aux (int, optional): key of auxiliary qubit (if exists)
            j (int, optional): if no auxiliary qubit, the j-th smallest element in s_idx would be the target qubit

        Returns:
            CompositeGate: CompositeGate for Equation 5 as Figure 8
        """
        gates = CompositeGate()
        s_bin = np.binary_repr(s, width=n)
        s_idx = []
        for i in range(n):
            if s_bin[i] == '1':
                s_idx.append(i)

        # Figure 8 (a)
        if aux is not None:
            if j is not None:
                cls._logger.warn('With auxiliary qubit in phase_shift_s, no i_j is needed.')
            assert aux >= n, ValueError('Invalid auxiliary qubit in phase_shift_s.')
            for i in s_idx:
                CX & [i, aux] | gates
            U1(alpha) & aux | gates
            for i in reversed(s_idx):
                CX & [i, aux] | gates
            return gates

        # Figure 8 (b)
        else:
            assert j < len(s_idx), ValueError('Invalid target in phase_shift without auxiliary qubit.')
            for i in s_idx:
                if i == s_idx[j]:
                    continue
                CX & [i, s_idx[j]] | gates
            U1(alpha) & s_idx[j] | gates
            for i in s_idx:
                if i == s_idx[j]:
                    continue
                CX & [i, s_idx[j]] | gates
            return gates

    @classmethod
    def linear_fjk(cls, j: int, k: int, x: int, n: int, t: int) -> int:
        r"""
        Implement the linear functions $f_{jk}(x) = <s(j, k), x>$

        Args:
            j (int): j is the label of n-bit strings s(j, k)
            k (int): k is the label of n-bit strings s(j, k)
            n (int): length of 0-1 string to be partitioned
            t (int): length of the shared prefix of each row
            x (int): the independent variables of the function $f_{jk}$

        Returns:
            int: $f_{jk}(x)$
        """
        s = cls.partitioned_gray_code(n, t)
        decimal_integer = int(s[j - 1][k - 1], 2)
        # Convert the binary string s[j - 1][k - 1] to an integer
        return cls.binary_inner_prod(decimal_integer, x, width=n)

    @classmethod
    def ket_fjk(cls, j: int, k: int, n: int, t: int, target_num: int) -> CompositeGate:
        r"""
        Implement the part of unitary U1 for every j:
        $|0\rangle -> |<s(j, k), x>\rangle$ by adding the CNOT gates

        Args:
            j (int): j is the label of n-bit strings s(j,k)
            k (int): k is the label of n-bit strings s(j,k)
            n (int): length of 0-1 string to be partitioned
            t (int): length of the shared prefix of each row
            target_num (int): the target label connecting the CNOT gate

        Returns:
            CompositeGate: $|0\rangle -> |<s(j, k), x>\rangle$
        """
        s = cls.partitioned_gray_code(n, t)
        st = s[j - 1][k - 1]

        gates = CompositeGate()
        for i in range(len(st)):
            if st[i] == '1':
                CX & [i, target_num] | gates
        return gates

    @classmethod
    def binary_addition(cls, binary_string1: str, binary_string2: str, n: int) -> str:
        r"""
        Implement the function:
        $x \otimes y = (x1 \otimes y1, x2 \otimes y2, · · · , xn \otimes yn)^T$

        Args:
            binary_string1 (str): binary string like x
            binary_string2 (str): binary string like y
            n (int): the length of the binary strings

        return:
            str: a string with bitwise binary addition
        """
        result = ''
        for i in range(n):
            bit1 = int(binary_string1[i])
            bit2 = int(binary_string2[i])
            sum_bits = (bit1 + bit2) % 2
            result += str(sum_bits)
        return result

    @classmethod
    def int_to_binary(cls, num: int, n: int) -> str:
        """
        Args:
            num (int): the number from 0 to 2^n-1
            n (int): the length of the binary strings

        return:
            str: numeric num converted binary string
        """
        binary_str = bin(num)[2:]  # convert to binary without the '0b' prefix
        if len(binary_str) < n:
            binary_str = '0' * (n - len(binary_str)) + binary_str
        elif len(binary_str) > n:
            raise ValueError("Integer is not within the valid range.")
        return binary_str

    @classmethod
    def S_x(cls, x: int, n: int) -> str:
        r"""
        Implement the Appendix H, also the construction of sets $S_x$.

        Args:
            x (int): the number from $0$ to $2^n-1$
            n (int): the length of these binary strings

        return:
            str: an array $S_x = [x \otimes e_1,x \otimes e_2,...,x \otimes e_n]$
        """
        sx = [cls.int_to_binary(x, n)] * n
        for i in range(n):
            en = cls.int_to_binary(1 << (n - i - 1), n)
            sx[i] = cls.binary_addition(sx[i], en, n)

        return sx

    @classmethod
    def Hx(cls, x, H, n):
        binary_x = cls.int_to_binary(x, n)
        binary_x_array = np.array([int(digit) for digit in binary_x])
        H_matrix = np.array([list(map(int, list(item))) for item in H])
        result = np.dot(binary_x_array, H_matrix) % 2
        return ''.join(map(str, result))

    @classmethod
    def linearly_independent_sets_T(cls, n: int) -> Tuple[List[List[str]], int]:
        """
        Implement the Appendix H, also the construction of sets T.

        Args:
            n (int): the size of each sublist T^(i),i = 1,2,...,ell

        return:
            Tuple[List[List[str]], int]: 2-dimension n-bit string array,
                also the linear independent set T with ell rows and n columns and the number of T, ell.
        """
        if n == 1:
            return [['1', '0']], 1

        k = int(np.ceil(np.log2(n + 1)))
        H = []
        for i in range(1, n + 1):
            st_k = cls.int_to_binary(i, k)
            st_k = st_k[::-1]
            H.append(st_k)

        L = []

        zero_k = '0' * k
        one_k = '1' * k

        # count the number of the sets T
        ell = 0

        # construct the set L except 0^n.
        for x in range(1, 1 << n):
            if cls.Hx(x, H, n) == zero_k:
                L.append(cls.int_to_binary(x, n))
                ell += 1
            if cls.Hx(x, H, n) == one_k:
                L.append(cls.int_to_binary(x, n))
                ell += 1

        # ell has already equals to the size of set L
        ell = 2 * ell + 1

        # Next we construct the set T
        T = [[]]
        T[0] = cls.S_x(0, n)

        for x in L:
            T_x0 = cls.S_x(int(x, 2), n)
            T_x1 = T_x0.copy()

            if x.count('1') == 1 and '1' in x:
                i = int(np.log2(int(x, 2)))

                T_x0.pop(n - i - 1)
                T_x1.pop(n - i - 1)
                T_x1.append(x)

                if (n - i - 1) != 0:
                    T_x0.append('1' + '0' * (n - 1))
                else:
                    if n > 1:
                        T_x0.append('01' + '0' * (n - 2))
                    if n == 1:
                        T_x0.append('1')

            else:
                for i in range(len(T_x1)):
                    if x.count('1') >= T_x1[i].count('1'):
                        T_x1[i] = x
                        break

            sorted_T_x0 = sorted(T_x0, key=lambda x: int(x, 2), reverse=True)
            sorted_T_x1 = sorted(T_x1, key=lambda x: int(x, 2), reverse=True)

            T.append(sorted_T_x0)
            T.append(sorted_T_x1)

        return T, ell

    @classmethod
    def inverse_T(cls, T, ell, n):
        if n == 1:
            T_inv = T
            return T_inv
        T_inv = [[] for _ in range(ell)]
        for k in range(ell):
            T_matrix = np.array([list(map(int, list(item))) for item in T[k]])
            T_inv[k] = np.linalg.inv(T_matrix).astype(int) % 2
            T_inv[k] = [''.join(str(i) for i in row) for row in T_inv[k]]
        return T_inv

    @classmethod
    def disjoint_families_F(cls, r_c: int, r_t: int) -> List[Set[str]]:
        """
        Implement the Eq(15),disjoint families F_1,...,F_ell

        Args:
            r_c (int): size of the prefixes c
            r_t (int): size of the suffix t

        Returns:
            List[Set[str]]: 2-dimension (r_c + r_t)-bit string array, also the linear independent set F
                with ell rows and not fixed columns
        """
        T, ell = cls.construct_T(r_t)

        F = [set() for _ in range(ell)]

        cset = []
        for i in range(1 << r_c):
            cset.append(cls.int_to_binary(i, r_c))

        # avoid the repeating strings in F_d
        intersection_t = set()

        # implement F_k, 1<= k<= ell
        for k in range(ell):
            for i in range(len(T[k])):
                if T[k][i] not in intersection_t:
                    for c in cset:
                        if int(c + T[k][i], 2) != 0:
                            F[k].add(c + T[k][i])
                            intersection_t.add(T[k][i])

        return F

    @classmethod
    def construct_T(cls, n: int) -> Tuple[List[List[str]], int]:
        """
        Realize the construction of a two-dimensional string array T,
        each row of the array constitutes a matrix with diagonal elements of 1.

        Args:
            n (int): size of the prefixes c

        Returns:
            Tuple[List[List[str]], int]: 2-dimension T string array, with the number of rows: ell
        """
        # Initialize the two-dimensional array T
        T = [['0'] * n]

        # Generate 2**n-1 binary strings
        binary_strings = [format(i, f'0{n}b') for i in range(2 ** n - 1, 0, -1)]

        # Fill the 2D array T sequentially
        for st in binary_strings:
            # Iterate over each row
            ltnow = len(T)
            for i in range(ltnow):
                # Iterate over each column
                for j in range(n):
                    # If the current position is empty and meets the requirements
                    if T[i][j] == '0' and st[j] == '1':
                        # fill the current position
                        T[i][j] = st
                        break

                    if i == ltnow - 1 and j == n - 1 and st[j] == '0':
                        # If none of the lines fit, a new line is needed
                        T.append(['0'] * n)

                        for k in range(n):
                            if st[k] == '1':
                                T[ltnow][k] = st
                                break
                        break

        ell = len(T)
        for i in range(ell):
            for j in range(n):
                if T[i][j] == '0':
                    T[i][j] = '0' * j + '1' + '0' * (n - j - 1)

        return T, ell
