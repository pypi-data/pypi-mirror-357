from __future__ import annotations
from typing import Union, List

from QuICT.core.utils import unique_id_generator
from QuICT.tools.exception.core import TypeError, ValueError, IndexExceedError, QubitMeasureError


class Qubit(object):
    """ Implement a Quantum bit

    Qubit is the basic unit of Quantum Compute.
    """

    @property
    def id(self):
        return self._id

    @property
    def probability(self) -> float:
        return self._probability

    @probability.setter
    def probability(self, prob: float):
        assert prob >= 0 and prob <= 1, f"{prob}"
        self._probability = prob

    @property
    def measured(self) -> int:
        return self._measured

    @measured.setter
    def measured(self, measured: int):
        assert measured == 0 or measured == 1, ValueError("Qubit.measured", "one of [0, 1]", measured)
        self._prob = 1 if measured == 0 else 0
        self._measured = measured
        self._historical_measured.append(measured)

    @property
    def historical_measured(self) -> list:
        return self._historical_measured

    @property
    def fidelity(self) -> float:
        return self._fidelity

    @fidelity.setter
    def fidelity(self, fidelity: Union[float, tuple]):
        if isinstance(fidelity, tuple):
            assert len(fidelity) == 2, "Only need [f0, f1] 2 fidelity for qubit measured fidelity."
            for f in fidelity:
                self._validate_fidelity(f, "fidelity")
        else:
            self._validate_fidelity(fidelity, "fidelity")

        self._fidelity = fidelity

    @property
    def preparation_fidelity(self) -> float:
        return self._qsp_fidelity

    @preparation_fidelity.setter
    def preparation_fidelity(self, fidelity: float):
        self._validate_fidelity(fidelity, "preparation_fidelity")
        self._qsp_fidelity = fidelity

    @property
    def gate_fidelity(self) -> float:
        return self._gate_fidelity

    @gate_fidelity.setter
    def gate_fidelity(self, gate_fidelity: Union[float, dict]):
        if isinstance(gate_fidelity, dict):
            for fidelity in gate_fidelity.values():
                self._validate_fidelity(fidelity, "gate_fidelity")
        else:
            self._validate_fidelity(gate_fidelity, "gate_fidelity")

        self._gate_fidelity = gate_fidelity

    @property
    def T1(self) -> float:
        return self._t1

    @T1.setter
    def T1(self, t1: float):
        assert isinstance(t1, (float, int)) and t1 >= 0, ValueError("Qubit.T1", "greater than 0", t1)
        self._t1 = t1

    @property
    def T2(self) -> float:
        return self._t2

    @T2.setter
    def T2(self, t2: float):
        assert isinstance(t2, (float, int)) and t2 >= 0, ValueError("Qubit.T2", "greater than 0", t2)
        self._t2 = t2

    @property
    def work_frequency(self):
        return self._work_frequency

    @work_frequency.setter
    def work_frequency(self, wf):
        assert isinstance(wf, (float, int)) and wf >= 0, \
            ValueError("Qubit.work_frequency", "greater than 0", wf)
        self._work_frequency = wf

    @property
    def readout_frequency(self):
        return self._readout_frequency

    @readout_frequency.setter
    def readout_frequency(self, rf):
        assert isinstance(rf, (float, int)) and rf >= 0, \
            ValueError("Qubit.work_frequency", "greater than 0", rf)
        self._readout_frequency = rf

    @property
    def gate_duration(self):
        return self._gate_duration

    @gate_duration.setter
    def gate_duration(self, gd):
        assert isinstance(gd, (float, int)) and gd >= 0, \
            ValueError("Qubit.work_frequency", "greater than 0", gd)
        self._gate_duration = gd

    def _validate_fidelity(self, fidelity: float, place: str) -> bool:
        assert isinstance(fidelity, (float, int)), TypeError(f"Qubit.{place}", "float, int", type(fidelity))
        assert fidelity >= 0 and fidelity <= 1, ValueError(f"Qubit.{place}", "within [0, 1]", {fidelity})

        return True

    def __init__(
        self,
        fidelity: Union[float, tuple] = 1.0,
        preparation_fidelity: float = 1.0,
        gate_fidelity: Union[float, dict] = 1.0,
        T1: float = 0.0,
        T2: float = 0.0,
        work_frequency: float = 0.0,
        readout_frequency: float = 0.0,
        gate_duration: float = 0.0,
    ):
        """
        Args:
            fidelity (Union[float, tuple]): The qubit's measured fidelity, where the fidelity of a quantum qubit is the
                overlap between the ideal theoretical operation and the actual experimental operation. if it is list,
                it represent the measured fidelity for state 0 and state 1.
            preparation_fidelity (float): The qubit's state preparation fidelity refers to the degree of accuracy with
                which a quantum bit (qubit) can be prepared in a specific state.
            gate_fidelity (Union[float, dict]): The fidelity for applying single-qubit quantum gate in this qubit.
                e.g. {GateType.h: 0.993, GateType.x: 0.989}
            T1 (float, μs): The longitudinal coherence time, which refers to the time it takes for the qubit to decay
                back to its ground state from an excited state. Default to None.
            T2 (float, μs): the transverse coherence time, which refers to the time it takes for the qubit to lose its
                coherence when subjected to unwanted phase or amplitude fluctuations. Default to None.
            work_frequency (Union[float, list]): The working frequency in current Qubit.
            readout_frequency (Union[float, list]): The frequency when measured qubit in current Qubit.
            gate_duration (Union[float, list]): The amount of time that a Quantum Gate operators on a Qubit.
        """
        self._id = unique_id_generator()
        self.fidelity = fidelity
        self.preparation_fidelity = preparation_fidelity
        self.gate_fidelity = gate_fidelity
        self.T1 = T1
        self.T2 = T2
        self.work_frequency = work_frequency
        self.readout_frequency = readout_frequency
        self.gate_duration = gate_duration

        self._measured = None
        self._probability = None    # The prob of measured 0
        self._historical_measured = []

    def __str__(self):
        """ string describe of the qubit

        Returns:
            str: a simple describe
        """
        return f"qubit id: {self.id}; fidelity: {self.fidelity}; QSP_fidelity: {self.preparation_fidelity}; " \
            + f"Gate_fidelity: {self.gate_fidelity}; Coherence time: T1: {self._t1}; T2: {self._t2}; " \
            + f"Work Frequency: {self.work_frequency}; Readout Frequency: {self.readout_frequency}; " \
            + f"Gate Duration: {self.gate_duration}"

    def __int__(self):
        """ int value of the qubit(measure result)

        Returns:
            int: measure result

        Raises:
            The qubit has not be measured.
        """
        if self._measured is None:
            raise QubitMeasureError(f"The qubit {self.id} has not be measured")

        return self.measured

    def __bool__(self):
        """ int value of the qubit(measure result)

        Returns:
            bool: measure result

        Raises:
            The qubit has not be measured.
        """
        return bool(int(self))

    def reset(self):
        """ Reset self qubit status. """
        self._measured = None
        self._historical_measured = []


class Qureg(list):
    """ Implement a Quantum Register

    Qureg is a list of Qubits, which is a subClass of list.
    """
    @property
    def fidelity(self) -> List[Union[float, tuple]]:
        return [qubit.fidelity for qubit in self]

    @property
    def preparation_fidelity(self) -> List[float]:
        return [qubit.preparation_fidelity for qubit in self]

    @property
    def gate_fidelity(self) -> List[Union[dict, float]]:
        return [qubit.gate_fidelity for qubit in self]

    @property
    def T1(self) -> List[float]:
        return [qubit.T1 for qubit in self]

    @property
    def T2(self) -> List[float]:
        return [qubit.T2 for qubit in self]

    @property
    def work_frequency(self) -> List[float]:
        return [qubit.work_frequency for qubit in self]

    @property
    def readout_frequency(self) -> List[float]:
        return [qubit.readout_frequency for qubit in self]

    @property
    def gate_duration(self) -> List[float]:
        return [qubit.gate_duration for qubit in self]

    def __init__(self, qubits: Union[int, Qubit, Qureg] = None):
        """ initial a qureg with qubit(s)

        Args:
            qubits: the qubits which make up the qureg, it can have below form,
                1) int
                2) qubit
                3) [qubits/quregs]
        """
        super().__init__()
        if qubits is None:
            return

        if isinstance(qubits, int):
            for _ in range(qubits):
                self.append(Qubit())
        elif isinstance(qubits, Qubit):
            self.append(qubits)
        elif isinstance(qubits, list):
            for qubit in qubits:
                if isinstance(qubit, Qubit):
                    self.append(qubit)
                elif isinstance(qubit, Qureg):
                    self.extend(qubit)
                else:
                    raise TypeError("Qureg.qubits", "int/Qubit/list<Qubit/Qureg>", type(qubit))
        else:
            raise TypeError("Qureg.qubits", "int/Qubit/list<Qubit/Qureg>", type(qubits))

    def __call__(self, indexes: object):
        """ get a smaller qureg from this qureg

        Args:
            indexes: the indexes passed in, it can have follow form:
                1) int
                2) list<int>
        Returns:
            Qubit[s]: the qureg correspond to the indexes
        """
        if isinstance(indexes, int):
            return Qureg(self[indexes])

        return self[indexes]

    def __getitem__(self, item):
        """ to fit the slice operator, overloaded this function.

        get a smaller qureg/qubit from this qureg

        Args:
            item(int/slice): slice passed in.

        Return:
            Qubit/Qureg: the result or slice
        """
        if isinstance(item, int):
            return super().__getitem__(item)

        qureg = Qureg()
        if isinstance(item, slice):
            qureg_list = super().__getitem__(item)
            for qubit in qureg_list:
                qureg.append(qubit)
        elif isinstance(item, list) or isinstance(item, tuple):
            for idx in item:
                assert isinstance(idx, int), TypeError("Qureg.getitem.item.value", "int", type(idx))
                if idx < 0 or idx > len(self):
                    raise IndexExceedError("Qureg.getitem", [0, len(self)], idx)

                qureg.append(self[idx])
        else:
            raise TypeError("Qureg.getitem", "int/list[int]/slice", type(item))

        return qureg

    def __int__(self):
        """ the value of the register

        Return the value of the register if all qubits have been measured.
        Note that the compute mode is BigEndian.

        Returns:
            int: the value of the register

        Raises:
            Exception: some qubit has not be measured
        """
        value = 0
        for qubit in self:
            value <<= 1
            value += int(qubit)

        return value

    def __str__(self):
        """ the string of the value of the register

        Returns:
            str: the value of the qureg
        """
        bit_idx = "{0:0b}".format(self.__int__())
        bit_idx = bit_idx.zfill(len(self))

        return bit_idx

    def __add__(self, other):
        """ get a combined qureg with this qureg and other qureg

        Args:
            other(Qureg): qureg to be added.

        Return:
            Qureg: the result or slice
        """
        return Qureg([self, other])

    def __iadd__(self, other):
        """ get a combined qureg with this qureg and other qureg

        Args:
            other(Qureg): qureg to be added.

        Return:
            Qureg: the result or slice
        """
        if isinstance(other, Qubit):
            self.append(other)
        elif isinstance(other, Qureg):
            self.extend(other)
        else:
            raise TypeError("Qureg.iadd", "Qureg/Qubit", type(other))

        return self

    def __eq__(self, other):
        """
        check two qureg is same or not. Iff all qubits in two qureg are same will
        return True; otherwise, return False.

        Args:
            other(Qureg): qureg to be checked.
        """
        assert isinstance(other, Qureg), TypeError("Qureg.eq", "Qureg", type(other))
        if not len(other) == len(self):
            return False

        current_qubit_ids = [qubit.id for qubit in self]
        for qubit in other:
            if qubit.id not in current_qubit_ids:
                return False

        return True

    def index(self, qubit: Union[List[Qubit], Qubit]) -> Union[int, list]:
        """ Return the index of given qubits.

        Args:
            qubit (Union[List[Qubit], Qubit]): The given qubits

        Returns:
            Union[int, list]: The index of given qubits in current qureg.
        """
        if isinstance(qubit, Qubit):
            return super().index(qubit)

        if isinstance(qubit, list):
            idxes = []
            for q in qubit:
                idxes.append(super().index(q))

            return idxes

        raise ValueError("Qureg.index.qubit", "within current Qureg", "qubit is not")

    def _normalized_parameters(self, parameters: Union[float, list], place: str):
        if not isinstance(parameters, list):
            parameters = [parameters] * len(self)
        else:
            assert isinstance(parameters, list), \
                TypeError(f"Qureg.{place}", "List", f"{type(parameters)}")
            assert len(parameters) == len(self), \
                ValueError(f"Qureg.{place}", f"the length should equal {len(self)}", f"{len(parameters)}")

        return parameters

    def set_fidelity(self, fidelity: Union[float, tuple, list]):
        """ Set the fidelity for each qubits

        Args:
            fidelity (list): The list of fidelity for each qubits, should equal to len(qureg).
        """
        fidelity = self._normalized_parameters(fidelity, "fidelity")
        for idx, qubit in enumerate(self):
            qubit.fidelity = fidelity[idx]

    def set_preparation_fidelity(self, fidelity: Union[float, list]):
        """ Set the QSP fidelity for each qubits

        Args:
            fidelity (list): The list of fidelity for each qubits, should equal to len(qureg).
        """
        fidelity = self._normalized_parameters(fidelity, "preparation_fidelity")
        for idx, qubit in enumerate(self):
            qubit.preparation_fidelity = fidelity[idx]

    def set_gate_fidelity(self, gate_fidelity: Union[float, list]):
        """ Set the Single-Qubit Gate Fidelity for each qubits

        Args:
            gate_fidelity (list): The list of gate fidelity for each qubits, should equal to len(qureg).
        """
        gate_fidelity = self._normalized_parameters(gate_fidelity, "gate_fidelity")
        for idx, qubit in enumerate(self):
            qubit.gate_fidelity = gate_fidelity[idx]

    def set_t1_time(self, t1_time: list):
        """ Set the T1 coherence time for each qubit

        Args:
            t1_time (list): The T1 time for each qubit
        """
        t1_time = self._normalized_parameters(t1_time, "t1")
        for idx, qubit in enumerate(self):
            qubit.T1 = t1_time[idx]

    def set_t2_time(self, t2_time: list):
        """ Set the T2 coherence time for each qubit

        Args:
            t2_time (list): The T2 time for each qubit
        """
        t2_time = self._normalized_parameters(t2_time, "t2")
        for idx, qubit in enumerate(self):
            qubit.T2 = t2_time[idx]

    def set_work_frequency(self, work_frequency: Union[float, list]):
        work_frequency = self._normalized_parameters(work_frequency, "work_frequency")
        for idx, qubit in enumerate(self):
            qubit.work_frequency = work_frequency[idx]

    def set_readout_frequency(self, readout_frequency: Union[float, list]):
        readout_frequency = self._normalized_parameters(readout_frequency, "readout_frequency")
        for idx, qubit in enumerate(self):
            qubit.readout_frequency = readout_frequency[idx]

    def set_gate_duration(self, gate_duration: Union[float, list]):
        gate_duration = self._normalized_parameters(gate_duration, "gate_duration")
        for idx, qubit in enumerate(self):
            qubit.gate_duration = gate_duration[idx]

    def reset_qubits(self):
        """ Reset all qubits' status. """
        for qubit in self:
            qubit.reset()
