from QuICT.core.gate import CompositeGate, H, S, S_dagger, CX, CCX
from .mct_linear_dirty_aux import MCTLinearHalfDirtyAux


class MCZOneAux(CompositeGate):
    """ Decomposition of n-control Z gate with one ancillary qubit and linear circuit complexity

    References:
        `Decompositions of n-qubit Toffoli gates with linear circuit complexity`
        <https://link.springer.com/article/10.1007/s10773-017-3389-4>
    """
    def __init__(
        self,
        num_ctrl: int
    ):
        """
        Args:
            num_ctrl (int): number of control qubits.
        """
        super().__init__(name=f"{num_ctrl}-cZ_1")
        if num_ctrl < 1:
            raise ValueError("Number of control qubit cannot be less than 1.")

        # special case without use of ancilla
        if num_ctrl == 1:
            H | self(1)
            CX | self([0, 1])
            H | self(1)
            return
        if num_ctrl == 2:
            H | self(2)
            CCX | self([0, 1, 2])
            H | self(2)
            return

        n = num_ctrl + 1
        k = n // 2 + n % 2
        qubit_list = list(range(n + 1))

        MCT_half_dirty = MCTLinearHalfDirtyAux()
        half_dirty_gates = MCT_half_dirty.execute(k, n + 1)

        qubit_remain = qubit_list[k:k + n // 2] + qubit_list[:k] + [qubit_list[-1]]
        if n // 2 < 1:
            raise Exception("there must be at least one control bit")
        controls_remain = [qubit_remain[i] for i in range(n // 2)]
        auxs_remain = [qubit_remain[i] for i in range(n // 2, n)]
        gates_remain = MCT_half_dirty.assign_qubits(n + 1, n // 2, controls_remain, auxs_remain, n)

        if n > 4:
            H | self(qubit_list[-2])
        half_dirty_gates | self
        if n > 4:
            H | self(qubit_list[-2])
        S | self(qubit_list[-1])
        gates_remain | self
        S_dagger | self(qubit_list[-1])
        half_dirty_gates | self
        S | self(qubit_list[-1])
        gates_remain | self
        S_dagger | self(qubit_list[-1])

        self.set_ancilla([qubit_list[-1]])
