.. _ref_dyndep:

Dynamic Dependencies
====================

*Available since Ninja 1.10.*

Some use cases require implicit dependency information to be dynamically
discovered from source file content *during the build* in order to build
correctly on the first run (e.g. Fortran module dependencies). This is
unlike :ref:`header dependencies <ref_headers>` which are only needed on
the second run and later to rebuild correctly. A build statement may
have a ``dyndep`` binding naming one of its inputs to specify that
dynamic dependency information must be loaded from the file. For
example:

.. code-block:: text

   build out: ... || foo
     dyndep = foo
   build foo: ...

This specifies that file ``foo`` is a dyndep file. Since it is an input,
the build statement for ``out`` can never be executed before ``foo`` is
built. As soon as ``foo`` is finished Ninja will read it to load
dynamically discovered dependency information for ``out``. This may
include additional implicit inputs and/or outputs. Ninja will update the
build graph accordingly and the build will proceed as if the information
was known originally.

A dyndep file may only affect dependent portions of the build graph,
i.e., the set of build statements that specify the file as a ``dyndep``
binding, or build statements known by the *original* build manifest to
depend directly or indirectly on at least one member of that set. In
particular, dynamically discovered outputs of a build statement may not
correspond to inputs of build statements that were originally
independent of the dyndep file. In other words, a dyndep file may not
change the build graph in a way that causes up-to-date build statements
to become out-of-date.

Dyndep file reference
---------------------

Files specified by ``dyndep`` bindings use the same :ref:`lexical syntax <ref_lexer>` as :ref:`ninja build files <ref_ninja_file>` and
have the following layout.

1. A version number in the form ``<major>[.<minor>][<suffix>]``:

   .. code-block:: text

      ninja_dyndep_version = 1

   Currently the version number must always be ``1`` or ``1.0`` but may
   have an arbitrary suffix.

2. One or more build statements of the form:

   .. code-block:: text

      build out | imp-outs... : dyndep | imp-ins...

   Every statement must specify exactly one explicit output and must use
   the rule name ``dyndep``. The ``| imp-outs...`` and ``| imp-ins...``
   portions are optional.

3. An optional ``restat`` :ref:`variable binding <ref_rule>` on each build
   statement.

The build statements in a dyndep file must have a one-to-one
correspondence to build statements in the :ref:`ninja build file <ref_ninja_file>` that name the dyndep file in a ``dyndep``
binding. No dyndep build statement may be omitted and no extra build
statements may be specified.

Dyndep Examples
---------------

Fortran Modules
~~~~~~~~~~~~~~~

Consider a Fortran source file ``foo.f90`` that provides a module
``foo.mod`` (an implicit output of compilation) and another source file
``bar.f90`` that uses the module (an implicit input of compilation).
This implicit dependency must be discovered before we compile either
source in order to ensure that ``bar.f90`` never compiles before
``foo.f90``, and that ``bar.f90`` recompiles when ``foo.mod`` changes.
We can achieve this as follows:

.. code-block:: text

   rule f95
     command = f95 -o $out -c $in
   rule fscan
     command = fscan -o $out $in

   build foobar.dd: fscan foo.f90 bar.f90

   build foo.o: f95 foo.f90 || foobar.dd
     dyndep = foobar.dd
   build bar.o: f95 bar.f90 || foobar.dd
     dyndep = foobar.dd

In this example the order-only dependencies ensure that ``foobar.dd`` is
generated before either source compiles. The hypothetical ``fscan`` tool
scans the source files, assumes each will be compiled to a ``.o`` of the
same name, and writes ``foobar.dd`` with content such as:

.. code-block:: text

   ninja_dyndep_version = 1
   build foo.o | foo.mod: dyndep
   build bar.o: dyndep |  foo.mod

Ninja will load this file to add ``foo.mod`` as an implicit output of
``foo.o`` and implicit input of ``bar.o``. This ensures that the Fortran
sources are always compiled in the proper order and recompiled when
needed.

Tarball Extraction
~~~~~~~~~~~~~~~~~~

Consider a tarball ``foo.tar`` that we want to extract. The extraction
time can be recorded with a ``foo.tar.stamp`` file so that extraction
repeats if the tarball changes, but we also would like to re-extract if
any of the outputs is missing. However, the list of outputs depends on
the content of the tarball and cannot be spelled out explicitly in the
Ninja build file. We can achieve this as follows:

.. code-block:: text

   rule untar
     command = tar xf $in && touch $out
   rule scantar
     command = scantar --stamp=$stamp --dd=$out $in
   build foo.tar.dd: scantar foo.tar
     stamp = foo.tar.stamp
   build foo.tar.stamp: untar foo.tar || foo.tar.dd
     dyndep = foo.tar.dd

In this example the order-only dependency ensures that ``foo.tar.dd`` is
built before the tarball extracts. The hypothetical ``scantar`` tool
will read the tarball (e.g. via ``tar tf``) and write ``foo.tar.dd``
with content such as:

.. code-block:: text

   ninja_dyndep_version = 1
   build foo.tar.stamp | file1.txt file2.txt : dyndep
     restat = 1

Ninja will load this file to add ``file1.txt`` and ``file2.txt`` as
implicit outputs of ``foo.tar.stamp``, and to mark the build statement
for ``restat``. On future builds, if any implicit output is missing the
tarball will be extracted again. The ``restat`` binding tells Ninja to
tolerate the fact that the implicit outputs may not have modification
times newer than the tarball itself (avoiding re-extraction on every
build).
