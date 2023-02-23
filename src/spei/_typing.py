# flake8: noqa
from typing import Any, Union

from matplotlib.axes import Axes as mplAxes
from numpy import float64
from numpy.typing import NDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Union[Any, rv_continuous]
Axes = Union[Any, mplAxes]
NDArrayAxes = NDArray[Axes]
NDArrayFloat = NDArray[float64]
