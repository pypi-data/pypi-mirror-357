import numpy as np
from sympy import *

from QuICT.core.utils import GateType


class GateMatrixGenerator:
    """ Generator the Quantum Gates' Matrix. """
    def get_matrix(self, gate, precision: str = None, is_get_target: bool = False) -> np.ndarray:
        """ Return the given BasicGate's matrix.

        Args:
            gate (BasicGate): The Quantum Gate
            precision (str, optional): The precision of Quantum Gate. Defaults to None.
            is_get_target (bool, optional): Whether return the completed BasicGate's matrix, or only return the target
            qubits part. Defaults to False.

        Returns:
            np.ndarray: The Quantum Gates' matrix.
        """
        # Step 1: Get based matrix's value
        gate_type = gate.type
        _precision = gate.precision if precision is None else precision
        gate_precision = np.complex128 if _precision == "double" else np.complex64
        gate_params = gate.params
        if gate_params == 0:
            based_matrix = self.based_matrix(gate_type, gate_precision)
        else:
            based_matrix = self.matrix_with_param(
                gate_type,
                gate.pargs,
                gate.symbol_gate,
                gate.symbol_pargs,
                gate_precision,
            )

        if is_get_target:
            return based_matrix

        # Step 2: Depending on controlled_by, generate final matrix
        if gate.controls > 0:
            if gate_type == GateType.rccx:
                control_args = gate.controls - 1
                target_args = gate.targets + 1
            else:
                control_args = gate.controls
                target_args = gate.targets

            controlled_matrix = np.identity(
                1 << (control_args + target_args), dtype=gate_precision
            )
            target_border = 1 << target_args
            controlled_matrix[-target_border:, -target_border:] = based_matrix

            return controlled_matrix

        return based_matrix

    def based_matrix(self, gate_type: GateType, precision: complex):
        """ Return the no-parameter Quantum Gates' matrix.

        Args:
            gate_type (GateType): The type of Quantum Gate
            precision (complex): The precision of Quantum Gate

        Returns:
            np.ndarray: The Quantum Gate's matrix
        """
        if gate_type in [GateType.h, GateType.ch]:
            return np.array([
                [1 / np.sqrt(2), 1 / np.sqrt(2)],
                [1 / np.sqrt(2), -1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.hy:
            return np.array([
                [1 / np.sqrt(2), -1j / np.sqrt(2)],
                [1j / np.sqrt(2), -1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.s:
            return np.array([
                [1, 0],
                [0, 1j]
            ], dtype=precision)
        elif gate_type == GateType.sdg:
            return np.array([
                [1, 0],
                [0, -1j]
            ], dtype=precision)
        elif gate_type in [GateType.x, GateType.cx, GateType.ccx]:
            return np.array([
                [0, 1],
                [1, 0]
            ], dtype=precision)
        elif gate_type in [GateType.y, GateType.cy]:
            return np.array([
                [0, -1j],
                [1j, 0]
            ], dtype=precision)
        elif gate_type in [GateType.z, GateType.cz, GateType.ccz]:
            return np.array([
                [1, 0],
                [0, -1]
            ], dtype=precision)
        elif gate_type == GateType.sx:
            return np.array([
                [0.5 + 0.5j, 0.5 - 0.5j],
                [0.5 - 0.5j, 0.5 + 0.5j]
            ], dtype=precision)
        elif gate_type == GateType.sxdg:
            return np.array([
                [0.5 - 0.5j, 0.5 + 0.5j],
                [0.5 + 0.5j, 0.5 - 0.5j]
            ], dtype=precision)
        elif gate_type == GateType.sy:
            return np.array([
                [1 / np.sqrt(2), -1 / np.sqrt(2)],
                [1 / np.sqrt(2), 1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.sydg:
            return np.array([
                [1 / np.sqrt(2), 1 / np.sqrt(2)],
                [-1 / np.sqrt(2), 1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.sw:
            return np.array([
                [1 / np.sqrt(2), -np.sqrt(1j / 2)],
                [np.sqrt(-1j / 2), 1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.id:
            return np.array([
                [1, 0],
                [0, 1]
            ], dtype=precision)
        elif gate_type == GateType.t:
            return np.array([
                [1, 0],
                [0, 1 / np.sqrt(2) + 1j * 1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type == GateType.tdg:
            return np.array([
                [1, 0],
                [0, 1 / np.sqrt(2) + 1j * -1 / np.sqrt(2)]
            ], dtype=precision)
        elif gate_type in [GateType.swap, GateType.cswap]:
            return np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ], dtype=precision)
        elif gate_type == GateType.iswap:
            return np.array([
                [1, 0, 0, 0],
                [0, 0, 1j, 0],
                [0, 1j, 0, 0],
                [0, 0, 0, 1]
            ], dtype=precision)
        elif gate_type == GateType.iswapdg:
            return np.array([
                [1, 0, 0, 0],
                [0, 0, -1j, 0],
                [0, -1j, 0, 0],
                [0, 0, 0, 1]
            ], dtype=precision)
        elif gate_type == GateType.sqiswap:
            return np.array([
                [1, 0, 0, 0],
                [0, 1 / np.sqrt(2), 1j / np.sqrt(2), 0],
                [0, 1j / np.sqrt(2), 1 / np.sqrt(2), 0],
                [0, 0, 0, 1]
            ], dtype=precision)
        elif gate_type == GateType.ecr:
            return np.array([
                [0, 0, 1 / np.sqrt(2), 1j / np.sqrt(2)],
                [0, 0, 1j / np.sqrt(2), 1 / np.sqrt(2)],
                [1 / np.sqrt(2), -1j / np.sqrt(2), 0, 0],
                [-1j / np.sqrt(2), 1 / np.sqrt(2), 0, 0]
            ], dtype=precision)
        elif gate_type == GateType.rccx:
            return np.array([
                [1, 0, 0, 0],
                [0, -1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ], dtype=precision)
        else:
            raise TypeError(gate_type)

    def matrix_with_param(
        self,
        gate_type: GateType,
        gate_pargs: list,
        symbol_gate: bool,
        symbol_pargs: dict,
        precision: complex,
    ):
        """ Return the Quantum Gates' matrix, which has parameters.

        Args:
            gate_type (GateType): The type of Quantum Gate.
            gate_pargs (List): The Quantum Gate's parameters.
            symbol_gate (bool): Whether the Quantum Gate is a symbol gate.
            symbol_pargs (dict): The Quantum Gate's symbol parameters.
            precision (complex): The precision of Quantum Gate.

        Returns:
            np.ndarray: The Quantum Gate's matrix.
        """
        pargs = []
        if symbol_gate:
            assert len(symbol_pargs) > 0, "The symbol gate must be assigned values before calculation."
            for i in range(len(gate_pargs)):
                pargs.append(symbol_pargs[gate_pargs[i]])
        else:
            pargs = gate_pargs

        if gate_type in [GateType.u1, GateType.cu1]:
            return np.array([
                [1, 0],
                [0, np.exp(1j * pargs[0])]
            ], dtype=precision)

        elif gate_type == GateType.u2:
            sqrt2 = 1 / np.sqrt(2)
            return np.array([
                [1 * sqrt2,
                 -np.exp(1j * pargs[1]) * sqrt2],
                [np.exp(1j * pargs[0]) * sqrt2,
                 np.exp(1j * (pargs[0] + pargs[1])) * sqrt2]
            ], dtype=precision)

        elif gate_type in [GateType.u3, GateType.cu3]:
            return np.array([
                [np.cos(pargs[0] / 2),
                 -np.exp(1j * pargs[2]) * np.sin(pargs[0] / 2)],
                [np.exp(1j * pargs[1]) * np.sin(pargs[0] / 2),
                 np.exp(1j * (pargs[1] + pargs[2])) * np.cos(pargs[0] / 2)]
            ], dtype=precision)

        elif gate_type == GateType.rx:
            cos_v = np.cos(pargs[0] / 2)
            sin_v = -np.sin(pargs[0] / 2)
            return np.array([
                [cos_v, 1j * sin_v],
                [1j * sin_v, cos_v]
            ], dtype=precision)

        elif gate_type in [GateType.ry, GateType.cry]:
            cos_v = np.cos(pargs[0] / 2)
            sin_v = np.sin(pargs[0] / 2)
            return np.array([
                [cos_v, -sin_v],
                [sin_v, cos_v]
            ], dtype=precision)

        elif gate_type in [GateType.rz, GateType.crz, GateType.ccrz]:
            return np.array([
                [np.exp(-pargs[0] / 2 * 1j), 0],
                [0, np.exp(pargs[0] / 2 * 1j)]
            ], dtype=precision)

        elif gate_type == GateType.phase:
            return np.array([
                [1, 0],
                [0, np.exp(pargs[0] * 1j)]
            ], dtype=precision)

        elif gate_type == GateType.gphase:
            return np.array([
                [np.exp(pargs[0] * 1j), 0],
                [0, np.exp(pargs[0] * 1j)]
            ], dtype=precision)

        elif gate_type == GateType.fsim:
            costh = np.cos(pargs[0])
            sinth = np.sin(pargs[0])
            phi = pargs[1]
            return np.array([
                [1, 0, 0, 0],
                [0, costh, -1j * sinth, 0],
                [0, -1j * sinth, costh, 0],
                [0, 0, 0, np.exp(-1j * phi)]
            ], dtype=precision)

        elif gate_type == GateType.rxx:
            costh = np.cos(pargs[0] / 2)
            sinth = np.sin(pargs[0] / 2)

            return np.array([
                [costh, 0, 0, -1j * sinth],
                [0, costh, -1j * sinth, 0],
                [0, -1j * sinth, costh, 0],
                [-1j * sinth, 0, 0, costh]
            ], dtype=precision)

        elif gate_type == GateType.ryy:
            costh = np.cos(pargs[0] / 2)
            sinth = np.sin(pargs[0] / 2)

            return np.array([
                [costh, 0, 0, 1j * sinth],
                [0, costh, -1j * sinth, 0],
                [0, -1j * sinth, costh, 0],
                [1j * sinth, 0, 0, costh]
            ], dtype=precision)

        elif gate_type == GateType.rzz:
            expth = np.exp(0.5j * pargs[0])
            sexpth = np.exp(-0.5j * pargs[0])

            return np.array([
                [sexpth, 0, 0, 0],
                [0, expth, 0, 0],
                [0, 0, expth, 0],
                [0, 0, 0, sexpth]
            ], dtype=precision)

        elif gate_type == GateType.rzx:
            costh = np.cos(pargs[0] / 2)
            sinth = np.sin(pargs[0] / 2)

            return np.array([
                [costh, -1j * sinth, 0, 0],
                [-1j * sinth, costh, 0, 0],
                [0, 0, costh, 1j * sinth],
                [0, 0, 1j * sinth, costh]
            ], dtype=precision)

        elif gate_type == GateType.rxy:
            costh = np.cos(pargs[1] / 2)
            sinth = np.sin(pargs[1] / 2)

            return np.array([
                [costh, -1j * np.exp(-1j * pargs[0]) * sinth],
                [-1j * np.exp(1j * pargs[0]) * sinth, costh]
            ], dtype=precision)

        elif gate_type == GateType.xy:
            return np.array([
                [0, -1j * np.exp(-1j * pargs[0])],
                [-1j * np.exp(1j * pargs[0]), 0]
            ], dtype=precision)

        elif gate_type == GateType.xy2p:
            return np.array([
                [1 / np.sqrt(2), -1j / np.sqrt(2) * np.exp(-1j * pargs[0])],
                [-1j / np.sqrt(2) * np.exp(1j * pargs[0]), 1 / np.sqrt(2)]
            ], dtype=precision)

        elif gate_type == GateType.xy2m:
            return np.array([
                [1 / np.sqrt(2), 1j / np.sqrt(2) * np.exp(-1j * pargs[0])],
                [1j / np.sqrt(2) * np.exp(1j * pargs[0]), 1 / np.sqrt(2)]
            ], dtype=precision)

        else:
            TypeError(gate_type)

    def grad_for_param(self, gate_type: GateType, gate_pargs: list, symbol_pargs: dict, precision: str):
        """Return the Parameterized Quantum Gates' gradient matrices.

        Args:
            gate_type (GateType): The type of Quantum Gate.
            gate_pargs (List): The Quantum Gate's parameters.
            symbol_pargs (dict): The Quantum Gate's symbol parameters.
            precision (str): The precision of Quantum Gate, one of [double, single]

        Returns:
            list: Parameterized Quantum Gates' gradient matrices.
        """
        pargs = []
        assert len(symbol_pargs) > 0, "The symbol gate must be assigned values before calculation."
        for i in range(len(gate_pargs)):
            pargs.append(symbol_pargs[gate_pargs[i]])

        precision = np.complex128 if precision == "double" else np.complex64

        if gate_type in [GateType.u1, GateType.cu1]:
            return [np.array([
                [1, 0],
                [0, np.exp(1j * pargs[0])]
            ], dtype=precision)]

        elif gate_type == GateType.u2:
            sqrt2 = 1 / np.sqrt(2)
            grad1 = np.array([
                [1 * sqrt2,
                 -np.exp(1j * pargs[1]) * sqrt2],
                [1j * np.exp(1j * pargs[0]) * sqrt2,
                 1j * np.exp(1j * (pargs[0] + pargs[1])) * sqrt2]
            ], dtype=precision)
            grad2 = np.array([
                [1 * sqrt2,
                 -1j * np.exp(1j * pargs[1]) * sqrt2],
                [np.exp(1j * pargs[0]) * sqrt2,
                 1j * np.exp(1j * (pargs[0] + pargs[1])) * sqrt2]
            ], dtype=precision)
            return [grad1, grad2]

        elif gate_type in [GateType.u3, GateType.cu3]:
            sin_v = np.sin(pargs[0] / 2)
            cos_v = np.cos(pargs[0] / 2)
            grad1 = np.array([
                [-sin_v / 2,
                 -np.exp(1j * pargs[2]) * cos_v / 2],
                [np.exp(1j * pargs[1]) * cos_v / 2,
                 -np.exp(1j * (pargs[1] + pargs[2])) * sin_v / 2]
            ], dtype=precision)
            grad2 = np.array([
                [cos_v,
                 -np.exp(1j * pargs[2]) * sin_v],
                [1j * np.exp(1j * pargs[1]) * sin_v,
                 1j * np.exp(1j * (pargs[1] + pargs[2])) * cos_v]
            ], dtype=precision)
            grad3 = np.array([
                [cos_v,
                 -1j * np.exp(1j * pargs[2]) * sin_v],
                [np.exp(1j * pargs[1]) * sin_v,
                 1j * np.exp(1j * (pargs[1] + pargs[2])) * cos_v]
            ], dtype=precision)
            return [grad1, grad2, grad3]

        elif gate_type == GateType.rx:
            cos_v = -np.cos(pargs[0] / 2) / 2
            sin_v = -np.sin(pargs[0] / 2) / 2
            return [np.array([
                [sin_v, 1j * cos_v],
                [1j * cos_v, sin_v]
            ], dtype=precision)]

        elif gate_type in [GateType.ry, GateType.cry]:
            cos_v = np.cos(pargs[0] / 2) / 2
            sin_v = np.sin(pargs[0] / 2) / 2
            return [np.array([
                [-sin_v, -cos_v],
                [cos_v, -sin_v]
            ], dtype=precision)]

        elif gate_type in [GateType.rz, GateType.crz, GateType.ccrz]:
            return [np.array([
                [-1j * np.exp(-pargs[0] / 2 * 1j) / 2, 0],
                [0, 1j * np.exp(pargs[0] / 2 * 1j) / 2]
            ], dtype=precision)]

        elif gate_type == GateType.phase:
            return [np.array([
                [1, 0],
                [0, 1j * np.exp(pargs[0] * 1j)]
            ], dtype=precision)]

        elif gate_type == GateType.gphase:
            return [np.array([
                [1j * np.exp(pargs[0] * 1j), 0],
                [0, 1j * np.exp(pargs[0] * 1j)]
            ], dtype=precision)]

        elif gate_type == GateType.fsim:
            costh = np.cos(pargs[0])
            sinth = np.sin(pargs[0])
            phi = pargs[1]
            grad1 = np.array([
                [1, 0, 0, 0],
                [0, -sinth, -1j * costh, 0],
                [0, -1j * costh, -sinth, 0],
                [0, 0, 0, np.exp(-1j * phi)]
            ], dtype=precision)
            grad2 = np.array([
                [1, 0, 0, 0],
                [0, costh, -1j * sinth, 0],
                [0, -1j * sinth, costh, 0],
                [0, 0, 0, -1j * np.exp(-1j * phi)]
            ], dtype=precision)
            return [grad1, grad2]

        elif gate_type == GateType.rxx:
            costh = np.cos(pargs[0] / 2) / 2
            sinth = np.sin(pargs[0] / 2) / 2

            return [np.array([
                [-sinth, 0, 0, -1j * costh],
                [0, -sinth, -1j * costh, 0],
                [0, -1j * costh, -sinth, 0],
                [-1j * costh, 0, 0, -sinth]
            ], dtype=precision)]

        elif gate_type == GateType.ryy:
            costh = np.cos(pargs[0] / 2) / 2
            sinth = np.sin(pargs[0] / 2) / 2

            return [np.array([
                [-sinth, 0, 0, 1j * costh],
                [0, -sinth, -1j * costh, 0],
                [0, -1j * costh, -sinth, 0],
                [1j * costh, 0, 0, -sinth]
            ], dtype=precision)]

        elif gate_type == GateType.rzz:
            expth = 0.5j * np.exp(0.5j * pargs[0])
            sexpth = -0.5j * np.exp(-0.5j * pargs[0])

            return [np.array([
                [sexpth, 0, 0, 0],
                [0, expth, 0, 0],
                [0, 0, expth, 0],
                [0, 0, 0, sexpth]
            ], dtype=precision)]

        elif gate_type == GateType.rzx:
            costh = np.cos(pargs[0] / 2) / 2
            sinth = np.sin(pargs[0] / 2) / 2

            return [np.array([
                [-sinth, -1j * costh, 0, 0],
                [-1j * costh, -sinth, 0, 0],
                [0, 0, -sinth, 1j * costh],
                [0, 0, 1j * costh, -sinth]
            ], dtype=precision)]

        elif gate_type == GateType.rxy:
            costh = np.cos(pargs[1] / 2)
            sinth = np.sin(pargs[1] / 2)

            grad1 = np.array([
                [costh, -np.exp(-1j * pargs[0]) * sinth],
                [np.exp(1j * pargs[0]) * sinth, costh]
            ], dtype=precision)

            grad2 = np.array([
                [-sinth / 2, -1j * np.exp(-1j * pargs[0]) * costh / 2],
                [-1j * np.exp(1j * pargs[0]) * costh / 2, -sinth / 2]
            ], dtype=precision)
            return [grad1, grad2]

        elif gate_type == GateType.xy:
            return [np.array([
                [0, -np.exp(-1j * pargs[0])],
                [np.exp(1j * pargs[0]), 0]
            ], dtype=precision)]

        elif gate_type == GateType.xy2p:
            return [np.array([
                [1 / np.sqrt(2), -1 / np.sqrt(2) * np.exp(-1j * pargs[0])],
                [1 / np.sqrt(2) * np.exp(1j * pargs[0]), 1 / np.sqrt(2)]
            ], dtype=precision)]

        elif gate_type == GateType.xy2m:
            return [np.array([
                [1 / np.sqrt(2), 1 / np.sqrt(2) * np.exp(-1j * pargs[0])],
                [-1 / np.sqrt(2) * np.exp(1j * pargs[0]), 1 / np.sqrt(2)]
            ], dtype=precision)]

        else:
            TypeError(gate_type)


class ComplexGateBuilder:
    """ The class of all build_gate functions for BasicGate. """
    @classmethod
    def build_gate(cls, gate_type, parg, gate_matrix=None):
        """ Gate Decomposition, divided the current gate with a set of small gates

        Args:
            gate_type (GateType): The type of Quantum Gate.
            parg (list): The parameters of Quantum Gate.
            gate_matrix (_type_, optional): The matrix of Quantum Gate, only use for CU3. Defaults to None.

        Returns:
            List: List of gate_info(gate_type, qubit_index, parameters)
        """
        if gate_type == GateType.cu3:
            cgate = cls.build_unitary(gate_matrix)
        elif gate_type == GateType.cu1:
            cgate = cls.build_cu1(parg[0])
        elif gate_type == GateType.swap:
            cgate = cls.build_swap()
        elif gate_type == GateType.ccx:
            cgate = cls.build_ccx()
        elif gate_type == GateType.ccz:
            cgate = cls.build_ccz()
        elif gate_type == GateType.ccrz:
            cgate = cls.build_ccrz(parg[0])
        elif gate_type == GateType.cswap:
            cgate = cls.build_cswap()
        elif gate_type == GateType.iswap:
            cgate = cls.build_iswap()
        elif gate_type == GateType.iswapdg:
            cgate = cls.build_iswapdg()
        elif gate_type == GateType.sqiswap:
            cgate = cls.build_sqiswap()
        elif gate_type == GateType.rccx:
            cgate = cls.build_rccx()
        elif gate_type == GateType.rxy:
            cgate = cls.build_rxy(parg)
        elif gate_type in [GateType.xy, GateType.xy2p, GateType.xy2m]:
            cgate = cls.build_xy(gate_type, parg[0])
        else:
            return None

        return cgate

    @staticmethod
    def build_rxy(parg):
        return [
            (GateType.rz, [0], [np.pi / 2 - parg[0]]),
            (GateType.rx, [0], [np.pi / 2]),
            (GateType.rz, [0], [parg[1]]),
            (GateType.rx, [0], [-np.pi / 2]),
            (GateType.rz, [0], [parg[0] - np.pi / 2]),
        ]

    @staticmethod
    def build_xy(gate_type, parg):
        if gate_type == GateType.xy:
            return [
                (GateType.rz, [0], [np.pi - parg]),
                (GateType.y, [0], None),
                (GateType.rz, [0], [parg]),
                (GateType.gphase, [0], [-np.pi / 2])
            ]
        elif gate_type == GateType.xy2p:
            return [
                (GateType.rz, [0], [np.pi / 2 - parg]),
                (GateType.ry, [0], [np.pi / 2]),
                (GateType.rz, [0], [parg - np.pi / 2])
            ]
        else:
            return [
                (GateType.rz, [0], [-(parg + np.pi / 2)]),
                (GateType.ry, [0], [np.pi / 2]),
                (GateType.rz, [0], [np.pi / 2 + parg])
            ]

    @staticmethod
    def build_unitary(gate_matrix):
        from QuICT.qcda.synthesis import UnitaryDecomposition

        cgate, _ = UnitaryDecomposition(include_phase_gate=True).execute(gate_matrix)

        return cgate

    @staticmethod
    def build_cu1(parg):
        return [(GateType.crz, [0, 1], [parg]), (GateType.u1, [0], [parg / 2])]

    @staticmethod
    def build_swap():
        return [
            (GateType.cx, [0, 1], None),
            (GateType.cx, [1, 0], None),
            (GateType.cx, [0, 1], None),
        ]

    @staticmethod
    def build_ccx():
        return [
            (GateType.h, [2], None),
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [0, 2], None),
            (GateType.tdg, [2], None),
            (GateType.cx, [0, 2], None),
            (GateType.t, [0], None),
            (GateType.t, [2], None),
            (GateType.h, [2], None),
        ]

    @staticmethod
    def build_ccz():
        return [
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [0, 2], None),
            (GateType.tdg, [2], None),
            (GateType.cx, [0, 2], None),
            (GateType.t, [0], None),
            (GateType.t, [2], None),
        ]

    @staticmethod
    def build_ccrz(parg):
        return [
            (GateType.crz, [1, 2], [parg / 2]),
            (GateType.cx, [0, 1], None),
            (GateType.crz, [1, 2], [-parg / 2]),
            (GateType.cx, [0, 1], None),
            (GateType.crz, [0, 2], [parg / 2]),
        ]

    @staticmethod
    def build_cswap():
        return [
            (GateType.cx, [2, 1], None),
            (GateType.h, [2], None),
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [2, 1], None),
            (GateType.tdg, [1], None),
            (GateType.cx, [0, 1], None),
            (GateType.t, [1], None),
            (GateType.cx, [0, 2], None),
            (GateType.tdg, [2], None),
            (GateType.cx, [0, 2], None),
            (GateType.t, [0], None),
            (GateType.t, [2], None),
            (GateType.h, [2], None),
            (GateType.cx, [2, 1], None),
        ]

    @staticmethod
    def build_iswap():
        return [(GateType.fsim, [0, 1], [-np.pi / 2, 0]), ]

    @staticmethod
    def build_iswapdg():
        return [(GateType.fsim, [0, 1], [np.pi / 2, 0]), ]

    @staticmethod
    def build_sqiswap():
        return [(GateType.fsim, [0, 1], [-np.pi / 4, 0]), ]

    @staticmethod
    def build_rccx():
        return [
            (GateType.ry, [2], [np.pi / 4]),
            (GateType.cx, [1, 2], None),
            (GateType.ry, [2], [np.pi / 4]),
            (GateType.cx, [0, 2], None),
            (GateType.ry, [2], [-np.pi / 4]),
            (GateType.cx, [1, 2], None),
            (GateType.ry, [2], [-np.pi / 4]),
        ]


class InverseGate:
    """ The class of all Inverse functions for Quantum Gate. """
    __GATE_INVERSE_MAP = {
        GateType.s: GateType.sdg,
        GateType.sdg: GateType.s,
        GateType.sx: GateType.sxdg,
        GateType.sxdg: GateType.sx,
        GateType.sy: GateType.sydg,
        GateType.sydg: GateType.sy,
        GateType.sw: (GateType.u2, [3 * np.pi / 4, 5 * np.pi / 4]),
        GateType.t: GateType.tdg,
        GateType.tdg: GateType.t,
        GateType.iswap: GateType.iswapdg,
        GateType.iswapdg: GateType.iswap,
        GateType.sqiswap: (GateType.fsim, [np.pi / 4, 0]),
    }
    __INVERSE_GATE_WITH_NEGATIVE_PARAMS = [
        GateType.u1,
        GateType.rx,
        GateType.ry,
        GateType.cry,
        GateType.phase,
        GateType.gphase,
        GateType.cu1,
        GateType.rxx,
        GateType.ryy,
        GateType.rzz,
        GateType.rzx,
        GateType.rz,
        GateType.crz,
        GateType.ccrz,
        GateType.fsim,
    ]

    @classmethod
    def get_inverse_gate(cls, gate_type: GateType, pargs: list) -> tuple:
        """ Get Inverse Quantum Gate Information.

        Args:
            gate_type (GateType): The type of Quantum Gate.
            pargs (list): The parameters of Quantum Gate.

        Returns:
            tuple: The inverse gate info.
        """
        if len(pargs) == 0:
            if gate_type in cls.__GATE_INVERSE_MAP.keys():
                inverse_args = cls.__GATE_INVERSE_MAP[gate_type]

                return inverse_args if isinstance(inverse_args, tuple) else (inverse_args, pargs)
        else:
            inv_params = None
            if gate_type in cls.__INVERSE_GATE_WITH_NEGATIVE_PARAMS:
                inv_params = [p * -1 for p in pargs]
            elif gate_type == GateType.u2:
                inv_params = [np.pi - pargs[1], np.pi - pargs[0]]
            elif gate_type in [GateType.u3, GateType.cu3]:
                inv_params = [pargs[0], np.pi - pargs[2], np.pi - pargs[1]]
            elif gate_type in [GateType.xy, GateType.xy2p, GateType.xy2m]:
                inv_params = [pargs[0] + np.pi]
            elif gate_type == GateType.rxy:
                inv_params = [pargs[0] + np.pi, pargs[1]]

            if inv_params is not None:
                return (gate_type, inv_params)

        return None, pargs

    @staticmethod
    def inverse_perm_gate(targets: int, targs: list):
        inverse_targs = [targets - 1 - t for t in targs]

        return inverse_targs
