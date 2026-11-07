# Ninja

Ninja is a small build system with a focus on speed.
https://ninja-build.org/

See [the manual](https://ninja-build.org/manual.html) or the Sphinx
documentation sources under `doc/` included in the distribution for
background and more details.

Binaries for Linux, Mac and Windows are available on
  [GitHub](https://github.com/ninja-build/ninja/releases).
Run `./ninja -h` for Ninja help.

Installation is not necessary because the only required file is the
resulting ninja binary. However, to enable features like Bash
completion and Emacs and Vim editing modes, some files in misc/ must be
copied to appropriate locations.

If you're interested in making changes to Ninja, read
[CONTRIBUTING.md](CONTRIBUTING.md) first.

## Building Ninja itself

You can either build Ninja via the custom generator script written in Python or
via CMake. For more details see
[the wiki](https://github.com/ninja-build/ninja/wiki).

### Python

```
./configure.py --bootstrap
```

This will generate the `ninja` binary and a `build.ninja` file you can now use
to build Ninja with itself.

If you have a GoogleTest source directory, you can build the tests
by passing its path with `--gtest-source-dir=PATH` option, or the
`GTEST_SOURCE_DIR` environment variable, e.g.:

```sh
./configure.py --bootstrap --gtest-source-dir=/path/to/googletest
./ninja all     # build ninja_test and other auxiliary binaries
./ninja_test    # run the unit-test suite.
```

Use the CMake build below if you want to use a preinstalled binary
version of the library.

### CMake

To build the ninja binary without building the unit tests, disable test building
by setting `BUILD_TESTING` to `OFF`:

```
cmake -Bbuild-cmake -DBUILD_TESTING=OFF
cmake --build build-cmake
```

The `ninja` binary will now be inside the `build-cmake` directory (you can
choose any other name you like).

To run the unit tests, omit the `-DBUILD_TESTING=OFF` option, and after
building, run:

```
build-cmake/ninja_test
```

## Generating documentation

The documentation is a [Sphinx](https://www.sphinx-doc.org/) project
written in reStructuredText and lives under `doc/`.

### Ninja documentation (HTML)

If you have configured Ninja itself, the `manual` target creates a
virtual environment under `build/venv`, installs the packages from
`doc/requirements.txt` (including the Shibuya theme), and builds the
HTML:

```sh
./configure.py
ninja manual
```

The first run needs network access to install the packages; later runs
reuse the environment. The entry point is `build/html/index.html`.

To build the documentation without Ninja's wrapper, install the
requirements into the environment that provides `sphinx-build`:

```sh
pip install -r doc/requirements.txt
sphinx-build -b html doc doc/_build/html
```

`uv` can also supply the packages on demand:

```sh
uv run --with-requirements doc/requirements.txt \
    sphinx-build -b html doc doc/_build/html
```

### Ninja manual (PDF)

The PDF manual requires a LaTeX toolchain (for example TeX Live) and is
built with:

```sh
./configure.py
ninja manual.pdf
```

This reuses the `build/venv` environment and writes the PDF to
`build/pdf/latex/manual.pdf`.

Without Ninja, generate the LaTeX sources and run `make`:

```sh
sphinx-build -b latex doc doc/_build/pdf/latex
make -C doc/_build/pdf/latex
```

### Doxygen documentation

If you have `doxygen` installed, you can build documentation extracted from C++
declarations and comments to help you navigate the code. Note that Ninja is a
standalone executable, not a library, so there is no public API, all details
exposed here are internal.

```sh
./configure.py   # if needed
ninja doxygen
```

Then open `doc/doxygen/html/index.html` in a browser to look at it.
