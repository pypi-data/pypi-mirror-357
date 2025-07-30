from QuICT.core.gate import H, CX, T, T_dagger, CompositeGate


class HLTR1(CompositeGate):
    r"""
        Implement a TR1 Gate using T gates:

        $$
            \vert{c}\rangle \vert{b}\rangle \vert{a}\rangle
            \to
            \vert{a\cdot \bar{b}\oplus c}\rangle \vert{a\oplus b}\rangle \vert{a}\rangle
        $$

        References:
            [1]: "Efficient quantum arithmetic operation circuits for quantum image processing" by
            Hai-Sheng Li, Ping Fan, Haiying Xia, Huiling Peng and Gui-Lu Long
            <https://doi.org/10.1007/s11433-020-1582-8>
    """

    def __init__(self, name: str = "TR1"):
        """
            Args:
                name (str, optional): The name of TR1 gate.
        """
        super().__init__(name)
        self._tr1_build()

    def _tr1_build(self):
        """
            Construct a TR1 Gate.
        """
        H | self([0])
        CX | self([1, 0])
        CX | self([0, 2])
        T | self([0])
        T_dagger | self([1])
        T_dagger | self([2])
        CX | self([1, 2])
        CX | self([1, 0])
        T_dagger | self([2])
        CX | self([0, 2])
        CX | self([2, 1])
        T | self([0])
        T | self([1])
        T | self([2])
        H | self([0])


class HLTR2(CompositeGate):
    r"""
        Implement a TR2 Gate using T gates:

        $$
            \vert{c}\rangle \vert{b}\rangle \vert{a}\rangle
            \to
            \vert{a\cdot \bar{b}\oplus c}\rangle \vert{b}\rangle \vert{a \oplus b}\rangle
        $$

        References:
            [1]: "Efficient quantum arithmetic operation circuits for quantum image processing" by
            Hai-Sheng Li, Ping Fan, Haiying Xia, Huiling Peng and Gui-Lu Long
            <https://doi.org/10.1007/s11433-020-1582-8>
    """

    def __init__(self, name: str = "TR2"):
        """
            Args:
                name (str, optional): The name of TR2 gate.
        """
        super().__init__(name)
        self._tr2_build()

    def _tr2_build(self):
        """
            Construct a TR2 Gate.
        """
        T | self([1])
        T_dagger | self([2])
        H | self([0])
        CX | self([1, 2])
        T_dagger | self([0])
        CX | self([2, 0])
        CX | self([0, 1])
        T | self([1])
        T_dagger | self([2])
        T | self([0])
        CX | self([2, 1])
        T_dagger | self([1])
        CX | self([2, 0])
        CX | self([0, 1])
        H | self([0])
