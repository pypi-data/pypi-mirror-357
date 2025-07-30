from jax import numpy as jnp
from jaxtyping import Array, Float


class JaxKernelFunction:
    """
    A class to represent a JAX kernel function.
    This class is used to encapsulate the JAX kernel function and its associated parameters.
    """

    @staticmethod
    def rbf(
        x: Float[Array, "num"],
        y: Float[Array, "num"],
        sigma: float = 1.0,
    ) -> Float[Array, "num"]:
        """
        Radial Basis Function (RBF) kernel, also known as Gaussian kernel.

        Args:
            x (Float[Array, "num"]): Input data point.
            y (Float[Array, "num"]): Input data point.
            sigma (float): The bandwidth parameter for the RBF kernel.

        Returns:
            Float[Array, "num"]: The value of the RBF kernel at (x, y).
        """
        diff = x - y
        return jnp.exp(-jnp.dot(diff, diff) / (2 * sigma**2))

    @staticmethod
    def linear(
        x: Float[Array, "num"],
        y: Float[Array, "num"],
    ) -> Float[Array, "num"]:
        """
        Linear kernel function.

        Args:
            x (Float[Array, "num"]): Input data point.
            y (Float[Array, "num"]): Input data point.

        Returns:
            Float[Array, "num"]: The value of the linear kernel at (x, y).
        """
        return jnp.dot(x, y)

    @staticmethod
    def imq(
        x: Float[Array, "num"],
        y: Float[Array, "num"],
        linv: Float[Array, "num num"],
        beta: float = 0.5,
    ) -> Float[Array, "num"]:
        """
        Inverse Multiquadric kernel function.

        Args:
            x (Float[Array, "num"]): Input data point.
            y (Float[Array, "num"]): Input data point.
            linv (Float[Array, "num num"]): Inverse of the length scale matrix.
            beta (float): The shape parameter for the inverse multiquadric kernel.

        Returns:
            Float[Array, "num"]: The value of the inverse multiquadric kernel at (x, y).
        """
        diff = x - y
        return (1.0 + (diff @ linv @ diff)) ** (-beta)
