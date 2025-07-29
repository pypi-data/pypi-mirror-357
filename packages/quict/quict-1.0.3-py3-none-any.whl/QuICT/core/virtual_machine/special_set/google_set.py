from QuICT.core.utils import GateType
from QuICT.core.virtual_machine.instruction_set import InstructionSet


GoogleSet = InstructionSet(
    GateType.fsim,
    [GateType.sx, GateType.sy, GateType.sw, GateType.rx, GateType.ry]
)
GoogleSet.register_one_qubit_rule("xyx_rule")
