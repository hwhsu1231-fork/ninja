Using Ninja for your project
============================

Ninja currently works on Unix-like systems and Windows. It’s seen the
most testing on Linux (and has the best performance there) but it runs
fine on macOS and FreeBSD.

If your project is small, Ninja’s speed impact is likely unnoticeable.
(However, even for small projects it sometimes turns out that Ninja’s
limited syntax forces simpler build rules that result in faster builds.)
Another way to say this is that if you’re happy with the edit-compile
cycle time of your project already then Ninja won’t help.

There are many other build systems that are more user-friendly or
featureful than Ninja. For some recommendations: the Ninja author found
`the tup build system <http://gittup.org/tup/>`__ influential in Ninja’s
design, and thinks `redo <https://github.com/apenwarr/redo>`__'s design
is quite clever.

Ninja’s benefit comes from using it in conjunction with a smarter
meta-build system.

`GN <https://gn.googlesource.com/gn/>`__
   The meta-build system used to generate build files for Google Chrome
   and related projects (v8, node.js), as well as Google Fuchsia. GN can
   generate Ninja files for all platforms supported by Chrome.

`CMake <https://cmake.org/>`__
   A widely used meta-build system that can generate Ninja files on
   Linux as of CMake version 2.8.8. Newer versions of CMake support
   generating Ninja files on Windows and macOS too.

`others <https://github.com/ninja-build/ninja/wiki/List-of-generators-producing-ninja-build-files>`__
   Ninja ought to fit perfectly into other meta-build software like
   `premake <https://premake.github.io/>`__. If you do this work, please
   let us know!

Running Ninja
-------------

Run ``ninja``. By default, it looks for a file named ``build.ninja`` in
the current directory and builds all out-of-date targets. You can
specify which targets (files) to build as command line arguments.

There is also a special syntax ``target^`` for specifying a target as
the first output of some rule containing the source you put in the
command line, if one exists. For example, if you specify target as
``foo.c^`` then ``foo.o`` will get built (assuming you have those
targets in your build files).

``ninja -h`` prints help output. Many of Ninja’s flags intentionally
match those of Make; e.g ``ninja -C build -j 20`` changes into the
``build`` directory and runs 20 build commands in parallel. (Note that
Ninja defaults to running commands in parallel anyway, so typically you
don’t need to pass ``-j``.)

GNU Jobserver support
---------------------

Since version 1.13., Ninja builds can follow the `GNU Make
jobserver <https://www.gnu.org/software/make/manual/html_node/Job-Slots.html>`__
protocol.

The protocol is useful to efficiently control parallelism across a set
of concurrent and cooperating processes. This is useful when Ninja is
invoked as part of a larger build system controlled by a top-level Ninja
or GNU Make instance, or any other jobserver pool implementation.

Ninja becomes a protocol client automatically if it detects the right
values in the ``MAKEFLAGS`` environment variable (see exact conditions
below).

Since version 1.14, Ninja can also be a protocol server, if needed,
using the ``--jobserver-pool`` command-line flag, or if
``enable_jobserver_pool = 1`` is set in the Ninja build plan.

In jobserver-enabled builds, there is one top-level "server" process
which:

- Sets up a shared pool of job tokens.

- Sets the ``MAKEFLAGS`` environment variable with special values to
  reference the pool.

- Launches child processes (concurrent sub-commands).

Said child processes can be protocol clients if they:

- Recognize the special ``MAKEFLAGS`` values specific to the protocol.

- Use it to access the shared pool to acquire and release job tokens
  during the build.

Ninja automatically becomes a protocol client during builds when:

- Dry-run (i.e. ``-n`` or ``--dry-run``) is not enabled.

- No explicit job count (e.g. ``-j<COUNT>``) is passed on the command
  line.

- The ``MAKEFLAGS`` environment variable is defined and describes a
  valid jobserver mode using ``--jobserver-auth=SEMAPHORE_NAME`` on
  Windows, or ``--jobserver-auth=fifo:PATH`` on POSIX.

.. important::

   On POSIX, only the FIFO-based version of the protocol, which is
   implemented by GNU Make 4.4 and higher, is supported. Ninja will
   detect when a pipe-based jobserver is being used (i.e. when
   ``MAKEFLAGS`` contains ``--jobserver-auth=<read>,<write>``) and will
   print a warning, but will otherwise ignore it.

Using ``--jobserver-pool`` or ``enable_jobserver_pool = 1`` will make
Ninja act as a protocol server, unless any of these are true:

- An existing pool was detected, as this keeps all processes cooperating
  properly.

- ``-j1`` is used on the command-line, as this is asking Ninja to
  explicitly not perform parallel builds.

- Dry-run is enabled.

The size of the pool setup by Ninja matches its parallel count,
determined by the ``-j<COUNT>`` option, or auto-detected if that one is
not provided.

The load-average limitations (i.e. when using ``-l<count>``) are still
being enforced in both modes.

Environment variables
---------------------

Ninja supports two environment variables to control its behavior:
``NINJA_STATUS``, the progress status printed before the rule being run.

Several placeholders are available:

``%s``
   The number of started edges.

``%t``
   The total number of edges that must be run to complete the build.

``%p``
   The percentage of finished edges.

``%r``
   The number of currently running edges.

``%u``
   The number of remaining edges to start.

``%f``
   The number of finished edges.

``%o``
   Overall rate of finished edges per second

``%c``
   Current rate of finished edges per second (average over builds
   specified by ``-j`` or its default)

``%e``
   Elapsed time in seconds. *(Available since Ninja 1.2.)*

``%E``
   Remaining time (ETA) in seconds. *(Available since Ninja 1.12.)*

``%w``
   Elapsed time in [h:]mm:ss format. *(Available since Ninja 1.12.)*

``%W``
   Remaining time (ETA) in [h:]mm:ss format. *(Available since Ninja
   1.12.)*

``%P``
   The percentage (in ppp% format) of time elapsed out of predicted
   total runtime. *(Available since Ninja 1.12.)*

``%%``
   A plain ``%`` character.

The default progress status is ``"[%f/%t] "`` (note the trailing space
to separate from the build rule). Another example of possible progress
status could be ``"[%u/%r/%f] "``.

The ``--status FMT`` command-line flag also configures the progress
status, but uses Ninja’s regular variable-expansion syntax (``$var`` or
``${var}``) instead of ``%``-escapes, with descriptive variable names.
When passed, it takes precedence over ``NINJA_STATUS``.

The available variables and their ``NINJA_STATUS`` equivalents are:

``$started``
   ``%s`` — The number of started edges.

``$total``
   ``%t`` — The total number of edges.

``$progress``
   ``%p`` — The percentage of finished edges.

``$running``
   ``%r`` — The number of currently running edges.

``$remaining``
   ``%u`` — The number of remaining edges to start.

``$finished``
   ``%f`` — The number of finished edges.

``$rate``
   ``%o`` — Overall rate of finished edges per second.

``$current_rate``
   ``%c`` — Current rate of finished edges per second.

``$elapsed_seconds``
   ``%e`` — Elapsed time in seconds.

``$eta_seconds``
   ``%E`` — Remaining time (ETA) in seconds.

``$elapsed``
   ``%w`` — Elapsed time in [h:]mm:ss format.

``$eta``
   ``%W`` — Remaining time (ETA) in [h:]mm:ss format.

``$predicted_progress``
   ``%P`` — Percentage (in ``ppp%`` format) of time elapsed out of
   predicted total runtime.

``$description``
   The current edge’s ``description`` (or its command, when the
   description is empty or ``--verbose`` is in effect). Unlike
   ``NINJA_STATUS``, which always appends the description after the
   formatted status, ``--status`` only shows the description where
   ``$description`` appears in the format. Omit it to drop the
   description entirely; place it wherever you want it shown.

To produce a literal ``$``, use ``$$``. The ``--status`` flag was added
in Ninja 1.14.

If ``MAKEFLAGS`` is defined in the environment, if may alter how Ninja
dispatches parallel build commands. See the GNU Jobserver support
section for details.

Extra tools
-----------

The ``-t`` flag on the Ninja command line runs some tools that we have
found useful during Ninja’s development. The current tools are:

``query``
   dump the inputs and outputs of a given target.

``browse``
   browse the dependency graph in a web browser. Clicking a file focuses
   the view on that file, showing inputs and outputs. This feature
   requires a Python installation. By default, port 8000 is used and a
   web browser will be opened. This can be changed as follows:

   .. code-block:: text

      ninja -t browse --port=8000 --no-browser mytarget

   Use ``--help`` to see a full list of options.

``graph``
   output a file in the syntax used by ``graphviz``, an automatic graph
   layout tool. Use it like:

   .. code-block:: text

      ninja -t graph mytarget | dot -Tpng -ograph.png

   In the Ninja source tree, ``ninja graph.png`` generates an image for
   Ninja itself. If no target is given generate a graph for all root
   targets.

``targets``
   output a list of targets either by rule or by depth. If used like
   ``ninja -t targets rule name`` it prints the list of targets using
   the given rule to be built. If no rule is given, it prints the source
   files (the leaves of the graph). If used like
   ``ninja -t targets depth digit`` it prints the list of targets in a
   depth-first manner starting by the root targets (the ones with no
   outputs). Indentation is used to mark dependencies. If the depth is
   zero it prints all targets. If no arguments are provided
   ``ninja -t targets depth 1`` is assumed. In this mode targets may be
   listed several times. If used like this ``ninja -t targets all`` it
   prints all the targets available without indentation and it is faster
   than the *depth* mode.

``commands``
   given a list of targets, print a list of commands which, if executed
   in order, may be used to rebuild those targets, assuming that all
   output files are out of date. Use ``-s`` to only print the final
   command, not the chain.

``inputs``
   given a list of targets, print a list of all inputs used to rebuild
   those targets. For compatibility reasons, inputs are shell-quoted by
   default. Use ``--no-shell-escape`` to disable quoting. See
   ``ninja -t inputs --help`` for all options. *Available since Ninja
   1.11.*

``multi-inputs``
   print one or more sets of inputs required to build targets. Each line
   will consist of a target, a delimiter, an input and a terminator
   character. The list produced by the tool can be helpful if one would
   like to know which targets that are affected by a certain input.

   The output will be a series of lines with the following elements:

   .. code-block:: text

      <target> <delimiter> <input> <terminator>

   The default ``<delimiter>`` is a single TAB character. The delimiter
   can be modified to any string using the ``--delimiter`` argument.

   The default ``<terminator>`` is a line terminator (i.e. ``\n`` on
   POSIX and ``\r\n`` on Windows). The terminator can be changed to
   ``\0`` by using the ``--print0`` argument.

   Example usage of the ``multi-inputs`` tool:

   .. code-block:: text

      ninja -t multi-inputs target1 target2 target3

   Example of produced output from the ``multi-inputs`` tool:

   .. code-block:: text

      target1 file1.c
      target2 file1.c
      target2 file2.c
      target3 file1.c
      target3 file2.c
      target3 file3.c

   *Note that a given input may appear for several targets if it is used
   by more than one targets.* *Available since Ninja 1.13.*

``clean``
   remove built files. By default, it removes all built files except for
   those created by the generator. Adding the ``-g`` flag also removes
   built files created by the generator (see :ref:`the rule reference for the generator attribute <ref_rule>`). Additional arguments are
   targets, which removes the given targets and recursively all files
   built for them.

   If used like ``ninja -t clean -r rules`` it removes all files built
   using the given rules.

   Files created but not referenced in the graph are not removed. This
   tool takes in account the ``-v`` and the ``-n`` options (note that
   ``-n`` implies ``-v``).

``cleandead``
   remove files produced by previous builds that are no longer in the
   build file. *Available since Ninja 1.10.*

``compdb``
   given a list of rules, each of which is expected to be a C family
   language compiler rule whose first input is the name of the source
   file, prints on standard output a compilation database in the `JSON
   format <http://clang.llvm.org/docs/JSONCompilationDatabase.html>`__
   expected by the Clang tooling interface. Use ``-x`` to expand
   ``@rspfile`` response file invocations. *Available since Ninja 1.2.*

``compdb-targets``
   like ``compdb``, but takes a list of targets instead of rules, and
   expects at least one target. The resulting compilation database
   contains all commands required to build the indicated targets, and
   *only* those commands. Use ``-x`` to expand ``@rspfile`` response
   file invocations.

``deps``
   show all dependencies stored in the ``.ninja_deps`` file. When given
   a target, show just the target’s dependencies. *Available since Ninja
   1.4.*

``missingdeps``
   given a list of targets, look for targets that depend on a generated
   file, but do not have a proper dependency (possibly transitive) on
   the generator. Such targets may cause build flakiness on clean
   builds.

   The broken targets can be found assuming deps log / depfile
   dependency information is correct. Any target that depends on a
   generated file (output of a generator-target) implicitly, but does
   not have an explicit or order-only dependency path to the
   generator-target, is considered broken.

   The tool’s findings can be verified by trying to build the listed
   targets in a clean outdir without building any other targets. The
   build should fail for each of them with a missing include error or
   equivalent pointing to the generated file. *Available since Ninja
   1.11.*

``recompact``
   recompact the ``.ninja_deps`` file. *Available since Ninja 1.4.*

``restat``
   updates all recorded file modification timestamps in the
   ``.ninja_log`` file. *Available since Ninja 1.10.*

   The build manifest won’t be parsed when running this tool. If you’re
   using a ``builddir`` you must pass it via ``--builddir=DIR``.
   *Available since Ninja 1.14.*

``rules``
   output the list of all rules. It can be used to know which rule name
   to pass to ``ninja -t targets rule name`` or ``ninja -t compdb``.
   Adding the ``-d`` flag also prints the description of the rules.

``msvc``
   Available on Windows hosts only. Helper tool to invoke the ``cl.exe``
   compiler with a pre-defined set of environment variables, as in:

   .. code-block:: text

      ninja -t msvc -e ENVFILE -- cl.exe <arguments>

   Where ``ENVFILE`` is a binary file that contains an environment block
   suitable for CreateProcessA() on Windows (i.e. a series of
   zero-terminated strings that look like NAME=VALUE, followed by an
   extra zero terminator). Note that this uses the local codepage
   encoding.

   This tool also supports a deprecated way of parsing the compiler’s
   output when the ``/showIncludes`` flag is used, and generating a
   GCC-compatible depfile from it:

   .. code-block:: text

      ninja -t msvc -o DEPFILE [-p STRING] -- cl.exe /showIncludes <arguments>

   When using this option, ``-p STRING`` can be used to pass the
   localized line prefix that ``cl.exe`` uses to output dependency
   information. For English-speaking regions this is
   ``"Note: including file: "`` without the double quotes, but will be
   different for other regions.

   Note that Ninja supports this natively now, with the use of
   ``deps = msvc`` and ``msvc_deps_prefix`` in Ninja files. Native
   support also avoids launching an extra tool process each time the
   compiler must be called, which can speed up builds noticeably on
   Windows.

``wincodepage``
   Available on Windows hosts (*since Ninja 1.11*). Prints the Windows
   code page whose encoding is expected in the build file. The output
   has the form:

   .. code-block:: text

      Build file encoding: <codepage>

   Additional lines may be added in future versions of Ninja.

   The ``<codepage>`` is one of:

   ``UTF-8``
      Encode as UTF-8.

   ``ANSI``
      Encode to the system-wide ANSI code page.
