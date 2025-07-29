from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


OriginSet = InstructionSet(
    GateType.cz,
    [GateType.u3]
)
OriginSet.register_one_qubit_rule("u3_rule")
