from typing import Union, List


class Operator:
    """ The SuperClass of all the operator. """
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self._name = name

    @property
    def qubits(self):
        return self._qubit_number

    @property
    def targets(self):
        return self._qubit_number

    @property
    def targ(self):
        return self._targs[0]

    @property
    def targs(self):
        return self._targs

    @targs.setter
    def targs(self, targets: Union[List, int]):
        if isinstance(targets, int):
            targets = [targets]

        assert isinstance(targets, list), TypeError(
            f"qubits must be one of [List[int], int], not {type(targets)}"
        )
        assert len(targets) == self.qubits, f"The length of targets should be equal {self.qubits}."
        for idx in targets:
            assert idx >= 0, f"targets must be a positive integer, not {idx}"

        self._targs = targets

    def __init__(
        self,
        targets: int,
        name: str = None
    ):
        """
        Args:
            targets (int): the number of the target bits of the gate
            name (str): The name of current trigger, Default to None.
        """
        assert targets >= 0 and isinstance(targets, int), f"targets must be a positive integer, not {type(targets)}"
        self._qubit_number = targets
        self._targs = []
        self.cargs = []
        self._name = name

    def __and__(self, targets: Union[List[int], int],):
        """ Assigned the trigger's target qubits.

        Args:
            targets (Union[List[int], int]): The indexes of target qubits.
        """
        if isinstance(targets, int):
            assert targets >= 0 and self.qubits == 1
            self._targs = [targets]
        elif isinstance(targets, list):
            assert len(targets) == self.qubits
            for q in targets:
                assert q >= 0 and isinstance(q, int), f"targets must be a positive integer, not {q}"

            self._targs = targets
        else:
            raise TypeError(f"qubits must be one of [List[int], int], not {type(targets)}")

        return self

    def __or__(self, targets):
        """ Append the trigger to the circuit.

        Args:
            targets (Circuit): The circuit which contains the trigger.
        """
        try:
            targets.append(self)
        except Exception as e:
            raise TypeError(f"Failure to append Trigger to targets, due to {e}")

    def copy(self):
        return self
