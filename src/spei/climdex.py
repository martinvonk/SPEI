# https://www.climdex.org/

from pandas import Series

from .utils import validate_index, validate_series


def rxnday(series: Series, interval: str, period: str = "30D") -> Series:
    """Maximum consecutive precipitation amount over an interval"""
    series = validate_series(series)
    _ = validate_index(series.index)

    return series.rolling(interval).sum().rolling(period).max()


def rx1day(series: Series, interval: str = "1D", period: str = "30D") -> Series:
    """Maximum 1-day precipitation amount"""
    return rxnday(series=series, interval=interval, period=period)


def rx5day(series: Series, interval: str = "5D", period: str = "30D") -> Series:
    """Maximum consecutive precipitation amount over an 5-day interval"""
    return rxnday(series=series, interval=interval, period=period)


def sdii(series: Series, threshold: float = 1.0, period: str = "30D") -> Series:
    """Simple precipitation intensity index"""
    series = validate_series(series)
    _ = validate_index(series.index)

    w = series >= threshold

    return series.loc[w].resample(period).sum() / w.sum()


def rnmm(series: Series, threshold: float, period: str = "1YE") -> Series:
    """Annual count of days when precipitation ≥ n mm. n is a user-defined threshold"""
    series = validate_series(series)
    _ = validate_index(series.index)

    w = series >= threshold

    return w.resample(period).sum()


def r10mm(series: Series, threshold: float = 10.0, period: str = "1YE") -> Series:
    """Annual count of days when precipitation ≥ 10 mm"""
    return rnmm(series=series, threshold=threshold, period=period)


def r20mm(series: Series, threshold: float = 20.0, period: str = "1YE") -> Series:
    """Annual count of days when precipitation ≥ 20 mm"""
    return rnmm(series=series, threshold=threshold, period=period)


def cdd(series: Series, threshold: float = 1.0, period: str = "365D") -> Series:
    """Maximum length of dry spell: maximum number of consecutive days with
    precipitation < 1mm"""
    series = validate_series(series)
    _ = validate_index(series.index)

    w = series < threshold

    return w.diff().rolling(period).sum().dropna().astype(int)


def cwd(series: Series, threshold: float = 1.0, period: str = "365D") -> Series:
    """Maximum length of wet spell: maximum number of consecutive days with
    precipitation ≥ 1mm"""
    series = validate_series(series)
    _ = validate_index(series.index)

    w = series >= threshold

    return w.diff().rolling(period).sum().dropna().astype(int)


def prcptot(series: Series, period: str = "1YE") -> Series:
    """Total precipitation on wet days over a certain period"""
    series = validate_series(series)
    _ = validate_index(series.index)

    return series.resample(period).sum()


def rnnp(
    series: Series, quantile: float, threshold: float = 1.0, period: str = "1YE"
) -> Series:
    """Total amount of precipitation on wet days above certain quantile"""
    series = validate_series(series)
    _ = validate_index(series.index)

    series_w = series[series >= threshold]
    wq = series_w > series_w.quantile(quantile)

    return series_w.loc[wq].resample(period).sum()


def r95p(
    series: Series, quantile: float = 0.95, threshold: float = 1.0, period: str = "1YE"
) -> Series:
    """Total amount of precipitation on very wet days"""
    return rnnp(series=series, quantile=quantile, threshold=threshold, period=period)


def r99p(
    series: Series, quantile: float = 0.99, threshold: float = 1.0, period: str = "1YE"
) -> Series:
    """Total amount of precipitation on extremely wet days"""
    return rnnp(series=series, quantile=quantile, threshold=threshold, period=period)


def r95ptot(
    series: Series, quantile: float = 0.95, threshold: float = 1.0, period: str = "1YE"
) -> Series:
    """Contribution to total precipitation from very wet days"""
    r95 = r95p(series=series, quantile=quantile, threshold=threshold, period=period)
    tot = prcptot(series=series, period=period)
    return r95 * 100 / tot


def r99ptot(
    series: Series, quantile: float = 0.99, threshold: float = 1.0, period: str = "1YE"
) -> Series:
    """Contribution to total precipitation from extremely wet days"""
    r99 = r99p(series=series, quantile=quantile, threshold=threshold, period=period)
    tot = prcptot(series=series, period=period)
    return r99 * 100 / tot
