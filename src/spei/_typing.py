# flake8: noqa
from typing import Any, Union, TypeVar

# from matplotlib.axes import Axes
from numpy import float64, generic
from numpy.typing import NDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Union[Any, rv_continuous]
Axes = TypeVar("Axes", bound=generic, covariant=True)
NDArrayAxes = NDArray[Axes]
NDArrayFloat = NDArray[float64]
