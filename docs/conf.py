# Configuration file for the Sphinx documentation builder.

project = 'svdep'
copyright = '2023-2024, Matthew Ballance and Contributors'
author = 'Matthew Ballance'

# The full version, including alpha/beta/rc tags
release = '0.0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']

# Create _static directory if it doesn't exist
import os
os.makedirs(os.path.join(os.path.dirname(__file__), '_static'), exist_ok=True)
