import matplotlib.pyplot as plt
from numpy import meshgrid, linspace

def plot_si(si, figsize=(8,4)):

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
    ax.contourf(x, y, y, cmap=plt.cm.seismic_r, levels=linspace(nmin, nmax, 100))
    ax.fill_between(x=si.index, y1=droughts, y2=nmin, color='w')
    ax.fill_between(x=si.index, y1=nodroughts, y2=nmax, color='w')
    ax.set_ylim(nmin, nmax)

    return ax
