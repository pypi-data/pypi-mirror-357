# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../timeseries_compute"))
sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Timeseries Compute"
copyright = "2025, Garth Mortensen"
author = "Garth Mortensen"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # autodoc from docstrings
    "sphinx.ext.napoleon",  # Google-style docstrings
    "sphinx.ext.viewcode",  # source code links
    "sphinx.ext.githubpages",  # GitHub Pages support
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_default_options = {
    "members": True,  # include all class members
    "undoc-members": True,  # include members without docstrings
    "show-inheritance": True,  # show class inheritance
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
