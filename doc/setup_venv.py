#!/usr/bin/env python3
"""Create the virtualenv used to build the manual with Sphinx.

Invoked by the `manual` build target as:

    python doc/setup_venv.py <venv-dir> <stamp-file>

The virtualenv is only created if it does not exist yet, then the packages
from requirements.txt are installed into it. The stamp file records a
successful setup so that Ninja can skip this step on later builds.
"""

import os
import subprocess
import sys
import venv


def _venv_python(venv_dir):
    if os.name == 'nt':
        return os.path.join(venv_dir, 'Scripts', 'python.exe')
    return os.path.join(venv_dir, 'bin', 'python')


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: setup_venv.py <venv-dir> <stamp-file>')
    venv_dir, stamp = sys.argv[1], sys.argv[2]
    requirements = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'requirements.txt')

    if not os.path.exists(os.path.join(venv_dir, 'pyvenv.cfg')):
        venv.EnvBuilder(with_pip=True).create(venv_dir)

    subprocess.check_call([
        _venv_python(venv_dir), '-m', 'pip', 'install', '-q', '-r',
        requirements,
    ])
    open(stamp, 'w').close()


if __name__ == '__main__':
    main()
