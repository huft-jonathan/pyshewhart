"""
Headless smoke tests for pyshewhart.

Purpose
-------
These tests are the payload of the multi-version compatibility sweep defined in
``noxfile.py``.  They are deliberately *smoke tests*: they do not check that the
statistics or the pixels are correct, only that pyshewhart's public API can be
exercised end-to-end on a given (Python version, dependency set) combination
**without raising an exception**.  That is exactly the signal we want when
asking "does this package still work on Python 3.8 ... 3.14, against the oldest
and newest numpy/matplotlib each allows?"

Why not just run the example scripts?
-------------------------------------
The scripts in ``pyshewhart/examples/`` and the ``pyshewhart`` console script
(``pyshewhart/__init__.py:main``) all end with ``input("Enter to close ...")``,
which blocks forever without a human at the keyboard.  So instead of invoking
those, we call the same underlying public API they use (the chart classes and
the ``data_types`` import helpers), which is fully non-interactive once the
``Agg`` backend is active (see ``conftest.py``).

What is covered
---------------
* All four chart types: X-bar & R, X-bar & S, CUSUM, and P-attribute.
* Every time-info input format the README advertises (elapsed seconds,
  ``datetime`` objects, and ISO-8601 strings).
* The CSV import path used by the console script
  (``import_csv_to_arrays`` -> ``import_times_values`` -> chart).
* The Western Electric rule-set evaluation.
"""

import datetime
import random

import pytest

import pyshewhart
from pyshewhart import data_types


# Absolute path to the CSV that ships inside the package, so the CSV-import test
# works no matter what directory pytest is invoked from.
import pathlib

EXAMPLE_CSV = (
    pathlib.Path(pyshewhart.__file__).parent / "examples" / "example_data_1.csv"
)


@pytest.fixture
def measurements():
    """A fixed, reproducible list of 100 'in control' measurements.

    Seeded so results are identical on every interpreter -- a compatibility
    sweep should differ only because of Python/dependency versions, never
    because of random noise.  100 points / default sample size of 5 == 20
    samples, comfortably enough for every chart type and the Western Electric
    rules to have something to work with.
    """
    rng = random.Random(1234)
    return [rng.normalvariate(mu=10.0, sigma=0.5) for _ in range(100)]


# ---------------------------------------------------------------------------
# The four chart types
# ---------------------------------------------------------------------------

def test_xbar_r(measurements):
    """X-bar and R (mean and range) chart builds from a bare measurement list."""
    pyshewhart.XbarR(measurements)


def test_xbar_s(measurements):
    """X-bar and S (mean and standard deviation) chart builds."""
    pyshewhart.XbarS(measurements)


def test_cusum(measurements):
    """CUSUM chart builds.  It requires an explicit target value to accumulate
    deviations against, so we hand it the data's own mean."""
    target = sum(measurements) / len(measurements)
    pyshewhart.CUSUM(measurements, cusum_target=target)


def test_p_attribute():
    """P-attribute chart builds from pass/fail (0/1) attribute data.

    Unlike the variable charts, this one needs a Record built with
    ``is_attribute=True`` so the samples expose a 'proportion defective'.
    We generate 200 Bernoulli outcomes and let the default sample size group
    them into subgroups.
    """
    rng = random.Random(1234)
    attribute_values = [1 if rng.random() < 0.1 else 0 for _ in range(200)]
    record = data_types.import_times_values(
        values=attribute_values, sample_size=20, is_attribute=True
    )
    pyshewhart.PAttribute(record=record)


# ---------------------------------------------------------------------------
# Time-info input formats (the package's headline feature)
# ---------------------------------------------------------------------------

def _elapsed_seconds(n):
    """n measurements taken one hour apart, expressed as elapsed seconds."""
    return [3600 * i for i in range(n)]


def _datetimes(n):
    """n measurements taken one day apart, as datetime objects."""
    start = datetime.datetime(2023, 1, 1)
    return [start + datetime.timedelta(days=i) for i in range(n)]


def _iso_strings(n):
    """The same datetimes, serialized to ISO-8601 strings (dateutil parses)."""
    return [dt.isoformat() for dt in _datetimes(n)]


@pytest.mark.parametrize(
    "times_factory",
    [_elapsed_seconds, _datetimes, _iso_strings],
    ids=["elapsed-seconds", "datetimes", "iso-strings"],
)
def test_time_formats(measurements, times_factory):
    """Every supported time format can be paired with measurements and charted.

    This exercises the ``python-dateutil`` parsing path for the string case and
    the numpy/matplotlib time handling for all three -- a common place for
    dependency-version incompatibilities to surface.
    """
    times = times_factory(len(measurements))
    pyshewhart.XbarR(times, measurements)


# ---------------------------------------------------------------------------
# CSV import path (mirrors what the console script does)
# ---------------------------------------------------------------------------

def test_csv_import_and_chart():
    """The CSV -> arrays -> Record -> chart pipeline used by the CLI works.

    Mirrors ``pyshewhart/__init__.py:55-56`` without invoking ``main()`` (which
    would block on ``input()``).
    """
    times, values = data_types.import_csv_to_arrays(str(EXAMPLE_CSV))
    assert len(values) > 0
    record = data_types.import_times_values(
        times=times, values=values, sample_size=5
    )
    pyshewhart.XbarS(record=record)


# ---------------------------------------------------------------------------
# Western Electric rule set
# ---------------------------------------------------------------------------

def test_western_electric_rules(measurements):
    """The Western Electric anomaly rule set can be evaluated without error."""
    pyshewhart.XbarR(measurements, check_western_elec_rules=True)
