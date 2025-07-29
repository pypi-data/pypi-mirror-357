from QuICT.core import Circuit, Layout
from QuICT.core.virtual_machine import VirtualQuantumMachine, InstructionSet
from QuICT.tools.drawer import PhotoDrawer


def display_compiled_circuit(
    circuit: Circuit,
    vqm: VirtualQuantumMachine,
    filename: str = None
):
    """ Warning: It will decomposition and flatten the given circuit. """
    iset: InstructionSet = vqm.instruction_set
    layout: Layout = vqm.layout
    assert vqm.qubit_number >= circuit.width()
    if circuit.size() != circuit.count_1qubit_gate() + circuit.count_2qubit_gate():
        circuit.decomposition()

    circuit.flatten()

    drawer = PhotoDrawer(layout, iset)
    drawer.run(circuit, filename=filename, hidden_empty_qubits=True)
    if filename is None:
        from IPython.display import display

        display(drawer.figure)
