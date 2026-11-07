Writing your own Ninja files
============================

The remainder of this manual is only useful if you are constructing
Ninja files yourself: for example, if you’re writing a meta-build system
or supporting a new language.

Conceptual overview
-------------------

Ninja evaluates a graph of dependencies between files, and runs
whichever commands are necessary to make your build target up to date as
determined by file modification times. If you are familiar with Make,
Ninja is very similar.

A build file (default name: ``build.ninja``) provides a list of
*rules* — short names for longer commands, like how to run the
compiler — along with a list of *build* statements saying how to build
files using the rules — which rule to apply to which inputs to produce
which outputs.

Conceptually, ``build`` statements describe the dependency graph of your
project, while ``rule`` statements describe how to generate the files
along a given edge of the graph.

Syntax example
--------------

Here’s a basic ``.ninja`` file that demonstrates most of the syntax. It
will be used as an example for the following sections.

.. code-block:: text

   cflags = -Wall

   rule cc
     command = gcc $cflags -c $in -o $out

   build foo.o: cc foo.c

Variables
---------

Despite the non-goal of being convenient to write by hand, to keep build
files readable (debuggable), Ninja supports declaring shorter reusable
names for strings. A declaration like the following

.. code-block:: text

   cflags = -g

can be used on the right side of an equals sign, dereferencing it with a
dollar sign, like this:

.. code-block:: text

   rule cc
     command = gcc $cflags -c $in -o $out

Variables can also be referenced using curly braces like ``${in}``.

Variables might be better called "bindings", in that a given variable
cannot be changed, only shadowed. There is more on how shadowing works
later in this document.

Rules
-----

Rules declare a short name for a command line. They begin with a line
consisting of the ``rule`` keyword and a name for the rule. Then follows
an indented set of ``variable = value`` lines.

The basic example above declares a new rule named ``cc``, along with the
command to run. In the context of a rule, the ``command`` variable
defines the command to run, ``$in`` expands to the list of input files
(``foo.c``), and ``$out`` to the output files (``foo.o``) for the
command. A full list of special variables is provided in :ref:`the reference <ref_rule>`.

Build statements
----------------

Build statements declare a relationship between input and output files.
They begin with the ``build`` keyword, and have the format
``build outputs: rulename inputs``. Such a declaration says that all of
the output files are derived from the input files. When the output files
are missing or when the inputs change, Ninja will run the rule to
regenerate the outputs.

The basic example above describes how to build ``foo.o``, using the
``cc`` rule.

In the scope of a ``build`` block (including in the evaluation of its
associated ``rule``), the variable ``$in`` is the list of inputs and the
variable ``$out`` is the list of outputs.

A build statement may be followed by an indented set of ``key = value``
pairs, much like a rule. These variables will shadow any variables when
evaluating the variables in the command. For example:

.. code-block:: text

   cflags = -Wall -Werror
   rule cc
     command = gcc $cflags -c $in -o $out

   # If left unspecified, builds get the outer $cflags.
   build foo.o: cc foo.c

   # But you can shadow variables like cflags for a particular build.
   build special.o: cc special.c
     cflags = -Wall

   # The variable was only shadowed for the scope of special.o;
   # Subsequent build lines get the outer (original) cflags.
   build bar.o: cc bar.c

For more discussion of how scoping works, consult :ref:`the reference <ref_scope>`.

If you need more complicated information passed from the build statement
to the rule (for example, if the rule needs "the file extension of the
first input"), pass that through as an extra variable, like how
``cflags`` is passed above.

If the top-level Ninja file is specified as an output of any build
statement and it is out of date, Ninja will rebuild and reload it before
building the targets requested by the user.

Generating Ninja files from code
--------------------------------

``misc/ninja_syntax.py`` in the Ninja distribution is a tiny Python
module to facilitate generating Ninja files. It allows you to make
Python calls like
``ninja.rule(name='foo', command='bar', depfile='$out.d')`` and it will
generate the appropriate syntax. Feel free to just inline it into your
project’s build system if it’s useful.
