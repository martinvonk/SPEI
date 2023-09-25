# flake8: noqa
from typing import Any, TypeVar, Union

from matplotlib.axes import Axes as mplAxes
from numpy import float64
from numpy.typing import NDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Union[Any, rv_continuous]
Axes = TypeVar("Axes", bound=Union[mplAxes, Any])
NDArrayAxes = NDArray[Any]
NDArrayFloat = NDArray[float64]
