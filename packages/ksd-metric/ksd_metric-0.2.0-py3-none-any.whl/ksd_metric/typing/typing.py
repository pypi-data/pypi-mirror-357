from typing import Any, Callable, TypeAlias, Union

import numpy as np
from jaxtyping import Array, Float
from numpy import typing as npt

# Define a differentiable function type that accepts and returns floating-point arrays
DifferentiableFunction: TypeAlias = Callable[[Float[Array, "num"]], Float[Array, "num"]]

# Define a generic array type that supports both JAX and NumPy arrays
ArrayLike: TypeAlias = Union[
    Float[Array, "num"], Float[npt.NDArray[np.floating], "num"]
]
