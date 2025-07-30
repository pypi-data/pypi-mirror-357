"""
Decomposition of SU(4) with Cartan KAK Decomposition
"""

from typing import Tuple

import numpy as np

from QuICT.core.gate import CompositeGate, CX, Ry, Rz, Unitary, Rxx, Ryy, Rzz


class CartanKAKDecomposition(object):
    r"""Cartan KAK Decomposition in $SU(4)$

    $\forall U \in SU(4)$, $\exists KL_0, KL_1, KR_0, KR_1 \in SU(2)$ and $a, b, c \in \mathbb{R}$, s.t.
    $U = (KL_0 \otimes KL_1) \exp(i(a XX + b YY + c ZZ)) (KR_0 \otimes KR_1)$

    Proof of this proposition in general cases is too 'mathematical'. [2] gives a proof for $U(4)$.
    Be aware that [2] uses a different notation.

    The process of this part is taken from [1], while some notations are from [3].

    References:
        [1] `Constructive Quantum Shannon Decomposition from Cartan Involutions`
        <https://arxiv.org/abs/0806.4015>

        [2] `An Introduction to Cartan's KAK Decomposition for QC Programmers`
        <https://arxiv.org/abs/quant-ph/0507171>

        [3] `Optimal Quantum Circuits for General Two-Qubit Gates`
        <https://arxiv.org/abs/quant-ph/0308006>
    """
    # Magic basis
    magic_basis = (1.0 / np.sqrt(2)) * np.array(
        [[1, 1j, 0, 0],
         [0, 0, 1j, 1],
         [0, 0, 1j, -1],
         [1, -1j, 0, 0]], dtype=complex
    )

    def __init__(self, target: str = 'cx', eps: float = 1e-15):
        r"""
        Args:
            target (str, optional): how the core part $\exp(i(a XX + b YY + c ZZ))$ would be decomposed,
                which could be chosen from `'cx'` (by default) and `'rot'` (rxx, ryy, rzz)
            eps (float, optional): eps of decomposition process
        """
        assert target in ['cx', 'rot'], ValueError('Invalid target gate type')
        self.target = target
        self.eps = eps

    @staticmethod
    def diagonalize_unitary_symmetric(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Diagonalize unitary symmetric matrix with real orthogonal matrix

        Args:
            matrix (np.ndarray): unitary symmetric matrix to be diagonalized

        Returns:
            Tuple[np.ndarray, np.ndarray]: Eigenvalues and eigenvectors
        """
        M2 = matrix.copy()
        # D, P = la.eig(M2)  # this can fail for certain kinds of degeneracy
        for i in range(100):  # FIXME: this randomized algorithm is horrendous
            state = np.random.default_rng(i)
            M2real = state.normal() * M2.real + state.normal() * M2.imag
            _, P = np.linalg.eigh(M2real)
            D = np.diagonal(P.T.dot(M2).dot(P))
            if np.allclose(P.dot(np.diag(D)).dot(P.T), M2, rtol=1.0e-6, atol=1.0e-6):
                break
        else:
            raise ValueError("CartanKAKDecomposition: failed to diagonalize M2")
        return D, P

    @staticmethod
    def tensor_decompose(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Decompose $U \in SU(2) \otimes SU(2)$ to $U_0, U_1 \in SU(2)$, s.t. $U = U_0 \otimes U_1$

        Args:
            matrix (np.ndarray): Matrix to be decomposed

        Returns:
            Tuple[np.ndarray, np.ndarray]: Decomposed result $U_0, U_1$
        """
        U = matrix.copy()
        # Decompose U1
        U1 = U[:2, :2].copy()
        # There is chance that U0[0, 0] == 0 (or more explicitly, is close to 0)
        if np.abs(np.linalg.det(U1)) < 0.1:
            U1 = U[2:, :2].copy()
        # If U0[0, 0], U0[1, 0] are both close to 0, U0 would not be unitary.
        if np.abs(np.linalg.det(U1)) < 0.1:
            raise ValueError("tensor_decompose: U1 failed")
        U1 /= np.sqrt(np.linalg.det(U1))

        # Decompose U0
        U1_inv = np.kron(np.eye(2), U1.T.conj())
        U0_tensor = U1_inv.dot(U)
        U0 = U0_tensor[::2, ::2]
        if np.abs(np.linalg.det(U0)) < 0.9:
            raise ValueError("tensor_decompose: U0 failed")
        U0 /= np.sqrt(np.linalg.det(U0))

        # Final test
        res = np.kron(U0, U1)
        dev = np.abs(np.abs(res.conj(res).T.dot(U).trace()) - 4)
        assert dev < 1e-6, ValueError("tensor_decompose: Final failed")
        return U0, U1

    def execute(self, matrix: np.ndarray) -> CompositeGate:
        r"""
        Decompose a matrix $U \in SU(4)$ with Cartan KAK Decomposition to
        a circuit, which contains only 1-qubit gates and CNOT gates.
        The decomposition of $\exp(i(a XX + b YY + c ZZ))$ may vary a global phase.

        Args:
            matrix (np.ndarray): 4*4 unitary matrix to be decomposed

        Returns:
            CompositeGate: Decomposed gates.
        """
        assert matrix.shape == (4, 4), \
            ValueError("CartanKAKDecomposition: Input must be a 4*4 matrix.")
        assert np.allclose(matrix.T.conj().dot(matrix), np.eye(4), rtol=1e-6, atol=1e-6), \
            ValueError("CartanKAKDecomposition: Input must be a unitary matrix.")

        U = matrix.copy()
        U /= np.linalg.det(U) ** (0.25)
        eps = self.eps

        # Some preparation derived from Cartan involution
        Up = self.magic_basis.T.conj().dot(U).dot(self.magic_basis)
        M2 = Up.T.dot(Up)
        M2.real[abs(M2.real) < eps] = 0.0
        M2.imag[abs(M2.imag) < eps] = 0.0

        # Since M2 is a symmetric unitary matrix, we can diagonalize its real and
        # imaginary part simultaneously. That is, ∃ P in SO(4), s.t. M2 = P.D.P^T,
        # where D is diagonal with unit-magnitude elements.
        D, P = self.diagonalize_unitary_symmetric(M2)

        # Calculated D is usually in U(4) instead of SU(4), therefore d[3] is reset
        # so that D is now in SU(4)
        d = np.angle(D) / 2
        d[3] = -d[0] - d[1] - d[2]
        a = (d[0] + d[2]) / 2
        b = (d[1] + d[2]) / 2
        c = (d[0] + d[1]) / 2

        # Similarly, P could be in O(4) instead of SO(4).
        if np.linalg.det(P) < 0:
            P[:, -1] = -P[:, -1]

        # Now is the time to calculate KL and KR
        KL = self.magic_basis.dot(Up).dot(P).dot(np.diag(np.exp(-1j * d))).dot(self.magic_basis.T.conj())
        KR = self.magic_basis.dot(P.T).dot(self.magic_basis.T.conj())
        KL.real[abs(KL.real) < eps] = 0.0
        KL.imag[abs(KL.imag) < eps] = 0.0
        KR.real[abs(KR.real) < eps] = 0.0
        KR.imag[abs(KR.imag) < eps] = 0.0
        KL0, KL1 = self.tensor_decompose(KL)
        KR0, KR1 = self.tensor_decompose(KR)

        # Finally we could combine everything together
        if self.target == 'cx':
            KL0 = KL0.dot(Rz(-np.pi / 2).matrix)
            KR1 = Rz(np.pi / 2).matrix.dot(KR1)
            gates = CompositeGate()
            Unitary(KR0) & 0 | gates
            Unitary(KR1) & 1 | gates
            CX & [1, 0] | gates
            Rz(np.pi / 2 - 2 * c) & 0 | gates
            Ry(np.pi / 2 - 2 * a) & 1 | gates
            CX & [0, 1] | gates
            Ry(2 * b - np.pi / 2) & 1 | gates
            CX & [1, 0] | gates
            Unitary(KL0) & 0 | gates
            Unitary(KL1) & 1 | gates
        elif self.target == 'rot':
            gates = CompositeGate()
            Unitary(KR0) & 0 | gates
            Unitary(KR1) & 1 | gates
            Rxx(-2 * a) & [0, 1] | gates
            Ryy(-2 * b) & [0, 1] | gates
            Rzz(-2 * c) & [0, 1] | gates
            Unitary(KL0) & 0 | gates
            Unitary(KL1) & 1 | gates
        else:
            raise ValueError('Invalid target gate type')

        return gates
