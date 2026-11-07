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

`conf.py` holds the Sphinx configuration (using the Furo theme), and
`requirements.txt` lists the Python dependencies (`sphinx` and `furo`).

To build the HTML documentation:

```
pip install -r doc/requirements.txt
sphinx-build -b html doc doc/_build/html
```

or, if you have configured Ninja itself:

```
./configure.py
ninja manual
```

The output is written to `doc/_build/html` (or the configured build
directory when using `ninja manual`). A PDF can be produced with
`sphinx-build -M latexpdf doc doc/_build/pdf` if a LaTeX toolchain is
installed.
