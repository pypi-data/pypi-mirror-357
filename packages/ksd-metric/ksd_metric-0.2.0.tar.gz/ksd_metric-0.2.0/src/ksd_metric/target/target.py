from abc import ABC, abstractmethod

from jax import jacfwd, jit
from jaxtyping import Array, Float

from ..typing import ArrayLike, DifferentiableFunction


class TargetDistributionInterface(ABC):
    """
    Interface for target distributions used in Kernel Stein Discrepancy (KSD).
    """

    @abstractmethod
    def log_target_pdf(
        self,
        x: ArrayLike,
    ) -> ArrayLike:
        """
        Logarithmic Probability Density Function.

        Args:
            x (ArrayLike): Input data point.

        Returns:
            (ArrayLike): Logarithmic probability density at x.
        """
        raise NotImplementedError("log_target_pdf method must be implemented.")

    @abstractmethod
    def grad_log_target_pdf(
        self,
        x: ArrayLike,
    ) -> ArrayLike:
        """
        Gradient of Logarithmic Probability Density Function.

        Args:
            x (ArrayLike): Input data point.

        Returns:
            (ArrayLike): Gradient of logarithmic probability density at x.
        """
        raise NotImplementedError("grad_log_target_pdf method must be implemented.")


class TargetDistributionJax(TargetDistributionInterface):
    """
    Represents a target distribution for the KSD.
    """

    def __init__(
        self,
        log_target_pdf: DifferentiableFunction,
    ) -> None:
        """
        Initializes the target distribution with a logarithmic probability density function.

        Args:
            log_target_pdf (DifferentiableFunction): A function that computes the log of the target PDF.
        """
        self._log_target_pdf_func = log_target_pdf

    def log_target_pdf(
        self,
        x: Float[Array, "num dim"],
    ) -> Float[Array, "num dim"]:
        """
        Computes the log probability density at the given point.

        Args:
            x (Float[Array, "num dim"]): Input data point.

        Returns:
            Float[Array, "num dim"]: Logarithmic probability density at x.
        """
        return self._log_target_pdf_func(x)

    def grad_log_target_pdf(
        self,
        x: Float[Array, "num dim"],
    ) -> Float[Array, "num dim"]:
        """
        Gradient of Logarithmic Probability Density Function.

        Args:
            x (Float[Array, "num dim"]): Input data point.

        Returns:
            Float[Array, "num dim"]: Gradient of logarithmic probability density at x.
        """
        return jit(jacfwd(self._log_target_pdf_func))(x)
