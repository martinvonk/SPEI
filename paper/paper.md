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

<!-- \openup 1em -->

# Summary
SPEI is a Python package to calculate drought indices for time series.
Popular Python packages such as Pandas [@pandas_paper_2010], SciPy [@scipy_paper_2020], and Matplotlib [@matplotlib_paper_2007] are used for handling the time series, statistics, and visualization, respectively.
This makes calculating and visualizing drought indices straightforward and flexible.

# Statement of need
Water is a vital natural resource and essential for all life on Earth.
The availability of freshwater is increasingly threatened by the impacts of droughts caused by climate change and human activities.
Drought refers to a water deficit when compared to normal conditions [@sheffield_droughtdefinition_2011].
Both the definition of drought and the baseline for what constitutes "normal" conditions vary depending on the context and objective of a given analysis [@dracup_droughtdefinition_1980].
As a result, many different drought indices have been developed to quantify drought characteristics.
Each index quantitatively describes the severity, location, timing, and duration of a drought and can be used to track and predict the impact of a drought.

# Standardized drought indices
The most common drought indices are standardized indices, which fit a time series to a probability distribution and translate it into a Z-score of the standardized normal distribution.
For meteorological droughts, widely used indices include the Standardized Precipitation Index (SPI) [@mckee_spi_1993; @lloydhughes_spi_2002] and the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]; the latter index is also the name of the SPEI package. For hydrological droughts, standardized indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013] and the Standardized Streamflow Index (SSFI or SSI) [@vicenteserrano_ssfi_2010]. For agricultural droughts, the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004] can be used.
All of these standardized indices are explicitly supported by the SPEI package, though any other standardized drought index can also be computed using the same methodology.

## Computation
Standardized indices are commonly calculated from a time series of at least 30 years [@mckee_spi_1993].
Rolling sums or averages are computed over typical time scales (e.g., 1, 3, 6, 12, 24, or 48 months)[^1], and a continuous probability distribution is fitted to each.
Alternatively, non-parametric methods like normal-scores transforms or kernel density estimates can be used.
The probability of each value is then translated to a Z-score using the inverse normal distribution, yielding a standardized index with a mean of zero and standard deviation of one.

[^1]: A month is not an unambiguous time unit, varying between 28 and 31 days, which adds complexity to computations.
The package handles this internally using Pandas to ensure consistent time aggregation.

### Implementation
The SPEI Python package is built on Pandas [@pandas_paper_2010; @pandas_software_2020], which in turn relies heavily on NumPy [@numpy_article_2020].
It uses `pandas.Series` with a `DatetimeIndex`, enabling powerful time series methods such as `resample` and `rolling`.
Probability density functions are provided via SciPy's `stats` module [@scipy_paper_2020].
Literature offers general guidance for what distribution to use for each standardized index; e.g., a gamma distribution for SPI [@thom_gamma_1996] and a fisk (log-logistic) distribution for SPEI. However, with the SciPy package, users are free to experiment with any of the 200+ univariate continuous distributions available.
Each SciPy continuous distribution has a `fit` method for maximum likelihood estimation to the data.

#### Example
As an example, the Standardized Precipitation Evaporation Index is computed using a dataset with daily precipitation and potential evaporation from the Royal Dutch Meteorological Institute (KNMI), shown in \autoref{fig:meteo_surplus}a.
The SPEI uses the precipitation surplus (precipitation minus potential evaporation), which is aggregated monthly for this example and shown in \autoref{fig:meteo_surplus}b.

![Meteorological time series. (a) Precipitation and potential evaporation. (b) Monthly precipitation surplus \label{fig:meteo_surplus}](figures/monthly_precipitation_surplus.png)

The Python code to compute the package to compute the SPEI-1 (`-1` denoting a one month time scale) with a fisk distribution is as follows:

```python
# load packages
import pandas as pd
import scipy.stats as sps
import spei as si

# load daily time series
meteo: pd.DataFrame = pd.read_csv(
  "meteo.csv",
  index_col="datetime",
  parse_dates=["datetime"],
)
prec: pd.Series = meteo["precipitation"]
evap: pd.Series = meteo["pot_evaporation"]

# compute monthly precipitation surplus
surplus: pd.Series = (prec - evap).resample("MS").sum() # MS: month-start

# compute SPEI-1
spei1: pd.Series = si.spei(
  series=surplus,
  dist=sps.fisk,
  timescale=1, # unit: frequency of the data (months in this case)
)
```

The standardization process is illustrated in \autoref{fig:surplus_fit}.
The empirical cumulative density function of the surplus in March (red dots, matching \autoref{fig:meteo_surplus}b) with the fitted fisk distribution are shown in \autoref{fig:surplus_fit}a.
The fitted probability for eeach red dot is plotted in \autoref{fig:sursurplus_fit}b (blue dots) and translated to a Z-score using a standardized normal distribution (purple line).
The black dashed line traces this procedure for a 31 mm surplus from March 1994, near the 69th percentile, corresponding to a Z-score of around 0.4925.

![Example equiprobability transformation for the precipitation surplus in March. Figure adapted from @edwards_transformation_1997. \label{fig:surplus_fit}](figures/surplus_fit_cdf.png)

Applocation of this procedur for all data points and months results in the standardized index, SPEI-1, as shown in \autoref{fig:spei1}.
The background filling and categories [based on @mckee_spi_1993] in \autoref{fig:spei1} allow for the interpretation of drought (and wet) periods.
The SPEI package has additional options to allow for other time scales, time series frequencies (e.g., daily), and fit window options to ensure valid distribution fit.

![Resulting SPEI-1 from the monthly precipitation surplus \label{fig:spei1}](figures/spei1.png)

## Threshold
Drought characteristics can also be derived from time series using a threshold level.
This defines at what level a drought starts and how large the deficit is.
The threshold can be either fixed or variable.
A variable threshold, as shown in \autoref{fig:threshold} for part of the series of \autoref{fig:meteo_surplus}b, is typically derived from percentiles of the time series or from a fitted probability density function [@vanloon_hydrodrought_2015].

![Visualization of drought based on a variable threshold level \label{fig:threshold}](figures/threshold.png)

## Heatmap
When multiple time scales are used, standardized drought indices can be visualized in a single graph to reveal whether a drought persists over time and to identify the build-up to multi-year droughts [@mourik_use_2025].
For hydrological droughts, this persistence relates to the system’s storage capacity and memory (i.e., response time) [e.g., @bloomfield_sgi_2013], as illustrated by the SPEI heatmap in \autoref{fig:spei_heatmap}, which shows six time scales: 1, 3, 6, 9, 12, and 24 months. For example, this graph shows a persistent drought from 1996-1999 as can be seen from the large red zone.

![Visualization of the SPEI as a heatmap with different time scales \label{fig:spei_heatmap}](figures/spei_heatmap.png)

# Other drought indices in the SPEI package

Other drought indices available in scientific literature, some of which are also implemented in the SPEI package. The following sections quickly highlight the other supported drought indices in the SPEI package.

## Rainfall anomaly index
The Rainfall Anomaly Index (RAI) is a relative drought index that quantifies deviations from historical precipitation to identify dry and wet periods [@vanrooy_rai_1965], without fitting a probability density function.
This package also includes the Modified RAI (mRAI) [@hansel_mrai_2016], which adds a scaling factor for local conditions.

## Climdex
Climdex is an online platform providing indices for heat, cold, precipitation, and drought changes over time [@alexander_climdex_2025], with several of its precipitation indices available in the SPEI Python package.

## Precipitation deficit
The KNMI defines drought during the growing season using the precipitation deficit (potential evaporation minus precipitation).
This package includes five functions [after @witte_knmi_2025] to calculate this absolute drought index, primarily for the Netherlands but adaptable to other regions by adjusting the keyword arguments.

# Acknowledgements
Thanks to all the scientists who used and cited this package so far [@adla_use_2024;@segura_use_2025;@mourik_use_2025;@panigrahi_use_2025] via Zenodo [@vonk_spei_zenodo].
Thanks to Mark Bakker for reading this manuscript and providing feedback.

# References
