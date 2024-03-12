from calendar import month_abbr
from itertools import cycle
from typing import List, Optional

import matplotlib.pyplot as plt
from numpy import array, linspace, meshgrid, reshape
from pandas import Series
from scipy.stats import gaussian_kde

from ._typing import Axes
from .utils import validate_index, validate_series


def si(
    si: Series,
    ybound: float = 3.0,
    figsize: tuple = (6.5, 4),
    ax: Optional[Axes] = None,
) -> Axes:
    """Plot the standardized index values as a time series.

    Parameters
    ----------
    si : pandas.Series
        Series of the standardized index
    ybound : int, optional
        Maximum and minimum ylim of plot
    figsize : tuple, optional
        Figure size, by default (8, 4)
    ax : matplotlib.Axes, optional
        Axes handle, by default None which create a new axes

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    ax.plot(si.index, si.values, linewidth=1.0, color="k")
    ax.axhline(0, linestyle="--", linewidth=1.0, color="k")

    nmin = -ybound
    nmax = ybound
    droughts = si.to_numpy(dtype=float, copy=True)
    droughts[droughts > 0] = 0
    nodroughts = si.to_numpy(dtype=float, copy=True)
    nodroughts[nodroughts < 0] = 0

    x, y = meshgrid(si.index, linspace(nmin, nmax, 100))
    ax.contourf(
        x, y, y, cmap=plt.get_cmap("seismic_r"), levels=linspace(nmin, nmax, 100)
    )
    ax.fill_between(x=si.index, y1=droughts, y2=nmin, color="w")
    ax.fill_between(x=si.index, y1=nodroughts, y2=nmax, color="w")
    ax.set_ylim(nmin, nmax)

    return ax


def monthly_density(
    si: Series,
    years: List[int],
    months: List[int],
    cmap: str = "tab20c",
    ax: Optional[Axes] = None,
) -> Axes:
    """Plot the monthly kernel-density estimate for a specific year.

    Parameters
    ----------
    si : pandas.Series
        Series of the standardized index
    year : list, optional
        List of years as int
    months : list, optional
        List of months as int, by default all months
    cmap : str, optional
        matlotlib colormap, by default 'tab10'
    ax : matplotlib.Axes, optional
        Axes handle, by default None which create a new axes

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """

    si = validate_series(si)
    index = validate_index(si.index)

    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4))

    cm = plt.get_cmap(cmap, 20)
    colors = reshape(array([cm(x) for x in range(20)], dtype="f,f,f,f"), (5, 4))
    lsts = cycle(["--", "-.", ":"])

    ind = linspace(-3.3, 3.3, 1000)
    for i, month in enumerate(months):
        gkde_all = gaussian_kde(si[(index.month == month)])
        ax.plot(
            ind,
            gkde_all.evaluate(ind),
            c=colors[i, 0],
            label=f"{month_abbr[month]} all",
        )
        for j, year in enumerate(years, start=1):
            gkde_spec = gaussian_kde(si[(index.month == month) & (index.year == year)])
            ax.plot(
                ind,
                gkde_spec.evaluate(ind),
                c=colors[i, j],
                label=f"{month_abbr[month]} {year}",
                linestyle=next(lsts),
            )
    ax.set_ylabel("Kernel-Density Estimate")
    ax.set_xlim(ind[0], ind[-1])
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(True)

    return ax
