from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


QuafuSet = InstructionSet(
    GateType.cx,
    [GateType.rx, GateType.ry, GateType.rz, GateType.h]
)
QuafuSet.register_one_qubit_rule("zxz_rule")
