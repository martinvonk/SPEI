# SPEI

[![PyPI](https://img.shields.io/pypi/v/spei?style=flat-square)](https://pypi.org/project/spei/)
[![PyPi Supported Python Versions](https://img.shields.io/pypi/pyversions/spei?style=flat-square)](https://pypi.org/project/spei/)
[![Code Size](https://img.shields.io/github/languages/code-size/martinvonk/spei?style=flat-square)](https://pypi.org/project/spei/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/spei?style=flat-square)](https://pypi.org/project/spei/)
[![License](https://img.shields.io/pypi/l/spei?style=flat-square)](https://pypi.org/project/spei/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.10816741-blue?style=flat-square)](https://doi.org/10.5281/zenodo.10816741)

[![Tests](https://img.shields.io/github/actions/workflow/status/martinvonk/spei/tests.yml?style=flat-square)](https://github.com/martinvonk/SPEI/actions/workflows/tests.yml)
[![CodacyCoverage](https://img.shields.io/codacy/coverage/908b566912314666b84e1add22ea7d66?style=flat-square)](https://app.codacy.com/gh/martinvonk/SPEI/)
[![CodacyGrade](https://img.shields.io/codacy/grade/908b566912314666b84e1add22ea7d66?style=flat-square)](https://app.codacy.com/gh/martinvonk/SPEI/)
[![Typed: MyPy](https://img.shields.io/badge/type_checker-mypy-2A6DB2?style=flat-square)](https://mypy-lang.org/)
[![Formatter and Linter: ruff](https://img.shields.io/badge/linter-ruff-red?style=flat-square)](https://github.com/charliermarsh/ruff)

SPEI is a simple Python package to calculate drought indices for hydrological time series. This package uses popular Python packages such as Pandas and Scipy to make it easy and versatile for the user to calculate the drought indices. Pandas Series are great for dealing with time series; providing interpolation, rolling average, and other manipulation options. SciPy enables us to use all different kinds of [distributions](https://docs.scipy.org/doc/scipy/reference/stats.html#probability-distributions) to fit the data. Different popular drought indices are supported such as the SPI (Standardized Precipitation Index), SPEI (Standardized Precipitation Evaporation Index), and SGI (Standardized Groundwater Index).

If you happen to use this package, please cite: Vonk, M. A. (XXXX). SPEI: A simple Python package to calculate and visualize drought indices (vX.X.X). Zenodo. https://doi.org/10.5281/zenodo.10816740.

## Available Drought Indices

| Drought Index                                 | Abbreviation | Literature |
| --------------------------------------------- | ------------ | ---------- |
| Standardized Precipitation Index              | SPI          | 1          |
| Standardized Precipitation Evaporation Index* | SPEI         | 2          |
| Standardized Groundwater Index                | SGI          | 3,4        |
| Standardized Streamflow Index                 | SSFI         | 5,6        |
| Standardized Soil Moisture Index              | SSMI         | 7          |

The package is not limited to only these five drought indices. If any of the distributions in the Scipy library is valid on the observed hydrological series, the drought index can be calculated.

*For the calculation of potential evaporation, take a look at [pyet](https://github.com/phydrus/pyet). This is another great package that also uses pandas Series to calculate different kinds of potential evaporation time series.

## Installation

To get the latest stable version install using:

`pip install spei`

To get the development version download or clone the GitHub repository to your local device. Install using:

`pip install -e <download_directory>`

## Literature

This list of scientific literature is helpful as a reference to understand the context and application of drought indices.

1. Lloyd-Hughes, B. and M.A. Saunders (2002) - A Drought Climatology for Europe. DOI: 10.1002/joc.846
2. Vicente-Serrano, S.M., S. Beguería and J.I. López-Moreno (2010) - A Multi-scalar drought index sensitive to global warming: The Standardized Precipitation Evapotranspiration Index. DOI: 10.1175/2009JCLI2909.1
3. Bloomfield, J.P. and B.P. Marchant (2013) - Analysis of groundwater drought building on the standardised precipitation index approach. DOI: 10.5194/hess-17-4769-2013
4. Babre, A., A. Kalvāns, Z. Avotniece, I. Retiķe, J. Bikše, K.P.M. Jemeljanova, A. Zelenkevičs and A. Dēliņa (2022) - The use of predefined drought indices for the assessment of groundwater drought episodes in the Baltic States over the period 1989–2018. DOI: 10.1016/j.ejrh.2022.101049
5. Vicente-Serrano, S. M., J. I. López-Moreno, S. Beguería, J. Lorenzo-Lacruz, C. Azorin-Molina, and E. Morán-Tejeda (2012). Accurate Computation of a Streamflow Drought Index. Journal of Hydrologic Engineering. American Society of Civil Engineers. DOI: 10.1061/(asce)he.1943-5584.0000433
6. Tijdeman, E.,  K. Stahl and L.M. Tallaksen (2020) - Drought characteristics derived based on the Standardized Streamflow Index: A large sample comparison for parametric and nonparametric methods. DOI: 10.1029/2019WR026315
7. Carrão. H., Russo, S., Sepulcre-Canto, G., Barbosa, P.: An empirical standardized soil moisture index for agricultural drought assessment from remotely sensed data. DOI: 10.1016/j.jag.2015.06.011s

### Publications
These are scientific publications that use and cite this Python package via [Zenodo](https://doi.org/10.5281/zenodo.10816741):

van Mourik, J., Ruijsch, D., van der Wiel, K., Hazeleger, W., & Wanders, N. (2025). Regional drivers and characteristics of multi-year droughts. Weather and Climate Extremes, 48, 100748. https://doi.org/10.1016/j.wace.2025.100748

Segura-Barrero, R., Lauvaux, T., Lian, J., Ciais, P., Badia, A., Ventura, S., Bazzi, H., Abbessi, E., Fu, Z., Xiao, J., Li, X., & Villalba, G. (2025). Heat and Drought Events Alter Biogenic Capacity to Balance CO2 Budget in South-Western Europe. Global biogeochemical cycles, 39(1), e2024GB008163. https://doi.org/10.1029/2024GB008163

Adla, S., Šaponjić, A., Tyagi, A., Nagi, A., Pastore, P., & Pande, S. (2024). Steering agricultural interventions towards sustained irrigation adoption by farmers: socio-psychological analysis of irrigation practices in Maharashtra, India. Hydrological Sciences Journal, 69(12), 1586–1603. https://doi.org/10.1080/02626667.2024.2376709

Panigrahi, S., Vidyarthi, V.K. (2025). Assessing the Suitability of SPI and SPEI in Steppe Hot and Arid Climatic Zones in India. In: Sefelnasr, A., Sherif, M., Singh, V.P. (eds) Water Resources Management and Sustainability. Water Science and Technology Library, vol 114. Springer, Cham. https://doi.org/10.1007/978-3-031-80520-2_12
