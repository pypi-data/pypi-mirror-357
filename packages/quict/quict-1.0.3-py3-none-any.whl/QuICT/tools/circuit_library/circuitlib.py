import os
import shutil
from typing import Union, List

from QuICT.core import Circuit
from QuICT.lib.qasm.exceptions import QasmError
from QuICT.tools import Logger
from QuICT.tools.interface import OPENQASMInterface
from .circuit_lib_sql import CircuitLibDB


logger = Logger("QuICT_Circuit_Library")


class CircuitLib:
    """
    A class handling QuICT circuit library.

    Args:
        output_type (str, optional): one of [circuit, qasm, file]. Defaults to "circuit".
        output_path (str, optional): The path to store qasm file if output type is file.
            Defaults to the current working path.
    """

    __DEFAULT_TYPE = ["machine", "algorithm"]
    __DEFAULT_CLASSIFY = {
        "machine": ["aspen-4", "ourense", "rochester", "sycamore", "tokyo"],
        "algorithm": ["adder", "clifford", "cnf", "grover", "maxcut", "qft", "qnn", "quantum_walk", "vqe"],
    }
    __LIB_PATH = os.path.join(
        os.path.dirname(__file__),
        '../../lib/circuitlib'
    )

    def __init__(
        self,
        output_type: str = "circuit",
        output_path: str = '.'
    ):
        self._output_type = output_type
        self._output_path = output_path
        logger.debug(f"Initial Circuit Library with output {self._output_type}.")

        self._db = CircuitLibDB()
        if output_type == "file":
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

    @property
    def size(self) -> int:
        return self._db.size()

    def _get_circuit_from_qasm(self, file_path: str) -> Circuit:
        """ Load Circuit from a qasm file. """
        qasm = OPENQASMInterface.load_file(file_path)
        if not qasm.valid_circuit:
            logger.warn("Failure to load circuit from qasm.")
            raise QasmError("Invalid Circuit from QASM file.")

        split_symbol = '/' if file_path.rfind('/') > file_path.rfind('\\') else '\\'
        split_path = file_path.split(split_symbol)
        cir_name, cir_classify = split_path[-1:-3:-1]
        cir_name = os.path.splitext(cir_name)[0]
        qasm.circuit.name = "+".join([cir_classify, cir_name])
        return qasm.circuit

    def _get_string_from_qasm(self, file_path: str) -> str:
        """ Return qasm string from qasm file. """
        with open(file_path, 'r') as qasm_file:
            qstring = qasm_file.read()

        return qstring

    def _copy_qasm_file(self, file_path: str):
        """ Copy target qasm file to the given output path. """
        shutil.copy(file_path, self._output_path)

    def _get_all(self, folder: str, files: list) -> Union[List, None]:
        """ Load all qasm files in the list of files.

        Args:
            folder (str): The path of the qasm folder
            files (list): the list of file names

        Returns:
            List[(Circuit|string)]: _description_
        """
        circuit_all = []
        for file in files:
            file_path = os.path.join(folder, file[0])
            if self._output_type == "circuit":
                circuit_all.append(self._get_circuit_from_qasm(file_path))
            elif self._output_type == "qasm":
                circuit_all.append(self._get_string_from_qasm(file_path))
            else:
                self._copy_qasm_file(file_path)

        return circuit_all

    def get_template_circuit(
        self,
        qubits_interval: Union[list, int] = None,
        max_size: int = None,
        max_depth: int = None,
        typelist: list = None
    ) -> Union[List[Union[Circuit, str]], None]:
        """
        Get template circuits in QuICT circuit library. A template will be loaded if
        it satisfies the following restrictions:
            1. the circuit in the given classify.
            2. its number of qubits <= `max_width`,
            3. its number of gates <= `max_size`,
            4. its depth <= `max_depth`.
            5. its gates' types are in `typelist`

        Restrictions will be ignored if not specified.

        Args:
            qubits_interval (Union[List, int], optional): The interval of qubit number, if it givens an interger,
                it equals to the interval of [1, qubits_interval], Otherwise, if it is list, it should contains the
                minimal qubits number and maximul qubits number. The range should be [1, 5].
            max_size(int): max number of gates, range is [2, 6].
            max_depth(int): max depth of circuit, range is [2, 9].
            typelist(Iterable[GateType]): list of allowed gate types

        Returns:
            (List[Circuit | String] | None): Return the list of output circuit order by output_type.
        """
        path = os.path.join(self.__LIB_PATH, "template")
        files = self._db.circuit_filter("template", "template", qubits_interval, max_size, max_depth)

        if typelist is not None:
            target_type = [gtype.name for gtype in typelist]
            valid_files = []
            for f in files:
                valid = True
                temp_f: str = f[0][:-5]
                g_info = temp_f.split('_')[4:]
                for gi in g_info:
                    if gi not in target_type:
                        valid = False
                        continue

                if valid:
                    valid_files.append(f)
        else:
            valid_files = files

        return self._get_all(path, valid_files)

    def get_circuit(
        self,
        type: str,
        classify: str = None,
        qubits_interval: Union[list, int] = None
    ) -> Union[List[Union[Circuit, str]], None]:
        """Get the target circuits from QuICT Circuit Library.

        Args:
            type (str): The type of circuits, one of [machine, algorithm].
            classify (str, optional): The classify of selected circuit's type.
                For machine circuit's type, classify is one of
                    [aspen-4, ourense, rochester, sycamore, tokyo]
                For algorithm circuit's type, classify is one of
                    [adder, clifford, qnn, grover, qft, vqe, cnf, maxcut, quantum_walk]

            qubits_interval (Union[List, int], optional): The interval of qubit number, if it givens an interger,
                it equals to the interval of [1, qubits_interval], Otherwise, if it is list, it should contains the
                minimal qubits number and maximul qubits number.

        Returns:
            (List[Circuit | String] | None): Return the list of output circuit order by output_type.
        """
        if type not in self.__DEFAULT_TYPE:
            raise KeyError("error_type")

        if classify is not None:
            assert classify in self.__DEFAULT_CLASSIFY[type], "error classify."
            classify_list = [classify]
        else:
            classify_list = self.__DEFAULT_CLASSIFY[type]

        if isinstance(qubits_interval, list):
            assert len(qubits_interval) == 2, f"{len(qubits_interval)}"

        circuit_list = []
        for classify in classify_list:
            path = os.path.join(self.__LIB_PATH, type, classify)
            files = self._db.circuit_filter(type, classify, qubits_interval)
            circuit_list += self._get_all(path, files)

        return circuit_list
