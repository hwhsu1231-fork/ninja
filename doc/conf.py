# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import re


def _ninja_version():
    """Read kNinjaVersion from src/version.cc, falling back to 'unknown'."""
    path = os.path.join(os.path.dirname(__file__), os.pardir, 'src',
                        'version.cc')
    try:
        with open(path, encoding='utf-8') as handle:
            match = re.search(r'kNinjaVersion\s*=\s*"([^"]+)"', handle.read())
    except OSError:
        return 'unknown'
    return match.group(1) if match else 'unknown'


project = 'Ninja'
copyright = '2011-, Ninja contributors'
author = 'Ninja contributors'
version = _ninja_version()
release = version

extensions = []

root_doc = 'index'

exclude_patterns = ['_build']

html_theme = 'shibuya'
html_title = 'Ninja'

# Build the PDF from a dedicated root so the website landing page does not
# become a chapter and so the manual chapters stay at the top level.
latex_documents = [
    ('manual', 'manual.tex', 'The Ninja build system',
     'Ninja contributors', 'manual'),
]
