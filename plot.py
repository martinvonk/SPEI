import matplotlib.pyplot as plt
from numpy import meshgrid, linspace
from calendar import month_name


def si(si, figsize=(8, 4)):

    _, ax = plt.subplots(figsize=figsize)

    ax.plot(si, color='k', label='SGI')
    ax.axhline(0, linestyle="--", color="k")

    nmin = -3
    nmax = 3
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


def dist(series, dist, cumulative=False, cmap='Set3', figsize=(8, 10), legend=True):

    _, axs = plt.subplots(4, 3, figsize=figsize, sharey=True, sharex=True)
    ax = axs.ravel()
    cm = plt.get_cmap(cmap)

    for i, month in enumerate(range(1, 13)):
        data = series[series.index.month == month].sort_values()
        *pars, loc, scale = dist.fit(data)
        cdf = dist.cdf(data, pars, loc=loc, scale=scale)
        ax[i].hist(data, color=cm(i), alpha=0.2, density=True,
                   cumulative=cumulative, label=f'Density')
        if cumulative:
            ax[i].plot(data, cdf, color=cm(
                i), label=f'{loc=:0.2f}\n{scale=:0.2f}')
        else:
            x = linspace(min(data), max(data))
            ax[i].plot(x, dist.pdf(x, pars, loc=loc, scale=scale), color=cm(
                i), label=f'{dist.name.capitalize()} fit:\n{loc=:0.2f}\n{scale=:0.2f}')
        ax[i].set_title(month_name[month])
        if legend:
            ax[i].legend()

    return axs
