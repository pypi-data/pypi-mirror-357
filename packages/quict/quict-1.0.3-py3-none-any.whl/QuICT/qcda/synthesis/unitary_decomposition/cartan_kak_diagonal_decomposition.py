"""
Another version of decomposition of SU(4) with Cartan KAK Decomposition,
which is specially designed for the optimization of unitary transform.
"""

import numpy as np

from QuICT.core.gate import CompositeGate, CX, Rx, Rz, Unitary, Rxx, Rzz
from .cartan_kak_decomposition import CartanKAKDecomposition


class CartanKAKDiagonalDecomposition(object):
    r"""
    Decompose a matrix $U \in SU(4)$ with Cartan KAK Decomposition. Unlike the
    original version, now the result circuit has a two-qubit gate whose
    matrix is diagonal at the edge, which is useful in the optimization.
    The process is taken from [2] Proposition V.2 and Theorem VI.3,
    while the Cartan KAK Decomposition process is refined from [1].

    Reference:
        [1] `Constructive Quantum Shannon Decomposition from Cartan Involutions`
        <https://arxiv.org/abs/0806.4015>

        [2] `Optimal Quantum Circuits for General Two-Qubit Gates`
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
            eps (float, optional): Eps of decomposition process
        """
        assert target in ['cx', 'rot'], ValueError('Invalid target gate type')
        self.target = target
        self.eps = eps

    def execute(self, matrix: np.ndarray) -> CompositeGate:
        r"""
        Decompose a matrix $U \in SU(4)$ with Cartan KAK Diagonal Decomposition.

        Args:
            matrix (np.ndarray): 4*4 unitary matrix to be decomposed

        Returns:
            CompositeGate: Decomposed gates.
        """
        sy2 = np.array([[0, 0, 0, -1],
                        [0, 0, 1, 0],
                        [0, 1, 0, 0],
                        [-1, 0, 0, 0]], dtype=complex)

        # Proposition V.2
        U = matrix.copy()
        U /= np.linalg.det(U) ** 0.25
        gUTT = U.T.dot(sy2).dot(U).dot(sy2).T
        denominator = (gUTT[0, 0] - gUTT[1, 1] - gUTT[2, 2] + gUTT[3, 3]).real
        if np.isclose(denominator, 0):
            psi = np.pi / 2
        else:
            numerator = (gUTT[0, 0] + gUTT[1, 1] + gUTT[2, 2] + gUTT[3, 3]).imag
            psi = np.arctan(numerator / denominator)

        gates_Delta = CompositeGate()
        with gates_Delta:
            CX & [0, 1]
            Rz(psi) & 1
            CX & [0, 1]
        Delta = gates_Delta.matrix()
        U = U.dot(Delta)

        # Refined Cartan KAK Decomposition for U (because we have known Ud here!)
        # Some preparation derived from Cartan involution
        Up = self.magic_basis.T.conj().dot(U).dot(self.magic_basis)
        M2 = Up.T.dot(Up)
        M2.real[abs(M2.real) < self.eps] = 0.0
        M2.imag[abs(M2.imag) < self.eps] = 0.0

        # Since M2 is a symmetric unitary matrix, we can diagonalize its real and
        # imaginary part simultaneously. That is, ∃ P in SO(4), s.t. M2 = P.D.P^T,
        # where D is diagonal with unit-magnitude elements.
        D, P = CartanKAKDecomposition.diagonalize_unitary_symmetric(M2)
        d = np.angle(D) / 2

        # A special case occurs when there are pairs of -1 in D
        if np.any(np.isclose(D, -1)):
            if np.count_nonzero(np.isclose(D, -1)) == 2:
                d[np.where(np.isclose(D, -1))] = np.pi / 2, -np.pi / 2
            elif np.count_nonzero(np.isclose(D, -1)) == 4:
                d[:] = np.pi / 2, np.pi / 2, -np.pi / 2, -np.pi / 2
            else:
                raise ValueError('Odd number of -1 in D')

        # Refinement time, by some mathematics we know that d here must be a rearragement
        # of d_Ud. However, the diagonalization process does not guarantee that they are
        # correctly sorted.
        order = np.argsort(d)[::-1]
        d[:] = d[order]
        P[:, :] = P[:, order]
        a = (d[0] + d[2]) / 2
        b = (d[1] + d[2]) / 2
        c = (d[0] + d[1]) / 2
        assert np.isclose(b, 0)

        # P could be in O(4) instead of SO(4).
        if np.linalg.det(P) < 0:
            P[:, -1] = -P[:, -1]

        # Now is the time to calculate KL and KR
        KL = self.magic_basis.dot(Up).dot(P).dot(np.diag(np.exp(-1j * d))).dot(self.magic_basis.T.conj())
        KR = self.magic_basis.dot(P.T).dot(self.magic_basis.T.conj())
        KL.real[abs(KL.real) < self.eps] = 0.0
        KL.imag[abs(KL.imag) < self.eps] = 0.0
        KR.real[abs(KR.real) < self.eps] = 0.0
        KR.imag[abs(KR.imag) < self.eps] = 0.0
        KL0, KL1 = CartanKAKDecomposition.tensor_decompose(KL)
        KR0, KR1 = CartanKAKDecomposition.tensor_decompose(KR)

        # Finally we could combine everything together
        if self.target == 'cx':
            gates = CompositeGate()
            Unitary(Delta.conj()) & [0, 1] | gates
            Unitary(KR0) & 0 | gates
            Unitary(KR1) & 1 | gates
            CX & [0, 1] | gates
            Rx(-2 * a) & 0 | gates
            Rz(-2 * c) & 1 | gates
            CX & [0, 1] | gates
            Unitary(KL0) & 0 | gates
            Unitary(KL1) & 1 | gates
        elif self.target == 'rot':
            gates = CompositeGate()
            Unitary(Delta.conj()) & [0, 1] | gates
            Unitary(KR0) & 0 | gates
            Unitary(KR1) & 1 | gates
            Rxx(-2 * a) & [0, 1] | gates
            Rzz(-2 * c) & [0, 1] | gates
            Unitary(KL0) & 0 | gates
            Unitary(KL1) & 1 | gates
        else:
            raise ValueError('Invalid target gate type')

        return gates
