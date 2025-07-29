from QuICT.core import Circuit
from QuICT.tools.circuit_library.circuitlib import CircuitLib
from QuICT.qcda.optimization.template_optimization.template_matching.template_matching import (
    MatchingDAGCircuit, TemplateMatching)
from QuICT.qcda.optimization.template_optimization.template_matching.template_substitution import \
    TemplateSubstitution
from QuICT.qcda.utility import OutputAligner

from ...utility.circuit_cost import CircuitCost


class TemplateOptimization(object):
    """
    Template optimization algorithm.

    References:
        [1] `Exact and practical pattern matching for quantum circuit optimization.`
        <https://arxiv.org/abs/1909.05270>

    Examples:
        >>> from QuICT.qcda.optimization.template_optimization import TemplateOptimization
        >>> # suppose the typelist is nct
        >>> typelist = [GateType.x, GateType.cx, GateType.ccx]
        >>> TO = TemplateOptimization(
        >>>     template_max_size=None,
        >>>     template_typelist=typelist
        >>> )
        >>> # optimize the circuit until no further gates can be reduced
        >>> cur_circ = circuit
        >>> while True:
        >>>     circuit_opt = TO.execute(circuit)
        >>>     if circuit_opt.size() == cur_circ.size():
        >>>         break
        >>>     cur_circ = circuit_opt
    """

    def __init__(
            self,
            template_max_width=None,
            template_max_size=2,
            template_max_depth=None,
            template_typelist=None,
            template_list=None,
            qubit_fixing_num=1,
            prune_step=3,
            prune_survivor_num=1,
            backend=None,
    ):
        """
        Execute template optimization algorithm.

        Specify `template_max_width/template_max_size/template_max_depth/template_typelist`
        if you want to use templates in CircuitLib limiting size/width/depth/gate types.
        No limit if set to None. By default all templates of size 2 in CircuitLib are used.

        Specify `template_list` if you want to use customized templates.
        Setting `template_list` will invalidate
        `template_max_width/template_max_size/template_max_depth/template_typelist`.

        `qubit_fixing_num`, `prune_step`, `prune_survivor_num` are 3 heuristic parameters
        used in template matching. Their default values are recommended values.
            1. `qubit_fixing_num` the number of additional qubits explored when enumerating
                the qubit mapping (default value is 1).
            2. `prune_step`, `prune_survivor_num` are parameters for backward matching.
                Backward match will prune the search tree when depth=k * `prune_step`
                (k = 1, 2, ...) and at most `prune_survivor_num` maximal matching scenarios
                will survive (default values are 3, 1).

        Args:
            template_max_width (int): Limit on number of qubits of templates used.
            template_max_size (int): Limit on number of gates of templates used.
            template_max_depth (int): Limit on depth of templates used.
            template_typelist (Iterable[GateType]): Limit on gate types of templates used.
            template_list (List[Circuit]): List of templates used.
            qubit_fixing_num (int): heuristic parameter for qubit exploring
            prune_step (int): heuristic parameter for backward match
            prune_survivor_num (int): heuristic parameter for backward match
            backend (VirtualQuantumMachine): the target machine, by default is None.
        """

        if template_list is None:
            template_list = CircuitLib().get_template_circuit(
                template_max_width,
                template_max_size,
                template_max_depth,
                template_typelist
            )

        self.template_list = template_list
        self.heuristics_qubits_param = [qubit_fixing_num]
        self.heuristics_backward_param = [prune_step, prune_survivor_num]
        if backend is None:
            self.cost_measure = CircuitCost(method='static')
        else:
            self.cost_measure = CircuitCost(method='fidelity_simple', backend=backend)

    def __repr__(self):
        return f'TemplateOptimization(' \
               f'heuristics_qubits_param={self.heuristics_qubits_param}), ' \
               f'heuristics_backward_param={self.heuristics_backward_param})'

    @OutputAligner()
    def execute(self, circuit) -> Circuit:
        """
        Execute template optimization algorithm.

        Args:
            circuit (Circuit): the circuit to be optimized

        Returns:
            Circuit: the optimized circuit
        """

        circ_dag = MatchingDAGCircuit(circuit)

        for template in self.template_list:
            template_dag = MatchingDAGCircuit(template)

            if template_dag.width > circ_dag.width:
                continue

            matches = TemplateMatching.execute(
                circ_dag,
                template_dag,
                self.heuristics_qubits_param,
                self.heuristics_backward_param
            )

            circ_dag = TemplateSubstitution.execute(circ_dag, template_dag, matches, self.cost_measure)

        return circ_dag.get_circuit()
