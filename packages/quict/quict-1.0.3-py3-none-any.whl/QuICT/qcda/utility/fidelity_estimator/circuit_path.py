from copy import deepcopy

from QuICT.core.gate import BasicGate
from QuICT.core.utils import GateType, GATEINFO_MAP
from QuICT.core.virtual_machine import InstructionSet

gate_type_dict = {GateType.x: 0, GateType.cx: 1, GateType.sx: 2, GateType.rz: 3}


def enumerate_all_path(max_step,
                       instruction_set: InstructionSet):
    # enumerate all kinds of path given certain gate_type list
    # note that all path with steps less than max_step will be included
    r_type = ("parallel", "next")
    gate_type = instruction_set.gates
    gate_type.sort(key=lambda x: gate_type_dict[x] if x in gate_type_dict.keys() else -1)
    step = 0
    path_list = []
    for gt in gate_type:
        path_list.append(CircuitPath(((gt, "start"),), max_step=max_step, has_full=False))
    path_list = [path_list]
    while step < max_step:
        temp = []
        for path in path_list[step]:
            for gt in gate_type:
                for r in r_type:
                    if r == "next":
                        pre_gt = path.get_gate_type(-1)
                        new_path = deepcopy(path)
                        new_path.add(gt, r)
                        if new_path not in temp:
                            temp.append(new_path)
                        # should have control qubits
                        if GATEINFO_MAP[instruction_set.two_qubit_gate][0] > 0:
                            if pre_gt == instruction_set.two_qubit_gate \
                                    and gt == instruction_set.two_qubit_gate:
                                for rr in ["next2", "next3"]:
                                    new_path = deepcopy(path)
                                    new_path.add(gt, rr)
                                    if new_path not in temp:
                                        temp.append(new_path)
                            elif (pre_gt == instruction_set.two_qubit_gate
                                  and gt != instruction_set.two_qubit_gate) or \
                                    (pre_gt != instruction_set.two_qubit_gate
                                     and gt == instruction_set.two_qubit_gate):
                                new_path = deepcopy(path)
                                new_path.add(gt, "next2")
                                if new_path not in temp:
                                    temp.append(new_path)
                    else:
                        new_path = deepcopy(path)
                        new_path.add(gt, r)
                        if new_path not in temp:
                            temp.append(new_path)
        path_list.append(temp)
        del temp
        step += 1
    out = []
    for i in path_list:
        out.extend(i)
    return out


class CircuitPath:
    def __init__(
            self,
            path: tuple = None,
            max_step: int = 1,
            has_full=True):
        """
        Args:
            path(tuple[(BasicGate, r_type)]): a k-step path with each element in the
            form of (gate_type, r_type).
            max_step(int): max step of the path.
            has_full(bool): has full path or not. Has full path means
            that this path consists of BasicGate, not GateType.
        Info:
            r_type in ["parallel", "next", "next2", "next3"].
            Let cx be the example of two qubit gate.
            for cx gate and 1-qubit gate, next means connected on control qubit,
            next2 means connected on target qubit,
            for two cx gates, next means control connect target, next2 means
            target connect target, next3 means control connect target doubly.
            if the two qubit gate has two target qubits, then only next.
        """
        self.path = []
        self.max_step = max_step
        self.full_path = []
        self.has_full = has_full
        self.type_list = ["parallel", "next", "next2", "next3"]
        if path is None or len(path) == 0:
            return
        assert len(path) <= self.max_step + 1, r"path too long"
        assert path[0][1] == "start", "first gate should be start type"

        for item in path:
            if self.has_full:
                self.path.append((item[0].type, item[1]))
                self.full_path.append((item[0], item[1]))
            else:
                self.path.append((item[0], item[1]))

    def add(self, item, r_type: str = "next"):
        """
        Args:
            item(BasicGate or GateType): the gate or gate type to add
            r_type(str): r_type in ["parallel", "next", "next2", "next3"]
        Returns:
            bool: succeed or not
        """
        if self.has_full:
            return self.add_gate(item, r_type)
        else:
            return self.add_gatetype(item, r_type)

    def get_gate_type(self, num):
        """
        Args:
            num(int): index in this path
        Returns:
            GateType
        """
        return self.path[num][0]

    def get_r_type(self, num):
        """
        Args:
            num(int): index in this path
        Returns:
            str
        """
        return self.path[num][1]

    def get_gate(self, num):
        """
        Args:
            num(int): index in this path
        Returns:
            BasicGate if exists, and None if not
        """
        if self.has_full:
            return self.full_path[num][0]
        else:
            return None

    def add_gatetype(self, gatetype: GateType, r_type: str = "next"):
        """
        Args:
            gatetype(GateType): GateType to add
            r_type(str): in ["start", "former", "parallel", "next", "next2", "next3],
            only the first one can be "start".
        Returns:
            bool: succeed or not
        """
        if len(self.path) > self.max_step:
            return False
        if len(self.path) > 0:
            assert r_type in self.type_list, r"r_type not in desired list!"
        else:
            assert r_type == "start", r"r_type not in desired list!"
        self.path.append((gatetype, r_type))
        return True

    def add_gate(self, gate: BasicGate, r_type: str = "next"):
        """
        Args:
            gate(BasicGate): gate to add
            r_type(str): in ["start", "parallel", "next", "next2", "next3],
            only the first one can be "start".
        Returns:
            bool: succeed or not
        """
        gatetype = gate.type
        if len(self.path) > self.max_step:
            return False
        if len(self.path) > 0:
            assert r_type in self.type_list, r"r_type not in desired list!"
        else:
            assert r_type == "start", r"r_type not in desired list!"
        self.path.append((gatetype, r_type))
        self.full_path.append((gate, r_type))
        return True

    def __str__(self):
        return str(self.path)

    def __len__(self):
        return len(self.path) - 1

    def __hash__(self):
        return hash(tuple(self.path))

    def __eq__(self, other):
        # only consider gate type
        if not isinstance(other, CircuitPath):
            return False
        if len(other.path) != len(self.path):
            return False
        self_parallel = []
        other_parallel = []
        for index in range(len(other.path)):
            # for parallel, they have no order
            if other.path[index][1] == "parallel" and self.path[index][1] == "parallel":
                self_parallel.append(self.path[index][0])
                other_parallel.append(other.path[index][0])
                continue
            # if not parallel, compare previously parallel gates
            if other.path[index][1] != "parallel" and self.path[index][1] != "parallel":
                if len(self_parallel) > 0 and len(other_parallel) > 0:
                    self_parallel.sort(key=lambda x: gate_type_dict[x] if x in gate_type_dict.keys() else -1)
                    other_parallel.sort(key=lambda x: gate_type_dict[x] if x in gate_type_dict.keys() else -1)
                    for ii in range(len(other_parallel)):
                        if other_parallel[ii] != self_parallel[ii]:
                            return False
                    self_parallel = []
                    other_parallel = []

            if other.path[index][0] != self.path[index][0] \
                    or other.path[index][1] != self.path[index][1]:
                return False
        if len(self_parallel) > 0 and len(other_parallel) > 0:
            self_parallel.sort(key=lambda x: gate_type_dict[x] if x in gate_type_dict.keys() else -1)
            other_parallel.sort(key=lambda x: gate_type_dict[x] if x in gate_type_dict.keys() else -1)
            for ii in range(len(other_parallel)):
                if other_parallel[ii] != self_parallel[ii]:
                    return False
        return True
