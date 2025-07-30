from abc import ABC, abstractmethod
from functools import partial

import jax
from jax import numpy as jnp
from jaxtyping import Array, Float

from ..kernel import KernelInterface, KernelJax
from ..target import TargetDistributionInterface, TargetDistributionJax
from ..typing import ArrayLike


class KernelSteinDiscrepancyInterface(ABC):
    def __init__(
        self,
        target: TargetDistributionInterface,
        kernel: KernelInterface,
    ) -> None:
        """
        Initializes the KernelSteinDiscrepancyInterface with a target distribution.

        Args:
            target (TargetDistributionInterface): The target distribution interface.
            kernel (KernelInterface): The kernel interface used for computing the Stein kernel.
        """
        self.target = target
        self.kernel = kernel

    @abstractmethod
    def stein_kernel(
        self,
        x: ArrayLike,
        y: ArrayLike,
    ) -> ArrayLike:
        """
        Computes the Stein kernel using the base kernel function and the gradient of the log target PDF.

        Args:
            x (Float[Array, "num"]): Input data point.
            y (Float[Array, "num"]): Input data point.

        Returns:
            Float[Array, "num"]: The value of the Stein kernel at (x, y).
        """
        raise NotImplementedError("stein_kernel must be implemented.")

    @abstractmethod
    def kernel_stein_discrepancy(
        self,
        samples: ArrayLike,
    ) -> float:
        """
        Computes the kernel Stein discrepancy for the given samples.

        Args:
            samples (ArrayLike): A collection of samples from the target distribution.

        Returns:
            float: The value of the kernel Stein discrepancy for the given samples.
        """
        raise NotImplementedError("kernel_stein_discrepancy must be implemented.")


class KernelSteinDiscrepancyJax(KernelSteinDiscrepancyInterface):
    def __init__(
        self,
        target: TargetDistributionJax,
        kernel: KernelJax,
    ) -> None:
        """
        Initializes the KernelSteinDiscrepancyJax with a target distribution and a kernel.

        Args:
            target (TargetDistributionJax): The target distribution.
            kernel (KernelJax): The kernel function.
        """
        super().__init__(target=target, kernel=kernel)

    @partial(jax.jit, static_argnums=(0,))
    def stein_kernel(
        self,
        x: Float[Array, "num"],
        y: Float[Array, "num"],
    ) -> Float[Array, "num"]:
        """
        Computes the Stein kernel using the base kernel function and the gradient of the log target PDF.

        Args:
            x (Float[Array, "num"]): Input data point.
            y (Float[Array, "num"]): Input data point.

        Returns:
            Float[Array, "num"]: The value of the Stein kernel at (x, y).
        """
        dx_k = self.kernel.partial_derivative_x_kernel_function(x, y)
        dy_k = self.kernel.partial_derivative_y_kernel_function(x, y)
        dxdy_k = self.kernel.cross_partial_derivative_kernel_function(x, y)

        grad_log_p_x = self.target.grad_log_target_pdf(x)
        grad_log_p_y = self.target.grad_log_target_pdf(y)

        return (
            jnp.trace(dxdy_k)
            + dx_k @ grad_log_p_y
            + dy_k @ grad_log_p_x
            + self.kernel.base_kernel_function(x, y) * grad_log_p_x @ grad_log_p_y
        )

    @partial(jax.jit, static_argnums=(0,))
    def _vectorised_kernel_stein_discrepancy(
        self,
        samples: Float[Array, "num dim"],
    ) -> Float[Array, "float"]:
        """
        Computes the kernel Stein discrepancy for a collection of samples.

        Args:
            samples (Float[Array, "num dim"]): A collection of samples from the target distribution.

        Returns:
            Float[Array, "float"]: The value of the kernel Stein discrepancy for the given samples
        """
        num = samples.shape[0]
        k = jax.vmap(jax.vmap(self.stein_kernel, in_axes=(None, 0)), in_axes=(0, None))(
            samples, samples
        )
        ksd = (1.0 / num) * jnp.sqrt(jnp.sum(k))
        return ksd

    def kernel_stein_discrepancy(self, samples: Float[Array, "num dim"]) -> float:
        """
        Computes the kernel Stein discrepancy for the given samples.

        Args:
            samples (Float[Array, "num dim"]): A collection of samples from the target distribution.

        Returns:
            float: The value of the kernel Stein discrepancy for the given samples.
        """
        return self._vectorised_kernel_stein_discrepancy(samples).item()
