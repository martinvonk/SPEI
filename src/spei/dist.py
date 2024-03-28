from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple

from numpy import std
from pandas import Series
from scipy.stats import kstest

from ._typing import ContinuousDist


@dataclass
class Dist:
    data: Series = field(init=True, repr=False)
    dist: ContinuousDist
    loc: float = field(init=False, repr=True)
    scale: float = field(init=False, repr=True)
    pars: Optional[List[float]] = field(init=False, repr=False)
    prob_zero: bool = field(default=False, init=True, repr=False)
    p0: float = field(default=0.0, init=False, repr=False)
    data_window: Optional[Series] = field(default=None, init=True, repr=False)
    """
    Represents a distribution associated with data.

    Parameters
    ----------
    data : Series
        The input data for fitting the distribution.
    dist : ContinuousDist
        The SciPy continuous distribution associated to be fitted.
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.
    data_window : Optional[Series], default=None
        Subset of data for fitting more data (if provided).

    Attributes
    ----------
    loc : float
        Location of the distribution
    scale : float
        Scale of the distribution
    pars : Optional[List[float]]
        Attribute storing additional distribution parameters (if applicable).
    p0 : float
        The probability of zero values in the data. Only calculated if prob_zero=True.

    Methods
    -------
    __post_init__(self) -> None
        Initializes the Dist class and fits the distribution.
    fit_dist(data: Series, dist: ContinuousDist) -> Tuple
        Fits a Scipy continuous distribution to the data.

    Notes
    -----
    The `fit_dist` method uses the `dist.fit` function from Scipy to estimate
    distribution parameters. If the fitted distribution requires additional
    parameters beyond `loc` and `scale`, they are stored in the `pars` attribute.
    """

    def __post_init__(self):
        """
        Post initializes the Dist class by fitting the distribution.
        """
        data_fit = self.data_window if self.data_window is not None else self.data
        pars, loc, scale = self.fit_dist(data=data_fit, dist=self.dist)
        self.loc = loc
        self.scale = scale
        self.pars = pars

        if self.prob_zero:
            self.p0 = (data_fit == 0.0).sum() / len(data_fit)

    @staticmethod
    def fit_dist(
        data: Series, dist: ContinuousDist
    ) -> Tuple[Optional[List[float]], float, float]:
        """
        Fits a Scipy continuous distribution to the data.

        Parameters
        ----------
        data : Series
            The input data for fitting.
        dist : ContinuousDist
            The continuous distribution to be fitted.

        Returns
        -------
        Tuple
            Tuple containing distribution parameters (pars, loc, scale).
        """
        fit_tuple = dist.fit(data, scale=std(data))
        if len(fit_tuple) == 2:
            loc, scale = fit_tuple
            pars = None
        else:
            *pars, loc, scale = fit_tuple
        return pars, loc, scale

    def cdf(self) -> Series:
        """Compute cumulative density function of a Scipy Continuous Distribution"""
        if self.pars is not None:
            cdf = self.dist.cdf(
                self.data.values, *self.pars, loc=self.loc, scale=self.scale
            )
        else:
            cdf = self.dist.cdf(self.data.values, loc=self.loc, scale=self.scale)

        if self.prob_zero:
            cdf = self.p0 + (1 - self.p0) * cdf
            cdf[self.data == 0.0] = self.p0

        return Series(cdf, index=self.data.index, dtype=float)

    def pdf(self) -> Series:
        data_pdf = self.data.sort_values()
        if self.pars is not None:
            pdf = self.dist.pdf(
                data_pdf.values, *self.pars, loc=self.loc, scale=self.scale
            )
        else:
            pdf = self.dist.pdf(data_pdf.values, loc=self.loc, scale=self.scale)

        # TODO: check what to do if prob_zero

        return Series(pdf, index=data_pdf.index, dtype=float)

    def ks_test(
        self,
        method: Literal["auto", "exact", "approx", "asymp"] = "auto",
    ) -> float:
        """Fit a distribution and perform the two-sided
        Kolmogorov-Smirnov test for goodness of fit. The
        null hypothesis is that the data and distributions
        are identical, the alternative is that they are
        not identical. [scipy_2021]_

        Parameters
        ----------
        method : Literal['auto', 'exact', 'approx', 'asymp'], optional
            Defines the distribution used for calculating the p-value. The
            following options are available (default is 'auto'): 'auto' selects
            one of the other options, 'exact' uses the exact distribution of
            test statistic, 'approx' approximates the two-sided probability
            with twice the one-sided probability, 'asymp' uses asymptotic
            distribution of test statistic

        Returns
        -------
        float
            p-value

        References
        -------
        .. [scipy_2021] Onnen, H.: Intro to Probability
        Distributions and Distribution Fitting with Pythons
        SciPy, 2021.
        """
        args = (
            (self.pars, self.loc, self.scale)
            if self.pars is not None
            else (self.loc, self.scale)
        )
        kstest_result = kstest(
            rvs=self.data, cdf=self.dist.name, args=args, method=method
        )
        # rej_h0 = kstest_result.pvalue < alpha
        return kstest_result.pvalue
