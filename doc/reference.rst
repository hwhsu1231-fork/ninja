.. _ref_ninja_file:

Ninja file reference
====================

A file is a series of declarations. A declaration can be one of:

1. A rule declaration, which begins with ``rule rulename``, and then has
   a series of indented lines defining variables.

2. | A build edge, which looks like
     ``build output1 output2: rulename input1 input2``.
   | Implicit dependencies may be tacked on the end with
     ``| dependency1 dependency2``.
   | Order-only dependencies may be tacked on the end with
     ``|| dependency1 dependency2``. (See :ref:`the reference on dependency types <ref_dependencies>`.) Validations may be tacked on the end
     with ``|@ validation1 validation2``. (See :ref:`the reference on validations <validations>`.)

   Implicit outputs *(available since Ninja 1.7)* may be added before
   the ``:`` with ``| output1 output2`` and do not appear in ``$out``.
   (See :ref:`the reference on output types <ref_outputs>`.)

3. Variable declarations, which look like ``variable = value``.

4. Default target statements, which look like
   ``default target1 target2``.

5. References to more files, which look like ``subninja path`` or
   ``include path``. The difference between these is explained below :ref:`in the discussion about scoping <ref_scope>`.

6. A pool declaration, which looks like ``pool poolname``. Pools are
   explained :ref:`in the section on pools <ref_pool>`.

.. _ref_lexer:

Lexical syntax
--------------

Ninja is mostly encoding-agnostic, as long as the bytes Ninja cares
about (like slashes in paths) are ASCII. This means e.g. UTF-8 or
ISO-8859-1 input files ought to work.

Comments begin with ``#`` and extend to the end of the line.

Newlines are significant. Statements like ``build foo bar`` are a set of
space-separated tokens that end at the newline. Newlines and spaces
within a token must be escaped.

There is only one escape character, ``$``, and it has the following
behaviors:

``$`` followed by a newline
   escape the newline (continue the current line across a line break).

``$`` followed by text
   a variable reference.

``${varname}``
   alternate syntax for ``$varname``.

``$`` followed by space
   a space. (This is only necessary in lists of paths, where a space
   would otherwise separate filenames. See below.)

``$:``
   a colon. (This is only necessary in ``build`` lines, where a colon
   would otherwise terminate the list of outputs.)

``$^``
   a newline *(available since Ninja 1.14)*.

Inserts *\\n* into the resulting string. This is useful to write build
commands that require several shell lines as a single ``command`` value
in the build plan.

Requires ``ninja_required_version`` to be specified and greater or equal
to 1.14 in the build file.

``$$``
   a literal ``$``.

A ``build`` or ``default`` statement is first parsed as a
space-separated list of filenames and then each name is expanded. This
means that spaces within a variable will result in spaces in the
expanded filename.

.. code-block:: text

   spaced = foo bar
   build $spaced/baz other$ file: ...
   # The above build line has two outputs: "foo bar/baz" and "other file".

In a ``name = value`` statement, whitespace at the beginning of a value
is always stripped. Whitespace at the beginning of a line after a line
continuation is also stripped.

.. code-block:: text

   two_words_with_one_space = foo $
       bar
   one_word_with_no_space = foo$
       bar

Other whitespace is only significant if it’s at the beginning of a line.
If a line is indented more than the previous one, it’s considered part
of its parent’s scope; if it is indented less than the previous one, it
closes the previous scope.

.. _ref_toplevel:

Top-level variables
-------------------

Three variables are significant when declared in the outermost file
scope.

``builddir``
   a directory for some Ninja output files. See :ref:`the discussion of the build log <ref_log>`. (You can also store other build output in
   this directory.)

``ninja_required_version``
   the minimum version of Ninja required to process the build correctly.
   See :ref:`the discussion of versioning <ref_versioning>`.

``enable_jobserver_pool``
   If set to ``1`` (any other value is ignored), enable jobserver pool
   mode, as if ``--jobserver-pool`` was passed on the command line. Note
   that ``0`` does not disable the feature, and that the size of the
   pool is determined by the parallel job count that is either
   auto-detected or controlled by the ``-j<COUNT>`` command-line option.

.. _ref_rule:

Rule variables
--------------

A ``rule`` block contains a list of ``key = value`` declarations that
affect the processing of the rule. Here is a full list of special keys.

``command`` (*required*)
   the command line to run. Each ``rule`` may have only one ``command``
   declaration. See :ref:`the next section <ref_rule_command>` for more
   details on quoting and executing multiple commands.

``depfile``
   path to an optional ``Makefile`` that contains extra *implicit
   dependencies* (see :ref:`the reference on dependency types <ref_dependencies>`). This is explicitly to support C/C++
   header dependencies; see :ref:`the full discussion <ref_headers>`.

``deps``
   *(Available since Ninja 1.3.)* if present, must be one of ``gcc`` or
   ``msvc`` to specify special dependency processing. See :ref:`the full discussion <ref_headers>`. The generated database is stored as
   ``.ninja_deps`` in the ``builddir``, see :ref:`the discussion of builddir <ref_toplevel>`.

``msvc_deps_prefix``
   *(Available since Ninja 1.5.)* defines the string which should be
   stripped from msvc’s /showIncludes output. Only needed when
   ``deps = msvc`` and no English Visual Studio version is used.

``description``
   a short description of the command, used to pretty-print the command
   as it’s running. The ``-v`` flag controls whether to print the full
   command or its description; if a command fails, the full command line
   will always be printed before the command’s output.

``dyndep``
   *(Available since Ninja 1.10.)* used only on build statements. If
   present, must name one of the build statement inputs. Dynamically
   discovered dependency information will be loaded from the file. See
   the :ref:`dynamic dependencies <ref_dyndep>` section for details.

``generator``
   if present, specifies that this rule is used to re-invoke the
   generator program. Files built using ``generator`` rules are treated
   specially in two ways: firstly, they will not be rebuilt if the
   command line changes; and secondly, they are not cleaned by default.

``in``
   the space-separated list of files provided as inputs to the build
   line referencing this ``rule``, shell-quoted if it appears in
   commands. (``$in`` is provided solely for convenience; if you need
   some subset or variant of this list of files, just construct a new
   variable with that list and use that instead.)

``in_newline``
   the same as ``$in`` except that multiple inputs are separated by
   newlines rather than spaces. (For use with ``$rspfile_content``; this
   works around a bug in the MSVC linker where it uses a fixed-size
   buffer for processing input.)

``out``
   the space-separated list of files provided as outputs to the build
   line referencing this ``rule``, shell-quoted if it appears in
   commands.

``pool``
   *(Available since Ninja 1.1.)* used to allocate one or more rules or
   edges a finite number of concurrent jobs. See the
   :ref:`pools <ref_pool>` section for details.

``restat``
   if present, causes Ninja to re-stat the command’s outputs after
   execution of the command. Each output whose modification time the
   command did not change will be treated as though it had never needed
   to be built. This may cause the output’s reverse dependencies to be
   removed from the list of pending build actions.

``rspfile``, ``rspfile_content``
   if present (both), Ninja will use a response file for the given
   command, i.e. write the selected string (``rspfile_content``) to the
   given file (``rspfile``) before calling the command and delete the
   file after successful execution of the command.

   This is particularly useful on Windows, where the maximum length of a
   command line is limited and response files must be used instead.

   Use it like in the following example:

   .. code-block:: text

      rule link
        command = link.exe /OUT$out [usual link flags here] @$out.rsp
        rspfile = $out.rsp
        rspfile_content = $in

      build myapp.exe: link a.obj b.obj [possibly many other .obj files]

.. _ref_rule_command:

Interpretation of the ``command`` variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fundamentally, command lines behave differently on Unix and Windows.

On Unix systems, commands are arrays of arguments. The Ninja ``command``
variable is passed directly to ``sh -c``, which is then responsible for
interpreting that string into an argv array. Therefore, the quoting
rules are those of the shell, and you can use all the normal shell
operators, like ``&&`` to chain multiple commands, or ``VAR=value cmd``
to set environment variables.

On Windows, commands are strings, so Ninja passes the ``command`` string
directly to ``CreateProcess``. (In the common case of simply executing a
compiler this means there is less overhead.) Consequently, the quoting
rules are determined by the called program, which on Windows are usually
provided by the C library. If you need shell interpretation of the
command (such as the use of ``&&`` to chain multiple commands), make the
command execute the Windows shell by prefixing the command with
``cmd /c``. Ninja may error with "invalid parameter" which usually
indicates that the command line length has been exceeded.

.. _ref_outputs:

Build outputs
-------------

There are two types of build outputs which are subtly different.

1. *Explicit outputs*, as listed in a build line. These are available as
   the ``$out`` variable in the rule.

   This is the standard form of output to be used for e.g. the object
   file of a compile command.

2. *Implicit outputs*, as listed in a build line with the syntax
   ``| out1 out2`` before the ``:`` of a build line *(available since
   Ninja 1.7)*. The semantics are identical to explicit outputs, the
   only difference is that implicit outputs don’t show up in the
   ``$out`` variable.

   This is for expressing outputs that don’t show up on the command line
   of the command.

.. _ref_dependencies:

Build dependencies
------------------

There are three types of build dependencies which are subtly different.

1. *Explicit dependencies*, as listed in a build line. These are
   available as the ``$in`` variable in the rule. Changes in these files
   cause the output to be rebuilt; if these files are missing and Ninja
   doesn’t know how to build them, the build is aborted.

   This is the standard form of dependency to be used e.g. for the
   source file of a compile command.

2. *Implicit dependencies*, either as picked up from a ``depfile``
   attribute on a rule or from the syntax ``| dep1 dep2`` on the end of
   a build line. The semantics are identical to explicit dependencies,
   the only difference is that implicit dependencies don’t show up in
   the ``$in`` variable.

   This is for expressing dependencies that don’t show up on the command
   line of the command; for example, for a rule that runs a script that
   reads a hardcoded file, the hardcoded file should be an implicit
   dependency, as changes to the file should cause the output to
   rebuild, even though it doesn’t show up in the arguments.

   Note that dependencies as loaded through depfiles have slightly
   different semantics, as described in the :ref:`rule reference <ref_rule>`.

3. *Order-only dependencies*, expressed with the syntax ``|| dep1 dep2``
   on the end of a build line. When these are out of date, the output is
   not rebuilt until they are built, but changes in order-only
   dependencies alone do not cause the output to be rebuilt.

   Order-only dependencies can be useful for bootstrapping dependencies
   that are only discovered during build time: for example, to generate
   a header file before starting a subsequent compilation step. (Once
   the header is used in compilation, a generated dependency file will
   then express the implicit dependency.)

File paths are compared as is, which means that an absolute path and a
relative path, pointing to the same file, are considered different by
Ninja.

.. _validations:

Validations
-----------

*Available since Ninja 1.11.*

Validations listed on the build line cause the specified files to be
added to the top level of the build graph (as if they were specified on
the Ninja command line) whenever the build line is a transitive
dependency of one of the targets specified on the command line or a
default target.

Validations are added to the build graph regardless of whether the
output files of the build statement are dirty are not, and the dirty
state of the build statement that outputs the file being used as a
validation has no effect on the dirty state of the build statement that
requested it.

A build edge can list another build edge as a validation even if the
second edge depends on the first.

Validations are designed to handle rules that perform error checking but
don’t produce any artifacts needed by the build, for example, static
analysis tools. Marking the static analysis rule as an implicit input of
the main build rule of the source files or of the rules that depend on
the main build rule would slow down the critical path of the build, but
using a validation would allow the build to proceed in parallel with the
static analysis rule once the main build rule is complete.

Variable expansion
------------------

Variables are expanded in paths (in a ``build`` or ``default``
statement) and on the right side of a ``name = value`` statement.

When a ``name = value`` statement is evaluated, its right-hand side is
expanded immediately (according to the below scoping rules), and from
then on ``$name`` expands to the static string as the result of the
expansion. It is never the case that you’ll need to "double-escape" a
value to prevent it from getting expanded twice.

All variables are expanded immediately as they’re encountered in
parsing, with one important exception: variables in ``rule`` blocks are
expanded when the rule is *used*, not when it is declared. In the
following example, the ``demo`` rule prints "this is a demo of bar".

.. code-block:: text

   rule demo
     command = echo "this is a demo of $foo"

   build out: demo
     foo = bar

.. _ref_scope:

Evaluation and scoping
----------------------

Top-level variable declarations are scoped to the file they occur in.

Rule declarations are also scoped to the file they occur in. *(Available
since Ninja 1.6)*

The ``subninja`` keyword, used to include another ``.ninja`` file,
introduces a new scope. The included ``subninja`` file may use the
variables and rules from the parent file, and shadow their values for
the file’s scope, but it won’t affect values of the variables in the
parent.

To include another ``.ninja`` file in the current scope, much like a C
``#include`` statement, use ``include`` instead of ``subninja``.

Variable declarations indented in a ``build`` block are scoped to the
``build`` block. The full lookup order for a variable expanded in a
``build`` block (or the ``rule`` is uses) is:

1. Special built-in variables (``$in``, ``$out``).

2. Build-level variables from the ``build`` block.

3. Rule-level variables from the ``rule`` block (i.e. ``$command``).
   (Note from the above discussion on expansion that these are expanded
   "late", and may make use of in-scope bindings like ``$in``.)

4. File-level variables from the file that the ``build`` line was in.

5. Variables from the file that included that file using the
   ``subninja`` keyword.
