import numpy as np
from typing import Union, List

from QuICT.core import Circuit
from QuICT.core.gate import CompositeGate
from QuICT.core.utils import GateType
from QuICT.core.virtual_machine.virtual_machine import VirtualQuantumMachine

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from .fidelity_estimator.simple_fidelity_estimator import SimpleFidelityEstimator

try:
    from .fidelity_estimator.nn_fidelity_estimator import NNFidelityEstimator
except ImportError:
    NNFidelityEstimator = None


class CircuitCost:
    """
    Evaluate cost of a circuit.
    """

    NISQ_GATE_COST = {
        GateType.id: 0, GateType.x: 1, GateType.y: 1, GateType.z: 1, GateType.h: 1,
        GateType.t: 1, GateType.tdg: 1, GateType.s: 1, GateType.sdg: 1, GateType.u1: 1,
        GateType.u2: 2, GateType.u3: 2, GateType.rx: 1, GateType.ry: 1, GateType.rz: 1,
        GateType.cx: 2, GateType.cy: 4, GateType.cz: 4, GateType.ch: 8, GateType.swap: 6,
        GateType.cswap: 8, GateType.rxx: 9, GateType.ryy: 9, GateType.rzz: 5,
        GateType.cu3: 10, GateType.ccx: 21, GateType.measure: 9
    }

    def __init__(self, method='static', backend=None, cost_dict=None):
        """
        Evaluate cost of a circuit. 3 methods are available:
            1. 'static': Use a static cost dictionary to evaluate the cost of a circuit.
            2. 'fidelity_simple': Based on a simple fidelity estimator that multiplies fidelity of all gates.
               A VirtualQuantumMachine type backend is needed.
            3. 'fidelity_nn': Based on a neural network fidelity estimator. A str type backend is needed.
               See `NNFidelityEstimator.SUPPORTED_MACHINE` for supported machines.

        Args:
            method(str): Method to evaluate the cost of a circuit. Default is 'static'.
            backend(Union[VirtualQuantumMachine, str]): the target quantum machine. Default is None.
            cost_dict(dict): Cost of each gate type if method='static'. If None, NISQ_GATE_COST will be used.
        """

        self.method = method
        self.cost_dict = cost_dict if cost_dict is not None else self.NISQ_GATE_COST

        if self.method == 'static':
            self.estimator = None
        elif self.method == 'fidelity_simple':
            assert isinstance(backend, VirtualQuantumMachine), \
                'fidelity_simple method needs a vqm as backend'
            self.estimator = SimpleFidelityEstimator(backend)
        elif self.method == 'fidelity_nn':
            assert isinstance(backend, str), 'fidelity_nn method needs a str as backend'
            assert NNFidelityEstimator is not None, "pytorch or sklearn are not installed. fidelity_nn is not available"
            self.estimator = NNFidelityEstimator.from_target_machine(backend)
        else:
            raise ValueError(f'Unsupported method: {method}')

    def __getitem__(self, gate_type):
        """
        Get static cost of a gate type. Subscript can be a GateType or string of a gate type.

        Args:
            gate_type(GateType/str): Gate type

        Returns:
            int: Cost of the gate type
        """
        if isinstance(gate_type, str):
            gate_type = GateType(gate_type)

        if gate_type in self.cost_dict:
            return self.cost_dict[gate_type]
        else:
            return 0

    def _get_static_cost(self, circuit: Union[Circuit, CompositeGate]):
        """
        Compute the static cost of a circuit by adding up static weight of gates.
        """
        return sum(
            self._get_static_cost(n) if isinstance(n, CompositeGate) else self[n.type]
            for n in circuit.gates
        )

    def estimate_cost(self,
                      circuit: Union[Circuit, CompositeGate],
                      vqm: VirtualQuantumMachine = None,
                      mapping: List[int] = None
                      ):
        """
        Estimate the cost of a circuit. If self.backend == None, compute static cost. Otherwise compute
        cost based on estimated fidelity.

        Args:
            circuit(Union[Circuit, CompositeGate]): Circuit to evaluate.
            vqm(VirtualQuantumMachine): Target machine when using method 'fidelity_simple'
                or 'fidelity_nn'. Use default machine if set to None.
            mapping(List[int]): Mapping of the circuit. Identity if None.

        Returns:
            float: Estimated cost of the circuit.
        """
        if self.estimator is None:
            return self._get_static_cost(circuit)
        else:
            return -np.log(self.estimate_fidelity(circuit, vqm, mapping))

    def estimate_fidelity(self,
                          circuit: Union[Circuit, CompositeGate],
                          vqm: VirtualQuantumMachine = None,
                          mapping: List[int] = None):
        """
        Estimate the fidelity of a circuit.
        Available only when self.method == 'fidelity_simple' or 'fidelity_nn'.

        Args:
            circuit(Union[Circuit, CompositeGate]): Circuit to evaluate.
            vqm(VirtualQuantumMachine): Target machine. Use default machine if set to None.
            mapping(List[int]): Mapping of the circuit. Identity if None.

        Returns:
            float: Estimated fidelity of the circuit.
        """
        if self.method == 'fidelity_simple':
            return self.estimator.estimate_fidelity(circuit, mapping=mapping)
        else:
            return self.estimator.estimate_fidelity(circuit, vqm=vqm, mapping=mapping)
