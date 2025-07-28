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
`SPEI` is a Python package for calculating drought indices from time series.
Popular Python packages such as `Pandas` [@pandas_paper_2010], `SciPy` [@scipy_paper_2020], and `Matplotlib` [@matplotlib_paper_2007] are used for handling the time series, statistics, and visualization respectively.
This makes the calculation and visualization of drought indices straightforward and flexible.

# Statement of need
Water is a vital natural resource, but freshwater availability is increasingly threatened by droughts linked to climate change and human activities.
Drought refers to a water deficit relative to normal conditions [@sheffield_droughtdefinition_2011].
Both the definition of drought and the baseline for what constitutes "normal" conditions vary depending on the context and objective of a given analysis [@dracup_droughtdefinition_1980].
As a result, many drought indices have been developed to quantify drought characteristics.
Each index quantifies a drought's severity, location, timing, and duration, helping to track and predict its impact.

# Standardized drought indices
The most common drought indices are standardized indices, which fit a time series to a probability distribution and convert it into a Z-score of the standardized normal distribution.
For meteorological droughts, widely used indices include the Standardized Precipitation Index (SPI) [@mckee_spi_1993; @lloydhughes_spi_2002] and the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]; the latter index is also the name of the `SPEI` package.
Hydrological droughts are often measured using the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013] and the Standardized Streamflow Index (SSFI or SSI) [@vicenteserrano_ssfi_2010].
For agricultural droughts, the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004] can be used.
All of these standardized indices are explicitly supported by the `SPEI` package, though other standardized drought index can also be computed using the same methodology.

## Computation
Standardized indices are commonly calculated from a time series of at least 30 years [@mckee_spi_1993].
Rolling sums or averages are computed over typical time scales (generally 1, 3, 6, 12, 24, or 48 months)[^1], and a continuous probability distribution is fitted to each.
Alternatively, non-parametric methods like normal-scores transforms or kernel density estimates can be used.
The probability of each value is then converted to a Z-score using the inverse normal distribution, yielding a standardized index with a mean of zero and standard deviation of one.

[^1]: A month is not an unambiguous time unit, varying between 28 and 31 days, which adds complexity to computations.
The package handles this internally using `Pandas` to ensure consistent time aggregation.

### Implementation
The `SPEI` package is built on `Pandas` [@pandas_paper_2010; @pandas_software_2020], which in turn relies heavily on `NumPy` [@numpy_article_2020].
It uses `pandas.Series` with a `DatetimeIndex`, enabling powerful time series methods such as `resample` and `rolling`.
Probability density functions are provided via the `SciPy` `stats` module [@scipy_paper_2020].
Literature offers general guidance for what distribution to use for each standardized index; e.g., a gamma distribution for SPI [@thom_gamma_1996] and a fisk (log-logistic) distribution for SPEI. However, with the `SciPy` package, users are free to experiment with any of the 200+ univariate continuous distributions available.
Each distribution has a `fit` method for maximum likelihood estimation on the data.

#### Example
As an example, the Standardized Precipitation Evaporation Index is computed using a dataset with daily precipitation and potential evaporation from the Royal Netherlands Meteorological Institute (KNMI), shown in \autoref{fig:meteo_surplus}a.
The SPEI uses the precipitation surplus (precipitation minus potential evaporation), which is aggregated monthly for this example and shown in \autoref{fig:meteo_surplus}b.

![Example meteorological time series \label{fig:meteo_surplus}](figures/monthly_precipitation_surplus.png)

The Python code to compute the SPEI-1 (`-1` indicating a one month time scale) with a fisk distribution is as follows:

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
The fitted probability for each red dot is plotted in \autoref{fig:surplus_fit}b (blue dots) and converted to a Z-score using a standardized normal distribution (purple line).
The black dashed line traces this procedure for a 31 mm surplus from March 1994, near the 69th percentile, corresponding to a Z-score of around 0.4925.

![Example equiprobability transformation for the precipitation surplus in March. Figure adapted from @edwards_transformation_1997. \label{fig:surplus_fit}](figures/surplus_fit_cdf.png)

Application of this procedure for all data points and months results in the standardized index, SPEI-1, as shown in \autoref{fig:spei1}.
The background filling and categories [based on @mckee_spi_1993] in \autoref{fig:spei1} allow for the interpretation of drought (and wet) periods.
The `SPEI` package has additional options to allow for other time scales, time series frequencies (e.g., daily), and fit window options to ensure valid distribution fit.

![Resulting SPEI-1 from the monthly precipitation surplus \label{fig:spei1}](figures/spei1.png)

## Threshold
Drought characteristics can also be derived from time series using a threshold level.
This defines at what level a drought starts and quantifies the deficit.
The threshold can be either fixed or variable.
A variable threshold, as shown in \autoref{fig:threshold} for part of the series of \autoref{fig:meteo_surplus}b, is typically derived from percentiles of the time series or from a fitted probability density function [@vanloon_hydrodrought_2015].

![Visualization of drought based on a variable threshold level \label{fig:threshold}](figures/threshold.png)

## Heatmap
When multiple time scales are used, standardized drought indices can be visualized in a single graph to reveal whether a drought persists over time and to identify the build-up to multi-year droughts [@mourik_use_2025].
For hydrological droughts, this persistence relates to the system’s storage capacity and response time [e.g., @bloomfield_sgi_2013].
The SPEI heatmap (\autoref{fig:spei_heatmap}) illustrates this across six time scales (1, 3, 6, 9, 12, and 24 months), clearly highlighting the 1995–1998 multi-year drought as a large red zone.

![Visualization of the SPEI as a heatmap with different time scales \label{fig:spei_heatmap}](figures/spei_heatmap.png)

# Other drought indices in the SPEI package

Several other drought indices from the literature are also supported by the `SPEI` package, briefly outlined below.

## Rainfall anomaly index
The Rainfall Anomaly Index (RAI) is a relative drought index that quantifies deviations from historical precipitation without fitting a distribution [@vanrooy_rai_1965].
The package also includes the Modified RAI (mRAI), which adds a scaling factor for local conditions. [@hansel_mrai_2016].

## Climdex
Climdex is an online platform providing indices for heat, cold, precipitation, and drought changes over time [@alexander_climdex_2025], with several of its precipitation indices available in the `SPEI` package.

## Precipitation deficit
The KNMI defines drought during the growing season using the precipitation deficit (potential evaporation minus precipitation).
The package includes five functions [after @witte_knmi_2025] to calculate this absolute drought index, primarily for the Netherlands but adaptable to other regions by adjusting the keyword arguments.

# Acknowledgements
Thanks to all the scientists who have used and cited this package so far [@adla_use_2024;@segura_use_2025;@mourik_use_2025;@panigrahi_use_2025] via Zenodo [@vonk_spei_zenodo].
Thanks to Mark Bakker for reading this manuscript and providing feedback.

# References
