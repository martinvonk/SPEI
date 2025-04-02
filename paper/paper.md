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
SPEI is a simple Python package to calculate drought indices for time series. This package uses popular Python packages such as Pandas [@pandas_paper_2010] and Scipy [@scipy_paper_2020] to make it easy and versatile for the user to calculate the drought indices. Matplotlib [@matplotlib_paper_2007] used for the visualization of the drought indices.

# Statement of need
Water is a vital natural resource essential for life on Earth. However, the global availability of freshwater is increasingly threatened by the impacts of climate change and human activities. If water availability is below normal conditions, a drought occurs. Droughts are classified as meteorological, hydrological, agricultural, or socioeconomic, often starting with meteorological droughts that trigger cascading effects. To quantify droughts, many different indices have been developed. These indices provide a way to quantitatively describe the severity, location, timing, and duration of a drought and are essential in tracking and predicting the impact of drought.

Different drought indices exist to indicated different types of drought. For meteorological droughts common indices are the Standardized Precipitation Index (SPI) [@mckee_spi_1993,;@lloydhughes_spi_2002], the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]. For hydrological droughts common indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013], the Standardized Streamflow Index (SSFI/SSI) [@vicenteserrano_ssfi_2010] and the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004].

# Methodology
In this article an example dataset is considered with the precipitation and potential evaporation from the Royal Dutch Meteorological Institute (KNMI). To calculate the SPI, only the precipitation time series while the SPEI uses both the precipitation and potential evaporation in the form of the precipitation excess; precipitation minus potential evaporation.

The base of the Python package is Pandas [@pandas_paper_2010;@pandas_software_2020], which is heavily reliant on NumPy [@numpy_article_2020]. Pandas provides the pandas `Series` with a `DatetimeIndex` which supports extensive capabilities  for the manipulation of the time series. For instance via the `resample` and `rolling` methods. For time with outliers or missing values can also be handled via Pandas` API.

For the drought index, sets of rolling average periods are computed to define various time scales, typically spanning 1, 3, 6, 12, 24, or 48 months[^1]. Each dataset is fitted to a continuous probability distribution to establish the relationship between the probability and the time series. The probability of any data point is determined and then transformed using the inverse normal distribution, assuming a normally distributed probability density function with a mean of zero and a standard deviation of one.

[^1]: Please note that a month does not represent and unambiguous time delta since a month can have have 28 up to 31 days. This can result in some extra complexity in the computation.

The SciPy [@scipy_paper_2020] package provides continious distribution available via their `stats` library. General recommendations are provided in literature for the distributions of different drought indices, e.g. a gamma distribution for the SPI or log-logistic distribution for the SPEI. However, with this setup the Python allows for easy trial of different distribution which might be more suitable for for the relationship between the probability and the time series.

When the time series is in the proper `pandas.Series` format, the Python package provides a function for each seperate drought index. For instance:

```python
import spei as si
import pandas as pd
import scipy.stats as sps

prec: pd.Series = pd.read_csv("prec.csv", index_col="datetime", parse_dates=["datetime"]).squeeze()
spi = si.spi(
  series=prec,
  dist=sps.gamma,
  timescale=3, # the frequency of the data in this case months
  fit_window="MS", # =Month-Start, if not infered from the time series
  prob_zero=True, # allow for separate computation of the probability of zero values in the series because the gamma distribution is not defined in zero
)
```

One can also choose to use the `fit_window` argument. This allows the window of the used data to be expanded up to a certain size. This means that for instance, to fit the distribution of march, additionaly the data from february and april can be used. This is especially helpful for smaller timescales, e.g. daily data where a dataset of less than 30 values can give an inaccurate fit for the data.

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements


# References