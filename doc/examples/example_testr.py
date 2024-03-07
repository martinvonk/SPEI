# %%
import numpy as np
import spei as si
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as scs

# %%
fileurl = "https://raw.githubusercontent.com/pastas/pastas/master/doc/examples/data"
prec = (
    pd.read_csv(f"{fileurl}/rain_nb1.csv", index_col=0, parse_dates=True)
    .squeeze()
    .multiply(1e3)
)  # to mm
evap = (
    pd.read_csv(f"{fileurl}/evap_nb1.csv", index_col=0, parse_dates=True)
    .squeeze()
    .multiply(1e3)
)  # to mm

series = (prec - evap).dropna().rolling("90D").sum()
index = series.index
dfval = si.utils.group_yearly_df(series=series)
inf_freq = si.utils.infer_frequency(index)
dist = scs.fisk
# %%
# groubpy Y
sti = pd.Series(index=index, dtype=float)
for _, grval in dfval.groupby(pd.Grouper(freq=inf_freq)):
    data = si.utils.get_data_series(grval)
    pars, loc, scale = si.si.fit_dist(data=data, dist=dist)
    cdf = si.si.compute_cdf(
        data=data.values,
        dist=dist,
        loc=loc,
        scale=scale,
        pars=pars,
    )
    ppf = scs.norm.ppf(cdf)
    sti.loc[data.index] = ppf

# %%
window = 31
window = window + 1 if window % 2 == 0 else window # make sure window is odd
period = int(np.ceil(window / 2)) # period around window
# fill values around data to get cyclic period window
dfval_window_index_start = [
    dfval.index[0] + pd.Timedelta(value=-i, unit=inf_freq)
    for i in reversed(range(1, period))
]
dfval_window_index_end = [
    dfval.index[-1] + pd.Timedelta(value=i, unit=inf_freq) for i in range(1, period)
]
dfval_window_index = pd.DatetimeIndex(
    dfval_window_index_start + dfval.index.to_list() + dfval_window_index_end
)

dfval_window = pd.DataFrame(
    np.nan, index=dfval_window_index, columns=dfval.columns, dtype=float
)
dfval_window.loc[dfval.index, dfval.columns] = dfval.values
dfval_window.iloc[:period-1] = dfval.iloc[-period+1:].values
dfval_window.iloc[-period+1:] = dfval.iloc[:period-1].values

# loop through window
stiw = pd.Series(np.nan, index=index, dtype=float)
for dfval_rwindow in dfval_window.rolling(window=window, min_periods=window, closed="right"):
    if len(dfval_rwindow) < window:
        continue # min_periods ignored by Rolling.__iter__
    data_window = dfval_rwindow.values.ravel()
    data_window = data_window[~np.isnan(data_window)]
    pars, loc, scale = si.si.fit_dist(data=data_window, dist=dist)
    data = si.utils.get_data_series(dfval_rwindow.iloc[[period]])
    cdf = si.si.compute_cdf(
        data=data.values,
        dist=dist,
        loc=loc,
        scale=scale,
        pars=pars,
    )
    ppf = scs.norm.ppf(cdf)
    stiw.loc[data.index] = ppf
# %%
sd = pd.Timestamp("2015")
sti.loc[sd:].plot()
stiw.loc[sd:].plot()
# %%
