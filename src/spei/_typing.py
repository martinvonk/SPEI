# flake8: noqa
from typing import Any, Union

from matplotlib.axes import Axes
from numpy import float64 as npfloat64
from numpy.typing import NDArray as npNDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Union[Any, rv_continuous]
Axes = Union[Any, Axes]
NDArray = npNDArray
float64 = npfloat64
