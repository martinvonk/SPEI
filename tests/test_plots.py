import matplotlib as mpl
from pandas import Series

from spei.plot import heatmap, monthly_density, threshold
from spei.plot import si as plot_si

mpl.use("Agg")  # prevent _tkinter.TclError: Can't find a usable tk.tcl error


def test_plot_si(si: Series) -> None:
    _ = plot_si(si)


def test_plot_si_no_background(si: Series) -> None:
    _ = plot_si(si, cmap="roma_r", background=False)


def test_plot_monthly_density(si: Series) -> None:
    _ = monthly_density(si, years=[2011], months=[1, 2, 3, 4, 5])


def test_plot_heatmap(si: Series) -> None:
    _ = heatmap([si], cmap="vik", vmin=-3.0, vmax=3.0)


def test_plot_threshold(head: Series) -> None:
    th = Series(head.mean(), index=head.index, dtype=float)
    _ = threshold(series=head, threshold=th, fill_color="orange")
