"""
Multi-version compatibility matrix for pyshewhart.

What this does
--------------
For every supported Python version, this builds a fresh virtual environment,
installs pyshewhart plus its dependencies, and runs the headless smoke tests in
``tests/``.  It does so twice per Python version -- once pinning the *oldest*
dependency versions that version allows, and once the *newest* -- so a single
``nox`` run tells us where pyshewhart really works across both the Python axis
and the dependency axis.

How to run
----------
``nox`` itself is a dev-only tool; install it in isolation (it will not touch
the project's own virtual environment) with::

    uv tool install nox

or run it ad hoc without installing::

    uvx nox

Then::

    nox                                             # the full 7 x 2 matrix
    nox -s "compat-3.12(resolution='highest')"      # one specific cell

``venv_backend="uv"`` makes nox create each environment with ``uv``, which will
automatically download any CPython interpreter that isn't already present.

Reading the results
--------------------
nox prints a pass/fail summary line per session at the end.  A red session
names the exact (Python version, dependency resolution) combination that
breaks -- that is the boundary of real support, and the input to fixing the
version claims and lower bounds in ``setup.py``.
"""

import nox

# uv's managed CPython builds start at 3.8, so 3.7 -- which setup.py currently
# advertises -- cannot be tested here; 3.8 is the practical floor.
PYTHONS = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]

# pyshewhart's runtime dependencies (mirrors install_requires in setup.py).  We
# pass these EXPLICITLY on the install command below so the resolver treats them
# as *direct* requirements -- otherwise, coming in only via ``-e .``, they'd be
# transitive and the "lowest-direct" strategy would leave them at their newest
# versions, defeating the whole point of the lowest leg.
RUNTIME_DEPS = ["matplotlib", "numpy", "python-dateutil"]

# The two ends of the dependency range, expressed as uv resolver strategies:
#   * "lowest-direct" -> the OLDEST versions of the direct requirements
#     (RUNTIME_DEPS) that still support this interpreter, while keeping their
#     own transitive deps modern.  Catches use of an API that didn't exist in
#     early matplotlib/numpy releases.
#   * "highest" (uv's default) -> the NEWEST available versions.  Catches
#     breakage from removed/renamed APIs -- most importantly the numpy 2.0
#     changes of June 2024.
RESOLUTIONS = ["lowest-direct", "highest"]


@nox.session(venv_backend="uv", python=PYTHONS)
@nox.parametrize("resolution", RESOLUTIONS)
def compat(session, resolution):
    """Install pyshewhart at one dependency boundary and run the smoke tests.

    Note on the "lowest-direct" leg: because ``setup.py``'s ``install_requires``
    currently declares no lower bounds, this asks uv for the very oldest
    matplotlib/numpy that still claim to support the interpreter.  Some of those
    ancient releases ship no wheel and fail to build -- that failure is itself a
    useful result (it reveals the true minimum) rather than a broken test.
    """
    # Install the test runner separately and at its default (newest) version so
    # the --resolution strategy below applies ONLY to pyshewhart and its runtime
    # deps -- never dragging pytest itself down to an ancient, unbuildable release.
    session.install("pytest")

    # Restrict numpy/matplotlib to versions that ship a wheel for this
    # interpreter.  Without this, "lowest-direct" would pick each dependency's
    # absolute floor (e.g. numpy 1.17.0, the lower bound declared in setup.py)
    # and try to build it from source on *every* Python -- but numpy 1.17.0 only
    # has wheels up to ~3.8, so it fails to compile on 3.9+.  Forcing wheels
    # makes the "lowest" leg test the genuinely useful thing: the OLDEST
    # dependency versions a user could actually install on this Python.
    wheel_only = ["--only-binary", "numpy", "--only-binary", "matplotlib"]

    # With the uv backend, session.install shells out to `uv pip install`, which
    # accepts --resolution to pick which end of each dependency's range we get.
    # Listing RUNTIME_DEPS explicitly makes them direct requirements so
    # "lowest-direct" actually lowers them.
    session.install(
        "-e", ".", *RUNTIME_DEPS, "--resolution", resolution, *wheel_only
    )

    # MPLBACKEND=Agg is belt-and-suspenders alongside conftest.py's
    # matplotlib.use("Agg"), guaranteeing no attempt to open a GUI window.
    session.run("pytest", "-q", env={"MPLBACKEND": "Agg"})
