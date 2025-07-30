from abc import ABC, abstractmethod
from typing import Callable

from jax import jacfwd, jit
from jaxtyping import Array, Float

from ..typing import ArrayLike, DifferentiableFunction


class KernelInterface(ABC):
    def __init__(
        self, base_kernel_function: Callable[[ArrayLike, ArrayLike], ArrayLike]
    ) -> None:
        """
        Initializes the KernelInterface with a base kernel function.

        Args:
            base_kernel_function (Callable[[ArrayLike, ArrayLike], ArrayLike]): A function that computes the kernel between two points.
        """
        self._base_kernel_function = base_kernel_function

    @abstractmethod
    def base_kernel_function(self, x: ArrayLike, y: ArrayLike) -> ArrayLike:
        """
        Base kernel function to be implemented by subclasses.
        This function should return the base kernel function used in KSD.

        Args:
            x (ArrayLike): First input data point.
            y (ArrayLike): Second input data point.

        Returns:
            ArrayLike: The value of the base kernel function at (x, y).
        """
        raise NotImplementedError("base_kernel_function must be implemented.")

    @abstractmethod
    def partial_derivative_x_kernel_function(
        self, x: ArrayLike, y: ArrayLike
    ) -> ArrayLike:
        """
        Computes the partial derivative of the kernel function with respect to x.

        Args:
            x (ArrayLike): Input data point.
            y (ArrayLike): Input data point.

        Returns:
            ArrayLike: The partial derivative of the kernel function with respect to x.
        """
        raise NotImplementedError(
            "partial_derivative_x_kernel_function must be implemented."
        )

    @abstractmethod
    def partial_derivative_y_kernel_function(
        self, x: ArrayLike, y: ArrayLike
    ) -> ArrayLike:
        """
        Computes the partial derivative of the kernel function with respect to y.

        Args:
            y (ArrayLike): Input data point.
            x (ArrayLike): Input data point.

        Returns:
            ArrayLike: The partial derivative of the kernel function with respect to y.
        """
        raise NotImplementedError(
            "partial_derivative_y_kernel_function must be implemented."
        )

    @abstractmethod
    def cross_partial_derivative_kernel_function(
        self, x: ArrayLike, y: ArrayLike
    ) -> ArrayLike:
        """
        Computes the cross partial derivative of the kernel function with respect to x and y.

        Args:
            x (ArrayLike): First input data point.
            y (ArrayLike): Second input data point.

        Returns:
            ArrayLike: The cross partial derivative of the kernel function with respect to x and y.
        """
        raise NotImplementedError(
            "cross_partial_derivative_kernel_function must be implemented."
        )


class KernelJax(KernelInterface):
    """
    Represents a kernel function for the KSD.
    """

    def __init__(self, base_kernel_function: DifferentiableFunction) -> None:
        """
        Initializes the kernel with a base kernel function.

        Args:
            base_kernel_function (DifferentiableFunction): A function that computes the kernel between two points.
        """
        super().__init__(base_kernel_function=base_kernel_function)

    def base_kernel_function(
        self, x: Float[Array, "num"], y: Float[Array, "num"]
    ) -> Float[Array, "num"]:
        """
        Base kernel function to be implemented by subclasses.
        This function should return the base kernel function used in KSD.

        Args:
            x (Float[Array, "num"]): First input data point.
            y (Float[Array, "num"]): Second input data point.

        Returns:
            Float[Array, "num"]: The value of the base kernel function at (x, y).
        """
        return self._base_kernel_function(x, y)

    def partial_derivative_x_kernel_function(
        self, x: Float[Array, "num"], y: Float[Array, "num"]
    ) -> Float[Array, "num"]:
        """
        Computes the partial derivative of the kernel function with respect to x.

        Args:
            x (Float[Array, "num"]): Input data point.

        Returns:
            Float[Array, "num"]: The partial derivative of the kernel function with respect to x.
        """
        return jit(jacfwd(self.base_kernel_function, argnums=0))(x, y)

    def partial_derivative_y_kernel_function(
        self, x: Float[Array, "num"], y: Float[Array, "num"]
    ) -> Float[Array, "num"]:
        """
        Computes the partial derivative of the kernel function with respect to y.

        Args:
            y (Float[Array, "num"]): Input data point.

        Returns:
            Float[Array, "num"]: The partial derivative of the kernel function with respect to y.
        """
        return jit(jacfwd(self.base_kernel_function, argnums=1))(x, y)

    def cross_partial_derivative_kernel_function(
        self, x: Float[Array, "num"], y: Float[Array, "num"]
    ) -> Float[Array, "num"]:
        """
        Computes the cross partial derivative of the kernel function with respect to x and y.

        Args:
            x (Float[Array, "num"]): First input data point.
            y (Float[Array, "num"]): Second input data point.

        Returns:
            Float[Array, "num"]: The cross partial derivative of the kernel function with respect to x and y.
        """
        return jit(jacfwd(self.partial_derivative_y_kernel_function, argnums=0))(x, y)
