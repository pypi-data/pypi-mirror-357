import numpy as np
import matplotlib.pyplot as plt
from itertools import product


def amplitude_drawer(data: np.ndarray):
    """ Show the simulation result.

    Args:
        data Union[np.ndarray, list]: The result data.
        mode (str): The mode of given data, should be one of [state_vector, density_matrix]
    """
    plt.figure(figsize=(10, 10), dpi=80)
    plt.subplot(1, 1, 1)
    data = np.abs(data)

    N = data.size
    qubits = int(np.log2(N))
    mode = "state_vector" if data.ndim == 1 else "density_matrix"
    if mode == "state_vector":
        indexes = ["{0:0b}".format(i).zfill(qubits) for i in range(N)]
        data_no0, indexes_no0 = remove_zero_value(data, indexes)
        hist = plt.bar(indexes_no0, data_no0, label="State Vector")
        plt.ylabel("Amplitude")
    elif mode == "density_matrix":
        ax = plt.subplot(projection='3d')
        x = [i for i in range(int(np.sqrt(N)))]
        for xx, yy in product(x, x):
            ax.bar3d(
                xx, yy, 0, dx=1, dy=1, dz=data[xx, yy]
            )

        plt.ylabel("State")

    plt.xlabel("State")
    plt.show()


def sample_drawer(data: dict, qubits: int = None):
    """ Histogram of the sample result.

    Args:
        data (dict): The sample result.
    """
    plt.figure(figsize=(10, 10), dpi=80)
    plt.subplot(1, 1, 1)

    sorted_index = sorted(list(data.keys()))
    indexes, counts = [], []
    for s_idx in sorted_index:
        if qubits is None:
            indexes.append("{0:0b}".format(s_idx))
        else:
            indexes.append("{0:0b}".format(s_idx).zfill(qubits))

        counts.append(data[s_idx])

    hist = plt.bar(indexes, counts, label="Counts")

    plt.ylabel("Counts")
    plt.xlabel("State")
    plt.show()


def sample_drawer_with_auxiliary(data, qubits, anxiliary):
    """Draw the sample distribution.

    Args:
        data (list): The data list.
        qubits (int): The number of data qubits.
        anxiliary (int): The number of auxiliary qubits.
    """
    distribution = np.zeros(1 << qubits)
    idx = 0
    for i in range(0, 1 << qubits + anxiliary, 1 << anxiliary):
        for j in range(qubits):
            distribution[idx] += data[i + j]
        idx += 1
    plt.bar(range(1 << qubits), distribution)
    plt.ylabel("Counts")
    plt.xlabel("State")
    plt.show()


def remove_zero_value(data: list, indexes: list) -> tuple:
    data_without_zero, idxes_without_zero = [], []
    for idx, d in enumerate(data):
        if not np.isclose(d, 0):
            data_without_zero.append(d)
            idxes_without_zero.append(indexes[idx])

    return data_without_zero, idxes_without_zero
