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

Different drought indices exist to indicated different types of drought. For meteorological droughts common indices are the Standardized Precipitation Index (SPI) [@mckee_spi_1993,@lloydhughes_spi_2002], the Standardized Precipitation Evaporation Index (SPEI) [@vicenteserrano_spei_2010]. For hydrological droughts common indices are the Standardized Groundwater Index (SGI) [@bloomfield_sgi_2013], the Standardized Streamflow Index (SSFI/SSI) [@vicenteserrano_ssfi_2010] and the Standardized Soil Moisture Index (SSMI) [@sheffield_ssmi_2004].

# Methodology
The most common meteorological drivers of drought are precipitation in the form of rain and (potential) evaporation. In this article an example dataset is considered with the precipitation and potential evaporation from the Royal Dutch Meteorological Institute (KNMI). To calculate the Standardized Precipitation Index, only the precipitation time series has to be considered. To calculate the Standardized Precipitation Index

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements


# References