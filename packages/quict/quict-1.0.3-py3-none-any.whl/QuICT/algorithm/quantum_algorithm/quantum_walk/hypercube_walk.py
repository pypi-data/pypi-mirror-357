from typing import Optional, Dict
from numpy import pi, floor, ceil, sqrt, log2, binary_repr

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate, X, Measure
from .shift_op import HyperCubeShiftOp
from QuICT.algorithm.state import UniformState
from QuICT.core.gate.backend import MCRWithoutAux
from QuICT.algorithm.tools import QRegManager, QubitAligner
from QuICT.simulation.state_vector import StateVectorSimulator


class HypercubeWalk:
    """ Quantum walk on a hypercube. Assuming each node is binary encoded as unsigned integer and each direciton
    of the coin is also encoded as unsigned integer. Quantum circuit will have registers in the following order:

    |node register>
    |mark bit> (if search)
    |coin register>
    |ancilla> (if any)

    Reference:
        [1]: Tonchev, Hristo. “Alternative Coins for Quantum Random Walk Search Optimized for a Hypercube.”
            Journal of Quantum Information Science 05, no. 01 (2015): 6-15. https://doi.org/10.4236/jqis.2015.51002.

    """

    def __init__(
        self,
        node_deg: int
    ):
        """
        Args:
            node_deg (int): Degree for each node.
        """
        if node_deg < 2:
            raise ValueError(f"Node's degree cannot be less than 2, gut given {node_deg}.")

        self.graph_param = {"degree": node_deg}

        self._node_prep: CompositeGate = None
        self._coin_prep: CompositeGate = None
        self._iteration_core: CompositeGate = None
        self._node_reg: list[int] = None
        self._coin_reg: list[int] = None
        self._ancilla: list[int] = None
        self._total_qubits: int = None

    def build_walk(
        self,
        node_prep: Optional[CompositeGate] = None,
        coin_prep: Optional[CompositeGate] = None,
        coin: Optional[CompositeGate] = None,
        shift: Optional[CompositeGate] = None,
    ) -> None:
        """ Build the quantum walk circuit in walk mode.

        Args:
            node_prep (CompositeGate): gate for initializing the node register.
            coin_prep (CompositeGate): gate for initializing the coin register.
            coin (CompositeGate): the coin operator.
            shift (CompositeGate): the shift operator.

        """
        degree = self.graph_param["degree"]

        if coin_prep is None:
            coin_prep = UniformState(degree)
        if coin is None:
            coin = self._grover_coin(degree)
        if shift is None:
            shift = HyperCubeShiftOp(node_deg=degree, name="S")

        reg_manager = QRegManager()
        num_ancilla = reg_manager.ancilla_num([node_prep, coin_prep, coin, shift])

        node_reg_size = degree
        coin_reg_size = (degree - 1).bit_length()
        node_reg = reg_manager.alloc(node_reg_size)
        coin_reg = reg_manager.alloc(coin_reg_size)
        ancilla_reg = reg_manager.alloc(num_ancilla)

        node_ancilla_aligner = QubitAligner(node_reg, ancilla_reg)
        coin_ancilla_aligner = QubitAligner(coin_reg, ancilla_reg)

        coin_prep_actex = coin_ancilla_aligner.getMap(coin_prep)
        coin_actex = coin_ancilla_aligner.getMap(coin)
        shift_actex_wo_control = node_ancilla_aligner.getMap(shift, fix_top=coin_reg_size)

        iteration_core = CompositeGate("Iter")
        coin | iteration_core(coin_actex)
        shift | iteration_core(coin_reg + shift_actex_wo_control)

        if node_prep is not None:
            node_prep_actex = node_ancilla_aligner.getMap(node_prep)
            self._node_prep = node_prep & node_prep_actex
        self._coin_prep = coin_prep & coin_prep_actex
        self._iteration_core = iteration_core
        self._node_reg = node_reg
        self._coin_reg = coin_reg
        self._ancilla = ancilla_reg
        self._total_qubits = reg_manager.allocated

    def build_search(
        self,
        node_prep: Optional[CompositeGate] = None,
        coin_prep: Optional[CompositeGate] = None,
        coin: Optional[CompositeGate] = None,
        shift: Optional[CompositeGate] = None,
        target_marker: Optional[CompositeGate] = None,
        target_coin: Optional[CompositeGate] = None
    ) -> None:
        """ Build the quantum walk circuit in search mode. The search is using a alternative coin model.

        Args:
            node_prep (CompositeGate): gate for initializing the node register.
            coin_prep (CompositeGate): gate for initializing the coin register.
            coin (CompositeGate): the coin operator for the unmarked node.
            shift (CompositeGate): the shift operator.
            target_marker (CompositeGate): an oracle gate for marking the target, assume to be a bitflip oracle.
            target_coin (CompositeGate): the coin operator for the marked node.
        """
        degree = self.graph_param["degree"]

        node_reg_size = degree
        target_mark_bit = 1
        coin_reg_size = (degree - 1).bit_length()

        if node_prep is None:
            node_prep = UniformState(1 << degree)
        if coin_prep is None:
            coin_prep = UniformState(degree)
        if coin is None:
            coin = CompositeGate("c-C0")
            X | coin(0)
            self._grover_coin(degree, control=True) | coin(list(range(coin_reg_size + target_mark_bit)))
            X | coin(0)
        if shift is None:
            shift = HyperCubeShiftOp(node_deg=degree, name="S")
        if target_coin is None:
            target_coin = MCRWithoutAux(num_ctrl=coin_reg_size, theta=pi, targ_rot_mode="u1", name=f"c-C1")

        reg_manager = QRegManager()
        num_ancilla = reg_manager.ancilla_num([node_prep, coin_prep, coin, shift, target_marker, target_coin])

        node_reg = reg_manager.alloc(node_reg_size)
        target_mark_reg = reg_manager.alloc(target_mark_bit)
        coin_reg = reg_manager.alloc(coin_reg_size)
        ancilla_reg = reg_manager.alloc(num_ancilla)

        node_ancilla_aligner = QubitAligner(node_reg, ancilla_reg)
        node_plus_mark_ancilla_aligner = QubitAligner(node_reg + target_mark_reg, ancilla_reg)
        mark_plus_coin_ancilla_aligner = QubitAligner(target_mark_reg + coin_reg, ancilla_reg)
        coin_ancilla_aligner = QubitAligner(coin_reg, ancilla_reg)

        node_prep_actex = node_ancilla_aligner.getMap(node_prep)
        coin_prep_actex = coin_ancilla_aligner.getMap(coin_prep)
        coin_actex = mark_plus_coin_ancilla_aligner.getMap(coin)
        shift_actex_wo_control = node_ancilla_aligner.getMap(shift, fix_top=coin_reg_size)
        target_coin_actex = mark_plus_coin_ancilla_aligner.getMap(target_coin)
        if target_marker is not None:
            target_marker_actex = node_plus_mark_ancilla_aligner.getMap(target_marker)

        iteration_core = CompositeGate("Iter")
        if target_marker is not None:
            target_marker | iteration_core(target_marker_actex)
        coin | iteration_core(coin_actex)
        target_coin | iteration_core(target_coin_actex)
        if target_marker is not None:
            target_marker | iteration_core(target_marker_actex)
        shift | iteration_core(coin_reg + shift_actex_wo_control)

        self._node_prep = node_prep & node_prep_actex
        self._coin_prep = coin_prep & coin_prep_actex
        self._iteration_core = iteration_core
        self._node_reg = node_reg
        self._coin_reg = coin_reg
        self._ancilla = ancilla_reg
        self._total_qubits = reg_manager.allocated

    def circuit(
        self,
        iteration: int,
        contain_measure: bool = True
    ) -> Circuit:
        """ Construct circuit for quantum walk on the hyperbuce.

        Args:
            iteration (int): Number of walk iteration.
            contain_measure (bool): if `True`, the output circuit contains measurement gate on the node
                register.

        Returns:
            Circuit: the quantum walk circuit.
        """
        if self._total_qubits is None:
            raise RuntimeError("Please call build functions to initialize the quantum walk" +
                               " in either walk mode or search mode first.")

        qw_circ = Circuit(self._total_qubits)

        if self._node_prep is not None:
            self._node_prep | qw_circ

        self._coin_prep | qw_circ

        for _ in range(iteration):
            self._iteration_core | qw_circ

        if contain_measure:
            for i in self._node_reg:
                Measure | qw_circ(i)

        qw_circ.ancilla_qubits = self._ancilla

        return qw_circ

    def run(
        self,
        iteration: int,
        backend=StateVectorSimulator(),
        shots: int = 1,
        target_qubits: list[int] = None
    ) -> Dict[str, int]:
        """ Run the quantum walk on hypercube.

        Args:
            iteration (int): Number of walk iteration.
            backend (Any): Device to run the quantum walk.
            shots (int): Number of experiments to run.
            target_qubits (List[int]): the qubit indices to measure. If not given, will be set to the node
                register of the quantum walk.

        Returns:
            Dict[str, int]: sampling result on the node register of the quantum walk circuit.
        """
        if self._total_qubits is None:
            raise RuntimeError("Please call build functions to initialize the quantum walk" +
                               " in either walk mode or search mode first.")
        if target_qubits is None:
            target_qubits = self._node_reg

        qw_circ = self.circuit(iteration=iteration, contain_measure=False)
        backend.run(qw_circ)
        sample_res = backend.sample(shots=shots, target_qubits=target_qubits)

        res_dict = {}
        for key, val in enumerate(sample_res):
            if val != 0:
                res_dict[binary_repr(key, width=len(target_qubits))] = val

        return res_dict

    def optimal_search_iteration(self, num_target: int) -> int:
        return int(floor(pi / 2 * (sqrt((2 ** self.graph_param["degree"]) / num_target))))

    def _grover_coin(self, node_deg: int, control: bool = False) -> CompositeGate:
        cg = CompositeGate(name="c_grover")
        reg_size = int(ceil(log2(node_deg)))
        offset = int(control)

        UniformState(N=node_deg).inverse() | cg(list(range(offset, offset + reg_size)))

        for i in range(offset, offset + reg_size):
            X | cg(i)

        MCRWithoutAux(
            num_ctrl=reg_size - 1 + offset,
            theta=pi,
            targ_rot_mode="u1",
            name=f"c{reg_size - 1 + offset}-Z"
        ) | cg

        for i in range(offset, offset + reg_size):
            X | cg(i)

        UniformState(N=node_deg) | cg(list(range(offset, offset + reg_size)))

        return cg
