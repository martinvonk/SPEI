from typing import Any, Union

from matplotlib.axes import Axes
from numpy import float64
from numpy.typing import NDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Union[Any, rv_continuous]
Axes = Union[Any, Axes]
