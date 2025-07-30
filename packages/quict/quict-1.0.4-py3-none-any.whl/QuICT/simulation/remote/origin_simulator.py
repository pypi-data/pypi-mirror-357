from pyqpanda import *


class OriginSimulator:
    """ Origin Quantum Machine Interface. """
    def __init__(self, token: str):
        """ Initial OriginSimulator Class.

        Args:
            token (str): Personal Token for Origin Platform Login.
        """
        self.qm = QCloud()

        # Initialize
        self.qm.init_qvm(token)

    def run(self, circuit: str, shots: int = 1000, chip_id: int = 2):
        """ start origin quantum machine with given circuit.

        Args:
            circuit (str): The quantum circuit's QASM file path.
            shots (int, optional): The sample times. Defaults to 1000.
            chip_id (int, optional): The origin's Quantum Chip ID. Defaults to 2.

        Returns:
            list: The sample result.
        """
        prog, _, _ = convert_qasm_to_qprog(circuit, self.qm)

        assert chip_id in list(range(1, 4))
        # Call quantum chip
        result = self.qm.real_chip_measure(prog, shots, chip_id)
        self.qm.finalize()

        return result
