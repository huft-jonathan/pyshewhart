"""
Shared pytest configuration for the pyshewhart compatibility smoke tests.

Why this file exists
--------------------
pyshewhart is a plotting library: every control-chart object it builds creates
a matplotlib figure and, at the end of ``control_charts.py``, calls
``self.fig.show()``.  With a normal interactive backend that would try to open a
GUI window, which is impossible (and would hang) in an automated, headless
test run across many Python versions.

To make the whole test suite run unattended we force matplotlib's ``Agg``
backend *before* ``pyplot`` is ever imported.  ``Agg`` is a pure in-memory
renderer -- it draws to a buffer instead of a screen, so ``fig.show()`` becomes
a harmless no-op (it only emits a UserWarning, which we silence in
``pyproject.toml``).  This must happen at import time, hence it lives here in
``conftest.py`` rather than inside an individual test.
"""

import matplotlib

# Select the non-interactive backend up front.  Must precede any pyplot import.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (import after backend selection)
import pytest


@pytest.fixture(autouse=True)
def _close_figures():
    """Close every figure a test opened.

    pyshewhart never closes the figures it creates, so without this each test
    would leak one (or more), eventually tripping matplotlib's "too many open
    figures" warning and needlessly consuming memory during the 14-environment
    sweep.  ``autouse=True`` applies it to every test automatically.
    """
    yield
    plt.close("all")
