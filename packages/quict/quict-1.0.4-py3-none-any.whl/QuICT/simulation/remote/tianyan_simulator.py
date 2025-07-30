import datetime
from cqlib import TianYanPlatform


class TianyanSimulator:
    """ Tianyan Quantum Machine Interface. """
    __BACKEND = ["tianyan24", "tianyan176", "tianyan176-2", "tianyan504"]

    def __init__(self, token: str):
        """ Initial TianyanSimulator Class.

        Args:
            token (str): Personal Token for China Telecom Quantum Platform Login.
        """
        self.platform = TianYanPlatform(login_key=token)

    def run(self, circuit, backend: str = "tianyan24", exp_name: str = f"exp.{datetime.now().strftime("%Y%m%d%H%M%S")}", shots: int = 1000):
        """ start tianyan quantum machine with given circuit

        Args:
            circuit (Circuit): The quantum circuits.
            backend (str, optional): The backend choice. Defaults to "tianyan24".
            shots (int, optional): The sample times. Defaults to 1000.

        Returns:
            list: The sample result
        """
        assert backend in self.__BACKEND
        self.platform.set_machine(backend)
        qcis_str = circuit.qcis()
        query_id_single = self.platform.submit_job(
            circuit=qcis_str,
            exp_name=exp_name,
            shots=shots,
            )

        exp_result = self.platform.query_experiment(query_id=query_id_single, max_wait_time=120, sleep_time=5)
        # The return value is a list, which contains several dictionaries.
            # "resultStatus": Raw measurement data, including: The first entry is the bit order (e.g., [0, 6]). The remaining entries are shot results (ordered by bit sequence).
            # "probability": Statistically corrected probabilities (post-readout error mitigation). Returns null if measured qubits > 15 (due to server constraints).
            # "experimentTaskId": A unique task ID for experiment tracking.

            # When the "probability" field is unavailable, use the raw data from "resultStatus" along with the quantum processor’s readout fidelity for error correction.
            # Refer to advanced tutorials for reference functions or implement custom correction methods to enhance accuracy.
            
        for res_name, res_data in exp_result[0].items():
            print(f"{res_name} : {res_data}")
