import unittest
from QuICT.core import Circuit
from QuICT.algorithm.quantum_algorithm.quantum_walk.shift_op import CycleShiftOp
import numpy as np


class TestCycleShift(unittest.TestCase):

    def test_simple_matrix(self):
        num_q = np.random.randint(4, 7)
        num_node = np.random.randint(3, 1 << (num_q - 1))

        # target matrix
        dim = (1 << (num_q - 1))
        shift_up_mat = np.zeros((dim, dim))
        shift_dwn_mat = np.zeros((dim, dim))
        # only care about idx in node_num range
        for i in range(num_node):
            shift_up_mat[(i + 1) % num_node, i] = 1
            shift_dwn_mat[(i - 1) % num_node, i] = 1

        # check the circuit implementation is correct
        op_mat = CycleShiftOp(
            node_num=num_node,
            qreg_size=num_q,
            mode="simple"
        ).matrix()

        c0_submat = np.zeros((dim, dim), dtype=op_mat.dtype)
        c1_submat = np.zeros((dim, dim), dtype=op_mat.dtype)

        for i in range(dim):
            for j in range(dim):
                c1_offset = 1 << (num_q + 1)
                c0_submat[i, j] = op_mat[i << 1, j << 1]
                c1_submat[i, j] = op_mat[(i << 1) + c1_offset, (j << 1) + c1_offset]

        self.assertTrue(np.allclose(c0_submat, shift_dwn_mat))
        self.assertTrue(np.allclose(c1_submat, shift_up_mat))

    def test_exact_matrix(self):
        num_q = np.random.randint(4, 7)
        num_node = np.random.randint(3, 1 << (num_q - 1))

        # target matrix
        dim = (1 << (num_q - 1))
        shift_up_mat = np.zeros((dim, dim))
        shift_dwn_mat = np.zeros((dim, dim))
        for i in range(num_node):
            shift_up_mat[(i + 1) % num_node, i] = 1
            shift_dwn_mat[(i - 1) % num_node, i] = 1
        # require idx out of node_num range to be identity
        for i in range(num_node, dim):
            shift_up_mat[i, i] = 1
            shift_dwn_mat[i, i] = 1

        # check the circuit implementation is correct
        op_mat = CycleShiftOp(
            node_num=num_node,
            qreg_size=num_q,
            mode="exact"
        ).matrix()

        c0_submat = np.zeros((dim, dim), dtype=op_mat.dtype)
        c1_submat = np.zeros((dim, dim), dtype=op_mat.dtype)

        for i in range(dim):
            for j in range(dim):
                c1_offset = 1 << (num_q + 1)
                c0_submat[i, j] = op_mat[i << 1, j << 1]
                c1_submat[i, j] = op_mat[(i << 1) + c1_offset, (j << 1) + c1_offset]

        self.assertTrue(np.allclose(c0_submat, shift_dwn_mat))
        self.assertTrue(np.allclose(c1_submat, shift_up_mat))
