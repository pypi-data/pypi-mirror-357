from abc import ABC, abstractmethod
from typing import Any

from jax import jacfwd, jit
from jaxtyping import Array, Float

from ..typing import DifferentiableFunction


class TargetDistributionInterface(ABC):
    """
    Interface for target distributions used in Kernel Stein Discrepancy (KSD).
    """

    @abstractmethod
    def log_target_pdf(self, x: Any) -> Any:
        """
        Logarithmic Probability Density Function.

        Args:
            x (array-like): Input data point.

        Returns:
            (array-like): Logarithmic probability density at x.
        """
        raise NotImplementedError("log_target_pdf method must be implemented.")

    @abstractmethod
    def grad_log_target_pdf(self, x: Any) -> Any:
        """
        Gradient of Logarithmic Probability Density Function.

        Args:
            x (array-like): Input data point.

        Returns:
            (array-like): Gradient of logarithmic probability density at x.
        """
        raise NotImplementedError("grad_log_target_pdf method must be implemented.")


class TargetDistributionJax(TargetDistributionInterface):
    """
    Represents a target distribution for the KSD.
    """

    def __init__(self, log_target_pdf: DifferentiableFunction) -> None:
        """
        Initializes the target distribution with a logarithmic probability density function.

        Args:
            log_target_pdf (callable): A function that computes the log of the target PDF.
        """
        self._log_target_pdf_func = log_target_pdf

    def log_target_pdf(self, x: Float[Array, "num dim"]) -> Float[Array, "num dim"]:
        """
        Computes the log probability density at the given point.

        Args:
            x (array-like): Input data point.

        Returns:
            array-like: Logarithmic probability density at x.
        """
        return self._log_target_pdf_func(x)

    def grad_log_target_pdf(
        self, x: Float[Array, "num dim"]
    ) -> Float[Array, "num dim"]:
        """
        Gradient of Logarithmic Probability Density Function.

        Args:
            x (array-like): Input data point.

        Returns:
            array-like: Gradient of logarithmic probability density at x.
        """
        return jit(jacfwd(self._log_target_pdf_func))(x)
