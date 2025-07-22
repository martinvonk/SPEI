# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from spei import __version__

project = "SPEI"
copyright = "2025, Martin Vonk"
author = "Martin Vonk"
release = __version__

# make docs
# sphinx-build -M html docs/source docs/build

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",  # For Markdown support
    "nbsphinx",  # For Jupyter Notebooks support
    "sphinx.ext.autodoc",  # For automatic documentation generation from docstrings
    "sphinx.ext.apidoc", # For automatic API documentation generation
    "sphinx.ext.napoleon",  # For Google and NumPy style docstrings
]

exclude_patterns = [
    "_build",  # Exclude the build directory
    "**.ipynb_checkpoints",  # ignores  WARNING: Pygments lexer name 'ipython3' is not known
]

apidoc_modules = [
    {
        "path": "../src/spei",
        "destination": "_api",
        "separate_modules" : True,
        "max_depth": 2,
    }
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
