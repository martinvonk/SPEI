![PyPI](https://img.shields.io/pypi/v/SPEI)

# SPEI
SPEI is a simple Python package to calculate drought indices for time series such as the SPI (Standardized Precipitation Index), SPEI (Standardized Precipitation Evaporation Index) and SGI (Standardized Groundwater Index). There are other great packages available to calculate these indices. However, they are either written in R such as [SPEI](https://github.com/sbegueria/SPEI) or don't have the Standardized Groundwater Index such as [climate_indices](https://github.com/monocongo/climate_indices). Additionaly, these packages provide ways to analyse spatial data and calculate potential evaporation. This makes these packages complex, because it is easier to only deal with one time series.

This package uses the popular Python packages such as Pandas and Scipy to make it easy and versitile for the user to calculate the drought indices. Pandas Series are great for dealing with time series; providing interpolation, rolling average and other manipulation options. SciPy gives the option to use all [distributions](https://docs.scipy.org/doc/scipy/reference/stats.html) available in the library to fit the data.

For the calculation of potential evaporation, ta a look at [pyet](https://github.com/phydrus/pyet). This is another great package that uses pandas Series to calculate different kinds of potential evaporation time series.

Please feel free to contribute or ask questions!

## Available Drought Indices
| Drought Index                                | Abbreviation | Literature |
|----------------------------------------------|--------------|------------|
| Standardized Precipitation Index             | SPI          | 1          |
| Standardized Precipitation Evaporation Index | SPEI         | 2          |
| Standardized Groundwater Index               | SGI          | 3,4        |
| Standardized Streamflow Index                | SSFI         | 5          |

The package is not limited to only these four drought indices. If any of the distributions in the Scipy library is valid, the drought index can be calculated.

## Installation
To get the latest stable version install using:

`pip install spei`

To get the development version download the GitHub code to your computer. Use cd to get to the download directory and install using:

`pip install -e .`

## Literature
  1.  B. Lloyd-Hughes and M.A. Saunders (2002) - A Drought Climatology for Europe. DOI: 10.1002/joc.846
  2.  S.M. Vicente-Serrano, S. Beguer??a and J.I. L??pez-Moreno (2010) - A Multi-scalar drought index sensitive to global warming: The Standardized Precipitation Evapotranspiration Index. DOI: 10.1175/2009JCLI2909.1
  3.  J.P.Bloomfield and B.P. Marchant, B. P. (2013) - Analysis of groundwater drought building on the standardised precipitation index approach. DOI: 10.5194/hess-17-4769-2013
  4.  A. Babre, A. Kalv??ns, Z. Avotniece, I. Reti??e, J. Bik??e, K.P.M. Jemeljanova, A. Zelenkevi??s and A. D??li??a (2022) - The use of predefined drought indices for the assessment of groundwater drought episodes in the Baltic States over the period 1989???2018. DOI: 10.1016/j.ejrh.2022.101049
  5.  E. Tijdeman, K. Stahl and L.M. Tallaksen (2020) - Drought characteristics derived based on the Standardized Streamflow Index: A large sample comparison for parametric and nonparametric methods. DOI: 10.1029/2019WR026315

Note that the method for calculating the drought indices does not come from these articles and SciPy is used for deriving the distribution. However the literature is helpful as a reference to understand the context and application of drought indices.