from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


IonQSet = InstructionSet(
    GateType.rxx,
    [GateType.rx, GateType.ry, GateType.rz]
)
IonQSet.register_one_qubit_rule("zxz_rule")
