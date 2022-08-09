![PyPI](https://img.shields.io/pypi/v/SPEI)

# SPEI
A simple Python package to calculate drought indices for time series such as the SPI (Standardized Precipitation Index), SPEI (Standardized Precipitation Evaporation Index) and SGI (Standardized Groundwater Index). There are other great packages available to calculate these indices However, they are either written in R such as [SPEI](https://github.com/sbegueria/SPEI) or don't have the Standardized Groundwater Index such as [climate_indices](https://github.com/monocongo/climate_indices). Additionaly, these packages provide ways to analyse spatial data but it is easier to only deal with time series. Therefore, this package uses the popular Python packages such as Pandas and Scipy to make it easy but versitile for the user to calculate the drought indices. With the use of Scipy all [distributions](https://docs.scipy.org/doc/scipy/reference/stats.html) available in the library can be used to fit the data. However, there are general recommendations for distributions when calculating the SPEI, SPI an SGI.

Note that this package does not calculate potential evaporation, we refer to [pyet](https://github.com/phydrus/pyet) for that. All time series have to be calculated in advance and be provided as a pandas Series.

## Installation
To get the latest stable version install using:

`pip install spei`

To get the development version download the GitHub code to your computer. Use cd to get to the download directory and install using:

`pip install -e .`

## To Do

- [ ] Check SGI for other distributions

- [ ] Check distribution correction for x = 0

- [ ] Add way to identify best distribution on time series (with Scipy, Fitter or distfit)

- [x] Setup package in nice way

- [x] Add examples

- [x] Add docstring

- [x] Add Visualisation with Matplotlib