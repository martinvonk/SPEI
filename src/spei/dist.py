from dataclasses import dataclass, field
from typing import Literal

from numpy import std
from pandas import Series
from scipy.stats import kstest

from ._typing import ContinuousDist


@dataclass
class Dist:
    """Represents a distribution associated with data.

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
    loc : float
        Location of the distribution
    scale : float
        Scale of the distribution
    pars : Optional[List[float]]
        Attribute storing additional distribution parameters (if applicable).
    p0 : float
        The probability of zero values in the data. Only calculated if prob_zero=True.
    fit_method : Literal["MLE", "MM"], default="MLE"
        The method used for fitting the distribution. The default is "MLE"
        (Maximum Likelihood Estimate); "MM" (Method of Moments) is also available.

    Notes
    -----
    The `fit_dist` method uses the `dist.fit` function from Scipy to estimate
    distribution parameters. If the fitted distribution requires additional
    parameters beyond `loc` and `scale`, they are stored in the `pars` attribute.
    """

    data: Series = field(init=True, repr=False)
    dist: ContinuousDist
    loc: float = field(init=False, repr=True)
    scale: float = field(init=False, repr=True)
    pars: list[float] | None = field(init=False, repr=False)
    prob_zero: bool = field(default=False, init=True, repr=False)
    p0: float = field(default=0.0, init=False, repr=False)
    data_window: Series | None = field(default=None, init=True, repr=False)
    fit_method: Literal["MLE", "MM"] = field(default="MLE", init=True, repr=False)

    def __post_init__(self):
        """
        Post initializes the Dist class by fitting the distribution.
        """
        data_fit = self.data_window if self.data_window is not None else self.data
        pars, loc, scale = self.fit_dist(
            data=data_fit, dist=self.dist, fit_method=self.fit_method
        )
        self.loc = loc
        self.scale = scale
        self.pars = pars

        if self.prob_zero:
            self.p0 = (data_fit == 0.0).sum() / len(data_fit)

    @staticmethod
    def fit_dist(
        data: Series, dist: ContinuousDist, fit_method: Literal["MLE", "MM"] = "MLE"
    ) -> tuple[list[float] | None, float, float]:
        """
        Fits a Scipy continuous distribution to the data.

        Parameters
        ----------
        data : Series
            The input data for fitting.
        dist : ContinuousDist
            The continuous distribution to be fitted.
        fit_method : Literal["MLE", "MM"], optional
            The method used for fitting the distribution. The
            default is “MLE” (Maximum Likelihood Estimate);
            “MM” (Method of Moments) is also available.

        Returns
        -------
        Tuple
            Tuple containing distribution parameters (pars, loc, scale).
        """
        fit_tuple = dist.fit(
            data,
            scale=std(data),  # initial guess
            method=fit_method,
        )
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

        if self.prob_zero:
            pdf = (1 - self.p0) * pdf
            pdf[self.data == 0.0] = self.p0

        return Series(pdf, index=data_pdf.index, dtype=float)

    def ppf(self, q: float) -> Series:
        """Compute percent point function (inverse of cdf) at q"""
        if self.pars is not None:
            ppf = self.dist.ppf(q, *self.pars, loc=self.loc, scale=self.scale)
        else:
            ppf = self.dist.ppf(q, loc=self.loc, scale=self.scale)

        return Series(ppf, index=self.data.index, dtype=float)

    def ks_test(
        self,
        method: Literal["auto", "exact", "approx", "asymp"] = "auto",
    ) -> float:
        """Fit a distribution and perform the two-sided
        Kolmogorov-Smirnov test for goodness of fit. The
        null hypothesis is that the data and distributions
        are identical, the alternative is that they are
        not identical.

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
        Onnen, H.: Intro to Probability Distributions and Distribution
        Fitting with Pythons  SciPy, 2021.
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
