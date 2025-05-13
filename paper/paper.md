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
Water is a vital natural resource, essential for life on Earth. However, the global availability of freshwater is increasingly threatened by the impacts of climate change and human activities. At its core, drought refers to a water deficit when compared to normal conditions [@sheffield_droughtdefinition_2011]. Droughts can be classified as meteorological, hydrological, agricultural, or socioeconomic, often starting with meteorological droughts that trigger cascading [@vanloon_hydrodrought_2015]. However, many definitions of drought exist, and the definition and quantification drought might depends on the purpose and context of the analysis being conducted [@dracup_droughtdefinition_1980]. For this purpose many different indices have been developed to quantify droughts. These indices provide a way to quantitatively describe the severity, location, timing, and duration of a drought and are essential in tracking and predicting the impact of a drought. Using this package, the quantification of drought is made simple, and the choices of the users (definition of drought) are made are fully reproducible through scripting.

# Standardized drought indices
The most common class of drought indices are the standardized drought indices and are advocated by the World Meteorological Organisation [@wmo_spi_2012] in case of the Standardized Precipitation Index.

## Computation
Different drought indices exist to indicate different types of drought. For meteorological droughts, common indices are the Standardized Precipitation Index (SPI) [@mckee_spi_1993,;@lloydhughes_spi_2002] and the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]. For hydrological droughts, common indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013], the Standardized Streamflow Index (SSFI or SSI) [@vicenteserrano_ssfi_2010]. For agricultural drought the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004] can be used. These standardized drought indices transform a time series into a standardized normal distribution.

Generally, it is recommended to use a time series spanning at least 30 years [@mckee_spi_1993]. That way the series is long enough to have enough data points, but generally short enough to be (somewhat) stationary. Sets of rolling sum or average periods are computed to define various time scales, typically spanning 1, 3, 6, 12, 24, or 48 months[^1]. Each dataset is fitted to a continuous probability density function to establish the relationship between the probability and the time series. There are also non-parametric approaches using a normal-scores transform or kernel density estimate. The probability of any data point is determined and then transformed using the inverse normal distribution, assuming a normally distributed probability density function with a mean of zero and a standard deviation of one.

[^1]: A month does not represent an unambiguous time period since a month can have 28 up to 31 days. This can result in some extra complexity in the computation, which is dealt with by the SPEI package internally via Pandas.

### Implementation
The base of the SPEI Python package is Pandas [@pandas_paper_2010;@pandas_software_2020], which is heavily reliant on NumPy [@numpy_article_2020]. Use is made of the the `pandas.Series` with a `DatetimeIndex` which supports extensive capabilities for the manipulation of time series such as the `resample` and `rolling` methods.
<!-- Time series with outliers or missing values can also be handled by e.g., interpolation methods available in the Pandas library -->

The SciPy [@scipy_paper_2020] package provides probability density functions via its `stats` library. General recommendations are provided in the literature about which probability density functions might be appropriate for a certain drought index. For example, a gamma distribution is generally used for the SPI [@thom_gamma_1996] and a fisk (log-logistic) distribution for the SPEI. However, over 200 univariate continuous distributions in the SciPy stats library, the user has the freedom to try any of these. Each SciPy continuous distribution has a `fit` method, making it easy to fit the distribution to the time series using maximum likelihood estimation.

#### Example
As an example, drought indices are computed for an example dataset is considered with measured daily precipitation and daily potential evaporation from the Royal Dutch Meteorological Institute (KNMI), as shown in Figure \autoref{fig:meteo_surplus}a. To calculate the SPI, only the precipitation time series is needed, while the SPEI uses the precipitation surplus (precipitation minus potential evaporation), also called rainfall or precipitation excess. The monthly precipitation surplus is computed and shown in figure \autoref{fig:meteo_surplus}b.

![(a) Precipitation and potential (Makkink) evaporation flux from a weather station in Cabauw (Royal Netherlands Meteorological Institute) from January 1, 1990 until December 31, 2020. (b) Monthly precipitation surplus. \label{fig:meteo_surplus}](figures/monthly_precipitation_surplus.png)

The time series must be a `pandas.Series` with a `DatetimeIndex` as index. The Python package provides a function to compute each separate drought index. For instance, when computing the SPEI-1 (`-1` denoting one month time scale), using a fisk distribution for the example dataset is as follows:

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

The cumulative histogram of precipitation surplus data for March is shown in Figure \autoref{fig:surplus_fit}a (orange cumulative histogram); individual data points (red dots, corresponding to the same points in Figure \autoref{fig:meteo_surplus}b), and the fitted fisk distribution (blue line). The fisk distribution provides a good fit for the data of March, capturing the skewed nature of the observed data. The black dashed line illustrates the cumulative probability of a specific precipitation surplus value of 31 mm from March 1994, corresponding to approximately the 69th percentile.

![(a) Surplus in a certain month with the fit of the fisk (log-logistic) cumulative probability density function and (b) the transformation of to the standardized normal distribution \label{fig:surplus_fit}. Figure adapted from @edwards_transformation_1997.](figures/surplus_fit_cdf.png)

The standardization process is demonstrated in Figure \autoref{fig:surplus_fit}b. The fitted cumulative probabilities from the fisk distribution (blue dots) are transformed to a standard normal distribution (purple line), resulting in standardized values or Z-score. The black dashed line again indicating the same cumulative probability (~68.9%), which corresponds to a Z-score around 0.4925. Doing this for all data point and months results in the standardized index, SPEI-1, as shown in Figure \autoref{fig:spei1}.

![Resulting SPEI-1 from the monthly precipitation surplus \label{fig:spei1}](figures/spei1.png)

Drought intensity is arbitrarily defined for the Z-scores of the standardized drought index with the following categories [@mckee_spi_1993;@lloydhughes_spi_2002]:

| Z-score               | Category            | Probability (%) |
|-----------------------|---------------------|-----------------|
| ≥ 2.00                | Extremely wet       | 2.3             |
| 1.50 ≤ Z < 2.00       | Severely wet        | 4.4             |
| 1.00 ≤ Z < 1.50       | Moderately wet      | 9.2             |
| 0.00 ≤ Z < 1.00       | Mildly wet          | 34.1            |
| -1.00 < Z < 0.00      | Mild drought        | 34.1            |
| -1.50 < Z ≤ -1.00     | Moderate drought    | 9.2             |
| -2.00 < Z ≤ -1.50     | Severe drought      | 4.4             |
| ≤ -2.00               | Extreme drought     | 2.3             |

From this it can be concluded that for instance 1995 and 2018 were both extremely dry years.

#### Flexible time scales and distribution fitting
Meteorological and hydrological time series are nowadays typically available at a daily frequency. To accommodate this, the `timescale` argument in the drought index function is designed to be flexible, with units that match the frequency of the input time series. For example, when using daily data, a `timescale` value of `30` corresponds approximately to a one-month drought index, `90` for three months, `180` for six months, and so on.

The frequency at which distributions are fitted (`fit_freq`) determines how many different distributions are fitted. With a daily fit frequency (`fit_freq="D"`), one distribution is fitted for every day of the year — 365 or 366 in total, depending on leap years. In contrast, a monthly fit (`fit_freq="MS"` or `"ME"`) fits a distribution for every month of the year; 12 in total. Although daily fitting is more computationally intensive, it can yield more precise results, as shown in later sections. Therefore, the number of data points available for each distribution fit depends on both `fit_freq`, the frequency, and the time length of the time series. For instance, with 30 years of monthly data and `fit_freq="MS"`, each monthly distribution is based on 30 data points. However, fitting a distribution to just 30 values can be challenging — especially for daily data, which is more prone to noise and outliers. By default, the package attempts to infer `fit_freq` based on the time series frequency. If inference fails, it defaults to a monthly fit. Users can also specify `fit_freq` manually for full control.

To improve fit stability, the `fit_window` argument allows users to include additional data points around each time step. The window size is specified in the same units as the fit frequency. For example for daily data and fit frequency, `fit_window=3` includes data from the day before and after a given date (e.g., March 14th–16th for March 15th) for the fitting of the distribution. A `fit_window=31` for daily data provides a sample size similar to monthly fitting, while retaining daily resolution. Though experimental, this fit window feature has shown to improve the robustness of daily fits.

Figure \autoref{fig:surplus_fit_window} illustrates the influence of different distribution fitting strategies — namely, `fit_freq` and `fit_window` on the calculation of the SPEI-1 index over the year 2001. The top row displays the cumulative distribution functions of precipitation surplus data for an excerpt of the time series of April (the 15th). Figure \autoref{fig:surplus_fit_window}a shows the case where distributions are fitted daily (`fit_freq="D"`) without using a fitting window. Here, the fit is based solely on data from April 15th across 30 years, resulting in a limited sample size and consequently a noisier empirical distribution with a less stable fit. Figure \autoref{fig:surplus_fit_window}b also uses a daily fitting frequency but applies a 31-day fitting window (`fit_window=31`) centered on April 15th. This expands the sample to include 31 days of data, significantly increasing the total number of observations and yielding a much smoother and more robust distribution fit. In contrast, Figure \autoref{fig:surplus_fit_window}c shows a monthly fitting approach (`fit_freq="MS"`) with no fit window, where all April data from each year is used. This produces a stable fit, but because each month is treated separately, sharp transitions can occur at month boundaries, which may introduce artificial discontinuities into the resulting index. This is shown in the red line of Figure \autoref{fig:surplus_fit_window}e, which is smoother overall but exhibits abrupt changes at the start of each month (e.g., April 1st and November 1st), due to transitions between monthly distributions. These settings allow users to tailor the standardization process to their data and desired level of temporal precision. Figure \autoref{fig:surplus_fit_window}d shows the specific fisk distributions from each parameter set, shown in the text boxes of Figure \autoref{fig:surplus_fit_window}a,b and c. The changes to the fitted parameter values are obvious, but the fitted distrubtions look similar as seen in Figure\autoref{fig:surplus_fit_window}d. The result for the z-score is minimal on april 15th but larger for different dates as seen in Figure \autoref{fig:surplus_fit_window}e.

![Example of the results for the SPEI-1 from a daily surplus time series due to different settings in the fit frequency and window. (a) Use of `fit_freq="D"` and `fit_window=0`, (b) use of `fit_freq="D"` and `fit_window=31`, (c) use of `fit_freq="MS"` and `fit_window=0`. (d) The fitted fisk distrubtions for the three settings. (e) The resulting SPEI-1 indices for the three settings shown for example year 2001. \label{fig:surplus_fit_window}](figures/surplus_fit_cdf_window.png)

## Visualization

### Series
Figure \autoref{fig:spei1} is not very informative if the user is not familiar with the standardized index methodology and the meaning of the corresponding z-scores. Therefore, to visualize the drought indices in time and increase the information value, the SPEI package has multiple ways to visualize drought indices. For instance, with background filling to indicate dry (red) or wet (blue) periods as seen in Figure \ref{fig:spei3}. Additionally, the drought category, as proposed by @mckee_spi_1993, can be added for easier interpretation of the z-scores.

![Visualization of the SPEI-3 with background color and categorical indication and of the drought \label{fig:spei3}](figures/spei3.png)

### Heatmap
If multiple time scales are used, the standardized drought indices can be visualized within one graph. This can help with the interpretation of whether or not a drought persists over a long time span, and identify the build-up to multi-year droughts [@mourik_use_2025]. In the case of hydrological drought, there is a relation to the system response (and recovery) time. The heatmap, as shown in Figure \autoref{fig:spei_heatmap}, indicates such a graph for the SPEI with 6 time scale intervals; 1, 3, 6, 9, 12, and 24 months.

![Visualization of the SPEI as a heatmap with different time scales \label{fig:spei_heatmap}](figures/spei_heatmap.png)

## Supported standardized indices
At the time of writing the SPEI Python package explicitly supports the SPI, SPEI, SSFI, SSMI and SGI. However, any parametric standardized drought index can be computed on any time series if an appropriate distribution is available in the SciPy library. A non-parametric approach, using the normal-scores transform to find the probability density function, is also available. The normal-scores transform is used by default for the SGI as proposed by @bloomfield_sgi_2013.

# Other drought indices
## Threshold
@vanloon_hydrodrought_2015

![Visualization of drought based on a threshold \label{fig:threshold}](figures/threshold.png)

## Climdex
Climdex is an online platform that offers a range of different indices to describe changes in heat, cold, precipitation, and drought over time [@climdex]. Several precipitation indices of the climdex platform are available in the SPEI python package.

| Function Name | Description                                                                                      |
|---------------|--------------------------------------------------------------------------------------------------|
| `rxnday`      | Maximum consecutive precipitation amount over an interval                                        |
| `rx1day`      | Maximum 1-day precipitation amount                                                               |
| `rx5day`      | Maximum consecutive precipitation amount over a 5-day interval                                   |
| `sdii`        | Simple precipitation intensity index                                                             |
| `rnmm`        | Annual count of days when precipitation $\geq$ n mm                                              |
| `r10mm`       | Annual count of days when precipitation $\geq$ 10 mm                                             |
| `r20mm`       | Annual count of days when precipitation $\geq$ 20 mm                                             |
| `cdd`         | Maximum length of dry spell: maximum number of consecutive days with precipitation $<$ 1 mm      |
| `cwd`         | Maximum length of wet spell: maximum number of consecutive days with precipitation $\geq$ 1 mm   |
| `prcptot`     | Total precipitation on wet days over a certain period                                            |
| `rnnp`        | Total amount of precipitation on wet days above a certain quantile                               |
| `r95p`        | Total amount of precipitation on very wet days                                                   |
| `r99p`        | Total amount of precipitation on extremely wet days                                              |
| `r95ptot`     | Contribution to total precipitation from very wet days                                           |
| `r99ptot`     | Contribution to total precipitation from extremely wet days                                      |

## KNMI
KNMI precipitation deficit.

## Rainfall anomaly index
The Rainfall Anomaly Index (RAI) offers a comparable index to the SPI by analyzing the precipitation time series but without needing to fit a probability density function. The RAI effectively quantifies deviations from historical rainfall norms to identify both dry and wet periods [@vanrooy_rai_1965]. This package also includes the Modified Rainfall Anomaly Index (mRAI) [@hansel_mrai_2016], which enhances the RAI by incorporating a scaling factor to account for specific local conditions.

# Reproducibility
On the SPEI GitHub repository [@vonk_spei_github] there is a Jupyter Notebook available to reproduce the figures form this article.

# Acknowledgements
Thanks to all the scientists who used and cited this package so far [@adla_use_2024;@segura_use_2025;@mourik_use_2025;@panigrahi_use_2025] via Zenodo [@vonk_spei_zenodo]. Thanks to Mark Bakker for reading this manuscript and providing feedback.

# References
