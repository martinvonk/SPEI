---
title: 'SPEI: A Python package for calculating and visualizing drought indices'
tags:
  - hydrology
  - drought
  - time series
  - Python
authors:
  - name: Martin A. Vonk
    orcid: 0009-0007-3528-2991
    affiliation: "1, 2"
affiliations:
 - name: Department of Water Management, Faculty of Civil Engineering and Geosciences, Delft University of Technology, Delft, South Holland, The Netherlands
   index: 1
 - name: Artesia B.V., Schoonhoven, South Holland, The Netherlands
   index: 2
date: 24 February 2025
bibliography: paper.bib

---

# Summary
SPEI is a Python package to calculate drought indices for time series. Popular Python packages such as Pandas [@pandas_paper_2010], SciPy [@scipy_paper_2020], and Matplotlib [@matplotlib_paper_2007] are used for handling the time series, statistics, and visualization, respectively. This makes calculating and visualizing different drought indices with the SPEI package simple but versatile.

# Statement of need
Water is a vital natural resource essential for life on Earth. However, the global availability of freshwater is increasingly threatened by the impacts of climate change and human activities. If water availability is below normal conditions, a drought occurs. Droughts are classified as meteorological, hydrological, agricultural, or socioeconomic, often starting with meteorological droughts that trigger cascading effects. Many different indices have been developed to quantify droughts. These indices provide a way to quantitatively describe the severity, location, timing, and duration of a drought and are essential in tracking and predicting the impact of drought.

# Computation
Different drought indices exist to indicate different types of drought. For meteorological droughts, common indices are the Standardized Precipitation Index (SPI) [@mckee_spi_1993,;@lloydhughes_spi_2002], the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]. For hydrological droughts, common indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013], the Standardized Streamflow Index (SSFI or SSI) [@vicenteserrano_ssfi_2010], and the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004]. These standardized drought indices transform a time series into a standardized normal distribution.

Generally, a time series spanning at least 30 years is recommended [@mckee_spi_1993]. That way the series is long enough to have enough data points, but short enough to be stationary in time. Sets of rolling sum or average periods are computed to define various time scales, typically spanning 1, 3, 6, 12, 24, or 48 months[^1]. Each dataset is fitted to a continuous probability density function to establish the relationship between the probability and the time series. There are also non-parametric approaches using a normal-scores transform or kernel density estimate. The probability of any data point is determined and then transformed using the inverse normal distribution, assuming a normally distributed probability density function with a mean of zero and a standard deviation of one.

[^1]: Please note that a month does not represent an unambiguous time delta since a month can have 28 up to 31 days. This can result in some extra complexity in the computation, which is dealt with by the SPEI package internally.

## Implementation
The base of the SPEI Python package is Pandas [@pandas_paper_2010;@pandas_software_2020], which is heavily reliant on NumPy [@numpy_article_2020]. Pandas provides the `pandas.Series` with a `DatetimeIndex` which supports extensive capabilities  for the manipulation of the time series. For instance, via the `resample` and `rolling` methods. Time series with outliers or missing values can also be handled by e.g., interpolation methods available in the Pandas library

The SciPy [@scipy_paper_2020] package provides probability density functions via its `stats` library. General recommendations are provided in literature about which probability density functions might be appropriate for a certain drought index. For example, a gamma distribution is generally used for the SPI and a fisk (log-logistic) distribution for the SPEI. However, with over 200 univariate continuous distributions in the SciPy stats library, the user has the freedom to try and find different relations between the probability and the time series. Each SciPy continuous distribution has a `fit` method, making it easy to fit the distribution to the time series using maximum likelihood estimation.

## Example
In this article, an example dataset is considered with the measured daily precipitation and potential evaporation sum from the Royal Dutch Meteorological Institute (KNMI), as shown in Figure \autoref{fig:meteo_surplus}a. To calculate the SPI, only the precipitation time series is needed, while the SPEI uses the precipitation surplus (precipitation minus potential evaporation), also called rainfall or precipitation excess. The (computed) monthly precipitation surplus, used in this example, is visible in figure \autoref{fig:meteo_surplus}b.

![(a) Precipitation and potential (Makkink) evaporation flux from a weather station in Cabauw (Royal Netherlands Meteorological Institute) from January 1, 1990 until December 31, 2020. (b) Monthly precipitation surplus. \label{fig:meteo_surplus}](figures/monthly_precipitation_surplus.png)

When the time series is in the proper type (`pandas.Series` with a `DatetimeIndex` as index), the Python package provides a function for each separate drought index. For instance, when computing the SPEI-1, using a fisk (log-logistic) distribution, the code would look like the following:

```python
# load packages
import pandas as pd
import scipy.stats as sps
import spei as si

# load daily time series
meteo: pd.DataFrame = pd.read_csv(
  "meteo.csv",
  index_col="datetime",
  parse_dates=["datetime"]
)
prec: pd.Series = meteo["precipitation"]
evap: pd.Series = meteo["pot_evaporation"]

# compute monthly precipitation surplus
surplus: pd.Series = (prec - evap).resample("MS").sum() # MS: month-start

# compute SPEI-1
spei1: pd.Series = si.spei(
  series=surplus,
  dist=sps.fisk,
  timescale=1, # unit -> frequency of the data, in this case months
)
```

Figure \autoref{fig:surplus_fit}a shows the cumulative histogram of precipitation surplus data for March (orange step plot), individual data points (red dots, corresponding to the same points in Figure \autoref{fig:meteo_surplus}b), and the fitted fisk distribution (blue line). The fisk distribution provides a good fit for the data of March, capturing the skewed nature of the observed data. The black dashed line illustrates the cumulative probability of a specific precipitation surplus value of 31 mm from March 1994, corresponding to approximately the 69th percentile.

![a) Surplus in a certain month with the fit of the fisk (log-logistic) cumulative probability density function and b) the transformation of to the standardized normal distribution \label{fig:surplus_fit}](figures/surplus_fit_cdf.png)

Figure \autoref{fig:surplus_fit}b demonstrates the standardization process. The fitted cumulative probabilities from the fisk distribution (blue dots) are transformed to a standard normal distribution (purple line), resulting in standardized values or Z-score. The black dashed line again indicating the same cumulative probability (~69%), which corresponds to a Z-score around 0.49. This transformation enables the expression of precipitation anomalies on a normalized scale suitable for comparison across regions, time scales and other drought indices. Doing this for all months and data points results in the standardized index, SPEI-1, as shown in Figure \autoref{fig:spei1}.

![Resulting SPEI-1 from the monthly precipitation surplus \label{fig:spei1}](figures/spei1.png)

## Visualization

### Series
Figure \autoref{fig:spei1} for instance, is not very informative if the user is not familiar with the standardized index methodology and the meaning of the corresponding z-scores. Therefore, to visualize the drought indices in time and increase the information value, the SPEI package has multiple ways to visualize drought indices. For instance, with background filling to indicate dry (red) or wet (blue) periods \ref{fig:spei3}. Additionally, the drought category, as proposed by [@mckee_spi_1993], can be added for easier interpretation of the z-scores.

![Visualization of the SPEI-3 with background color indication of the drought \label{fig:spei3}](figures/spei3.png)

### Multiyear drought

After [@mourik_use_2025], it is possible to visualize the standardized drought indices over several time scales (1, 3, 6, 9, 12, and 24 months) within one graph. This can help with the interpretation of whether or not a drought persists over a long time span. In the case of hydrological drought, there is a relation to the systems response (and recovery) time. The heatmap, as shown in Figure \autoref{fig:spei_heatmap}, indicates such a graph for the SPEI, over 6 time scale intervals.

![Visualization of the SPEI as a heatmap with different time scales \label{fig:spei_heatmap}](figures/spei_heatmap.png)

## Supported drought indices
At the time of writing the SPEI Python package supports explicitly the SPI, SPEI, SSFI, SSMI and SGI. However, any parametric standardized drought index can be computed with the package as long as an appropriate distribution is available in the SciPy library. A non-parametric approach, using the normal-scores transform to find the probability density function, is also available. The normal-scores transform is used by default for the SGI as proposed by [@bloomfield_sgi_2013].

## Other features

### Flexible time scales and distribution fitting
Meteorological and hydrological time series are nowadays typically available at a daily frequency. To accommodate this, the `timescale` argument in the drought index function is designed to be flexible, with units that match the frequency of the input time series. For example, when using daily data, a `timescale` value of `30` corresponds approximately to a one-month drought index, `90` for three months, `180` for six months, and so on.

The frequency at which distributions are fitted (`fit_freq`) determines how many different distributions are fitted throughout the year. With a daily fit frequency (`fit_freq="D"`), one distribution is fitted per day — 365 or 366 in total, depending on leap years. In contrast, a monthly fit (`fit_freq="MS"` or `"ME"`) fits only 12 distributions. Although daily fitting is more computationally intensive, it can yield more precise results, as shown in later sections.

The number of data points available for each distribution fit depends on both `fit_freq`, the frequency and the time length of the time series. For instance, with 30 years of monthly data and `fit_freq="MS"`, each monthly distribution is based on 30 data points. However, fitting a distribution to just 30 values can be challenging — especially for daily data, which is more prone to noise and outliers.

To improve fit stability, the `fit_window` argument allows users to include additional data points around each time step. The window size is specified in the same unit as the time series frequency. For example for daily data, `fit_window=3` includes data from the day before and after a given date (e.g., March 14th–16th for March 15th). A `fit_window=31` for daily data provides a sample size similar to monthly fitting, while retaining daily resolution. Though experimental, this feature has shown to improve the robustness of daily fits.

By default, the package attempts to infer `fit_freq` based on the time series frequency. If inference fails, it defaults to a monthly fit. Users can also specify `fit_freq` manually for full control.

Figure \autoref{fig:surplus_fit_window} shows an example of the impact of different `fit_freq` and `fit_window` settings on the SPEI-1 index in 2001:

- **Left panel (blue)**: `fit_freq="D"` without `fit_window` for April 15th only. The limited sample size (30 years × 1 day) results in a noisy empirical distribution and unstable fit.
- **Middle panel (orange)**: `fit_freq="D"` with `fit_window=31`, using 31 days × 30 years of data. The fit is smoother and more robust.
- **Right panel (red)**: `fit_freq="MS"` (monthly fit), using all April data each year. The result is stable but transitions sharply at month boundaries.

The bottom panel compares the resulting SPEI-1 time series for 2001:
- The **daily fit** (blue) captures high-resolution variability but is sensitive to noise.
- The **windowed daily fit** (orange) offers a compromise between resolution and stability.
- The **monthly fit** (red) is smooth but introduces discontinuities at month transitions (e.g., April 1st, November 1st).

These settings allow users to tailor the standardization process to their data and desired level of temporal precision.

![Results for the SPEI-1 with different settings for the fit frequency and window \label{fig:surplus_fit_window}](figures/surplus_fit_cdf_window.png)

### Climdex

Climdex is an online platform that offers a range of different indices describe changes in heat, cold, precipitation and drought over time [@climdex]. Several precipitation indices of this platform are available in the SPEI python package.

# Acknowledgements
Thanks to all the scientists who used and cited this package [@adla_use_2024;@segura_use_2025;@mourik_use_2025;@panigrahi_use_2025] via @vonk_spei_zenodo. Thanks to ... for reading this manuscript and providing feedback.

# References
