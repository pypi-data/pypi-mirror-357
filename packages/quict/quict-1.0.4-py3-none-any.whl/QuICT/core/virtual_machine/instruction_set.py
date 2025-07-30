from typing import Union, List, Dict
from types import FunctionType

from QuICT.core.gate import GateType


class InstructionSet(object):
    """ InstructionSet describes a set of gates(expectly to be universal set)

    Instruction Set contains gates and some rules, which can be assigned by user.

    Attributes:
        two_qubit_gate (GateType): the type of the two_qubit_gate
        one_qubit_gates (list<GateType>): the types of the one_qubit_gate
        one_qubit_gates_fidelity (Union[float, Dict, List], optional): The fidelity for single qubit quantum gate.
            Defaults to None.
        one_qubit_rule (Union[str, callable], optional): rules to transform SU(2) into instruction set
    """
    # Divide supported 2-qubit gates into several categories, where gates in the same category are equivalent
    # under 1-qubit gates. In the Weyl chamber viewpoint, it means they share the same point or trajectory for
    # gates without or with parameters respectively.
    # Add more rules in QuICT/qcda/synthesis/gate_transform/transform_rule/two_qubit_gate_rules.py to support
    # more gates. Only the rules between key gates of different categories and between the key gate and the members
    # of the same category are necessary.
    two_qubit_categories = {
        GateType.cx: [GateType.cx, GateType.cy, GateType.cz, GateType.ch, GateType.ecr],
        GateType.rzz: [GateType.rxx, GateType.ryy, GateType.rzz, GateType.rzx, GateType.crz, GateType.cry],
        GateType.fsim: [GateType.fsim]
    }

    @property
    def size(self):
        return len(self.one_qubit_gates) + 1

    @property
    def gates(self) -> list:
        """ Return the list of GateType in current Instruction Set. """
        return self.one_qubit_gates + [self.two_qubit_gate]

    # Two-qubit gate and two-qubit rules
    @property
    def two_qubit_gate(self):
        return self.__two_qubit_gate

    @two_qubit_gate.setter
    def two_qubit_gate(self, two_qubit_gate):
        """ set two_qubit_gate

        Args:
            two_qubit_gate(GateType): two-qubit gate in the InstructionSet
        """
        assert isinstance(two_qubit_gate, GateType), TypeError('two_qubit_gate should be a GateType')
        self.__two_qubit_gate = two_qubit_gate

    @property
    def two_qubit_rule_map(self):
        return self.__two_qubit_rule_map

    @two_qubit_rule_map.setter
    def two_qubit_rule_map(self, two_qubit_rule_map):
        self.__two_qubit_rule_map = two_qubit_rule_map

    # One-qubit gates and one-qubit rule
    @property
    def one_qubit_gates(self):
        return self.__one_qubit_gates

    @one_qubit_gates.setter
    def one_qubit_gates(self, one_qubit_gates):
        """ set one_qubit_gates

        Args:
            one_qubit_gates(list<GateType>): one-qubit gates in the InstructionSet
        """
        assert isinstance(one_qubit_gates, list), TypeError('one_qubit_gates should be a list')
        for one_qubit_gate in one_qubit_gates:
            assert isinstance(one_qubit_gate, GateType), TypeError('each one_qubit_gate should be a GateType')
        self.__one_qubit_gates = one_qubit_gates

    @property
    def one_qubit_rule(self):
        """ the rule of decompose 2*2 unitary into target gates

        If not assigned by the register_one_qubit_rule method, some pre-implemented method would be chosen
        corresponding to the one_qubit_gates. An Exception will be raised when no method is chosen.

        Returns:
            callable: the corresponding rule
        """
        if self.__one_qubit_rule:
            return self.__one_qubit_rule
        if set((GateType.rz, GateType.rx)).issubset(set(self.one_qubit_gates)):
            return "zxz_rule"
        if set((GateType.rz, GateType.ry)).issubset(set(self.one_qubit_gates)):
            return "zyz_rule"
        if set((GateType.rx, GateType.ry)).issubset(set(self.one_qubit_gates)):
            return "xyx_rule"
        if set((GateType.h, GateType.rz)).issubset(set(self.one_qubit_gates)):
            return "hrz_rule"
        if set((GateType.rz, GateType.sx, GateType.x)).issubset(set(self.one_qubit_gates)):
            return "ibmq_rule"
        if set((GateType.rz, GateType.sx, GateType.sy, GateType.sxdg, GateType.sydg)
               ).issubset(set(self.one_qubit_gates)):
            return "ctek_rule"
        if set((GateType.u3,)).issubset(set(self.one_qubit_gates)):
            return "u3_rule"
        raise Exception("please register the SU2 decomposition rule.")

    def __init__(
        self,
        two_qubit_gate: GateType,
        one_qubit_gates: List[GateType],
        one_qubit_rule: Union[str, callable] = None
    ):
        self.two_qubit_gate = two_qubit_gate
        self.one_qubit_gates = one_qubit_gates
        self.__one_qubit_rule = None
        if one_qubit_rule is not None:
            self.register_one_qubit_rule(one_qubit_rule)

        self.__two_qubit_rule_map = {}

    def select_transform_rule(self, source):
        """ choose a rule which transforms source gate into target gate(2-qubit)

        Args:
            source(GateType): the type of source gate

        Returns:
            callable: the transform rules
        """
        assert isinstance(source, GateType)
        # If registered, no more check needed
        if source in self.two_qubit_rule_map.keys():
            return self.two_qubit_rule_map[source]

        source_cate = None
        target_cate = None
        for cate in self.two_qubit_categories.keys():
            if source in self.two_qubit_categories[cate]:
                source_cate = cate
            if self.two_qubit_gate in self.two_qubit_categories[cate]:
                target_cate = cate
        if source_cate is None or target_cate is None:
            raise ValueError(f'Transform rule not found between {source.name} and {self.two_qubit_gate.name}')

        # If source and target are in the same category
        if source_cate == target_cate:
            # Furthermore, if source or target is the key gate, a direct transform rule could be selected
            if source == source_cate or self.two_qubit_gate == target_cate:
                self.two_qubit_rule_map[source] = [
                    (source, f"{source.name}2{self.two_qubit_gate.name}_rule")
                ]
            # Otherwise, they need to be transformed to the key gate first
            else:
                self.two_qubit_rule_map[source] = [
                    (source, f"{source.name}2{source_cate.name}_rule"),
                    (target_cate, f"{target_cate.name}2{self.two_qubit_gate.name}_rule")
                ]
        # Otherwise, we need the two key gates as a tranfer
        else:
            self.two_qubit_rule_map[source] = []
            if source != source_cate:
                self.two_qubit_rule_map[source].append(
                    (source, f"{source.name}2{source_cate.name}_rule")
                )
            self.two_qubit_rule_map[source].append(
                (source_cate, f"{source_cate.name}2{target_cate.name}_rule")
            )
            if self.two_qubit_gate != target_cate:
                self.two_qubit_rule_map[source].append(
                    (target_cate, f"{target_cate.name}2{self.two_qubit_gate.name}_rule")
                )

        return self.two_qubit_rule_map[source]

    def register_one_qubit_fidelity(self, gates_fidelity: Union[float, List, Dict]):
        if isinstance(gates_fidelity, float):
            gates_fidelity = [gates_fidelity] * len(self.one_qubit_gates)
        elif isinstance(gates_fidelity, list):
            assert len(gates_fidelity) == len(self.one_qubit_fidelity)
        elif isinstance(gates_fidelity, dict):
            assert len(gates_fidelity.keys()) == len(self.one_qubit_fidelity)
            for gate_type, fidelity in gates_fidelity.items():
                assert gate_type in self.one_qubit_gates, ValueError(f"Unknown Single-Qubit Gate {gate_type}.")
                assert fidelity >= 0 and fidelity <= 1, \
                    ValueError(f"Wrong Fidelity {fidelity}, it should between 0 and 1.")
        else:
            raise TypeError(f"Unsupport Single-Qubit Gates' Fidelity, {type(gates_fidelity)}.")

        if isinstance(gates_fidelity, list):
            self.__one_qubit_gates_fidelity = {}
            for idx, fidelity in enumerate(gates_fidelity):
                assert fidelity >= 0 and fidelity <= 1, ValueError(
                    f"Wrong Fidelity {fidelity}, it should between 0 and 1."
                )
                self.__one_qubit_gates_fidelity[self.__one_qubit_gates[idx]] = fidelity
        else:
            self.__one_qubit_gates_fidelity = gates_fidelity

    def register_one_qubit_rule(self, one_qubit_rule: Union[str, callable]):
        """ register one-qubit gate decompostion rule

        Args:
            one_qubit_rule(callable): decompostion rule, you can define your self rule function or use one of
                [zyz_rule, zxz_rule, hrz_rule, xyx_rule, ibmq_rule, u3_rule].
        """
        assert isinstance(one_qubit_rule, (str, FunctionType)), \
            TypeError("Unsupport Type, should be one of [string, Callable].")
        self.__one_qubit_rule = one_qubit_rule

    def register_two_qubit_rule_map(self, two_qubit_rule: callable, source: GateType):
        """ register rule which transforms from source gate into target gate

        Args:
            two_qubit_rule(callable): the transform rule
            source(GateType): the type of source gate
        """
        assert isinstance(source, GateType)
        self.two_qubit_rule_map[source] = [(source, two_qubit_rule)]
