# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'agents'
copyright = '2025, DataPA Limited'
author = 'DataPA Limited'
release = '0.0.6'

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_favicon = '_static/favicon.ico'
html_logo = '_static/logo.png'
html_title = "agents API reference (0.0.5)"
html_short_title = "API reference"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#dd3333",
        "color-brand-content": "#ffffff",
    }
}

def setup(app):
    app.add_css_file('custom.css')
