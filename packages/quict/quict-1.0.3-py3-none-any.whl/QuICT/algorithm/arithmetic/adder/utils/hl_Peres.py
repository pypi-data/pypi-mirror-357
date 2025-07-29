from QuICT.core.gate import H, CX, T, T_dagger, CompositeGate


class HLPeres(CompositeGate):
    r"""
        Implement a Peres Gate using T gates:

        $$
            \vert{c}\rangle \vert{b}\rangle \vert{a}\rangle
            \to
            \vert{a \cdot b\oplus c}\rangle \vert{a \oplus b}\rangle \vert{a}\rangle
        $$

        References:
            [1]: "Efficient quantum arithmetic operation circuits for quantum image processing" by
            Hai-Sheng Li, Ping Fan, Haiying Xia, Huiling Peng and Gui-Lu Long
            <https://doi.org/10.1007/s11433-020-1582-8>
    """

    def __init__(self, name: str = "PG1"):
        """
            Args:
                 name (str): the name of the Peres gate.
        """
        super().__init__(name)
        self._pg_build()

    def _pg_build(self):
        """
            Construct a Peres Gate.
        """
        H | self([0])
        CX | self([1, 0])
        CX | self([0, 2])
        T_dagger | self([2])
        T_dagger | self([1])
        T | self([0])
        CX | self([1, 2])
        T | self([2])
        CX | self([1, 0])
        CX | self([0, 2])
        CX | self([2, 1])
        T_dagger | self([2])
        T | self([1])
        T_dagger | self([0])
        H | self([0])
