More details
============

The ``phony`` rule
------------------

The special rule name ``phony`` can be used to create aliases for other
targets. For example:

.. code-block:: text

   build foo: phony some/file/in/a/faraway/subdir/foo

This makes ``ninja foo`` build the longer path. Semantically, the
``phony`` rule is equivalent to a plain rule where the ``command`` does
nothing, but phony rules are handled specially in that they aren’t
printed when run, logged (see below), nor do they contribute to the
command count printed as part of the build process.

When a ``phony`` target is used as an input to another build rule, the
other build rule will, semantically, consider the inputs of the
``phony`` rule as its own. Therefore, ``phony`` rules can be used to
group inputs, e.g. header files.

``phony`` can also be used to create dummy targets for files which may
not exist at build time. If a phony build statement is written without
any dependencies, the target will be considered out of date if it does
not exist. Without a phony build statement, Ninja will report an error
if the file does not exist and is required by the build.

To create a rule that never rebuilds, use a build rule without any
input:

.. code-block:: text

   rule touch
     command = touch $out
   build file_that_always_exists.dummy: touch
   build dummy_target_to_follow_a_pattern: phony file_that_always_exists.dummy

Default target statements
-------------------------

By default, if no targets are specified on the command line, Ninja will
build every output that is not named as an input elsewhere. You can
override this behavior using a default target statement. A default
target statement causes Ninja to build only a given subset of output
files if none are specified on the command line.

Default target statements begin with the ``default`` keyword, and have
the format ``default targets``. A default target statement must appear
after the build statement that declares the target as an output file.
They are cumulative, so multiple statements may be used to extend the
list of default targets. For example:

.. code-block:: text

   default foo bar
   default baz

This causes Ninja to build the ``foo``, ``bar`` and ``baz`` targets by
default.

.. _ref_log:

The Ninja log
-------------

For each built file, Ninja keeps a log of the command used to build it.
Using this log Ninja can know when an existing output was built with a
different command line than the build files specify (i.e., the command
line changed) and knows to rebuild the file.

The log file is kept in the build root in a file called ``.ninja_log``.
If you provide a variable named ``builddir`` in the outermost scope,
``.ninja_log`` will be kept in that directory instead.

.. _ref_versioning:

Version compatibility
---------------------

*Available since Ninja 1.2.*

Ninja version labels follow the standard major.minor.patch format, where
the major version is increased on backwards-incompatible
syntax/behavioral changes and the minor version is increased on new
behaviors. Your ``build.ninja`` may declare a variable named
``ninja_required_version`` that asserts the minimum Ninja version
required to use the generated file. For example,

.. code-block:: text

   ninja_required_version = 1.1

declares that the build file relies on some feature that was introduced
in Ninja 1.1 (perhaps the ``pool`` syntax), and that Ninja 1.1 or
greater must be used to build. Unlike other Ninja variables, this
version requirement is checked immediately when the variable is
encountered in parsing, so it’s best to put it at the top of the build
file.

Ninja always warns if the major versions of Ninja and the
``ninja_required_version`` don’t match; a major version change hasn’t
come up yet so it’s difficult to predict what behavior might be
required.

.. _ref_headers:

C/C++ header dependencies
-------------------------

To get C/C++ header dependencies (or any other build dependency that
works in a similar way) correct Ninja has some extra functionality.

The problem with headers is that the full list of files that a given
source file depends on can only be discovered by the compiler: different
preprocessor defines and include paths cause different files to be used.
Some compilers can emit this information while building, and Ninja can
use that to get its dependencies perfect.

Consider: if the file has never been compiled, it must be built anyway,
generating the header dependencies as a side effect. If any file is
later modified (even in a way that changes which headers it depends on)
the modification will cause a rebuild as well, keeping the dependencies
up to date.

When loading these special dependencies, Ninja implicitly adds extra
build edges such that it is not an error if the listed dependency is
missing. This allows you to delete a header file and rebuild without the
build aborting due to a missing input.

depfile
~~~~~~~

``gcc`` (and other compilers like ``clang``) support emitting dependency
information in the syntax of a Makefile. (Any command that can write
dependencies in this form can be used, not just ``gcc``.)

To bring this information into Ninja requires cooperation. On the Ninja
side, the ``depfile`` attribute on the ``build`` must point to a path
where this data is written. (Ninja only supports the limited subset of
the Makefile syntax emitted by compilers.) Then the command must know to
write dependencies into the ``depfile`` path. Use it like in the
following example:

.. code-block:: text

   rule cc
     depfile = $out.d
     command = gcc -MD -MF $out.d [other gcc flags here]

The ``-MD`` flag to ``gcc`` tells it to output header dependencies, and
the ``-MF`` flag tells it where to write them.

deps
~~~~

*(Available since Ninja 1.3.)*

It turns out that for large projects (and particularly on Windows, where
the file system is slow) loading these dependency files on startup is
slow.

Ninja 1.3 can instead process dependencies just after they’re generated
and save a compact form of the same information in a Ninja-internal
database.

Ninja supports this processing in three forms.

1. ``deps = gcc`` specifies that the tool outputs ``gcc``-style
   dependencies in the form of Makefiles. Adding this to the above
   example will cause Ninja to process the ``depfile`` immediately after
   the compilation finishes, then delete the ``.d`` file (which is only
   used as a temporary).

2. ``deps = msvc`` specifies that the tool outputs header dependencies
   in the form produced by the Visual Studio compiler’s
   `the /showIncludes flag
   <http://msdn.microsoft.com/en-us/library/hdkef6tk(v=vs.90).aspx>`__.
   Briefly, this means the tool outputs specially-formatted lines to its
   stdout. Ninja then filters these lines from the displayed output. No
   ``depfile`` attribute is necessary, but the localized string in front
   of the header file path should be globally defined. For instance,
   ``msvc_deps_prefix = Note: including file:`` for an English Visual
   Studio (the default).

   .. code-block:: text

      msvc_deps_prefix = Note: including file:
      rule cc
        deps = msvc
        command = cl /showIncludes -c $in /Fo$out

3. ``deps = zero`` specifies that the tool outputs the dependencies as a
   list of NUL-terminated paths, like what ``find . -print0`` would
   produce. Although this format is not used by any known C/C++
   compilers, it is the easiest to produce from a script, so it works in
   ad hoc scenarios.

If the include directory directives are using absolute paths, your
depfile may result in a mixture of relative and absolute paths. Paths
used by other build rules need to match exactly. Therefore, it is
recommended to use relative paths in these cases.

.. _ref_pool:

Pools
-----

*Available since Ninja 1.1.*

Pools allow you to allocate one or more rules or edges a finite number
of concurrent jobs which is more tightly restricted than the default
parallelism.

This can be useful, for example, to restrict a particular expensive rule
(like link steps for huge executables), or to restrict particular build
statements which you know perform poorly when run concurrently.

Each pool has a ``depth`` variable which is specified in the build file.
The pool is then referred to with the ``pool`` variable on either a rule
or a build statement.

No matter what pools you specify, Ninja will never run more concurrent
jobs than the default parallelism, or the number of jobs specified on
the command line (with ``-j``).

.. code-block:: text

   # No more than 4 links at a time.
   pool link_pool
     depth = 4

   # No more than 1 heavy object at a time.
   pool heavy_object_pool
     depth = 1

   rule link
     ...
     pool = link_pool

   rule cc
     ...

   # The link_pool is used here. Only 4 links will run concurrently.
   build foo.exe: link input.obj

   # A build statement can be exempted from its rule's pool by setting an
   # empty pool. This effectively puts the build statement back into the default
   # pool, which has infinite depth.
   build other.exe: link input.obj
     pool =

   # A build statement can specify a pool directly.
   # Only one of these builds will run at a time.
   build heavy_object1.obj: cc heavy_obj1.cc
     pool = heavy_object_pool
   build heavy_object2.obj: cc heavy_obj2.cc
     pool = heavy_object_pool

The ``console`` pool
~~~~~~~~~~~~~~~~~~~~

*Available since Ninja 1.5.*

There exists a pre-defined pool named ``console`` with a depth of 1. It
has the special property that any task in the pool has direct access to
the standard input, output and error streams provided to Ninja, which
are normally connected to the user’s console (hence the name) but could
be redirected. This can be useful for interactive tasks or long-running
tasks which produce status updates on the console (such as test suites).

While a task in the ``console`` pool is running, Ninja’s regular output
(such as progress status and output from concurrent tasks) is buffered
until it completes.
