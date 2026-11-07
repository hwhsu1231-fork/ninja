Introduction
============

Ninja is yet another build system. It takes as input the
interdependencies of files (typically source code and output
executables) and orchestrates building them, *quickly*.

Ninja joins a sea of other build systems. Its distinguishing goal is to
be fast. It is born from `my work on the Chromium browser
project <http://neugierig.org/software/chromium/notes/2011/02/ninja.html>`__,
which has over 30,000 source files and whose other build systems
(including one built from custom non-recursive Makefiles) would take ten
seconds to start building after changing one file. Ninja is under a
second.

Philosophical overview
----------------------

Where other build systems are high-level languages, Ninja aims to be an
assembler.

Build systems get slow when they need to make decisions. When you are in
an edit-compile cycle you want it to be as fast as possible — you want
the build system to do the minimum work necessary to figure out what
needs to be built immediately.

Ninja contains the barest functionality necessary to describe arbitrary
dependency graphs. Its lack of syntax makes it impossible to express
complex decisions.

Instead, Ninja is intended to be used with a separate program generating
its input files. The generator program (like the ``./configure`` found
in autotools projects) can analyze system dependencies and make as many
decisions as possible up front so that incremental builds stay fast.
Going beyond autotools, even build-time decisions like "which compiler
flags should I use?" or "should I build a debug or release-mode binary?"
belong in the ``.ninja`` file generator.

Design goals
------------

Here are the design goals of Ninja:

- very fast (i.e., instant) incremental builds, even for very large
  projects.

- very little policy about how code is built. Different projects and
  higher-level build systems have different opinions about how code
  should be built; for example, should built objects live alongside the
  sources or should all build output go into a separate directory? Is
  there a "package" rule that builds a distributable package of the
  project? Sidestep these decisions by trying to allow either to be
  implemented, rather than choosing, even if that results in more
  verbosity.

- get dependencies correct, and in particular situations that are
  difficult to get right with Makefiles (e.g. outputs need an implicit
  dependency on the command line used to generate them; to build C
  source code you need to use gcc’s ``-M`` flags for header
  dependencies).

- when convenience and speed are in conflict, prefer speed.

Some explicit *non-goals*:

- convenient syntax for writing build files by hand. *You should
  generate your Ninja files using another program*. This is how we can
  sidestep many policy decisions.

- built-in rules. *Out of the box, Ninja has no rules for e.g. compiling
  C code.*

- build-time customization of the build. *Options belong in the program
  that generates the Ninja files*.

- build-time decision-making ability such as conditionals or search
  paths. *Making decisions is slow.*

To restate, Ninja is faster than other build systems because it is
painfully simple. You must tell Ninja exactly what to do when you create
your project’s ``.ninja`` files.

Comparison to Make
------------------

Ninja is closest in spirit and functionality to Make, relying on simple
dependencies between file timestamps.

But fundamentally, make has a lot of *features*: suffix rules,
functions, built-in rules that e.g. search for RCS files when building
source. Make’s language was designed to be written by humans. Many
projects find make alone adequate for their build problems.

In contrast, Ninja has almost no features; just those necessary to get
builds correct while punting most complexity to generation of the Ninja
input files. Ninja by itself is unlikely to be useful for most projects.

Here are some of the features Ninja adds to Make. (These sorts of
features can often be implemented using more complicated Makefiles, but
they are not part of Make itself.)

- Ninja has special support for discovering extra dependencies at build
  time, making it easy to get :ref:`header dependencies <ref_headers>`
  correct for C/C++ code.

- A build edge may have multiple outputs.

- Outputs implicitly depend on the command line that was used to
  generate them, which means that changing e.g. compilation flags will
  cause the outputs to rebuild.

- Output directories are always implicitly created before running the
  command that relies on them.

- Rules can provide shorter descriptions of the command being run, so
  you can print e.g. ``CC foo.o`` instead of a long command line while
  building.

- Builds are always run in parallel, based by default on the number of
  CPUs your system has. Underspecified build dependencies will result in
  incorrect builds.

- Command output is always buffered. This means commands running in
  parallel don’t interleave their output, and when a command fails we
  can print its failure output next to the full command line that
  produced the failure.
