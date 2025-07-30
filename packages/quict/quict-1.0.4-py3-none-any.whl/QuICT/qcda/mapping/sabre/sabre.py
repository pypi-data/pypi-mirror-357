import copy
from typing import List, Union

import numpy as np
from QuICT.core import Circuit
from QuICT.core.gate import Swap, GateType, CX
from QuICT.core.layout import Layout
from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.qcda.mapping.common import InitialMapping
from QuICT.tools.exception.core import TypeError


class AnsGroup:
    """
    The Ans of SABRE algorithm
    """

    def __init__(
        self,
        initial_l2p,
        final_l2p,
        ans,
    ):
        self.initial_l2p = copy.deepcopy(initial_l2p)
        self.final_l2p = copy.deepcopy(final_l2p)
        self.ans = ans

    def size(self):
        return len(self.ans)


class RatedSwap:
    """
    Swap gates with sabre score
    """

    def __init__(self, u=0, v=0, score=0, field=0):
        self.u = u
        self.v = v
        self.score = score
        self.field = field


class PendingGate:
    """
    gates to be dealt
    """

    def __init__(self, gate, gateid):
        self.gate = gate
        self.gateid = gateid
        self.attach_ids = []
        self.next_ids = []
        self.uv = gate.cargs + gate.targs


class AnsGate:
    """
    ans gates
    """

    def __init__(
        self,
        u,
        v,
        gate=None,
        bridge=None
    ):
        self.u = u
        self.v = v
        self.gate = gate
        self.bridge = bridge


class SABREMapping:
    """
    Mapping with the heuristic algorithm DSWO, which is based on SABRE

    References:
        [1] `Tackling the qubit mapping problem for NISQ-era quantum devices`
        <https://arxiv.org/abs/1809.02573>

    Examples:
        >>> from QuICT.core import Layout
        >>> from QuICT.qcda.mapping import SABREMapping
        >>> layout = Layout.load_file("example/layout/ibmqx2_layout.json")
        >>> sabre = SABREMapping(layout)
        >>> circuit_map = sabre.execute(circuit)
        >>> circuit_initial_map = sabre.logic2phy
    """

    def __init__(
        self,
        layout_info: Union[Layout, VirtualQuantumMachine],
        field_mode: bool = True,
        sizeE: int = 20,
        w: float = 0.5,
        decay_coff: float = 0.001,
        decay_reset_time: int = 5,
        greedy_strategy: int = 3,
        initial_iterations: int = 1,
        repeat_iterations: int = 1,
        swap_iterations: int = 1,
        seed: int = -1
    ):
        """
        Args:
            layout_info (Union[Layout, VirtualQuantumMachine]): the layout of the physical quantum circuit or
            the virtual quantum machine with more information.
            sizeE (int): the size of the extended set, default 20
            field_mode (bool): the edge with high field will be chosen
                preferentially if the field_mode is opened, default true
            w (float): the weight of the extended set, default 0.5
            decay_coff (float): the decay parameter of the SABRE algorithm,
                default 0.001
            decay_reset_time (int): the reset time of decay array, default 5
            greedy_strategy (int): the parameter of greedy strategy (0 means
                not use the strategy), default 0
            initial_iterations (int): times for which SABRE algorithm would
                repeat to find better initial mapping, default 1
            repeat_iterations (int): times for which SABRE algorithm would
                repeat to execute sabre initial mapping, default 0
            swap_iterations (int): iterations for which SABRE algorithm would
                repeat to find better mapping, default 1
        """
        self._layout = layout_info if isinstance(layout_info, Layout) else layout_info.layout
        self._field_mode = field_mode
        self.unreachable_nodes = [] if self._layout.unreachable_nodes is None else self._layout.unreachable_nodes
        self.double_gate_fidelity = self._layout.double_gate_fidelity
        self._sizeE = sizeE
        self._w = w
        self._decay_coff = decay_coff
        self._decay_reset_time = decay_reset_time
        self._greedy_strategy = greedy_strategy
        self.initial_iterations = initial_iterations
        self.repeat_iterations = repeat_iterations
        self.swap_iterations = swap_iterations

        self._sample_eps = 1e-10
        self._field_eps = 0.001
        self._build_layout_information()
        self.remained_nodes = [node for node in range(self._layout.qubit_number) if node not in self.unreachable_nodes]

        # Initial Mapping
        self._initial_mapping = InitialMapping(layout_info,)

    def _build_layout_information(self):
        self.qubit_number = self._layout.qubit_number
        self.connected_edges = []
        self.dist = []
        self.adj_matrix = [[False for _ in range(self.qubit_number)] for _ in range(self.qubit_number)]
        self.field = [[0 for _ in range(self.qubit_number)] for _ in range(self.qubit_number)]

        for edge in self._layout.edge_list:
            self.adj_matrix[edge.u][edge.v] = True
            self.adj_matrix[edge.v][edge.u] = True

        def is_connected():
            visited = [False] * self.qubit_number

            def dfs(node):
                visited[node] = True
                for neighbor in range(self.qubit_number):
                    if self.adj_matrix[node][neighbor] and not visited[neighbor]:
                        dfs(neighbor)
            dfs(0)
            return all(visited)

        if not is_connected():
            def find_largest_connected_component():
                visited = [False] * self.qubit_number
                largest_component = []

                def dfs(node):
                    stack = [node]
                    component = []
                    while stack:
                        current = stack.pop()
                        if not visited[current]:
                            visited[current] = True
                            component.append(current)
                            for neighbor in range(self.qubit_number):
                                if self.adj_matrix[current][neighbor] and not visited[neighbor]:
                                    stack.append(neighbor)
                    return component

                for node in range(self.qubit_number):
                    if not visited[node]:
                        component = dfs(node)
                        if len(component) > len(largest_component):
                            largest_component = component
                return largest_component

            largest_component = find_largest_connected_component()
            extra_nodes = [node for node in range(self.qubit_number) if node not in largest_component]
            for node in extra_nodes:
                if node not in self.unreachable_nodes:
                    self.unreachable_nodes.append(node)

        if self.double_gate_fidelity is not None:
            for u, key in self.double_gate_fidelity.items():
                for v, rate in key.items():
                    self.field[u][v] = rate
                    self.field[v][u] = rate
        else:
            for i in range(self.qubit_number):
                for j in range(self.qubit_number):
                    if i == j or self.adj_matrix[i][j]:
                        self.field[i][j] = 1

        qubit_number = self.qubit_number
        for i in range(qubit_number):
            dist = []
            connected_edges = []
            for j in range(qubit_number):
                if i == j:
                    dist.append(0)
                else:
                    if self.adj_matrix[i][j]:
                        dist.append(1)
                        connected_edges.append(j)
                    else:
                        dist.append(qubit_number * 2)
            self.dist.append(dist)
            self.connected_edges.append(connected_edges)

        for k in range(qubit_number):
            for i in range(qubit_number):
                if i == k:
                    continue
                for j in range(qubit_number):
                    if j == k or j == i:
                        continue
                    self.dist[i][j] = min(self.dist[i][j], self.dist[i][k] + self.dist[k][j])

    def set_circuit_information(self, pgates, pre_number, flayer):
        self.pendingGates = pgates
        self.pre_number = copy.deepcopy(pre_number)
        self.front_layer = copy.deepcopy(flayer)

    def _build_circuit_information(self, circuit: Circuit):
        gateid = 0
        pendingGates = []
        pre_numbers = [0]
        initialGates = []
        front_layer = set()

        gates = circuit.flatten_gates(no_copy=True)

        pre_gate: List[None, PendingGate] = [None for _ in range(self.qubit_number)]
        # pre_numbers = [0 for _ in range(circuit.size())]

        for gate in gates:
            bit_number = gate.targets + gate.controls
            assert bit_number == 1 or bit_number == 2, TypeError(
                "sabre input gates", "1q or 2q gates", f"{bit_number}q gates"
            )
            gateid += 1

            pendingGate = PendingGate(gate, gateid)
            pendingGates.append(pendingGate)
            pre_number = 0
            if bit_number == 1:
                u = gate.targ
                if pre_gate[u] is not None:
                    pre_gate[u].attach_ids.append(gateid)
                else:
                    initialGates.append((gate, u, -1))
            else:
                uv = gate.cargs + gate.targs
                for u in uv:
                    preGates = pre_gate[u]
                    if preGates is not None:
                        if gateid not in preGates.next_ids:
                            preGates.next_ids.append(gateid)
                            pre_number += 1

                pre_gate[uv[0]] = pendingGate
                pre_gate[uv[1]] = pendingGate
                if pre_number == 0:
                    front_layer.add(gateid)
            pre_numbers.append(pre_number)

        return pendingGates, pre_numbers, initialGates, front_layer

    def _add_ans_2qgate(self, gate):
        uv = gate.uv
        u, v = self.logic2phy[uv[0]], self.logic2phy[uv[1]]
        ans_gate = AnsGate(u, v, gate.gate)
        self.ans_gates.append(ans_gate)

    def _add_ans_1qgate(self, gate):
        u = gate.uv[0]
        ans_gate = AnsGate(self.logic2phy[u], -1, gate.gate)
        self.ans_gates.append(ans_gate)

    def _add_ans_swapgate(self, u, v):
        ans_gate = AnsGate(u, v)
        self.ans_gates.append(ans_gate)

    def _add_bridge_gate(self, gate: PendingGate):
        uv = gate.uv
        fixed_u, fixed_v = self.logic2phy[uv[0]], self.logic2phy[uv[1]]
        cp_u = self.connected_edges[fixed_u]
        cp_v = self.connected_edges[fixed_v]
        bridge_point = list(set(cp_u) & set(cp_v))[0]
        ans_gate = AnsGate(fixed_u, fixed_v, bridge=bridge_point)
        self.ans_gates.append(ans_gate)

    def _preprocessing_H(self):
        preprocessing_h = 0
        weight_gates = [[] for _ in range(self.qubit_number)]
        e_queue = []

        f_count = len(self.front_layer)
        for gateid in self.front_layer:
            uv = self.pendingGates[gateid - 1].uv
            preprocessing_h += self.dist[self.logic2phy[uv[0]]][self.logic2phy[uv[1]]] / f_count
            weight_gates[self.logic2phy[uv[0]]].append((gateid, 1.0 / f_count))
            weight_gates[self.logic2phy[uv[1]]].append((gateid, 1.0 / f_count))
            e_queue.append(gateid)

        e_set = []
        dec_queue = []
        while len(e_set) < self._sizeE and len(e_queue):
            gateid = e_queue.pop()
            gate = self.pendingGates[gateid - 1]
            dec_queue.append(gateid)
            for succid in gate.next_ids:
                succ = self.pendingGates[succid - 1]
                self.pre_number[succ.gateid] -= 1
                assert self.pre_number[succ.gateid] >= 0
                if self.pre_number[succ.gateid] == 0:
                    e_set.append(succid)
                    e_queue.append(succid)

        if len(e_set) > self._sizeE:
            e_set = e_set[:self._sizeE]

        e_count = len(e_set)
        for gateid in e_set:
            uv = self.pendingGates[gateid - 1].uv
            preprocessing_h += self.dist[self.logic2phy[uv[0]]][self.logic2phy[uv[1]]] / e_count * 0.5
            weight_gates[self.logic2phy[uv[0]]].append((gateid, 0.5 / e_count))
            weight_gates[self.logic2phy[uv[1]]].append((gateid, 0.5 / e_count))

        for gateid in dec_queue:
            for succid in self.pendingGates[gateid - 1].next_ids:
                self.pre_number[succid] += 1

        self.weight_gates = weight_gates
        self.preprocessing_h = preprocessing_h

    def _calculate_bridge_value(self, endpoint_u, endpoint_v, next_gids):
        bridge_point = -1
        neigh = self.connected_edges[endpoint_u]
        for temp_bp in neigh:
            if endpoint_v in self.connected_edges[temp_bp]:
                bridge_point = temp_bp
                break

        assert bridge_point != -1, f"Failure to find bridge point, from {endpoint_u} to {endpoint_v}."

        is_bridge = False
        endpoints = [endpoint_u, endpoint_v]
        connected_gids = copy.deepcopy(next_gids)
        # print(bridge_point)
        for _ in range(5):
            next_next_gids = []
            for gid in connected_gids:
                next_gate: PendingGate = self.pendingGates[gid - 1]
                next_gate_uv = next_gate.uv
                next_u, next_v = self.logic2phy[next_gate_uv[0]], self.logic2phy[next_gate_uv[1]]

                origin_connected = self.adj_matrix[next_u][next_v]
                if next_u in endpoints and next_v in endpoints:
                    bridge_connected = (self.adj_matrix[next_u][bridge_point] or self.adj_matrix[next_v][bridge_point])
                elif next_u in endpoints:
                    if next_v == bridge_point:
                        return True

                    bridge_connected = self.adj_matrix[next_u][bridge_point]
                elif next_v in endpoints:
                    if next_u == bridge_point:
                        return True

                    bridge_connected = self.adj_matrix[next_v][bridge_point]
                else:
                    continue

                # print(f"{next_u}, {next_v}, {origin_connected}, {bridge_connected}")
                if origin_connected and not bridge_connected:
                    return True
                elif not origin_connected and bridge_connected:
                    return False

                next_next_gids.extend(next_gate.next_ids)

            connected_gids = copy.deepcopy(next_next_gids)

        return is_bridge

    def _can_execute(self, gate: PendingGate):
        uv = gate.uv
        return self.adj_matrix[self.logic2phy[uv[0]]][self.logic2phy[uv[1]]]

    def _can_bridge(self, gate: PendingGate):
        if gate.gate.type != GateType.cx:
            return False

        uv = gate.uv
        fixed_u, fixed_v = self.logic2phy[uv[0]], self.logic2phy[uv[1]]
        if self.dist[fixed_u][fixed_v] != 2:
            return False

        # validate bridge cost
        return self._calculate_bridge_value(fixed_u, fixed_v, gate.next_ids)

    def _execute_2q_gates(self):
        while True:
            exe_gate_list = []
            for gateid in self.front_layer:
                gate: PendingGate = self.pendingGates[gateid - 1]
                if self._can_execute(gate):
                    exe_gate_list.append(gateid)
                    self._add_ans_2qgate(gate)
                    for attachid in gate.attach_ids:
                        attach_gate = self.pendingGates[attachid - 1]
                        self._add_ans_1qgate(attach_gate)
                elif self._can_bridge(gate):
                    exe_gate_list.append(gateid)
                    self._add_bridge_gate(gate)
                    for attachid in gate.attach_ids:
                        attach_gate = self.pendingGates[attachid - 1]
                        self._add_ans_1qgate(attach_gate)

            if len(exe_gate_list) == 0:
                break
            for gateid in exe_gate_list:
                self.front_layer.remove(gateid)
                gate = self.pendingGates[gateid - 1]
                for next_id in gate.next_ids:
                    succ: PendingGate = self.pendingGates[next_id - 1]
                    self.pre_number[succ.gateid] -= 1
                    assert self.pre_number[succ.gateid] >= 0
                    if self.pre_number[succ.gateid] == 0:
                        self.front_layer.add(succ.gateid)

    def _rated_swap(self, u, v):
        preprocessing_h = self.preprocessing_h
        for weight_gate in self.weight_gates[u]:
            coff = weight_gate[1]
            uv = self.pendingGates[weight_gate[0] - 1].uv

            vv = self.logic2phy[uv[0]]
            if vv == u:
                vv = self.logic2phy[uv[1]]
            if vv == v:
                continue
            preprocessing_h += coff * (self.dist[v][vv] - self.dist[u][vv])

        for weight_gate in self.weight_gates[v]:
            coff = weight_gate[1]
            uv = self.pendingGates[weight_gate[0] - 1].uv

            uu = self.logic2phy[uv[0]]
            if uu == v:
                uu = self.logic2phy[uv[1]]
            if uu == u:
                continue
            preprocessing_h += coff * (self.dist[u][uu] - self.dist[v][uu])
        preprocessing_h *= max(self.decay[u], self.decay[v])
        return RatedSwap(u, v, preprocessing_h, self.field[u][v])

    def _obtain_swaps(self):
        self._preprocessing_H()
        swaps = []
        bits = set()
        for gateid in self.front_layer:
            uv = self.pendingGates[gateid - 1].uv
            bits.add(self.logic2phy[uv[0]])
            bits.add(self.logic2phy[uv[1]])
        for u in bits:
            for v in self.connected_edges[u]:
                if u in bits or v in bits:
                    rated_swap = self._rated_swap(u, v)
                    swaps.append(rated_swap)

        return swaps

    def _execute_swap(self, u, v):
        self.logic2phy[self.phy2logic[u]] = v
        self.logic2phy[self.phy2logic[v]] = u

        t = self.phy2logic[u]
        self.phy2logic[u] = self.phy2logic[v]
        self.phy2logic[v] = t

        self._add_ans_swapgate(u, v)

    def _find_shortest_path(self):
        shortest = self.qubit_number * self.qubit_number
        u = 0
        v = 0
        for front_id in self.front_layer:
            uv = self.pendingGates[front_id - 1].uv

            if self.dist[self.logic2phy[uv[0]]][self.logic2phy[uv[1]]] < shortest:
                u = self.logic2phy[uv[0]]
                v = self.logic2phy[uv[1]]
                shortest = self.dist[u][v]

        assert u != v, f"{u}, {v}, {self.logic2phy}"

        pre = [-1 for _ in range(self.qubit_number)]
        dist = [self.qubit_number * self.qubit_number for _ in range(self.qubit_number)]

        queues = [u]
        dist[u] = 0
        while len(queues) > 0:
            head = queues.pop()
            for goal in self.connected_edges[head]:
                if pre[goal] == -1:
                    queues.append(goal)
                if dist[head] + 1 < dist[goal]:
                    dist[goal] = dist[head] + 1
                    pre[goal] = head
                if goal == v:
                    break
            if pre[v] != -1:
                break
        now = v
        path = [now]
        while pre[now] != u:
            goal = pre[now]
            path.append(goal)
            now = goal
        path.append(u)
        i = 0
        j = len(path) - 1
        while i + 1 < j:
            self._execute_swap(path[i], path[i + 1])
            i += 1
            if i + 1 >= j:
                break
            self._execute_swap(path[j], path[j - 1])
            j -= 1
        self._execute_2q_gates()

    def _check_greedy_strategy(self):
        if len(self.ans_gates) == 0:
            return
        last_index = len(self.ans_gates) - 1
        nowGate = self.ans_gates[last_index]
        last_index -= 1
        if nowGate.gate is not None:
            return
        count = self._greedy_strategy - 1
        while last_index >= 0 and count > 0:
            newGate = self.ans_gates[last_index]
            if newGate.gate is not None:
                return
            if (newGate.u == nowGate.u and newGate.v == nowGate.v) or (
                newGate.u == nowGate.v and newGate.v == nowGate.u
            ):
                self._find_shortest_path()
                return
            count -= 1
            last_index -= 1

    def _execute_rated_swap(self, rated_swap: RatedSwap):
        u, v = rated_swap.u, rated_swap.v
        self._execute_swap(u, v)
        self.decay[u] += self._decay_coff
        self.decay[v] += self._decay_coff
        self.decay_time += 1

        if self.decay_time % self._decay_reset_time == 0:
            self.decay = [1 for _ in range(self.qubit_number)]
        if self._greedy_strategy > 0:
            self._check_greedy_strategy()

    def _execute_once(self):
        self.ans_gates = []
        self.decay = [1 for _ in range(self._layout.qubit_number)]
        self.decay_time = 0
        self._execute_2q_gates()
        if len(self.front_layer) == 0:
            return

        history_selection = []
        while True:
            rated_swaps = self._obtain_swaps()
            rated_swaps.sort(key=lambda x: x.score)
            assert len(rated_swaps) > 0
            score = rated_swaps[0].score

            i = 0
            for swap in rated_swaps:
                if np.abs(swap.score - score) > self._sample_eps:
                    break
                i += 1
            if i > 1:
                if self._field_mode:
                    rated_swaps = rated_swaps[:i]
                    rated_swaps.sort(key=lambda x: x.field, reverse=True)
                    field = rated_swaps[0].field
                    i = 0
                    for swap in rated_swaps:
                        if np.abs(swap.field - field) > self._field_eps:
                            break
                        i += 1
                    selected_swap = np.random.choice(rated_swaps[:i])
                else:
                    selected_swap = np.random.choice(rated_swaps[:i])

            else:
                selected_swap = rated_swaps[0]

            for re_select_idx in range(len(rated_swaps)):
                exist_repeated = False
                for h_swap in history_selection:
                    if selected_swap.u in h_swap and selected_swap.v in h_swap:
                        exist_repeated = True
                        break

                if exist_repeated:
                    selected_swap = rated_swaps[re_select_idx]
                else:
                    break

            self._execute_rated_swap(rated_swap=selected_swap)
            self._execute_2q_gates()
            if len(self.front_layer) == 0:
                return

            if self.ans_gates[-1].gate is None:
                history_selection.append((selected_swap.u, selected_swap.v))
            else:
                history_selection = []

    def _calculate_ans_group_size(self, ans_group: list):
        count = 0
        for agate in ans_group:
            if agate.gate is not None:
                count += 1
            elif agate.bridge is not None:
                count += 4
            else:
                count += 3

        return count

    def _execute_routing(self, logic2phy):
        ansGroup = None
        pre_numbers = copy.deepcopy(self.pre_number)
        front_layer = copy.deepcopy(self.front_layer)

        initial_mapping = copy.deepcopy(logic2phy)
        self.logic2phy: list = copy.deepcopy(logic2phy)
        self.phy2logic = [0 for _ in range(self.qubit_number)]
        for i in range(len(self.logic2phy)):
            self.phy2logic[self.logic2phy[i]] = i

        best_ans_size = 0
        for _ in range(self.swap_iterations):
            self.pre_number = copy.deepcopy(pre_numbers)
            self.front_layer = copy.deepcopy(front_layer)
            self._execute_once()
            size_result = self._calculate_ans_group_size(self.ans_gates)

            if ansGroup is None or best_ans_size > size_result:
                ansGroup = AnsGroup(initial_mapping, self.logic2phy, self.ans_gates)
                best_ans_size = size_result

        return ansGroup, best_ans_size

    def _set_initial_mapping(self, initial_mapping, circuit_width):
        self._outer_pointer, self._inner_pointer = [], []
        for m_point in initial_mapping[:circuit_width]:
            point_neighbour = self._layout.out_edges(m_point, True)
            count_neighbour_in_mapping = 0
            for npoint in point_neighbour:
                if npoint in initial_mapping:
                    count_neighbour_in_mapping += 1

            if len(point_neighbour) == 1 or count_neighbour_in_mapping == 1:
                self._outer_pointer.append(m_point)
            else:
                self._inner_pointer.append(m_point)

        for i_point in self._inner_pointer:
            p_nei = self._layout.out_edges(i_point, True)
            for npoint in p_nei:
                if (
                    npoint not in self._outer_pointer and
                    npoint not in self._inner_pointer and
                    npoint not in self.unreachable_nodes
                ):
                    self._outer_pointer.append(npoint)

    def _analysis_connection(self, ansgroup):
        im_layout = Layout(self.qubit_number)
        swap_num = 0
        bridge_num = 0
        for ans_gate in ansgroup.ans:
            ans_gate: AnsGate
            if ans_gate.v == -1:
                continue

            u, v = ans_gate.u, ans_gate.v
            if not im_layout.check_edge(u, v):
                im_layout.add_edge(u, v, error_rate=0)

            target_edge = im_layout.get_edge(u, v)
            if ans_gate.gate is None:
                if ans_gate.bridge is None:
                    target_edge.error_rate += 1
                    swap_num += 1
                else:
                    target_edge.error_rate += 0.5
                    bridge_num += 1

        return swap_num, bridge_num, im_layout

    def execute(self, circuit):
        circuit_copy = Circuit(circuit.width())
        circuit | circuit_copy
        reverse_circuit = circuit_copy.inverse()

        # Build Circuit Information
        ori_pgates, ori_pnum, ori_igates, ori_flayer = self._build_circuit_information(circuit_copy)
        rev_pgates, rev_pnum, _, rev_flayer = self._build_circuit_information(reverse_circuit)

        ansGroup = None
        for _ in range(self.initial_iterations):
            # _, initial_mp = self._initial_mapping.run(circuit_copy)
            initial_mp = np.random.choice(self.remained_nodes, len(self.remained_nodes), replace=False).tolist()
            for i in range(self.repeat_iterations + 1):
                self.set_circuit_information(ori_pgates, ori_pnum, ori_flayer)
                newAnsGroup, new_group_size = self._execute_routing(initial_mp)
                if ansGroup is None or newAnsGroup.size() < ansGroup.size():
                    ansGroup = AnsGroup(newAnsGroup.initial_l2p, newAnsGroup.final_l2p, newAnsGroup.ans)

                if i == self.repeat_iterations:
                    break

                self.set_circuit_information(rev_pgates, rev_pnum, rev_flayer)
                reverse_result, _ = self._execute_routing(newAnsGroup.final_l2p)
                initial_mp = reverse_result.final_l2p

            # swap_num, bridge_num, layout_info = self._analysis_connection(ansGroup)

        self.phy2logic = [0 for _ in range(self.qubit_number)]
        for i in range(len(ansGroup.final_l2p)):
            self.phy2logic[ansGroup.final_l2p[i]] = i
        self.logic2phy = ansGroup.initial_l2p

        ans_circuit = Circuit(self.qubit_number)

        def add_pending_gate(gate, u, v):
            _g = gate.copy()
            if v == -1:
                _g | ans_circuit(u)
            else:
                _g | ans_circuit([u, v])

        def add_ans_gate(ans_gate: AnsGate):
            u, v = ans_gate.u, ans_gate.v
            gate = ans_gate.gate
            bridge = ans_gate.bridge
            if bridge is not None:
                CX | ans_circuit([bridge, v])
                CX | ans_circuit([u, bridge])
                CX | ans_circuit([bridge, v])
                CX | ans_circuit([u, bridge])
            elif gate is None:
                Swap | ans_circuit([u, v])
            else:
                add_pending_gate(gate, u, v)

        for gate_tuple in ori_igates:
            add_pending_gate(gate_tuple[0], ansGroup.initial_l2p[gate_tuple[1]], gate_tuple[2])
        for ans_gate in ansGroup.ans:
            add_ans_gate(ans_gate)

        return ans_circuit

    def execute_without_GA(self, circuit):
        qubit_number = self.qubit_number
        reverse_circuit = Circuit(qubit_number)
        for index in range(len(circuit.gates) - 1, -1, -1):
            _gate = circuit.gates[index]
            _gate | reverse_circuit

        ansGroup = None
        iter_count = 0
        for _ in range(self.initial_iterations):
            initial_mp = np.random.choice(self.remained_nodes, len(self.remained_nodes), replace=False).tolist()
            for i in range(self.repeat_iterations + 1):
                self._build_circuit_information(circuit)
                newAnsGroup, _ = self._execute_routing(initial_mp)
                if ansGroup is None or newAnsGroup.size() < ansGroup.size():
                    ansGroup = AnsGroup(newAnsGroup.initial_l2p, newAnsGroup.final_l2p, newAnsGroup.ans)

                if i == self.repeat_iterations:
                    break

                self._build_circuit_information(reverse_circuit)
                reverse_result, _ = self._execute_routing(newAnsGroup.final_l2p)
                initial_mp = reverse_result.final_l2p

            swap_num = 0
            for ans_gate in ansGroup.ans:
                if ans_gate.gate is None:
                    swap_num += 1

            # print(f"iter {iter_count}: using {swap_num} SWAP Gate, with initial mapping {ansGroup.initial_l2p}")
            # iter_count += 1

        self.phy2logic = [0 for _ in range(self.qubit_number)]
        for i in range(len(ansGroup.final_l2p)):
            self.phy2logic[ansGroup.final_l2p[i]] = i
        self.logic2phy = ansGroup.initial_l2p

        ans_circuit = Circuit(self.qubit_number)

        def add_pending_gate(gate, u, v):
            _g = gate.copy()
            if v == -1:
                _g | ans_circuit(u)
            else:
                _g | ans_circuit([u, v])

        def add_ans_gate(ans_gate: AnsGate):
            u, v = ans_gate.u, ans_gate.v
            gate = ans_gate.gate
            if gate is None:
                Swap | ans_circuit([u, v])
            else:
                add_pending_gate(gate, u, v)

        for gate_tuple in self.initialGates:
            add_pending_gate(gate_tuple[0], ansGroup.initial_l2p[gate_tuple[1]], gate_tuple[2])
        for ans_gate in ansGroup.ans:
            add_ans_gate(ans_gate)

        return ans_circuit
