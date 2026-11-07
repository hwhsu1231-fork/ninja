This directory contains the Ninja documentation, written as a Sphinx
project in reStructuredText. Here's a brief overview of how it works.

`index.rst` is the landing page. The manual itself is split by top-level
chapter:

* `intro.rst` -- Introduction
* `using-ninja.rst` -- Using Ninja for your project
* `writing-ninja.rst` -- Writing your own Ninja files
* `more-details.rst` -- More details
* `reference.rst` -- Ninja file reference
* `dependencies.rst` -- Dynamic Dependencies

`manual.rst` is a minimal root document used for the PDF build. It is
marked `:orphan:`, so it does not appear in the HTML navigation, and its
toctree turns the chapters above into top-level chapters in the PDF.

`conf.py` holds the Sphinx configuration (using the Shibuya theme), and
`requirements.txt` lists the Python dependencies (`sphinx` and `shibuya`).
The configuration reads `kNinjaVersion` from `src/version.cc`, so the PDF
title page shows the current release as "Release <version>".

The `manual` target in `configure.py` runs `setup_venv.py`, which creates
a virtual environment under `build/venv` and installs
`requirements.txt` into it, before building the HTML:

```
./configure.py
ninja manual
```

The first run needs network access; later runs reuse the environment.
The output is written to `build/html/index.html`.

To build the HTML without Ninja, install the requirements into the
environment that provides `sphinx-build`:

```
pip install -r doc/requirements.txt
sphinx-build -b html doc doc/_build/html
```

A PDF can be built with `ninja manual.pdf` if a LaTeX toolchain is
installed; it is written to `build/pdf/latex/manual.pdf`. Without Ninja:

```
build/venv/bin/sphinx-build -b latex doc doc/_build/pdf/latex
make -C doc/_build/pdf/latex
```
