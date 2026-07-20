"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pyshewhart",
    version="1.0.1",
    description="Statistical Process Control Charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="David Jonathan Huft",
    author_email="jhuft@protonmail.ch",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        # Verified by the nox compatibility sweep (see noxfile.py): the smoke
        # tests pass on CPython 3.8 through 3.14.  3.7 is no longer claimed --
        # it predates the versions uv can provision, so it is untested here.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3 :: Only"],
    keywords="control charts, statistical process control, SPC, "
             "quality control, manufacturing, statistics",
    packages=find_packages(),
    package_dir={"pyshewhart": "pyshewhart"},
    package_data={"pyshewhart": ["examples/*.csv"]},
    # Lower bounds established empirically by the compatibility sweep:
    #   * matplotlib>=3.5.0 is a HARD requirement -- control_charts.py calls
    #     ``Axis.set_xticks(..., labels=...)``, and the ``labels`` keyword was
    #     only added in matplotlib 3.5.0.  Older releases raise TypeError.
    #   * numpy>=1.17.0 matches matplotlib 3.5's own floor; pyshewhart itself
    #     only uses the long-stable numpy.mean / numpy.std.
    #   * python-dateutil>=2.7.0 is a safe, well-tested floor for time parsing.
    # Without these bounds, resolvers using a "lowest" strategy reach all the
    # way back to Python-2-era releases (e.g. matplotlib 0.86) that cannot build.
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.17.0",
        "python-dateutil>=2.7.0",
    ],
    python_requires=">=3.8, <4",
    entry_points={"console_scripts": ["pyshewhart=pyshewhart:main"]},
)
