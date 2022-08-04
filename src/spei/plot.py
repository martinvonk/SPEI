import matplotlib.pyplot as plt
from numpy import meshgrid, linspace
from calendar import month_name
from .utils import check_series


def si(si, bound=3, figsize=(8, 4), ax=None):
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

    ax.plot(si, color='k', label='SGI')
    ax.axhline(0, linestyle="--", color="k")

    nmin = -bound
    nmax = bound
    droughts = si.to_numpy(copy=True)
    droughts[droughts > 0] = 0
    nodroughts = si.to_numpy(copy=True)
    nodroughts[nodroughts < 0] = 0

    x, y = meshgrid(si.index, linspace(nmin, nmax, 100))
    ax.contourf(x, y, y, cmap=plt.cm.seismic_r,
                levels=linspace(nmin, nmax, 100))
    ax.fill_between(x=si.index, y1=droughts, y2=nmin, color='w')
    ax.fill_between(x=si.index, y1=nodroughts, y2=nmax, color='w')
    ax.set_ylim(nmin, nmax)

    return ax


def dist(series, dist, cumulative=False, cmap=None, figsize=(8, 10), legend=True):
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
        c = ['k' for _ in range(12)]

    for i, month in enumerate(range(1, 13)):
        data = series[series.index.month == month].sort_values()
        *pars, loc, scale = dist.fit(data, scale=data.std())
        ax[i].hist(data, color=c[i], alpha=0.2, density=True,
                   cumulative=cumulative, label='Density')
        if cumulative:
            cdf = dist.cdf(data, pars, loc=loc, scale=scale)
            ax[i].plot(data, cdf, color=c[i],
                       label=f'{dist.name.capitalize()} fit:\n{loc=:0.1f}\n{scale=:0.1f}')
            if i in range(0, 12, 3):
                ax[i].set_ylabel('Cumulative Probability')
        else:
            x = linspace(min(data), max(data))
            pdf = dist.pdf(x, pars, loc=loc, scale=scale)
            ax[i].plot(
                x, pdf, color=c[i], label=f'{dist.name.capitalize()} fit:\n{loc=:0.1f}\n{scale=:0.1f}')
            if i in range(0, 12, 3):
                ax[i].set_ylabel('Probability Density')
        ax[i].set_title(month_name[month])
        if legend:
            ax[i].legend()

    return axs
