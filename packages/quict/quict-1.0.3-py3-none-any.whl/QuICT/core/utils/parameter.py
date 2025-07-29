import numbers

from QuICT.tools.exception.core import TypeError


class Parameter:
    """Used to represent trainable parameters of parameterized quantum gates or parameterized quantum circuits.

    Note:
        Only supports number multiplication operation.

    Args:
        symbol (str): The symbol.

    Examples:
        >>> from QuICT.core.circuit import Circuit
        >>> from QuICT.core.gate import *
        >>> cir = Circuit(3)
        >>> H | cir
        >>> Rx("x") | cir(0)
        >>> Rx(Parameter("x") * 0.3) | cir(2)
        >>> Rzz("y") | cir([0, 1])
        >>> cir.draw("command")
                ┌───┐ ┌───────┐
        q_0: |0>┤ h ├─┤ rx(x) ├───■──────
                ├───┤ └───────┘   │ZZ(y)
        q_1: |0>┤ h ├─────────────■──────
                ├───┤┌──────────┐
        q_2: |0>┤ h ├┤ rx(0.3x) ├────────
                └───┘└──────────┘
    """

    @property
    def symbol(self) -> str:
        """The symbol in the parameter.

        Returns:
            str: The symbol.
        """
        return self._symbol

    @property
    def expr(self) -> str:
        """The expression of the parameter.

        Returns:
            str: The expression of the parameter.
        """
        return self._expr

    @property
    def multiplier(self) -> float:
        """The multiplier of the symbol.

        Returns:
            float: The multiplier.
        """
        return self._multiplier

    @property
    def dx(self) -> float:
        """The derivative of the parameter on the symbol.

        Returns:
            float: The derivative.
        """
        return self._dx

    def __init__(self, symbol: str):
        """Initialize a Parameter instance."""
        self._symbol = symbol
        self._expr = symbol
        self._multiplier = 1.0
        self._dx = 1.0

    def __str__(self) -> str:
        """Return the expression of the parameter."""
        return self._expr

    def __mul__(self, other):
        """Multiply a number.

        Args:
            other (numbers.Number): The multiplier.

        Returns:
            Parameter: The new parameter after number multiplication operation.
        """
        assert isinstance(other, numbers.Number), TypeError(
            "Parameter.__mul__.other", "numbers.Number", type(other)
        )
        new_param = Parameter(self._symbol)
        new_param._expr = str(other) + self._symbol
        new_param._multiplier = self._multiplier * other
        new_param._dx = self._dx * other
        return new_param

    def __rmul__(self, other):
        """Multiply a number.

        Args:
            other (numbers.Number): The multiplier.

        Returns:
            Parameter: The new parameter after number multiplication operation.
        """
        return self.__mul__(other)

    def __lt__(self, other):
        """Determine whether the current parameter is smaller than another parameter.

        Args:
            other (Parameter): Another parameter.

        Returns:
            bool: If True, the current parameter is smaller than another parameter.
        """
        assert isinstance(other, Parameter), TypeError(
            "Parameter.__lt__.other", "Parameter", type(other)
        )
        if self._symbol == other._symbol:
            if self._multiplier < other._multiplier:
                return True
        else:
            if self._expr < other._expr:
                return True
        return False
