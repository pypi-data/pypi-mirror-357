import random
from typing import Union

import networkx as nx
import numpy as np
from networkx.algorithms.isomorphism import GraphMatcher

from QuICT.core.circuit import Circuit
from QuICT.core.gate import CompositeGate
from QuICT.core.layout import Layout
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.core.utils import GateType


class InitialMapping:
    def __init__(self, layout_info: Union[Layout, VirtualQuantumMachine]):
        self._layout_info = layout_info
        self._layout = layout_info if isinstance(layout_info, Layout) else layout_info.layout
        self._gate_fidelity = None if isinstance(layout_info, Layout) else layout_info.gate_fidelity
        self._edge_fidelity = self._layout.double_gate_fidelity
        self._readout_fidelity = None if isinstance(layout_info, Layout) else layout_info.qubit_fidelity
        self._layout_graph = self._get_layout_graph()

    def run(self, circuit: Union[Circuit, CompositeGate], iterations: int = 10) -> list:
        unreachable_nodes = len(self._layout.unreachable_nodes) if self._layout.unreachable_nodes else 0
        assert (
            circuit.width() <= self._layout.qubit_number - unreachable_nodes
        ), "The width of circuit should not be greater than the number of qubits of the layout."
        circuit_graph, weighted_edges, weighted_nodes, cir_gate_info = self._get_circuit_info(circuit)
        two_bits_best_region, two_bits_mapping_rule = self._get_best_region(
            circuit_graph, weighted_edges, cir_gate_info, iterations
        )

        circuit_graph.add_nodes_from(list(range(circuit.width())))
        one_bit_best_region, one_bit_mapping_rule = self._get_best_isolates(
            circuit_graph, set(two_bits_best_region[0]), weighted_nodes
        )

        initial_region = one_bit_best_region + two_bits_best_region[0]
        mapping_rule = {**two_bits_mapping_rule[0], **one_bit_mapping_rule}
        initial_mapping = [-1] * circuit.width()
        for k, v in mapping_rule.items():
            initial_mapping[v] = k

        unmapped_idx = [i for i, x in enumerate(initial_mapping) if x == -1]
        random_mapped = random.sample(list(set(initial_region) - set(initial_mapping) - set([-1])), len(unmapped_idx))
        for idx, i in zip(unmapped_idx, range(len(unmapped_idx))):
            initial_mapping[idx] = random_mapped[i]
        return initial_region, initial_mapping

    def get_initial_groups(self, circuit: Union[Circuit, CompositeGate], polulation: int, iterations: int = 10) -> list:
        unreachable_nodes = len(self._layout.unreachable_nodes) if self._layout.unreachable_nodes else 0
        assert (
            circuit.width() <= self._layout.qubit_number - unreachable_nodes
        ), "The width of circuit should not be greater than the number of qubits of the layout."
        circuit_graph, weighted_edges, weighted_nodes, cir_gate_info = self._get_circuit_info(circuit)
        two_bits_best_regions, two_bits_mapping_rules = self._get_best_region(
            circuit_graph, weighted_edges, cir_gate_info, iterations, polulation
        )

        initial_regions = []
        initial_mappings = []
        circuit_graph.add_nodes_from(list(range(circuit.width())))
        for two_bits_best_region, two_bits_mapping_rule in zip(two_bits_best_regions, two_bits_mapping_rules):
            one_bit_best_region, one_bit_mapping_rule = self._get_best_isolates(
                circuit_graph, set(two_bits_best_region), weighted_nodes
            )
            initial_region = one_bit_best_region + two_bits_best_region
            mapping_rule = {**two_bits_mapping_rule, **one_bit_mapping_rule}
            initial_mapping = [-1] * circuit.width()
            for k, v in mapping_rule.items():
                initial_mapping[v] = k

            unmapped_idx = [i for i, x in enumerate(initial_mapping) if x == -1]
            random_mapped = random.sample(list(set(initial_region) - set(initial_mapping)), len(unmapped_idx))
            for idx, i in zip(unmapped_idx, range(len(unmapped_idx))):
                initial_mapping[idx] = random_mapped[i]
            initial_regions.append(initial_region)
            initial_mappings.append(initial_mapping)
        return initial_regions, initial_mappings

    def estimate_fidelity(self, circuit: Circuit, initial_mp):
        unreachable_nodes = len(self._layout.unreachable_nodes) if self._layout.unreachable_nodes else 0
        assert (
            circuit.width() <= self._layout.qubit_number - unreachable_nodes
        ), "The width of circuit should not be greater than the number of qubits of the layout."
        if self._layout.unreachable_nodes:
            assert not (
                set(initial_mp) & set(self._layout.unreachable_nodes)
            ), "Initial mapping should not contain unreachable nodes."
        if len(initial_mp) == circuit.width():
            initial_mp = initial_mp
        elif len(initial_mp) == self._layout.qubit_number - unreachable_nodes:
            initial_mp = initial_mp[: circuit.width()]
        else:
            raise ValueError("Invilid initial mapping.")
        circuit_graph, weighted_edges, weighted_nodes, cir_gate_info = self._get_circuit_info(circuit)
        mapping = {}
        for i in range(len(initial_mp)):
            mapping[i] = initial_mp[i]
        score = self._get_mapping_score(mapping, circuit_graph, weighted_edges, weighted_nodes, cir_gate_info)
        return score

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
        cir_gate_info = {"single": 0, "double": 0, "edge": 0, "readout": [0] * circuit.width()}
        weighted_nodes = [0] * circuit.width()
        weighted_edges = {}
        for gate in circuit.flatten_gates():
            gate_args = tuple(sorted(gate.cargs + gate.targs))
            if gate.is_single():
                if gate.type == GateType.measure:
                    cir_gate_info["readout"][gate_args[0]] += 1
                elif gate.type == GateType.barrier:
                    continue
                else:
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
        cir_gate_info["edge"] = graph.number_of_edges()
        weighted_edges = dict(sorted(weighted_edges.items(), key=lambda item: item[1], reverse=True))
        weighted_edges = {k: v / cir_gate_info["double"] for k, v in weighted_edges.items()}

        if cir_gate_info["single"] > 0:
            weighted_nodes = [w / cir_gate_info["single"] for w in weighted_nodes]
        return graph, weighted_edges, weighted_nodes, cir_gate_info

    def _get_wgtgraphs(self, weighted_edges: dict, iterations: int):
        edge_weights = {}
        for key, value in weighted_edges.items():
            if value in edge_weights.keys():
                edge_weights[value].append(key)
            else:
                edge_weights[value] = [key]

        wgtgraphs = []
        best_weight = 0.0
        for _ in range(iterations):
            edges = []
            for key in edge_weights.keys():
                np.random.shuffle(edge_weights[key])
                edges += edge_weights[key]
            wgtgraph = nx.Graph()
            weight = 0.0
            for u, v in edges:
                wgtgraph.add_edge(u, v)
                weight += weighted_edges[(u, v)]
                matcher = GraphMatcher(self._layout_graph, wgtgraph)
                if not matcher.subgraph_is_isomorphic():
                    wgtgraph.remove_edge(u, v)
                    weight -= weighted_edges[(u, v)]
                    wgtgraph.remove_nodes_from(list(nx.isolates(wgtgraph)))
            if abs(weight - best_weight) < 1e-5:
                equal = False
                for graph in wgtgraphs:
                    if nx.utils.graphs_equal(graph, wgtgraph):
                        equal = True
                        break
                if not equal:
                    wgtgraphs.append(wgtgraph)
            elif weight > best_weight:
                best_weight = weight
                wgtgraphs = [wgtgraph]
        return wgtgraphs

    def _get_best_region(
        self, circuit_graph: nx.Graph, weighted_edges: dict, cir_gate_info: dict, iterations: int, population: int = 1
    ):
        cir_2bit_qubits = circuit_graph.number_of_nodes()
        matchers = [GraphMatcher(self._layout_graph, circuit_graph)]
        isomorphic = True
        if not matchers[0].subgraph_is_isomorphic():
            isomorphic = False
            wgtgraphs = self._get_wgtgraphs(weighted_edges, iterations)
            matchers = [GraphMatcher(self._layout_graph, wgtgraph) for wgtgraph in wgtgraphs]

        best_regions = []
        best_mappings = []
        max_scores = []
        for matcher in matchers:
            mappings = matcher.subgraph_isomorphisms_iter()
            for mapping in mappings:
                region = self._get_region(cir_2bit_qubits, mapping, isomorphic)
                if self._gate_fidelity is None and self._edge_fidelity is None:
                    if len(best_mappings) < population:
                        best_regions.append(list(region.nodes()))
                        best_mappings.append(mapping)
                    else:
                        break
                score = self._get_region_score(region, mapping, weighted_edges, cir_gate_info)
                if len(max_scores) < population:
                    best_regions.append(list(region.nodes()))
                    best_mappings.append(mapping)
                    max_scores.append(score)
                else:
                    min_score = min(max_scores)
                    if score > min_score:
                        idx = max_scores.index(min_score)
                        best_regions[idx] = list(region.nodes())
                        best_mappings[idx] = mapping
                        max_scores[idx] = score
        return best_regions, best_mappings

    def _get_region(self, n_qubits: int, mapping: dict, isomorphic: bool) -> nx.Graph:
        mapping_nodes = set(mapping.keys())
        if isomorphic:
            return self._layout_graph.subgraph(mapping_nodes)
        region_nodes = mapping_nodes
        while len(region_nodes) < n_qubits:
            adjacent_nodes = self._sort_adjacent_nodes(mapping_nodes)
            for adj in adjacent_nodes:
                region_nodes.add(adj)
                if len(region_nodes) >= n_qubits:
                    break
        region = self._layout_graph.subgraph(region_nodes)
        return region

    def _sort_adjacent_nodes(self, nodes: set):
        adjacent_nodes = []
        neigbors = set()
        weighted_neigbors = {}
        for node in nodes:
            neigbors = neigbors | (set(self._layout_graph.adj[node]) - set(nodes))
        if self._gate_fidelity is None and self._edge_fidelity is None:
            adjacent_nodes = list(neigbors)
            np.random.shuffle(adjacent_nodes)
            return adjacent_nodes
        for adj in neigbors:
            node_score = self._gate_fidelity[adj] if self._gate_fidelity is not None else 1
            if self._edge_fidelity is None:
                edge_score = 1
            else:
                edge_score = []
                for node in self._layout_graph.adj[adj]:
                    if node in nodes:
                        edge_score.append(self._edge_fidelity[adj][node])
                edge_score = np.average(edge_score)
            score = node_score + edge_score
            if score in weighted_neigbors.keys():
                weighted_neigbors[score].append(adj)
            else:
                weighted_neigbors[score] = [adj]
        weighted_neigbors = dict(sorted(weighted_neigbors.items(), key=lambda item: item[0], reverse=True))
        for score, nodes in weighted_neigbors.items():
            if len(nodes) > 1:
                adjacent_nodes += np.random.shuffle(nodes)
            else:
                adjacent_nodes += nodes
        return adjacent_nodes

    def _get_region_score(self, region: nx.Graph, mapping: dict, weighted_edges: dict, cir_gate_info: dict):
        node_score = 1
        edge_score = 1
        node_weight = cir_gate_info["single"] / (cir_gate_info["single"] + cir_gate_info["double"])
        edge_weight = cir_gate_info["double"] / (cir_gate_info["single"] + cir_gate_info["double"])
        if self._gate_fidelity:
            node_score = np.average([self._gate_fidelity[node] for node in list(region)])
        if self._edge_fidelity:
            weights = []
            double_in_region = 0
            for u, v in region.edges():
                if u in mapping.keys() and v in mapping.keys():
                    cir_edge = tuple(sorted([mapping[u], mapping[v]]))
                    if cir_edge in weighted_edges.keys():
                        double_in_region += weighted_edges[cir_edge]
                        weights.append(weighted_edges[cir_edge] * self._edge_fidelity[u][v])
                else:
                    double_in_region += 1 / cir_gate_info["double"]
                    weights.append(self._edge_fidelity[u][v] / cir_gate_info["double"])
            edge_score = np.sum(weights) / double_in_region
        score = node_weight * node_score + edge_weight * edge_score
        return score

    def _get_mapping_score(
        self, mapping: dict, circuit_graph: nx.Graph, weighted_edges: dict, weighted_nodes: list, cir_gate_info: dict
    ):
        node_score = 1
        edge_score = 1
        readout_score = 1
        node_weight = cir_gate_info["single"] / (cir_gate_info["single"] + cir_gate_info["double"])
        edge_weight = cir_gate_info["double"] / (cir_gate_info["single"] + cir_gate_info["double"])
        readout_info = np.array(cir_gate_info["readout"])
        if self._gate_fidelity:
            node_score = 0
            for log, phy in mapping.items():
                node_score += self._gate_fidelity[phy] * weighted_nodes[log]
        if self._edge_fidelity:
            edge_score = 0
            for u, v in circuit_graph.edges():
                if (mapping[u], mapping[v]) in self._layout_graph.edges():
                    edge_score += self._edge_fidelity[mapping[u]][mapping[v]] * weighted_edges[tuple(sorted([u, v]))]
        readout_qids = np.where(readout_info > 0)[0]
        if self._readout_fidelity and len(readout_qids) > 0:
            readout_score = 0
            for qid in readout_qids:
                readout_score += np.average(self._readout_fidelity[qid]) ** readout_info[qid]
        score = node_weight * node_score + edge_weight * edge_score + readout_score
        return score

    def _get_best_isolates(self, circuit_graph: nx.Graph, used_nodes: set, weighted_nodes: list):
        remaining_nodes = list(set(self._layout_graph.nodes()) - used_nodes)
        # Region is equal to LayoutGraph
        if not remaining_nodes:
            return [], {}
        isolates = list(nx.isolates(circuit_graph))
        isolate_qubits = len(isolates)
        # No isolate nodes
        if isolate_qubits == 0:
            return [], {}

        cir_qubits = circuit_graph.number_of_nodes()
        remaining_nodes = list(set(self._layout_graph.nodes()) - used_nodes)
        if self._gate_fidelity is None:
            # Can choose any one in region
            if len(used_nodes) >= cir_qubits:
                return [], {}
            best_isolates = random.sample(remaining_nodes, cir_qubits - len(used_nodes))
            best_mapping = {k: v for k, v in zip(best_isolates, isolates)}
            return best_isolates, best_mapping
        else:
            sorted_nodes = sorted(
                range(len(self._gate_fidelity)), key=lambda idx: self._gate_fidelity[idx], reverse=True
            )
            choosed_nodes = sorted_nodes[:isolate_qubits]
            best_isolates = set(remaining_nodes) & set(choosed_nodes)
            unmapped_nodes = cir_qubits - len(used_nodes) - len(best_isolates)
            bias = unmapped_nodes
            while unmapped_nodes > 0:
                remaining_nodes = list(set(self._layout_graph.nodes()) - used_nodes - best_isolates)
                choosed_nodes = sorted_nodes[: isolate_qubits + bias]
                best_isolates = best_isolates | (set(remaining_nodes) & set(choosed_nodes))
                unmapped_nodes = cir_qubits - len(used_nodes) - len(best_isolates)
                bias += 1
            sorted_isolates = sorted(isolates, key=lambda idx: weighted_nodes[idx], reverse=True)
            best_mapping = {k: v for k, v in zip(best_isolates, sorted_isolates)}
            return list(best_isolates), best_mapping
