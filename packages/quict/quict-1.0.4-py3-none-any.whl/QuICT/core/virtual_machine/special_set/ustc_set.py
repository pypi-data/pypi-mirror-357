from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


USTCSet = InstructionSet(
    GateType.cx,
    [GateType.rx, GateType.ry, GateType.rz, GateType.h, GateType.x]
)
USTCSet.register_one_qubit_rule("zxz_rule")
