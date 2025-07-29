from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


NamSet = InstructionSet(
    GateType.cx,
    [GateType.h, GateType.rz]
)
NamSet.register_one_qubit_rule("hrz_rule")
