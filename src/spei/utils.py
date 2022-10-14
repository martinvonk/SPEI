from typing import Any
from pandas import Series, DataFrame
from scipy.stats import (
    norm,
    gamma,
    genextreme,
    pearson3,
    fisk,
    lognorm,
    logistic,
    genlogistic,
    kstest,
)


def check_series(series: Series) -> None:
    """Check if provided time series is of type pandas.Series

    Parameters
    ----------
    series : any
        Time series of any kind

    Raises
    ------
    TypeError
        If series is not a pandas.Series

    """
    if not isinstance(series, Series):
        if isinstance(series, DataFrame):
            raise TypeError(
                f"Please convert pandas.DataFrame to a pandas.Series using .squeeze()"
            )
        else:
            raise TypeError(f"Please provide a Pandas Series instead of {type(series)}")


def dist_test(data: Series, dist: Any, N: int = 100, alpha: float = 0.05) -> Any:
    """Fit a distribution and perform the two-sided
    Kolmogorov-Smirnov test for goodness of fit. The
    null hypothesis is that the data and distributions
    are identical, the alternative is that they are
    not identical. [scipy_2021]_

    Parameters
    ----------
    data : array_like
        1-D array of observations of random variables
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the
        scipy.stats library.
    N : int, optional
        Sample size, by default 100
    alpha : float, optional
        Significance level for testing, default is 0.05
        which is equal to a a confidence level of 95%;
        that is, the null hypothesis will be rejected in
        favor of the alternative if the p-value is
        less than 0.05.

    Returns
    -------
    string, float, bool, floats
        distribution name, p-value and fitted parameters

    References
    -------
    .. [scipy_2021] Onnen, H.: Intro to Probability
     Distributions and Distribution Fitting with Pythons
    SciPy, 2021.
    """
    fitted = dist.fit(data, scale=data.std())
    ks = kstest(data, dist.name, fitted, N=N)[1]
    rej_h0 = ks < alpha
    return dist.name, ks, rej_h0, *fitted


def dists_test(
    data: Series, distributions: list[Any] = None, N: int = 100, alpha: float = 0.05
) -> DataFrame:
    """Fit a list of distribution and perform the
    two-sided Kolmogorov-Smirnov test for goodness
    of fit. The null hypothesis is that the data and
    distributions are identical, the alternative is
    that they are not identical. [scipy_2021]_

    Parameters
    ----------
    data : array_like
        1-D array of observations of random variables
    distributions : list of scipy.stats._continuous_distns, optional
        A list of (can be) any continuous distribution from the scipy.stats library, by default None
    N : int, optional
        Sample size, by default 100
    alpha : float, optional
        Significance level for testing, default is 0.05
        which is equal to a a confidence level of 95%;
        that is, the null hypothesis will be rejected in
        favor of the alternative if the p-value is
        less than 0.05.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the distribution names,
        pvalues and parameters

    References
    -------
    .. [scipy_2021] Onnen, H.: Intro to Probability
     Distributions and Distribution Fitting with Pythons
    SciPy, 2021.
    """
    if distributions is None:
        distributions = [
            norm,
            gamma,
            genextreme,
            pearson3,
            fisk,
            lognorm,
            logistic,
            genlogistic,
        ]

    df = DataFrame([dist_test(data, D, N, alpha) for D in distributions])
    cols = ["Distribution", "KS p-value", f"Reject H0"]
    cols += [f"Param {i+1}" for i in range(df.columns.stop - len(cols))]
    df.columns = cols
    df = df.set_index(cols[0])
    df["Dist"] = distributions

    return df
