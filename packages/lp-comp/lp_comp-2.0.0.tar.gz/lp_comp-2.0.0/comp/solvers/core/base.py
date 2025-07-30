from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union, Dict, Any

from comp.models import BaseData

T_base_data = TypeVar("T_base_data", bound=BaseData)


class BaseSolver(ABC, Generic[T_base_data]):
    """Base class for all optimization solvers."""

    def __init__(self, data: T_base_data) -> None:
        """
        Initialize the base solver with data and validation.

        Stores the input data and calls the `validate_input` method.
        Sets `setup_done` flag to False.

        :param data: The data object (subclass of BaseData) for the solver.
        """

        self.data: T_base_data = data
        self.setup_done: bool = False

        self.validate_input()

    @abstractmethod
    def print_results(self, print_details: bool = True, tolerance: float = 1e-9) -> None:
        """
        Print the results of the optimization problem.

        Concrete implementations should define how to format and display
        the solution and relevant metrics.

        :param print_details: If True, print additional details about the optimization results.
        :param tolerance: The tolerance for comparing floating-point numbers.
        """

        pass

    @abstractmethod
    def validate_input(self) -> None:
        """
        Validate the input data for the optimization problem.

        Concrete implementations should define specific checks for their
        required data structures and values.
        """

        pass

    @abstractmethod
    def quality_functional(self) -> Union[str, float]:
        """
        Calculate and return the quality functional of the solved problem.

        Concrete implementations should define how the quality functional
        is computed based on the problem type and solution.
        It can return a numerical value or a string representation if appropriate.

        :return: The calculated quality is functional, as a float or a string.
        """

        pass

    @abstractmethod
    def get_results_dict(self) -> Dict[str, Any]:
        """
        Get the results of the optimization problem as a dictionary.

        Concrete implementations should return a dictionary containing
        relevant results, such as objective values, variable values, and
        any other pertinent information from the optimization process.

        :return: A dictionary with results from the optimization problem.
        """

        pass
