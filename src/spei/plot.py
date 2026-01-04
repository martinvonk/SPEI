import logging
from calendar import month_abbr
from itertools import cycle

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes._secondary_axes import SecondaryAxis
from matplotlib.dates import date2num
from numpy import arange, array, concatenate, linspace, meshgrid, reshape
from pandas import (
    DataFrame,
    DatetimeIndex,
    Series,
    Timedelta,
    Timestamp,
    concat,
    infer_freq,
)
from scipy.stats import gaussian_kde

from .utils import get_data_series, group_yearly_df, validate_index


def si(
    si: Series,
    add_category: bool = True,
    figsize: tuple[float, float] = (6.5, 4.0),
    cmap: str | mpl.colors.Colormap = "seismic_r",
    background: bool = True,
    ax: plt.Axes | None = None,
    **kwargs,
) -> plt.Axes:
    """Plot the standardized index values as a time series.

    Parameters
    ----------
    si : pandas.Series
        Series of the standardized index
    add_category: bool, optional
        Add the category labels to the right y-axis, by default True
    figsize : tuple[float], optional
        Figure size, by default (6.5, 4)
    cmap: str, optional
        Colormap for the background or line fill
    background: bool, optional
        Color the background if True, else color the line
    ax : matplotlib.Axes, optional
        Axes handle, by default None which create a new axes

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if isinstance(cmap, str):
        if cmap in Crameri._available_cmaps:
            colormap = Crameri(cmap).cmap
        else:
            colormap = plt.get_cmap(cmap)
    else:
        colormap = cmap

    if "ybound" in kwargs:
        raise DeprecationWarning(
            "The 'ybound' argument is deprecated and will be ignored. To set y-axis "
            "limits, use the 'set_ylim()' method on the returned Axes instance."
        )

    ymin, ymax = -3.0, 3.0  # default y-axis limits, also used for colormap norm

    if background:
        ax.plot(si.index, si.to_numpy(dtype=float), linewidth=0.8, color="k")
        ax.axhline(0, linestyle="--", linewidth=0.5, color="k")

        droughts = si.to_numpy(dtype=float, copy=True)
        droughts[droughts > 0] = 0
        nodroughts = si.to_numpy(dtype=float, copy=True)
        nodroughts[nodroughts < 0] = 0

        x, y = meshgrid(si.index, linspace(ymin, ymax, 100))
        ax.contourf(x, y, y, cmap=colormap, levels=linspace(ymin, ymax, 100))
        ax.fill_between(x=si.index, y1=droughts, y2=ymin, color="w", interpolate=True)
        ax.fill_between(x=si.index, y1=nodroughts, y2=ymax, color="w", interpolate=True)
    else:
        datetime = DatetimeIndex(si.index).to_pydatetime()
        x = date2num(datetime)
        y = si.to_numpy(dtype=float)
        points = array([x, y]).T.reshape(-1, 1, 2)
        segments = concatenate([points[:-1], points[1:]], axis=1)
        lc = mpl.collections.LineCollection(
            segments, cmap=colormap, norm=plt.Normalize(ymin, ymax)
        )
        lc.set_array(y)
        lc.set_linewidth(1.2)
        _ = ax.add_collection(lc)

    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(1))
    ax.set_ylim(ymin, ymax)

    if add_category:
        _ = _add_category_labels(ax)

    return ax


def threshold(
    series: Series,
    threshold: Series,
    figsize: tuple[float, float] = (6.5, 4.0),
    fill_color: str = "red",
    ax: plt.Axes | None = None,
    **kwargs,
) -> plt.Axes:
    """Plot the time series with a threshold line and fill the area below the threshold.

    Parameters
    ----------
    series : pandas.Series
        Time series of the meteorological of hydrological data
    threshold : pandas.Series
        Series of the threshold, must have the same index as series
    color : str, optional
        Color for the fill area, by default 'red'
    ax : matplotlib.Axes, optional
        Axes handle, by default None which create a new axes

    Returns
    -------
    matplotlib.Axes
        Axes handle
    """
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if kwargs is None:
        kwargs = {}

    series_values = series.to_numpy(float)
    threshold_values = threshold.to_numpy(dtype=float)

    line_color = kwargs.pop("color", "k")
    label = kwargs.pop("label", series.name)
    ax.plot(
        series.index, series_values, color=line_color, label=label, zorder=2, **kwargs
    )
    ax.plot(
        threshold.index,
        threshold_values,
        color="grey",
        label=threshold.name,
        linestyle="--",
        linewidth=1.0,
        zorder=0,
    )
    where = (series_values < threshold_values).ravel().tolist()
    ax.fill_between(
        x=series.index,
        y1=series_values,
        y2=threshold_values,
        where=where,
        interpolate=True,
        color=fill_color,
        label="Drought",
        zorder=1,
    )
    return ax


def _add_category_labels(ax: plt.Axes) -> SecondaryAxis:
    """Add category based on the standardized index values to the right y-axis."""
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.5))
    sax = ax.secondary_yaxis("right")
    sax.set_yticks([-2.5, -1.75, -1.25, -0.5, 0.5, 1.25, 1.75, 2.5], minor=True)
    sax.set_yticks([-3.0, -2.0, -1.5, -1.0, 0.0, 1.0, 1.5, 2.0, 3.0], minor=False)
    sax.set_yticklabels(
        [
            "Extreme drought",
            "Severe drought",
            "Moderate drought",
            "Mild drought",
            "Mildly wet",
            "Moderately wet",
            "Severely wet",
            "Extremely wet",
        ],
        minor=True,
    )
    sax.set_yticklabels([], minor=False)
    for tick in sax.yaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
    return sax


def monthly_density(
    si: Series,
    years: list[int],
    months: list[int],
    cmap: str | mpl.colors.Colormap = "tab20c",
    ax: plt.Axes | None = None,
) -> plt.Axes:
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

    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4.0))

    colormap = plt.get_cmap(cmap, 20) if isinstance(cmap, str) else cmap
    colors = reshape(array([colormap(x) for x in range(20)], dtype="f,f,f,f"), (5, 4))
    lsts = cycle(["--", "-.", ":"])

    ind = linspace(-3.3, 3.3, 100)
    si_grdf = group_yearly_df(si)
    index = validate_index(si_grdf.index)
    for i, month in enumerate(months):
        si_month = get_data_series(si_grdf.loc[index.month == month])
        si_month_index = validate_index(si_month.index)
        gkde_all = gaussian_kde(si_month)
        ax.plot(
            ind,
            gkde_all.evaluate(ind),
            c=colors[i, 0],
            label=f"{month_abbr[month]} all",
        )
        for j, year in enumerate(years, start=1):
            gkde_spec = gaussian_kde(si_month[si_month_index.year == year])
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


def heatmap(
    sis: list[Series],
    add_category: bool = False,
    cmap: str = "Reds_r",
    vmin: float = -3.0,
    vmax: float = -1.0,
    yticklabels: list[str] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Plots multiple standardized indices on a heatmap.

    Parameters
    ----------
    sis : List[Series]
        A list of pandas Series objects, each representing a time series of SI values.
    add_category : bool, optional
        If True, adds category labels to the colorbar. Default is False.
    cmap : str, optional
        The colormap to use for the heatmap. Default is "Reds_r".
    vmin : float, optional
        The minimum value for color normalization. Default is -3.0.
    vmax : float, optional
        The maximum value for color normalization. Default is -1.0.
    yticklabels : List[str] or None, optional
        Custom labels for the y-axis ticks. If None, the names of the Series objects are used. Default is None.
    ax : matplotlib Axes, optional
        A matplotlib Axes object to plot on. If None, a new figure and axes are created. Default is None.
    Returns
    -------
    Matplotlib Axes
        The matplotlib Axes object with the heatmap.

    References
    ----------
    van Mourik, J., Ruijsch, D., van der Wiel, K., Hazeleger, W., Wanders, N.: Regional
    drivers and characteristics of multi-year droughts. 2024
    """

    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4.0))

    fig = ax.get_figure()

    if isinstance(cmap, str):
        if cmap in Crameri._available_cmaps:
            colormap = Crameri(cmap).cmap
        else:
            colormap = plt.get_cmap(cmap)
    else:
        colormap = cmap

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    sisdf = concat(sis, axis=1)
    freq = infer_freq(DatetimeIndex(sisdf.index))
    # Efficiently extend the index for pcolormesh based on frequency
    if freq in ("MS", "YS"):
        dt = sisdf.index[1] - sisdf.index[0]
        index = sisdf.index.insert(0, sisdf.index[0] - dt)
    elif freq in ("ME", "YE", "D"):
        if freq == "D":
            logging.info(
                "With freq='D', it is assumed that the value is recorded"
                "at the end of the index value."
            )
        dt = sisdf.index[-1] - sisdf.index[-2]
        index = sisdf.index.append(DatetimeIndex([sisdf.index[-1] + dt]))
    else:
        raise ValueError(
            f"Unsupported frequency '{freq}' for the index of the Series. "
            "Expected 'MS', 'ME', 'YS', 'YE', or 'D'."
        )
    _ = ax.pcolormesh(
        index,
        arange(0.0, len(sis) + 1.0, 1.0),
        sisdf.values.T,
        cmap=colormap,
        norm=norm,
        shading="flat",
    )
    ax.set_yticks(arange(0.5, len(sis) + 0.5, 1.0), minor=False)
    ax.set_yticks(arange(0.0, len(sis) + 1.5, 1.0), minor=True)
    yticklabels = (
        [getattr(s, "name") for s in sis] if yticklabels is None else yticklabels
    )
    ax.set_yticklabels(yticklabels)
    for tick in ax.yaxis.get_major_ticks():  # don't show major ytick marker
        tick.tick1line.set_visible(False)

    ax.set_ylim(0, len(sis))

    if fig is not None:
        # add colorbar
        scm = mpl.cm.ScalarMappable(norm=norm, cmap=colormap)
        cax, cbar_kw = mpl.colorbar.make_axes(
            ax,
            fraction=0.05,
            pad=0.05 if add_category else 0.01,
            orientation="vertical",
        )
        _ = fig.colorbar(scm, cax=cax, **cbar_kw)

        if add_category:
            cax.yaxis.set_ticks_position("left")
            cax.yaxis.set_label_position("left")
            _add_category_labels(cax)
            for tick in cax.yaxis.get_minor_ticks():  # don't show minor ytick marker
                tick.tick1line.set_visible(False)

    return ax


def deficit_knmi(
    df: DataFrame, ax: plt.Axes | None = None, window: int = 0
) -> plt.Axes:
    """
    Plots the precipitation deficit for various scenarios using the given DataFrame.

    The function generates a plot that visualizes the precipitation deficit over time
    for different statistical measures and specific years. It includes the 5% driest years,
    the median, specific record years (1976 and 2018), the maximum deficit, and optionally
    the current year if present in the DataFrame.

    Parameters:
    -----------
    df : pandas.DataFrame
        A DataFrame where:
        - Rows represent time (e.g., days or months within a year).
        - Columns represent years (e.g., 1976, 2018, etc.).
        - Values represent cumulative precipitation deficit (in millimeters).
    ax : matplotlib.axes._axes.Axes, optional
        An Axes object to plot on. If None, a new figure and axes are created.
    window : int, optional
        If True, applies a rolling mean over a n-day window to the median and
        95th percentile. This is also done by the KNMI but not documented.

    Returns:
    --------
    matplotlib.axes._axes.Axes
        The Axes object of the generated plot.

    Notes:
    ------
    - The x-axis represents the time of year, formatted as months (April to October).
    - The y-axis represents the precipitation deficit in millimeters.
    - The plot includes a grid on the y-axis for better readability.
    - If the current year is present in the DataFrame, it is highlighted in black.
    - The maximum deficit is annotated with the range of years in the dataset.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4.5), layout="tight")
    quant = (
        df.quantile(0.95, axis=1).rolling(Timedelta(days=window)).mean()
        if window
        else df.quantile(0.95, axis=1)
    )
    ax.plot(quant, label="5% driest years", color="lime")
    median = (
        df.median(axis=1).rolling(Timedelta(days=window)).mean()
        if window
        else df.median(axis=1)
    )
    ax.plot(median, label="median", color="blue")
    ax.plot(df.loc[:, 1976], label="record year 1976", color="red")
    ax.plot(df.loc[:, 2018], label="year 2018", color="grey")
    ax.plot(
        df.max(axis=1),
        label=f"maximum ({df.columns[0]}-{df.columns[-1]})",
        color="orange",
        linestyle=":",
    )
    year_today = Timestamp.today().year
    if year_today in df.columns:
        ax.plot(df.loc[:, year_today], label=f"year {year_today}", color="k")
    ax.grid(visible=True, axis="y")
    ax.yaxis.set_major_locator(locator=mpl.ticker.MultipleLocator(100.0))
    ax.set_ylabel("Precipitation deficit (mm)")
    ax.xaxis.set_major_locator(locator=mpl.dates.MonthLocator())
    ax.xaxis.set_major_formatter(formatter=mpl.dates.DateFormatter("%b"))
    ax.set_xlim(
        left=mpl.dates.date2num(Timestamp("2000-04-01")),
        right=mpl.dates.date2num(Timestamp("2000-10-01")),
    )
    ax.legend(loc="upper left")
    ax.set_ylim(bottom=0.0)
    return ax


class Crameri:
    """Colormaps for matplotlib, useful for drought, based on Crameri et al. (2020).

    References
    ----------
    Crameri, F., G.E. Shephard, and P.J. Heron: The misuse of colour in science
    communication, Nature Communications, 11, 5444. 2020.
    """

    _available_cmaps = ("roma", "roma_r", "vik", "vik_r", "lajolla", "lajolla_r")

    def __init__(self, name: str) -> None:
        self.name = name
        self._r = False if "_r" not in name else True
        assert self.name in self._available_cmaps, (
            f"Invalid colormap name: {self.name}. Available colormaps: {self._available_cmaps}"
        )
        self.cmap = self._get_cmap()

    def _get_cmap(self) -> mpl.colors.Colormap:
        if "roma" in self.name:
            return self.roma()
        elif "vik" in self.name:
            return self.vik()
        elif "lajolla" in self.name:
            return self.lajolla()
        else:
            raise ValueError(f"Invalid colormap name: {self.name}")

    @staticmethod
    def cmap_from_list(
        colors: list[list[float]],
        name: str,
        _r: bool = False,
    ) -> mpl.colors.Colormap:
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            name=name,
            colors=list(reversed(colors)) if _r else colors,
            N=len(colors),
        )
        return cmap

    def vik(
        self,
    ) -> mpl.colors.Colormap:
        colors = [
            [0.001328, 0.069836, 0.379529],
            [0.002366, 0.076475, 0.383518],
            [0.003304, 0.083083, 0.387487],
            [0.004146, 0.08959, 0.391477],
            [0.004897, 0.095948, 0.395453],
            [0.005563, 0.102274, 0.399409],
            [0.006151, 0.1085, 0.403388],
            [0.006668, 0.114686, 0.407339],
            [0.007119, 0.120845, 0.411288],
            [0.007512, 0.126958, 0.41523],
            [0.00785, 0.133068, 0.419166],
            [0.008141, 0.139092, 0.423079],
            [0.008391, 0.145171, 0.427006],
            [0.008606, 0.151144, 0.43091],
            [0.00879, 0.15714, 0.434809],
            [0.008947, 0.163152, 0.438691],
            [0.00908, 0.169142, 0.442587],
            [0.009193, 0.175103, 0.446459],
            [0.00929, 0.181052, 0.450337],
            [0.009372, 0.187051, 0.454212],
            [0.009443, 0.193028, 0.458077],
            [0.009506, 0.198999, 0.461951],
            [0.009564, 0.205011, 0.465816],
            [0.009619, 0.211021, 0.469707],
            [0.009675, 0.217047, 0.473571],
            [0.009735, 0.223084, 0.477461],
            [0.009802, 0.229123, 0.481352],
            [0.009881, 0.235206, 0.48525],
            [0.009977, 0.241277, 0.489161],
            [0.010098, 0.247386, 0.49308],
            [0.010254, 0.253516, 0.49702],
            [0.010463, 0.259675, 0.500974],
            [0.010755, 0.265853, 0.504938],
            [0.011176, 0.272037, 0.508925],
            [0.011716, 0.278296, 0.512923],
            [0.012286, 0.284554, 0.516953],
            [0.012934, 0.290865, 0.520998],
            [0.01379, 0.297214, 0.525074],
            [0.014838, 0.303577, 0.529184],
            [0.016131, 0.310015, 0.533308],
            [0.017711, 0.316474, 0.537485],
            [0.01963, 0.322986, 0.541677],
            [0.021948, 0.32955, 0.545931],
            [0.02473, 0.336144, 0.55021],
            [0.028047, 0.342826, 0.554538],
            [0.03198, 0.349543, 0.558906],
            [0.036812, 0.356332, 0.563341],
            [0.042229, 0.363171, 0.567811],
            [0.048008, 0.370086, 0.572345],
            [0.054292, 0.37708, 0.576933],
            [0.060963, 0.384129, 0.581571],
            [0.068081, 0.391265, 0.58628],
            [0.075457, 0.39846, 0.591042],
            [0.083246, 0.40574, 0.595868],
            [0.091425, 0.413088, 0.600754],
            [0.099832, 0.420499, 0.605697],
            [0.108595, 0.428, 0.610711],
            [0.117694, 0.435566, 0.61577],
            [0.127042, 0.443194, 0.620895],
            [0.136702, 0.450888, 0.626062],
            [0.146607, 0.458643, 0.631289],
            [0.156787, 0.466457, 0.63656],
            [0.167187, 0.474324, 0.641866],
            [0.177807, 0.482238, 0.647218],
            [0.188606, 0.490191, 0.652599],
            [0.19958, 0.498193, 0.658021],
            [0.210783, 0.506201, 0.663465],
            [0.22212, 0.514263, 0.668924],
            [0.233602, 0.522322, 0.674403],
            [0.245231, 0.530414, 0.679894],
            [0.256999, 0.538517, 0.685405],
            [0.268867, 0.546617, 0.690908],
            [0.280797, 0.554717, 0.696428],
            [0.292852, 0.562822, 0.701935],
            [0.304985, 0.570907, 0.707448],
            [0.317174, 0.578997, 0.71295],
            [0.329438, 0.587064, 0.718447],
            [0.341729, 0.595123, 0.723934],
            [0.354067, 0.603164, 0.729412],
            [0.366459, 0.611186, 0.734877],
            [0.378862, 0.619189, 0.740325],
            [0.391305, 0.627159, 0.745757],
            [0.40376, 0.635114, 0.751183],
            [0.416227, 0.643046, 0.756582],
            [0.428711, 0.650956, 0.761968],
            [0.441199, 0.658836, 0.767341],
            [0.453697, 0.666696, 0.772699],
            [0.466195, 0.674537, 0.778044],
            [0.478697, 0.682349, 0.783369],
            [0.491208, 0.690143, 0.788682],
            [0.503691, 0.69791, 0.79398],
            [0.516178, 0.705661, 0.79926],
            [0.528677, 0.713387, 0.804525],
            [0.541149, 0.72109, 0.809775],
            [0.553624, 0.728778, 0.81501],
            [0.566096, 0.736441, 0.820229],
            [0.578557, 0.744089, 0.825435],
            [0.591014, 0.751718, 0.830626],
            [0.603468, 0.759314, 0.835793],
            [0.615908, 0.766896, 0.840941],
            [0.628351, 0.774452, 0.846058],
            [0.640779, 0.781988, 0.851147],
            [0.653203, 0.789485, 0.856206],
            [0.665631, 0.796945, 0.861214],
            [0.678051, 0.804371, 0.866172],
            [0.690457, 0.811742, 0.871059],
            [0.702868, 0.819048, 0.875866],
            [0.715265, 0.82629, 0.880567],
            [0.727646, 0.833439, 0.885146],
            [0.740019, 0.840479, 0.88957],
            [0.752354, 0.84738, 0.893807],
            [0.764662, 0.854125, 0.897821],
            [0.776918, 0.860678, 0.901565],
            [0.789096, 0.866991, 0.904992],
            [0.80117, 0.873031, 0.908043],
            [0.81311, 0.878738, 0.910653],
            [0.82487, 0.884062, 0.912761],
            [0.836396, 0.888934, 0.914302],
            [0.847617, 0.893289, 0.915195],
            [0.85847, 0.897074, 0.915385],
            [0.868874, 0.900206, 0.914812],
            [0.878729, 0.902636, 0.913418],
            [0.887965, 0.904303, 0.911164],
            [0.896497, 0.905178, 0.908034],
            [0.904242, 0.905221, 0.904013],
            [0.911151, 0.904422, 0.899132],
            [0.917175, 0.9028, 0.893409],
            [0.922285, 0.900367, 0.886911],
            [0.926482, 0.897173, 0.879687],
            [0.929789, 0.893256, 0.871826],
            [0.932236, 0.888698, 0.863396],
            [0.93388, 0.883552, 0.854476],
            [0.934782, 0.877893, 0.845152],
            [0.935013, 0.871795, 0.835493],
            [0.934644, 0.865313, 0.825561],
            [0.933752, 0.858522, 0.815421],
            [0.932408, 0.851469, 0.805112],
            [0.930682, 0.844208, 0.794685],
            [0.928622, 0.836778, 0.784169],
            [0.926298, 0.829215, 0.773579],
            [0.923752, 0.821545, 0.762958],
            [0.921017, 0.813795, 0.752313],
            [0.918147, 0.805997, 0.741659],
            [0.915156, 0.798157, 0.731008],
            [0.91208, 0.790294, 0.72037],
            [0.908933, 0.782421, 0.709752],
            [0.905741, 0.77454, 0.69915],
            [0.902506, 0.76667, 0.688588],
            [0.899249, 0.758812, 0.678051],
            [0.895973, 0.750973, 0.66755],
            [0.89269, 0.743148, 0.657086],
            [0.889402, 0.735345, 0.646657],
            [0.886118, 0.727569, 0.636274],
            [0.882831, 0.719826, 0.625923],
            [0.879556, 0.712106, 0.615618],
            [0.876289, 0.704419, 0.605357],
            [0.873033, 0.696764, 0.595141],
            [0.869784, 0.689144, 0.584972],
            [0.866551, 0.681541, 0.574832],
            [0.863333, 0.673985, 0.564746],
            [0.860121, 0.666453, 0.554708],
            [0.85692, 0.658957, 0.544709],
            [0.853732, 0.6515, 0.534753],
            [0.850562, 0.644061, 0.524842],
            [0.847402, 0.63667, 0.514974],
            [0.844258, 0.629296, 0.505146],
            [0.841125, 0.621957, 0.495369],
            [0.838005, 0.614653, 0.485627],
            [0.834895, 0.607392, 0.475941],
            [0.831802, 0.600144, 0.466284],
            [0.828715, 0.592938, 0.456675],
            [0.825639, 0.585758, 0.447109],
            [0.822582, 0.5786, 0.437595],
            [0.819528, 0.571478, 0.428106],
            [0.816496, 0.564388, 0.418657],
            [0.813463, 0.557328, 0.40926],
            [0.810446, 0.550285, 0.399892],
            [0.807443, 0.543274, 0.390575],
            [0.804446, 0.536288, 0.381299],
            [0.801454, 0.529329, 0.37204],
            [0.798475, 0.52238, 0.362835],
            [0.7955, 0.51546, 0.35366],
            [0.792535, 0.508575, 0.344523],
            [0.789573, 0.501692, 0.335435],
            [0.786617, 0.494827, 0.326343],
            [0.783657, 0.487977, 0.317312],
            [0.780695, 0.481123, 0.3083],
            [0.777737, 0.474295, 0.299327],
            [0.774763, 0.467464, 0.290352],
            [0.771788, 0.46062, 0.281424],
            [0.768787, 0.453783, 0.272508],
            [0.765776, 0.446929, 0.26364],
            [0.762724, 0.440055, 0.254764],
            [0.759638, 0.433147, 0.245872],
            [0.75651, 0.4262, 0.237047],
            [0.753316, 0.419216, 0.22819],
            [0.750051, 0.412163, 0.21933],
            [0.746698, 0.405028, 0.21047],
            [0.743239, 0.397819, 0.201593],
            [0.739651, 0.390493, 0.192739],
            [0.735899, 0.38306, 0.183852],
            [0.731988, 0.375473, 0.174977],
            [0.727865, 0.367743, 0.166045],
            [0.723516, 0.359852, 0.157131],
            [0.718915, 0.351766, 0.148211],
            [0.714028, 0.343503, 0.139282],
            [0.708841, 0.335048, 0.130458],
            [0.703318, 0.326354, 0.121545],
            [0.697448, 0.317502, 0.112841],
            [0.691227, 0.308462, 0.104132],
            [0.684653, 0.299264, 0.095633],
            [0.677734, 0.289916, 0.08735],
            [0.670476, 0.280477, 0.079197],
            [0.662904, 0.271015, 0.07151],
            [0.655048, 0.26152, 0.064079],
            [0.646969, 0.252081, 0.057104],
            [0.638686, 0.242711, 0.050618],
            [0.630261, 0.233488, 0.04475],
            [0.621722, 0.224449, 0.039414],
            [0.613135, 0.215657, 0.034829],
            [0.604539, 0.207086, 0.031072],
            [0.595947, 0.198741, 0.028212],
            [0.587403, 0.1907, 0.026019],
            [0.578937, 0.182918, 0.024396],
            [0.570545, 0.175423, 0.023257],
            [0.562268, 0.168171, 0.022523],
            [0.554076, 0.161202, 0.02211],
            [0.546007, 0.1544, 0.021861],
            [0.538043, 0.147854, 0.021737],
            [0.530182, 0.141491, 0.021722],
            [0.522424, 0.135276, 0.0218],
            [0.514776, 0.129209, 0.021957],
            [0.507213, 0.123272, 0.022179],
            [0.499733, 0.117487, 0.022455],
            [0.492348, 0.111818, 0.022775],
            [0.485034, 0.106209, 0.02313],
            [0.477801, 0.100607, 0.023513],
            [0.470639, 0.095156, 0.023916],
            [0.46353, 0.089668, 0.024336],
            [0.456494, 0.084258, 0.024766],
            [0.449521, 0.078741, 0.025203],
            [0.442603, 0.073404, 0.025644],
            [0.435737, 0.067904, 0.026084],
            [0.428918, 0.062415, 0.026522],
            [0.422146, 0.056832, 0.026954],
            [0.415437, 0.051116, 0.027378],
            [0.408768, 0.045352, 0.02779],
            [0.402132, 0.039448, 0.028189],
            [0.395562, 0.033385, 0.02857],
            [0.389015, 0.027844, 0.028932],
            [0.382496, 0.022586, 0.029271],
            [0.376028, 0.017608, 0.029583],
            [0.369578, 0.01289, 0.029866],
            [0.363161, 0.008243, 0.030115],
            [0.356785, 0.004035, 0.030327],
            [0.350423, 6.1e-05, 0.030499],
        ]
        return Crameri.cmap_from_list(colors, self.name, _r=self._r)

    def roma(self) -> mpl.colors.Colormap:
        colors = [
            [0.492325, 0.090787, 7.6e-05],
            [0.49673, 0.102802, 0.003675],
            [0.501125, 0.114034, 0.007134],
            [0.505473, 0.124685, 0.010421],
            [0.509813, 0.13489, 0.013817],
            [0.514125, 0.144643, 0.016841],
            [0.518397, 0.154036, 0.01972],
            [0.522634, 0.163193, 0.022451],
            [0.52685, 0.172041, 0.025034],
            [0.531016, 0.180682, 0.027528],
            [0.535142, 0.189147, 0.030132],
            [0.539225, 0.197418, 0.032869],
            [0.543266, 0.205524, 0.035925],
            [0.547254, 0.213477, 0.038888],
            [0.551203, 0.221318, 0.041994],
            [0.5551, 0.229015, 0.045012],
            [0.558954, 0.236607, 0.047967],
            [0.562776, 0.244053, 0.051012],
            [0.56654, 0.251456, 0.053998],
            [0.570257, 0.258727, 0.057033],
            [0.57394, 0.265922, 0.060051],
            [0.577577, 0.273024, 0.063001],
            [0.581178, 0.280048, 0.065873],
            [0.584739, 0.286993, 0.068856],
            [0.588249, 0.29388, 0.071712],
            [0.591737, 0.300697, 0.074564],
            [0.595174, 0.30745, 0.077376],
            [0.598577, 0.314151, 0.080252],
            [0.601948, 0.320797, 0.083076],
            [0.605282, 0.327364, 0.085853],
            [0.608593, 0.333908, 0.088711],
            [0.611855, 0.340387, 0.091525],
            [0.615092, 0.346826, 0.094279],
            [0.618309, 0.353217, 0.096979],
            [0.621487, 0.359572, 0.099753],
            [0.62465, 0.365896, 0.102506],
            [0.627785, 0.372174, 0.105218],
            [0.630901, 0.378439, 0.107956],
            [0.633994, 0.38467, 0.110736],
            [0.637068, 0.390894, 0.11348],
            [0.640129, 0.397078, 0.116219],
            [0.643171, 0.403273, 0.11896],
            [0.646208, 0.409445, 0.121674],
            [0.649242, 0.415612, 0.12447],
            [0.652261, 0.421776, 0.127267],
            [0.655276, 0.427961, 0.130152],
            [0.658297, 0.434132, 0.132974],
            [0.661315, 0.440331, 0.135825],
            [0.664334, 0.446543, 0.138777],
            [0.667364, 0.45278, 0.141759],
            [0.670402, 0.459031, 0.144786],
            [0.67344, 0.465303, 0.147848],
            [0.676494, 0.471628, 0.150966],
            [0.679554, 0.477967, 0.15416],
            [0.682637, 0.484345, 0.157428],
            [0.685735, 0.490782, 0.160789],
            [0.688849, 0.497239, 0.164248],
            [0.691977, 0.503744, 0.167748],
            [0.69512, 0.510297, 0.171371],
            [0.698285, 0.516904, 0.175115],
            [0.701472, 0.523556, 0.178956],
            [0.704681, 0.530258, 0.182899],
            [0.707908, 0.537021, 0.18701],
            [0.711162, 0.543825, 0.191228],
            [0.714426, 0.550692, 0.195605],
            [0.717725, 0.557617, 0.200115],
            [0.72103, 0.564592, 0.204829],
            [0.724366, 0.57163, 0.209678],
            [0.727717, 0.578727, 0.214708],
            [0.731087, 0.585886, 0.219946],
            [0.73448, 0.593098, 0.225346],
            [0.737879, 0.600364, 0.230969],
            [0.741297, 0.607699, 0.236808],
            [0.744731, 0.615074, 0.242822],
            [0.748175, 0.622516, 0.249103],
            [0.751624, 0.630013, 0.255599],
            [0.755074, 0.637558, 0.262334],
            [0.758523, 0.645147, 0.269325],
            [0.761963, 0.652786, 0.276547],
            [0.765406, 0.66047, 0.28401],
            [0.76882, 0.668197, 0.291755],
            [0.772224, 0.675947, 0.299742],
            [0.775598, 0.683727, 0.307981],
            [0.778939, 0.691534, 0.316505],
            [0.782242, 0.699353, 0.325257],
            [0.785493, 0.707188, 0.334299],
            [0.788687, 0.715019, 0.343564],
            [0.791812, 0.722841, 0.353091],
            [0.794864, 0.730654, 0.362848],
            [0.797828, 0.738438, 0.372842],
            [0.800699, 0.746187, 0.383072],
            [0.803461, 0.753893, 0.393496],
            [0.806107, 0.761537, 0.404131],
            [0.808624, 0.769113, 0.41495],
            [0.810997, 0.776617, 0.425936],
            [0.813218, 0.784025, 0.437088],
            [0.815281, 0.791322, 0.448363],
            [0.817167, 0.798508, 0.459757],
            [0.818865, 0.805562, 0.471253],
            [0.820371, 0.812478, 0.482813],
            [0.821675, 0.81924, 0.49444],
            [0.822757, 0.825842, 0.50608],
            [0.823613, 0.83227, 0.517753],
            [0.824237, 0.838506, 0.5294],
            [0.82462, 0.844553, 0.541003],
            [0.824755, 0.850392, 0.552561],
            [0.824634, 0.856022, 0.564037],
            [0.824253, 0.861429, 0.575407],
            [0.823606, 0.866611, 0.586656],
            [0.822692, 0.871564, 0.597769],
            [0.821502, 0.876273, 0.608734],
            [0.820031, 0.880744, 0.619513],
            [0.818285, 0.884972, 0.630101],
            [0.816266, 0.888952, 0.64049],
            [0.813955, 0.892681, 0.65066],
            [0.811371, 0.89616, 0.6606],
            [0.808502, 0.899389, 0.670314],
            [0.805347, 0.902364, 0.679761],
            [0.801918, 0.905092, 0.688973],
            [0.79821, 0.907568, 0.697906],
            [0.794228, 0.909794, 0.706586],
            [0.789963, 0.911771, 0.714983],
            [0.785431, 0.913506, 0.723105],
            [0.780623, 0.914991, 0.730953],
            [0.775551, 0.916237, 0.738521],
            [0.770217, 0.917249, 0.745803],
            [0.764624, 0.918014, 0.7528],
            [0.758773, 0.918542, 0.759517],
            [0.752665, 0.918838, 0.765957],
            [0.746318, 0.918903, 0.772108],
            [0.739731, 0.918739, 0.777981],
            [0.732897, 0.91835, 0.783574],
            [0.725834, 0.917737, 0.788893],
            [0.718537, 0.916896, 0.793938],
            [0.71103, 0.915828, 0.798708],
            [0.7033, 0.914552, 0.803212],
            [0.69536, 0.913054, 0.807458],
            [0.687217, 0.911341, 0.811442],
            [0.678874, 0.909414, 0.815168],
            [0.670351, 0.90728, 0.818643],
            [0.661635, 0.904933, 0.82188],
            [0.652735, 0.902379, 0.824863],
            [0.643676, 0.899624, 0.827614],
            [0.634464, 0.896664, 0.830135],
            [0.625086, 0.8935, 0.832423],
            [0.615567, 0.890145, 0.834491],
            [0.605914, 0.886598, 0.836336],
            [0.596145, 0.882852, 0.83797],
            [0.58626, 0.878925, 0.839394],
            [0.576278, 0.874814, 0.840613],
            [0.56619, 0.87052, 0.841632],
            [0.556024, 0.866058, 0.842458],
            [0.545813, 0.86142, 0.84309],
            [0.535527, 0.856619, 0.843538],
            [0.525217, 0.851658, 0.843811],
            [0.514877, 0.846543, 0.843909],
            [0.504532, 0.841286, 0.843838],
            [0.49418, 0.835884, 0.843605],
            [0.483842, 0.83035, 0.843216],
            [0.473543, 0.824685, 0.842677],
            [0.463293, 0.818902, 0.84199],
            [0.453115, 0.81301, 0.84116],
            [0.443005, 0.807018, 0.840201],
            [0.432982, 0.80092, 0.839108],
            [0.423057, 0.794738, 0.8379],
            [0.413269, 0.788474, 0.836571],
            [0.403599, 0.782136, 0.835134],
            [0.394062, 0.775727, 0.833595],
            [0.384684, 0.769261, 0.831959],
            [0.375472, 0.762745, 0.830227],
            [0.366446, 0.756186, 0.828409],
            [0.357593, 0.749581, 0.826514],
            [0.348916, 0.742958, 0.82454],
            [0.340447, 0.736291, 0.822504],
            [0.332185, 0.729618, 0.820394],
            [0.324113, 0.722919, 0.81823],
            [0.316282, 0.716224, 0.816018],
            [0.308653, 0.709514, 0.813746],
            [0.301225, 0.702804, 0.811437],
            [0.294036, 0.696099, 0.809086],
            [0.287067, 0.689401, 0.806696],
            [0.280322, 0.682707, 0.804272],
            [0.273816, 0.676034, 0.801816],
            [0.267484, 0.669377, 0.799343],
            [0.261414, 0.662739, 0.796836],
            [0.255543, 0.65612, 0.79432],
            [0.24986, 0.649522, 0.791778],
            [0.244403, 0.642944, 0.789229],
            [0.239162, 0.636402, 0.786665],
            [0.234103, 0.629874, 0.78409],
            [0.229233, 0.623385, 0.781503],
            [0.22453, 0.616915, 0.778909],
            [0.220062, 0.610472, 0.776315],
            [0.215727, 0.604065, 0.77371],
            [0.211566, 0.597675, 0.771114],
            [0.207553, 0.591317, 0.768502],
            [0.203709, 0.584989, 0.765902],
            [0.199968, 0.578679, 0.763292],
            [0.196442, 0.572403, 0.760691],
            [0.192988, 0.566143, 0.758086],
            [0.189677, 0.559913, 0.755482],
            [0.186487, 0.553693, 0.752873],
            [0.183398, 0.547501, 0.750276],
            [0.180424, 0.541321, 0.747679],
            [0.177586, 0.535164, 0.745074],
            [0.174797, 0.529026, 0.742478],
            [0.172082, 0.522885, 0.73988],
            [0.169502, 0.516755, 0.737273],
            [0.166959, 0.510628, 0.734673],
            [0.164485, 0.504518, 0.732066],
            [0.162089, 0.498397, 0.729453],
            [0.159699, 0.492262, 0.726836],
            [0.157413, 0.486128, 0.724215],
            [0.15518, 0.479992, 0.721583],
            [0.15296, 0.473828, 0.718948],
            [0.150805, 0.467661, 0.716306],
            [0.148654, 0.461471, 0.713644],
            [0.146549, 0.45526, 0.710977],
            [0.144488, 0.449025, 0.708292],
            [0.142409, 0.44276, 0.705595],
            [0.140344, 0.436466, 0.702886],
            [0.13831, 0.430142, 0.700156],
            [0.13621, 0.423782, 0.697413],
            [0.134205, 0.417407, 0.694652],
            [0.132133, 0.410984, 0.691884],
            [0.130086, 0.404521, 0.689094],
            [0.127967, 0.398042, 0.686279],
            [0.125859, 0.391517, 0.683451],
            [0.123663, 0.384945, 0.6806],
            [0.121475, 0.378353, 0.677747],
            [0.119286, 0.371714, 0.67486],
            [0.117003, 0.365049, 0.671962],
            [0.114652, 0.358343, 0.669046],
            [0.112324, 0.351597, 0.666107],
            [0.10989, 0.344819, 0.663159],
            [0.107324, 0.337994, 0.660182],
            [0.104641, 0.33113, 0.657195],
            [0.101951, 0.324237, 0.65418],
            [0.099119, 0.317305, 0.651154],
            [0.096135, 0.310338, 0.648101],
            [0.093031, 0.303295, 0.645033],
            [0.089832, 0.29624, 0.64195],
            [0.086378, 0.28914, 0.638844],
            [0.082771, 0.281987, 0.635717],
            [0.078888, 0.274774, 0.632572],
            [0.074823, 0.267513, 0.629402],
            [0.070429, 0.260237, 0.626217],
            [0.065707, 0.252891, 0.623014],
            [0.060588, 0.245475, 0.619791],
            [0.054957, 0.238038, 0.616544],
            [0.048861, 0.230521, 0.613271],
            [0.041963, 0.22298, 0.609992],
            [0.034076, 0.215343, 0.606696],
            [0.026246, 0.207675, 0.603381],
            [0.018222, 0.199913, 0.600048],
            [0.009824, 0.192129, 0.596704],
        ]
        return Crameri.cmap_from_list(colors, self.name, _r=self._r)

    def lajolla(self) -> mpl.colors.Colormap:
        colors = [
            [0.098791, 0.099669, 8.8e-05],
            [0.102398, 0.100814, 0.002016],
            [0.105856, 0.102014, 0.003932],
            [0.10917, 0.103273, 0.00584],
            [0.112474, 0.104439, 0.007746],
            [0.115773, 0.105695, 0.009656],
            [0.119086, 0.106937, 0.01176],
            [0.12237, 0.108079, 0.01367],
            [0.125765, 0.109344, 0.015595],
            [0.129083, 0.110536, 0.017532],
            [0.132479, 0.111731, 0.019486],
            [0.135832, 0.112947, 0.021462],
            [0.139249, 0.114096, 0.023462],
            [0.142721, 0.115314, 0.025492],
            [0.146188, 0.116556, 0.027555],
            [0.149714, 0.117765, 0.029655],
            [0.153215, 0.11901, 0.031796],
            [0.15682, 0.120223, 0.033961],
            [0.160419, 0.121466, 0.036412],
            [0.164141, 0.122736, 0.038709],
            [0.167834, 0.124034, 0.041058],
            [0.171613, 0.125365, 0.043253],
            [0.175448, 0.126668, 0.0456],
            [0.179347, 0.128031, 0.047889],
            [0.183292, 0.12937, 0.050218],
            [0.187338, 0.130777, 0.052456],
            [0.191398, 0.132157, 0.054749],
            [0.195552, 0.133574, 0.057052],
            [0.199759, 0.135025, 0.059373],
            [0.204093, 0.136445, 0.061524],
            [0.208438, 0.137979, 0.063852],
            [0.212867, 0.139428, 0.0661],
            [0.217399, 0.141015, 0.068401],
            [0.221979, 0.142548, 0.070615],
            [0.226668, 0.144129, 0.072894],
            [0.231424, 0.14575, 0.07511],
            [0.236255, 0.147356, 0.077324],
            [0.241152, 0.148993, 0.079626],
            [0.246126, 0.150675, 0.082053],
            [0.251203, 0.152365, 0.084452],
            [0.256313, 0.154101, 0.086925],
            [0.261529, 0.155889, 0.089444],
            [0.266808, 0.157647, 0.092067],
            [0.272159, 0.159456, 0.09475],
            [0.27762, 0.161336, 0.097443],
            [0.283142, 0.163196, 0.100219],
            [0.288738, 0.165057, 0.103107],
            [0.294406, 0.16702, 0.106026],
            [0.300173, 0.168975, 0.108981],
            [0.306035, 0.170932, 0.112027],
            [0.31193, 0.172936, 0.115071],
            [0.317951, 0.174991, 0.118267],
            [0.324033, 0.177046, 0.121403],
            [0.33021, 0.179135, 0.124669],
            [0.336449, 0.181231, 0.127997],
            [0.342792, 0.18338, 0.131345],
            [0.349191, 0.185585, 0.134755],
            [0.355681, 0.187779, 0.138191],
            [0.362234, 0.189962, 0.141663],
            [0.368872, 0.192199, 0.145203],
            [0.37557, 0.194487, 0.148714],
            [0.382348, 0.196763, 0.152311],
            [0.389208, 0.199025, 0.155973],
            [0.396126, 0.201339, 0.159588],
            [0.403111, 0.203702, 0.163305],
            [0.410167, 0.206055, 0.167007],
            [0.417279, 0.208396, 0.170707],
            [0.424448, 0.210766, 0.174453],
            [0.431694, 0.21313, 0.178213],
            [0.438972, 0.21553, 0.181919],
            [0.446327, 0.217923, 0.185715],
            [0.453734, 0.220327, 0.189437],
            [0.461197, 0.222709, 0.193178],
            [0.468712, 0.225073, 0.196918],
            [0.476277, 0.227476, 0.200586],
            [0.483887, 0.229823, 0.20431],
            [0.491568, 0.232214, 0.207943],
            [0.499268, 0.234569, 0.21157],
            [0.507032, 0.236904, 0.215121],
            [0.514841, 0.239198, 0.218665],
            [0.522691, 0.241494, 0.222129],
            [0.530585, 0.243739, 0.225557],
            [0.538526, 0.245982, 0.228915],
            [0.546498, 0.24822, 0.2322],
            [0.554505, 0.250369, 0.235417],
            [0.562556, 0.252534, 0.238525],
            [0.570622, 0.254658, 0.241596],
            [0.578732, 0.256723, 0.244541],
            [0.586863, 0.258774, 0.247442],
            [0.595019, 0.26078, 0.250209],
            [0.603195, 0.262762, 0.252927],
            [0.611383, 0.264701, 0.255529],
            [0.619582, 0.266626, 0.258022],
            [0.627779, 0.268526, 0.260449],
            [0.635979, 0.270408, 0.262772],
            [0.644165, 0.272236, 0.264987],
            [0.652346, 0.2741, 0.267119],
            [0.6605, 0.275957, 0.269192],
            [0.668632, 0.277791, 0.27114],
            [0.676724, 0.279653, 0.273014],
            [0.684764, 0.28152, 0.274801],
            [0.692762, 0.283434, 0.276532],
            [0.700683, 0.285371, 0.278167],
            [0.708537, 0.287376, 0.279741],
            [0.716305, 0.289458, 0.281228],
            [0.72397, 0.291602, 0.282691],
            [0.731535, 0.293812, 0.284053],
            [0.738987, 0.296143, 0.28537],
            [0.746299, 0.298576, 0.286641],
            [0.753474, 0.301124, 0.287867],
            [0.760502, 0.30381, 0.289058],
            [0.76736, 0.306647, 0.290172],
            [0.774048, 0.30962, 0.291279],
            [0.780555, 0.312723, 0.292319],
            [0.786871, 0.316022, 0.293327],
            [0.792976, 0.319454, 0.294303],
            [0.798871, 0.323061, 0.295249],
            [0.804548, 0.32681, 0.296165],
            [0.809995, 0.330734, 0.297055],
            [0.815214, 0.334831, 0.297889],
            [0.820195, 0.339049, 0.298716],
            [0.82494, 0.343407, 0.299513],
            [0.829449, 0.3479, 0.300265],
            [0.833714, 0.352506, 0.300996],
            [0.837741, 0.357235, 0.301703],
            [0.841532, 0.36204, 0.302385],
            [0.845096, 0.366931, 0.303044],
            [0.848438, 0.371886, 0.303681],
            [0.851566, 0.37692, 0.304295],
            [0.854494, 0.381975, 0.304888],
            [0.857225, 0.387073, 0.305464],
            [0.859779, 0.392203, 0.306015],
            [0.862161, 0.39734, 0.306537],
            [0.86438, 0.402483, 0.307036],
            [0.866454, 0.407633, 0.307521],
            [0.868402, 0.412782, 0.308001],
            [0.870213, 0.417898, 0.308478],
            [0.871931, 0.423001, 0.308939],
            [0.87354, 0.428101, 0.309379],
            [0.875064, 0.433164, 0.309804],
            [0.876507, 0.438212, 0.310225],
            [0.877887, 0.443229, 0.310636],
            [0.8792, 0.448215, 0.311034],
            [0.880462, 0.453182, 0.311418],
            [0.881681, 0.458116, 0.311798],
            [0.882852, 0.463019, 0.31218],
            [0.883997, 0.46791, 0.312564],
            [0.885105, 0.472767, 0.312945],
            [0.886191, 0.477603, 0.313322],
            [0.887249, 0.482417, 0.313691],
            [0.888294, 0.487206, 0.314051],
            [0.889321, 0.491971, 0.314404],
            [0.890332, 0.496706, 0.314759],
            [0.891333, 0.501443, 0.31512],
            [0.892326, 0.506138, 0.315483],
            [0.893303, 0.510831, 0.31584],
            [0.894281, 0.515501, 0.31619],
            [0.895249, 0.520158, 0.316534],
            [0.89621, 0.524808, 0.316878],
            [0.897169, 0.529444, 0.317222],
            [0.898117, 0.534052, 0.317567],
            [0.899069, 0.538669, 0.317912],
            [0.900015, 0.543262, 0.318255],
            [0.900957, 0.547848, 0.318598],
            [0.901898, 0.552429, 0.31894],
            [0.90284, 0.557003, 0.319282],
            [0.903774, 0.561563, 0.319625],
            [0.904711, 0.56612, 0.31997],
            [0.905648, 0.570671, 0.320313],
            [0.90658, 0.575224, 0.320652],
            [0.907514, 0.579777, 0.320985],
            [0.908445, 0.584316, 0.321317],
            [0.909375, 0.588853, 0.321654],
            [0.91031, 0.593404, 0.321998],
            [0.911239, 0.597943, 0.322345],
            [0.912171, 0.602489, 0.32269],
            [0.913105, 0.607042, 0.323029],
            [0.91404, 0.611586, 0.323367],
            [0.91497, 0.616139, 0.323706],
            [0.915902, 0.620702, 0.324049],
            [0.916845, 0.62526, 0.324396],
            [0.917784, 0.62983, 0.324746],
            [0.918718, 0.634415, 0.325101],
            [0.919662, 0.638998, 0.32546],
            [0.920604, 0.643592, 0.325826],
            [0.921555, 0.648201, 0.3262],
            [0.922507, 0.652822, 0.326584],
            [0.923462, 0.657468, 0.326981],
            [0.924416, 0.662121, 0.327392],
            [0.925379, 0.66678, 0.327822],
            [0.926347, 0.671471, 0.328275],
            [0.927318, 0.676184, 0.328757],
            [0.928297, 0.680911, 0.32927],
            [0.929285, 0.685678, 0.329814],
            [0.930283, 0.69046, 0.330396],
            [0.931285, 0.695281, 0.331033],
            [0.932296, 0.700132, 0.331753],
            [0.933319, 0.705021, 0.332557],
            [0.934357, 0.709951, 0.333431],
            [0.935409, 0.71492, 0.334417],
            [0.936478, 0.719941, 0.335521],
            [0.937557, 0.725011, 0.336755],
            [0.938655, 0.730132, 0.338153],
            [0.939775, 0.735308, 0.339755],
            [0.940913, 0.740544, 0.341539],
            [0.942077, 0.745845, 0.343556],
            [0.943262, 0.751218, 0.345825],
            [0.944473, 0.756645, 0.348394],
            [0.945709, 0.762144, 0.351264],
            [0.946974, 0.767714, 0.354472],
            [0.948266, 0.773354, 0.358043],
            [0.949586, 0.779063, 0.362002],
            [0.950938, 0.784838, 0.366377],
            [0.952312, 0.790667, 0.37117],
            [0.953719, 0.796554, 0.376445],
            [0.955147, 0.802494, 0.382156],
            [0.956597, 0.808479, 0.388366],
            [0.958072, 0.814491, 0.39505],
            [0.959559, 0.82053, 0.402205],
            [0.961064, 0.826587, 0.409861],
            [0.962575, 0.83264, 0.417961],
            [0.964092, 0.838685, 0.426519],
            [0.965612, 0.844713, 0.435518],
            [0.967132, 0.8507, 0.444911],
            [0.968639, 0.856648, 0.454686],
            [0.970133, 0.862544, 0.464801],
            [0.971612, 0.868368, 0.475238],
            [0.97307, 0.87411, 0.485938],
            [0.974498, 0.879773, 0.496891],
            [0.975902, 0.885348, 0.508061],
            [0.977278, 0.890823, 0.519386],
            [0.978614, 0.8962, 0.530851],
            [0.979924, 0.901469, 0.542424],
            [0.981192, 0.906636, 0.554064],
            [0.982426, 0.911693, 0.565746],
            [0.983617, 0.916646, 0.577452],
            [0.984777, 0.921492, 0.589147],
            [0.985893, 0.926235, 0.600822],
            [0.986977, 0.93088, 0.612445],
            [0.988017, 0.935424, 0.624015],
            [0.989027, 0.939877, 0.635493],
            [0.989999, 0.944235, 0.646891],
            [0.990934, 0.948505, 0.658185],
            [0.991836, 0.952694, 0.66937],
            [0.992705, 0.956799, 0.680431],
            [0.993538, 0.960832, 0.691381],
            [0.994334, 0.964785, 0.702202],
            [0.995098, 0.968676, 0.712897],
            [0.995829, 0.972501, 0.723465],
            [0.996528, 0.976256, 0.73391],
            [0.997193, 0.979964, 0.744228],
            [0.997826, 0.983613, 0.754434],
            [0.998426, 0.98722, 0.764524],
            [0.998993, 0.990779, 0.774513],
            [0.999523, 0.994303, 0.784423],
            [1.0, 0.997796, 0.794247],
        ]
        return Crameri.cmap_from_list(colors, self.name, _r=self._r)
