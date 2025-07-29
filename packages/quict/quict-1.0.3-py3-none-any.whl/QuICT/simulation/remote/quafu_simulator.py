from quafu import User, Task, QuantumCircuit


class QuafuSimulator:
    """ Quafu Quantum Machine Interface. """
    __BACKEND = ["Baihua", "Dongling"]

    def __init__(self, token: str):
        """ Initial QuafuSimulator Class.

        Args:
            token (str): Personal Token for Quafu Platform Login.
        """
        self.user = User()
        self.user.save_apitoken(token)

    def run(self, circuit, backend: str = "Baihua", shots: int = 1000, compile: bool = True, priority:int = 1):
        """ start quafu quantum machine with given circuit

        Args:
            circuit (Circuit): The quantum circuits.
            backend (str, optional): The backend choice. Defaults to "Baihua".
            shots (int, optional): The sample times. Defaults to 1000.
            compile (bool, optional): Whether use Quafu's compiler or not. Defaults to True.
            priority (int, optional): Task priority. Defaults to 1.
 
        Returns:
            list: The sample result
        """
        qc = QuantumCircuit(circuit.width())
        test_cir = circuit.qasm()
        qc.from_openqasm(test_cir)

        assert backend in self.__BACKEND
        task = Task()
        task.config(backend=backend, shots=shots, compile=compile, priority=priority)
        res = task.send(qc)

        return res.counts
