from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import InstructionSet


IBMQSet = InstructionSet(
    GateType.cx,
    [GateType.rz, GateType.sx, GateType.x]
)
IBMQSet.register_one_qubit_rule("ibmq_rule")
