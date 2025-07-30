"""
A mapping algorithm by solving subgraph isomorphism problem with VF2.
"""

import random
from typing import Union

import networkx as nx
import numpy as np
from networkx.algorithms.isomorphism import GraphMatcher

from QuICT.core.circuit import Circuit
from QuICT.core.gate import CompositeGate
from QuICT.core.layout import Layout
from QuICT.core.virtual_machine import VirtualQuantumMachine


class VF2Mapping:
    """
    A mapping algorithm to map a logic circuit onto a physical quantum circuit, as
    a subgraph isomorphism problem, solved by VF2++.
    Be careful the isomorphic algorithm may timeout when running on large and random circuits.

    Examples:
        >>> from QuICT.core import Layout
        >>> from QuICT.qcda.mapping import VF2Mapping
        >>> layout = Layout.load_file("example/layout/ibmqx2_layout.json")
        >>> vf2 = VF2Mapping(layout)
        >>> mapping_circuit = vf2.execute(circuit)
    """

    @property
    def logic2phy(self) -> list:
        return self._logic2phy

    @property
    def phy2logic(self) -> list:
        return self._phy2logic

    def __init__(self, layout_info: Union[Layout, VirtualQuantumMachine]):
        self._layout = layout_info if isinstance(layout_info, Layout) else layout_info.layout
        self._gate_fidelity = None if isinstance(layout_info, Layout) else layout_info.gate_fidelity
        self._edge_fidelity = self._layout.double_gate_fidelity
        self._layout_graph = self._get_layout_graph()
        self._logic2phy = []
        self._phy2logic = [-1 for _ in range(self._layout.qubit_number)]

    def execute(self, circuit: Union[Circuit, CompositeGate]) -> Circuit:
        unreachable_nodes = len(self._layout.unreachable_nodes) if self._layout.unreachable_nodes else 0
        assert (
            circuit.width() <= self._layout.qubit_number - unreachable_nodes
        ), "The width of circuit should not be greater than the number of qubits of the layout."
        mapping = self._get_mapping_rule(circuit)
        ans_circuit = Circuit(self._layout.qubit_number)
        for gate in circuit.flatten_gates():
            gate_args = gate.cargs + gate.targs
            mapping_gate = gate.copy() & [mapping[qubit] for qubit in gate_args]
            mapping_gate | ans_circuit
        return ans_circuit

    def _get_layout_graph(self) -> nx.Graph:
        graph = nx.Graph()
        for i in range(self._layout.qubit_number):
            if self._layout.unreachable_nodes and i in self._layout.unreachable_nodes:
                continue
            if self._gate_fidelity:
                assert 0 <= self._gate_fidelity[i] <= 1, ValueError("The gate fidelity should in the range of [0, 1].")
            graph.add_node(i)
        for edge in self._layout:
            if self._edge_fidelity:
                try:
                    assert (
                        self._edge_fidelity[edge.u][edge.v] is not None
                        and 0 <= self._edge_fidelity[edge.u][edge.v] <= 1
                    )
                except:
                    raise ValueError("The double gate fidelity provided is incomplete.")
            graph.add_edge(edge.u, edge.v)
        return graph

    def _get_circuit_info(self, circuit: Union[Circuit, CompositeGate]):
        graph = nx.Graph()
        cir_gate_info = {"single": 0, "double": 0}
        weighted_nodes = [0] * circuit.width()
        weighted_edges = {}
        for gate in circuit.flatten_gates():
            gate_args = tuple(sorted(gate.cargs + gate.targs))
            if gate.is_single():
                cir_gate_info["single"] += 1
                weighted_nodes[gate_args[0]] += 1
            elif len(gate_args) > 2:
                raise ValueError(
                    f"Can't map a circuit with {len(gate_args)}-qubit gate. Please decomposite the circuit first."
                )
            else:
                cir_gate_info["double"] += 1
                graph.add_edge(gate_args[0], gate_args[1])
                if gate_args not in weighted_edges.keys():
                    weighted_edges[gate_args] = 1
                else:
                    weighted_edges[gate_args] += 1
        weighted_edges = dict(sorted(weighted_edges.items(), key=lambda item: item[1], reverse=True))
        weighted_edges = {k: v / cir_gate_info["double"] for k, v in weighted_edges.items()}

        if cir_gate_info["single"] > 0:
            weighted_nodes = [w / cir_gate_info["single"] for w in weighted_nodes]
        return graph, weighted_edges, weighted_nodes, cir_gate_info

    def _get_mapping_score(self, mapping, circuit_graph, weighted_edges, weighted_nodes, cir_gate_info):
        node_score = 1
        edge_score = 1
        node_weight = cir_gate_info["single"] / (cir_gate_info["single"] + cir_gate_info["double"])
        edge_weight = cir_gate_info["double"] / (cir_gate_info["single"] + cir_gate_info["double"])
        if self._gate_fidelity:
            node_score = 0
            for node in list(mapping.keys()):
                node_score += self._gate_fidelity[node] * weighted_nodes[mapping[node]]
        if self._edge_fidelity:
            edge_score = 0
            cir2layout_mapping = {v: k for k, v in mapping.items()}
            for u, v in circuit_graph.edges():
                edge_score += weighted_edges[(u, v)] * self._edge_fidelity[cir2layout_mapping[u]][cir2layout_mapping[v]]
        score = node_weight * node_score + edge_weight * edge_score
        return score

    def _get_mapping_rule(self, circuit) -> dict:
        circuit_graph, weighted_edges, weighted_nodes, cir_gate_info = self._get_circuit_info(circuit)
        matcher = GraphMatcher(self._layout_graph, circuit_graph)
        assert matcher.subgraph_is_isomorphic(), ValueError("Subgraph is not isomorphic, can't use VF2 mapping.")
        max_score = 0
        best_mapping = None
        mappings = matcher.subgraph_isomorphisms_iter()
        for mapping in mappings:
            if self._edge_fidelity is None:
                best_mapping = mapping
                break
            score = self._get_mapping_score(mapping, circuit_graph, weighted_edges, weighted_nodes, cir_gate_info)
            if score > max_score:
                max_score = score
                best_mapping = mapping
        # Deal with isolates
        circuit_graph.add_nodes_from(list(range(circuit.width())))
        isolate_qubits = list(nx.isolates(circuit_graph))
        if len(isolate_qubits) > 0:
            remaining_nodes = list(set(self._layout_graph.nodes()) - set(best_mapping.keys()))
            if self._gate_fidelity is None:
                chosed_nodes = random.sample(remaining_nodes, len(isolate_qubits))
            else:
                chosed_nodes = np.array(remaining_nodes)[
                    np.array(self._gate_fidelity)[remaining_nodes].argsort()[-len(isolate_qubits) :]
                ]
            for k, v in zip(chosed_nodes, isolate_qubits):
                best_mapping[k] = v
        result_mapping = {}
        self._logic2phy = [-1 for _ in range(circuit.width())]
        for k, v in best_mapping.items():
            result_mapping[v] = k
            self._logic2phy[v] = k
            self._phy2logic[k] = v
        return result_mapping
