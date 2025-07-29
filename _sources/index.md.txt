# SPEI documentation

SPEI is a Python package designed for calculating drought indices from meteorological and hydrological time series. Built on widely used libraries like Pandas and SciPy, it offers a flexible and simple approach to drought analysis.

This website provides full documentation, example notebooks, and a detailed API reference to help you get started.

The SPEI package is open-source and hosted on [GitHub]((https://github.com/martinvonk/SPEI)), where you can find more information about the available drought indices and ongoing development. The package is published on [PyPi](https://pypi.org/project/spei/) from which it can be installed using `pip install spei`.

If you use this package for drought analysis and/or visualization, please cite it by referencing our article in the [Journal of Open Source Software](https://joss.theoj.org/papers/10.21105/joss.08454):

Vonk, M. A. (2025). SPEI: A Python package for calculating and visualizing drought indices. Journal of Open Source Software, 10(111), 8454. [doi.org/10.21105/joss.08454](https://doi.org/10.21105/joss.08454).

```bibtex
@article{Vonk_SPEI_2025,
    author  = {Vonk, M. A.},
    doi     = {10.21105/joss.08454},
    journal = {Journal of Open Source Software},
    number  = {111},
    pages   = {8454},
    title   = {{SPEI: A Python package for calculating and visualizing drought indices}},
    url     = {https://joss.theoj.org/papers/10.21105/joss.08454},
    volume  = {10},
    year    = {2025}
}
```

```{toctree}
:maxdepth: 2

examples/index.md
_api/modules.rst
```