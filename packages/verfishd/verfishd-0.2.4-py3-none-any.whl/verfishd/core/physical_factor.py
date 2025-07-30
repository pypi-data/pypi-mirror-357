from abc import ABC, abstractmethod


class PhysicalFactor(ABC):
    """
    Abstract base class for physical factors.

    Parameters
    ----------
    name : str
        The name of the factor which is used in the physical stimuli profile.
    weight : float
        The weight is used to scale the factor's contribution to the evaluation function E.
    """
    def __init__(self, name: str, weight: float):
        if not isinstance(weight, (int, float)):
            raise TypeError("Weight must be a number (int or float).")
        self.weight = weight
        self.name = name
        self.display_name = name.replace('_', ' ').capitalize()

    def calculate(self, value: float) -> float:
        """
        Validates the input value and calls the subclass's implementation of _calculate.

        Parameters
        ----------
        value : float
            A numeric input to the calculation.

        Returns
        -------
        float
            The result of the calculation as a float.
        """
        if not isinstance(value, (int, float)):
            raise TypeError("The input value must be a number (int or float).")

        return self._calculate(value)

    @abstractmethod
    def _calculate(self, value: float) -> float:
        """
        Abstract method for the actual calculation, to be implemented by subclasses.

        The result of this method must be between -1 and 1 to normalize the resulting fish movements.

        Parameters
        ----------
        value : float
            A numeric input to the calculation.

        Returns
        -------
        float
            The result of the calculation as a float.
        """
        pass
