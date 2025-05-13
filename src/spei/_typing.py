# flake8: noqa
from typing import Any

from numpy import float64
from numpy.typing import NDArray
from scipy.stats._continuous_distns import rv_continuous

ContinuousDist = Any | rv_continuous
NDArrayAxes = NDArray[Any]
NDArrayFloat = NDArray[float64]
