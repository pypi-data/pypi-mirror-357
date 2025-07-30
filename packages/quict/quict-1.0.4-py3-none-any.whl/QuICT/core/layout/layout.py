from __future__ import annotations
from math import log2
from numpy import int32, int64
from enum import Enum
from collections import defaultdict

import json
import warnings
from typing import Any, Dict, List, Tuple


class LayoutType(Enum):
    normal = "Normal Layout"
    linear = "Linearly Layout"
    grid = "Gridly Layout"
    rhombus = "Rhombus Layout"


class LayoutEdge:
    """Implement a physical connection between physical qubits

    Attributes:
        u(int): Node u of edge
        v(int): Node v of edge
        directional(bool): Whether the layout is directional
        error_rate(float): Error_rate between u and v, default 1.0
    """

    @property
    def u(self) -> int:
        return self._u

    @u.setter
    def u(self, u):
        warnings.warn("In general, the LayoutEdge shouldn't be re-write.")
        assert u != self._v, "Endpoints cannot be same."
        self._u = u

    @property
    def v(self) -> int:
        return self._v

    @v.setter
    def v(self, v):
        warnings.warn("In general, the LayoutEdge shouldn't be re-write.")
        assert v != self._u, "Endpoints cannot be same."
        self._v = v

    @property
    def error_rate(self) -> float:
        return self._error_rate

    @error_rate.setter
    def error_rate(self, error_rate):
        self._error_rate = error_rate

    @property
    def directional(self):
        return self._directional

    @directional.setter
    def directional(self, value: bool):
        self._directional = value

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        data["u"] = self._u
        data["v"] = self._v
        data["error_rate"] = self._error_rate
        data["directional"] = self._directional
        return data

    def __init__(self, u: int, v: int, directional: bool, error_rate: float):
        self._u = u
        self._v = v
        self._error_rate = error_rate
        self._directional = directional

    def __str__(self):
        dir = ' <-> ' if not self._directional else '-->'
        return f"{self._u} {dir} {self._v}, with error rate {self._error_rate}"


class Layout:
    """Implement a topology in a physical device

    """

    DIRECTIONAL_DEFAULT = False
    ERROR_RATE_DEFAULT = 1.0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def layout_type(self) -> LayoutType:
        return self._type

    @layout_type.setter
    def layout_type(self, layout_type: LayoutType):
        assert isinstance(layout_type, LayoutType)
        self._type = layout_type

    @property
    def edge_list(self) -> List[LayoutEdge]:
        return list(self._edges.values())

    def __iter__(self):
        yield from self._edges.values()

    @property
    def qubit_number(self):
        return self._qubit_number

    @property
    def unreachable_nodes(self) -> list:
        return self._unreachable_nodes

    @unreachable_nodes.setter
    def unreachable_nodes(self, unreachable_nodes: list):
        assert isinstance(unreachable_nodes, list)
        self._unreachable_nodes = unreachable_nodes

    @property
    def double_gate_fidelity(self) -> dict:
        return self._double_gate_fidelity

    def __init__(
        self,
        qubit_number: int,
        name: str = "unknown",
        layout_type: LayoutType = LayoutType.normal,
        unreachable_nodes: list = None,
        layout_width: int = -1
    ):
        """
        Args:
            qubit_number(int): the number of qubits
            name(string): the name of the topology
        """
        assert qubit_number >= 2, "qubits number should greater than 1"
        self._qubit_number = qubit_number
        self._name = name
        self._edges: Dict[Tuple[int, int], LayoutEdge] = {}
        self._directionalized = None
        self._type = layout_type
        self._unreachable_nodes = unreachable_nodes
        self._double_gate_fidelity = None
        self._width = layout_width
        self._rhombus_shape = 0

    def __str__(self):
        layout_str = f"{self._name} with {self._qubit_number} qubits."
        for edge in self.edge_list:
            layout_str += f"\n{edge}"

        return layout_str

    def set_double_gate_fidelity(self, double_gate_fidelity: list):
        """ Set the coupling strength between qubits

        Args:
            double_gate_fidelity List[Tuple(idx, idx, float)]: The strength of the interaction between two qubits in a
                quantum computing system.
        """
        # Reset coupling strength
        self._double_gate_fidelity = defaultdict(dict)

        for start, end, val in double_gate_fidelity:
            assert start != end and start >= 0 and end >= 0 and val >= 0 and val <= 1
            assert self.check_edge(start, end), f"inexistance edge ({start}, {end}) in current layout."

            self._double_gate_fidelity[start][end] = val
            self._double_gate_fidelity[end][start] = val
            target_edge = self._edges[(start, end)] if (start, end) in self._edges else self._edges[(end, start)]
            target_edge.error_rate = val

    def out_edges(self, begin_point: int, node_index_only: bool = False) -> List[LayoutEdge]:
        """edges begin from begin_point

        Args:
            begin_point(int): the index of begin node

        Return:
            list<LayoutEdge>: edges begin from begin_point
        """
        prior_list = []
        for edge in self.edge_list:
            if edge.u == begin_point:
                if node_index_only:
                    prior_list.append(edge.v)
                else:
                    prior_list.append(edge)
            elif edge.v == begin_point and not edge.directional:
                if node_index_only:
                    prior_list.append(edge.u)
                else:
                    prior_list.append(edge)

        return prior_list

    @property
    def directionalized(self) -> Layout:
        """Return a copy of current layout with all undirected edges
        replaced with 2 reversed directional edges.
        """
        layout = Layout(self._qubit_number, self._name)
        for edge in self:
            if edge.directional:
                layout.add_edge(u=edge.u, v=edge.v, directional=True, error_rate=edge.error_rate)
            else:
                layout.add_edge(
                    u=edge.u, v=edge.v, directional=True, error_rate=edge.error_rate
                )
                layout.add_edge(
                    u=edge.v, v=edge.u, directional=True, error_rate=edge.error_rate
                )
        return layout

    def add_edge(
        self,
        u,
        v,
        directional=DIRECTIONAL_DEFAULT,
        error_rate=ERROR_RATE_DEFAULT,
    ):
        """add an edge in the layout

        Args:
            u(int): Edge endpoint u
            v(int): Edge endpoint v
            directional(bool): Whether the edge is directional
            error_rate(float): Error rate, default 1.0
        """
        assert u != v, "Endpoints cannot be the same"
        assert isinstance(u, (int, int32, int64)) and isinstance(v, (int, int32, int64)), \
            "Endpoints should be integer."
        assert (u >= 0 and u < self._qubit_number) and (u >= 0 and u < self._qubit_number), \
            f"Endpoints should between [0, {self._qubit_number})"
        if self.check_edge(u, v):
            return

        edge = LayoutEdge(u, v, directional, error_rate)
        key = (u, v) if directional or u < v else (v, u)
        self._edges[key] = edge
        # Reset cache
        self._directionalized = None

    def remove_edge(self, u, v, directional=DIRECTIONAL_DEFAULT):
        """remove an edge in the layout

        Args:
            u(int): Edge endpoint u
            v(int): Edge endpoint v
            directional(bool): Whether the edge is directional
        """
        assert u != v, "Endpoints cannot be the same"
        assert isinstance(u, (int, int32, int64)) and isinstance(v, (int, int32, int64)), \
            "Endpoints should be integer."
        assert (u >= 0 and u < self._qubit_number) and (u >= 0 and u < self._qubit_number), \
            f"Endpoints should between [0, {self._qubit_number})"
        if not self.check_edge(u, v):
            return

        key = (u, v) if directional or u < v else (v, u)
        del self._edges[key]

    def build_layout_by_double_gate_fidelity(self, double_gate_fidelity: list):
        """build layout by double_gate_fidelity form virtual quantum machine. """
        assert isinstance(double_gate_fidelity, list), "Please input the double_gate_fidelity infos"

        for edge in double_gate_fidelity:
            u, v, error_rate = edge
            if (u, v) in self._edges:
                self._edges[(u, v)].error_rate = error_rate
            elif (v, u) in self._edges and not self._edges[(v, u)].directional:
                self._edges[(v, u)].error_rate = error_rate
            else:
                self.add_edge(
                    u, v, directional=False, error_rate=error_rate
                )

    def check_edge(self, u, v) -> bool:
        """Check whether layout contain u->v

        Args:
            u(int): the edge endpoint u
            v(int): the edge endpoint v
        Return:
            bool: whether layout contain u->v
        """
        return ((u, v) in self._edges) or (
            (v, u) in self._edges and not self._edges[(v, u)].directional
        )

    def valid_circuit(self, circuit) -> bool:
        """ Validate the given Circuit/CompositeGate is valid with current Layout.

        Args:
            circuit (Union[Circuit, CompositeGate]): The given Circuit/CompositeGate

        Returns:
            bool: Whether is valid for current layout.
        """
        if circuit.width() > self._qubit_number:
            return False

        for gate in circuit.gates:
            if type(gate).__name__ == "CompositeGate":
                if not self.valid_circuit(gate):
                    return False

                continue

            qidxes = gate.cargs + gate.targs
            if len(qidxes) > 2:
                return False
            elif len(qidxes) == 2:
                if not self.check_edge(qidxes[0], qidxes[1]) or not self.check_edge(qidxes[1], qidxes[0]):
                    return False

        return True

    def to_json(self) -> str:
        """Serialize current layout into json string."""
        data = {}
        data["name"] = self._name
        data["qubit_number"] = self._qubit_number
        edges = [edge.to_dict() for edge in self]
        data["edges"] = edges
        return json.dumps(data)

    def write_file(self, directory="./"):
        """Write layout into file.

        Args:
            directory(str): Directory to store layout file in, default "./"
        """
        with open(f"{directory}{self.name}.layout", "w") as f:
            f.write(self.to_json())

    @classmethod
    def from_json(cls, json_str: str) -> Layout:
        json_obj = json.loads(json_str)
        name = json_obj["name"]
        qubit_number = json_obj["qubit_number"]
        layout = Layout(qubit_number, name)
        edges = json_obj["edges"]
        for edge in edges:
            u = edge["u"]
            v = edge["v"]
            directional = (
                edge["directional"]
                if "directional" in edge
                else cls.DIRECTIONAL_DEFAULT
            )
            error_rate = (
                edge["error_rate"] if "error_rate" in edge else cls.ERROR_RATE_DEFAULT
            )
            layout.add_edge(u=u, v=v, directional=directional, error_rate=error_rate)
        return layout

    @classmethod
    def load_file(cls, file_path: str) -> Layout:
        """Load layout from file.
        Args:
            file_path(str): Path of layout file.
        Return:
            Layout: Layout parsed from file.
        """
        with open(file_path) as f:
            return cls.from_json(f.read())

    def get_sublayout_edges(self, qubits: list) -> List[LayoutEdge]:
        """ Get list of edges with target qubits from current Layout.

        Args:
            qubits (list): The target qubits

        Returns:
            list: The list of LayoutEdge
        """
        # Validate qubits:
        for q in qubits:
            assert isinstance(q, int), "The qubit index should be integer."
            assert q >= 0 and q < self._qubit_number, f"The qubit index should between [0, {self._qubit_number})"

        sub_edges = []
        for ledge in self._edges.values():
            if ledge.v not in qubits and ledge.u not in qubits:
                continue

            sub_edges.append(ledge)

        return sub_edges

    def sub_layout(self, qubits: list) -> Layout:
        """ Get partial layout. Only working for undirected layout.

        Args:
            qubits_number (list): The qubit indexes for sub-layout

        Returns:
            Layout: The sub-layout
        """
        assert len(qubits) == len(set(qubits)), "Repeatted qubit indexes."
        for q in qubits:
            assert q >= 0 and q < self._qubit_number, "The qubit index should in current Layout."

        sub_layout = Layout(len(qubits))
        sorted_qidx = sorted(qubits)
        for edge in self._edges.values():
            if edge.u not in qubits or edge.v not in qubits:
                continue

            sub_layout.add_edge(
                sorted_qidx.index(edge.u), sorted_qidx.index(edge.v), edge.directional, edge.error_rate
            )

        return sub_layout

    @staticmethod
    def linear_layout(qubit_number: int, directional: bool = DIRECTIONAL_DEFAULT, error_rate: list = None):
        """ Return the layout with linearly topology.

        Args:
            qubit_number(int): the number of qubits
            directional (_type_, optional): Whether the edge is directional. Defaults to DIRECTIONAL_DEFAULT.
            error_rate (list, optional): Error rate for each edges, default 1.0. Defaults to [].

        Returns:
            Layout: The layout with linearly topology
        """
        assert qubit_number >= 2, "qubits number should greater than 1"
        linear_layout = Layout(qubit_number, layout_type=LayoutType.linear)
        if error_rate is None:
            error_rate = [1.0] * (qubit_number - 1)

        assert len(error_rate) == (qubit_number - 1)
        for i in range(qubit_number - 1):
            linear_layout.add_edge(i, i + 1, directional, error_rate[i])

        return linear_layout

    @staticmethod
    def grid_layout(
        qubit_number: int,
        width: int = None,
        unreachable_nodes: list = [],
        directional: bool = DIRECTIONAL_DEFAULT,
        error_rate: list = None
    ):
        """ Get Grid Structure Topology.

        Args:
            qubit_number(int): the number of qubits
            width (int, optional): The width of grid layout. Defaults to None.
            unreachable_nodes (list, optional): The nodes which are not work. Defaults to [].
            directional (bool, optional): Whether the edge is directional. Defaults to DIRECTIONAL_DEFAULT.
            error_rate (list, optional): Error rate for each edge, default 1.0. Defaults to [].
                WARNING: The error rate is for each valid edges from top to bottom, left to right. Please make sure
                you know exactly every edges' position and rate.

        Returns:
            Layout: The layout with grid topology
        """
        assert qubit_number >= 2, "qubits number should greater than 1"
        grid_layout = Layout(qubit_number, layout_type=LayoutType.grid, unreachable_nodes=unreachable_nodes)
        exist_unreachable_nodes = len(unreachable_nodes) != 0
        grid_width = int(log2(qubit_number)) if width is None else width
        error_rate = [1] * (qubit_number * 4) if error_rate is None else error_rate
        edge_idx = 0
        for s in range(0, qubit_number - 1):
            horizontal_exist, vertical_exist = True, True
            u, hv, vv = s, s + 1, s + grid_width
            if exist_unreachable_nodes:
                if u in unreachable_nodes:
                    continue

                if hv in unreachable_nodes:
                    horizontal_exist = False

                if vv in unreachable_nodes:
                    vertical_exist = False

            # horizontal line draw
            if hv % grid_width != 0 and horizontal_exist:
                grid_layout.add_edge(u, hv, directional, error_rate[edge_idx])
                edge_idx += 1

            # vertical line draw
            if vv < qubit_number and vertical_exist:
                grid_layout.add_edge(u, vv, directional, error_rate[edge_idx])
                edge_idx += 1

        # TODO: not finish the shape
        grid_layout._width = grid_width
        return grid_layout

    @staticmethod
    def rhombus_layout(
        qubit_number: int,
        width: int = None,
        unreachable_nodes: list = [],
        directional: bool = DIRECTIONAL_DEFAULT,
        error_rate: list = None,
        shape: int = 0
    ):
        """ Get Rhombus Structure Topology.

        Args:
            qubit_number(int): the number of qubits
            width (int, optional): The width of grid layout. Defaults to None.
            unreachable_nodes (list, optional): The nodes which are not work. Defaults to [].
            directional (bool, optional): Whether the edge is directional. Defaults to DIRECTIONAL_DEFAULT.
            error_rate (list, optional): Error rate for each edge, default 1.0. Defaults to [].
                WARNING: The error rate is arranged in order of valid edges, from top to bottom, left to right.
                Please make sure you know exactly every edges' position and rate.
            shape (int, optional): The shape of rhombus; if 0, it will be close shape first; otherwise it will
                be open shape. default to close shape.

        Returns:
            Layout: The layout with rhombus topology
        """
        assert qubit_number >= 2, "qubits number should greater than 1"
        rhombus_layout = Layout(qubit_number, layout_type=LayoutType.rhombus, unreachable_nodes=unreachable_nodes)
        exist_unreachable_nodes = len(unreachable_nodes) != 0
        grid_width = int(log2(qubit_number)) if width is None else width
        error_rate = [1] * (qubit_number * 4) if error_rate is None else error_rate
        edge_idx = 0
        for s in range(0, qubit_number - grid_width + 1):
            vertical_exist, rhombus_exist = True, True
            # horizontal line draw
            u, lv, rv = s, s + grid_width, s + grid_width + (-1) ** (s // grid_width)
            if exist_unreachable_nodes:
                if u in unreachable_nodes:
                    continue

                if lv in unreachable_nodes:
                    vertical_exist = False

                if rv in unreachable_nodes:
                    rhombus_exist = False

            # vertical line draw
            if lv < qubit_number and vertical_exist:
                rhombus_layout.add_edge(u, lv, directional, error_rate[edge_idx])
                edge_idx += 1

            # rhombus line draw
            if rv < qubit_number and u // grid_width + 1 == rv // grid_width and rhombus_exist:
                rhombus_layout.add_edge(u, rv, directional, error_rate[edge_idx])
                edge_idx += 1

        rhombus_layout._width = grid_width
        rhombus_layout._rhombus_shape = shape
        return rhombus_layout

    def draw(self, mode: str = None):
        """ Visualization of the topology structure.

        Args:
            mode (str): The mode of topology, should be one of [random, grid, linear, circuit, rhombus];
                default to be grid.
        """
        from QuICT.tools.display import layout_drawer

        if mode is not None:
            mode_list = ["random", "grid", "linear", "circuit", "rhombus"]
            if mode not in mode_list:
                raise ValueError(
                    f"unsupport layout mode {mode}. Please use one of [random, grid, linear, circuit, rhombus]."
                )
        else:
            mode = "random" if self.layout_type == LayoutType.normal else self.layout_type.name

        layout_drawer(self, mode)
