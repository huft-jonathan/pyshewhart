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
    version="1.0.0",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only"],
    keywords="control charts, statistical process control, SPC, "
             "quality control, manufacturing, statistics",
    packages=find_packages(),
    package_dir={"pyshewhart": "pyshewhart"},
    package_data={"pyshewhart": ["examples/*.csv"]},
    install_requires=["matplotlib", "numpy", "python-dateutil"],
    python_requires=">=3.7, <4",
    entry_points={"console_scripts": ["pyshewhart=pyshewhart:main"]},
)
