import os
from math import log2, ceil

import networkx as nx
import matplotlib.pyplot as plt


def layout_drawer(layout, mode: str = "random"):
    """ Draw the graph about the given layout.

    Args:
        layout (Layout): The given topology structure.
        mode (str): The mode of topology, should be one of [random, grid, linear, circuit, rhombus];
            default to be random.
    """
    G = nx.Graph()
    for edge in layout.edge_list:
        G.add_edge(edge.u, edge.v)

    if mode == "grid":
        width = int(log2(layout.qubit_number)) if layout._width == -1 else layout._width
        length = int(ceil(layout.qubit_number / width))
        min_wid, min_len = -1, 1
        width_interval, length_interval = 2 / (width - 1), 2 / (length - 1)
        pos = {}
        for i in range(length):
            i_length = min_len - (i * length_interval)
            for j in range(width):
                q_idx = i * width + j
                if q_idx >= layout.qubit_number:
                    break

                i_width = min_wid + (j % width * width_interval)
                pos[q_idx] = [i_width, i_length]
    elif mode == "linear":
        min_wid, width_interval = -1, 1.8 / layout.qubit_number
        pos = {}
        for i in range(layout.qubit_number):
            pos[i] = [min_wid + i * width_interval, 0]
    elif mode == "rhombus":
        width = int(log2(layout.qubit_number)) if layout._width == -1 else layout._width
        length = int(ceil(layout.qubit_number / width))
        min_wid, min_len = -1, 1
        width_interval, length_interval = 2 / width, 2 / (length - 1)
        pos = {}
        for i in range(length):
            i_length = min_len - (i * length_interval)
            for j in range(width):
                q_idx = i * width + j
                if q_idx >= layout.qubit_number:
                    break

                i_width = min_wid + (j % width * width_interval)
                if i % 2 == 0:
                    i_width += width_interval / 2
                pos[q_idx] = [i_width, i_length]
    elif mode == "circuit":
        pos = nx.circular_layout(G)
    elif mode == "random":
        pos = nx.spring_layout(G)
    else:
        raise KeyError(f"Unsupportted topology mode {mode}, please choice one of [random, grid, linear]")

    nx.draw(G, pos, with_labels=True)
    plt.show()


def layout_graph_drawer(vqm_name: str = None, layout=None):
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout_graph")
    files_name = [fname[:-4] for fname in os.listdir(folder_path)]

    if vqm_name not in files_name:
        layout.draw()
    else:
        print(os.path.join(folder_path, f"{vqm_name}.png"))
        image = plt.imread(os.path.join(folder_path, f"{vqm_name}.png"))
        plt.imshow(image)
        plt.show()
