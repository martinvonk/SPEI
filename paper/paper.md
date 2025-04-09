---
title: 'SPEI: A simple Python package for calculating and visualizing drought indices'
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
SPEI is a simple Python package to calculate drought indices for time series. Popular Python packages such as Pandas [@pandas_paper_2010], Scipy [@scipy_paper_2020], Matplotlib [@matplotlib_paper_2007] are used for handling time series, statistics and visualization respectively. This makes calculating and visualizing different drought indices with the SPEI package easy but versitile.

# Statement of need
Water is a vital natural resource essential for life on Earth. However, the global availability of freshwater is increasingly threatened by the impacts of climate change and human activities. If water availability is below normal conditions, a drought occurs. Droughts are classified as meteorological, hydrological, agricultural, or socioeconomic, often starting with meteorological droughts that trigger cascading effects. To quantify droughts, many different indices have been developed. These indices provide a way to quantitatively describe the severity, location, timing, and duration of a drought and are essential in tracking and predicting the impact of drought.

# Computation
Different drought indices exist to indicated different types of drought. For meteorological droughts common indices are the Standardized Precipitation Index (SPI) [@mckee_spi_1993,;@lloydhughes_spi_2002], the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]. For hydrological droughts common indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013], the Standardized Streamflow Index (SSFI/SSI) [@vicenteserrano_ssfi_2010] and the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004].

These standardized drought indics transform a time series into a standardized normal distribution. Generally, a time series spanning at last 30 years is recommended [@mckee_spi_1993]. Sets of rolling average periods are computed to define various time scales, typically spanning 1, 3, 6, 12, 24, or 48 months[^1]. Each dataset is fitted to a continuous probability density function to establish the relationship between the probability and the time series. The probability of any data point is determined and then transformed using the inverse normal distribution, assuming a normally distributed probability density function with a mean of zero and a standard deviation of one.

[^1]: Please note that a month does not represent and unambiguous time delta since a month can have have 28 up to 31 days. This can result in some extra complexity in the computation which is dealt with by the SPEI package internallys.

## Implementation
The base of the SPEI Python package is Pandas [@pandas_paper_2010;@pandas_software_2020], which is heavily reliant on NumPy [@numpy_article_2020]. Pandas provides the pandas `Series` with a `DatetimeIndex` which supports extensive capabilities  for the manipulation of the time series. For instance via the `resample` and `rolling` methods. Time series with outliers or missing values can also be handled by e.g. interpolation methods via Pandas` API.

The SciPy [@scipy_paper_2020] package provides probality density functions via their `stats` library. General recommendations are provided in literature about which probability density function to use for a drought index, e.g. a gamma distribution for the SPI or log-logistic/fisk distribution for the SPEI. However, with over 200 univariate continuous distributions in the scipy stats library, the user has freedom to easily try and find different relations between the probability and the time series. Each of SciPy continuous distribution has a `fit` method making it easy to fit the distribution to the time series using maximum likelihood estimation.

## Example
In this article an example dataset is considered with the measured daily precipitation and potential evaporation sum from the Royal Dutch Meteorological Institute (KNMI). To calculate the SPI, only the precipitation time series is needed, while the SPEI uses precipitation surplus (precipitation minus potential evaporation), also called rainfall or precipitaiton excess. When the time series is in the proper `pandas.Series` format, the Python package provides a function for each seperate drought index. For instance:

![Monthly precipitation surplus.\label{fig:prec_surplus}](figures/monthly_precipitation_surplus.png)

```python
import spei as si
import pandas as pd
import scipy.stats as sps

surplusm: pd.Series = (prec - evap).resample("MS").sum()

spei1 = si.spei(
  series=surplusm,
  dist=sps.fisk, # fisk = log-logistic
  timescale=1, # unit -> frequency of the data, in this case months
)
```

![a) Surplus in a certain month with the fit of the fisk (log-logistic) cumulative probability density function and b) the transformation of to the standardized normal distribution \label{fig:surplus_fit}](figures/surplus_fit_cdf.png)

By default, the pecage uses `fit_freq` do determine on what frequency to fit the data. For instance, if the frequency of the time series is daily, a probability density function is fitted for each day of the year. If no frequency is parsed, the frequency of the time series is inferred.

One can also choose to use the `fit_window` argument, which is zero by default. This allows the window of the used data to be expanded up to a certain size. This means that for instance, to fit the distribution of March 2nd, additionaly the data from March 1st and March 3rd can be used. In this case `fit_window` would be equal to 3. This is especially helpful for smaller timescales, e.g. daily data where a small dataset (less than 30 values) can give an inaccurate fit for the probability density function.

![Resulting SPEI-1 \label{fig:spei1}](figures/spei1.png)

## Visualization

### Series
To visualize the drought indices as a time and increase the information value the SPEI package has multiple ways to visualize drought indices. For instance with background filling to indicate dry (red) or wet (blue) periods \ref{fig:spei3}. Additionaly, the drought category, as proposed by [@mckee_spi_1993], can be added for easier interpretation of the Z-scores

![Visualization of the SPEI-3 with background color indication of the drought \label{fig:spei3}](figures/spei3.png)


### Multiyear drought

After [@mourik_use_2025] it is possible to visualize the drought indices over several time spans within one graph. This can help with the interpretation whether or not a drought persists over a long timespan. And in the case of hydrological drought what the systems response is to the drought.

![Visualization of the SPEI as a heatmap with different timescales \label{fig:spei_heatmap}](figures/spei_heatmap.png)


# Acknowledgements
Thanks to all the scientists who used and cited this package [@adla_use_2024;@segura_use_2025;@mourik_use_2025;@panigrahi_use_2025] via @vonk_spei_zenodo. Thanks to Mark Bakker for reading this manuscript and providing feedback.

# References