import matplotlib.pyplot as plt

from typing import Any
from itertools import cycle
from calendar import month_name, month_abbr
from pandas import Series
from numpy import meshgrid, linspace, array, reshape
from scipy.stats import gaussian_kde
from .utils import check_series, dist_test


def si(si: Series, bound: float = 3.0, figsize: tuple = (8, 4), ax: Any = None) -> Any:
    """Plot the standardized index values as a time series.

    Parameters
    ----------
    si : pandas.Series
        Series of the standardized index
    bound : int, optional
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

    ax.plot(si, color="k", label="SGI")
    ax.axhline(0, linestyle="--", color="k")

    nmin = -bound
    nmax = bound
    droughts = si.to_numpy(copy=True)
    droughts[droughts > 0] = 0
    nodroughts = si.to_numpy(copy=True)
    nodroughts[nodroughts < 0] = 0

    x, y = meshgrid(si.index, linspace(nmin, nmax, 100))
    ax.contourf(x, y, y, cmap=plt.cm.seismic_r, levels=linspace(nmin, nmax, 100))
    ax.fill_between(x=si.index, y1=droughts, y2=nmin, color="w")
    ax.fill_between(x=si.index, y1=nodroughts, y2=nmax, color="w")
    ax.set_ylim(nmin, nmax)

    return ax


def dist(
    series: Series,
    dist: Any,
    cumulative: bool = False,
    test_dist: bool = True,
    cmap: str = None,
    figsize: tuple = (8, 10),
    legend: bool = True,
) -> Any:
    """Plot the (cumulative) histogram and scipy fitted distribution
    for the time series on a monthly basis.

    Parameters
    ----------
    series : pandas.Series
        Time series of the precipitation (excess) or head
    dist : scipy.stats._continuous_distns
        Continuous distribution of the scipy stats library
        to fit on series using maximum likelihood estimation
    cumulative : bool, optional
        If True plots cumulative histogram instead of probability
        density histogram, by default False
    test_dist : bool, optional
        If True, fit the distribution with the two-sided
        Kolmogorov-Smirnov test for goodness of fit.
    cmap : str, optional
        Matplotlib colormap name to use in subplots, by default None
        which uses black for all subplots.
    figsize : tuple, optional
        Figure size, by default (8, 10)
    legend : bool, optional
        Add legend, by default True

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """

    check_series(series)

    _, axs = plt.subplots(4, 3, figsize=figsize, sharey=True, sharex=True)
    ax = axs.ravel()
    if cmap is not None:
        cm = plt.get_cmap(cmap, 12)
        c = [cm(i) for i in range(12)]
    else:
        c = ["k" for _ in range(12)]

    for i, month in enumerate(range(1, 13)):
        data = series[series.index.month == month].sort_values()
        ax[i].hist(
            data,
            color=c[i],
            alpha=0.2,
            density=True,
            cumulative=cumulative,
            label="Density",
        )
        if test_dist:
            _, p_value, _, *pars, loc, scale = dist_test(data, dist)
            label = f"{dist.name.capitalize()} KS:\n{p_value=:0.2f}"
        else:
            *pars, loc, scale = dist.fit(data, scale=data.std())
            label = f"{dist.name.capitalize()} fit:\n{loc=:0.1f}\n{scale=:0.1f}"
        if cumulative:
            cdf = dist.cdf(data, pars, loc=loc, scale=scale)
            ax[i].plot(
                data,
                cdf,
                color=c[i],
                label=label,
            )
            if i in range(0, 12, 3):
                ax[i].set_ylabel("Cumulative Probability")
        else:
            x = linspace(min(data), max(data))
            pdf = dist.pdf(x, pars, loc=loc, scale=scale)
            ax[i].plot(
                x,
                pdf,
                color=c[i],
                label=label,
            )
            if i in range(0, 12, 3):
                ax[i].set_ylabel("Probability Density")
        ax[i].set_title(month_name[month])
        if legend:
            ax[i].legend()

    return axs


def monthly_density(
    si: Series,
    years: list[int] = [],
    months: list[int] = [],
    cmap: str = "tab20c",
    ax: Any = None,
) -> Any:
    """Plot the monthly kernel-density estimate for a specific year.

    Parameters
    ----------
    si : pandas.Series
        Series of the standardized index
    year : list
        List of years as int
    months : list
        List of months as int
    cmap : str, optional
        matlotlib colormap, by default 'tab10'
    ax : matplotlib.Axes, optional
        Axes handle, by default None which create a new axes

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    cm = plt.get_cmap(cmap, 20)
    colors = reshape(array([cm(x) for x in range(20)], dtype="f,f,f,f"), (5, 4))
    lsts = cycle(["--", "-.", ":"])

    ind = linspace(-3.3, 3.3, 1000)
    for i, month in enumerate(months):
        gkde_all = gaussian_kde(si[(si.index.month == month)])
        ax.plot(
            ind,
            gkde_all.evaluate(ind),
            c=colors[i, 0],
            label=f"{month_abbr[month]} all",
        )
        for j, year in enumerate(years, start=1):
            gkde_spec = gaussian_kde(
                si[(si.index.month == month) & (si.index.year == year)]
            )
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
