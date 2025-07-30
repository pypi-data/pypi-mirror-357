from QuICT.core.gate import *
from .mct_linear_dirty_aux import MCTLinearHalfDirtyAux


class MCTOneAux(object):
    """ Decomposition of n-qubit Toffoli gates with one ancillary qubit and linear circuit complexity

    References:
        `Decompositions of n-qubit Toffoli gates with linear circuit complexity`
        <https://link.springer.com/article/10.1007/s10773-017-3389-4>
    """
    def execute(self, n) -> CompositeGate:
        """
        Args:
            n (int): the number of used qubit, which is (n + 2) for n-qubit Toffoli gates

        Returns:
            CompositeGate: the result of Decomposition
        """
        n = n - 1
        gates = CompositeGate()
        qubit_list = list(range(n + 1))
        if n == 3:
            CCX | gates(qubit_list[:3])
            ID | gates(qubit_list[3])
            return gates
        elif n == 2:
            CX | gates(qubit_list[:2])
            ID | gates(qubit_list[2])
            return gates
        k = n // 2 + n % 2

        MCT_half_dirty = MCTLinearHalfDirtyAux()
        half_dirty_gates = MCT_half_dirty.execute(k, n + 1)

        qubit_remain = qubit_list[k:k + n // 2] + qubit_list[:k] + [qubit_list[-1]]
        if n // 2 < 1:
            raise Exception("there must be at least one control bit")
        controls_remain = [qubit_remain[i] for i in range(n // 2)]
        auxs_remain = [qubit_remain[i] for i in range(n // 2, n)]
        gates_remain = MCT_half_dirty.assign_qubits(n + 1, n // 2, controls_remain, auxs_remain, n)

        half_dirty_gates | gates
        H | gates(qubit_list[-2])
        S | gates(qubit_list[-1])
        gates_remain | gates
        S_dagger | gates(qubit_list[-1])
        half_dirty_gates | gates
        S | gates(qubit_list[-1])
        gates_remain | gates
        H | gates(qubit_list[-2])
        S_dagger | gates(qubit_list[-1])

        return gates
