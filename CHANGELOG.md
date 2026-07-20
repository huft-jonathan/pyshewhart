# Changelog

All notable changes to `pyshewhart` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-19

### Fixed
- Replaced the removed `matplotlib.axes.Axes.plot_date()` (deprecated in
  matplotlib 3.9, removed in 3.11) with `plot()` / `scatter()`, restoring
  compatibility with current matplotlib releases. (#2, #3)

### Changed
- **Python 3.7 support dropped.** Supported versions are now Python 3.8
  through 3.14 (`python_requires >= 3.8, < 4`), each verified by a new
  automated compatibility sweep. (#4)
- Declared minimum dependency versions, previously unbounded:
  `matplotlib >= 3.5.0` (required for `Axis.set_xticks(..., labels=...)`),
  `numpy >= 1.17.0`, and `python-dateutil >= 2.7.0`. (#4)

### Added
- Multi-version compatibility test suite: a nox session matrix covering
  CPython 3.8–3.14 against both lowest-supported and newest dependency
  resolutions, plus a pytest smoke-test suite. (#4)

### Packaging
- Fixed the `license_files` reference in `setup.cfg` (pointed at the old
  `LICENSE.txt` filename), so the license text is again included in wheels.

## [1.0.1] - 2025-06-16

### Changed
- Documentation and packaging-metadata cleanups (README image links,
  classifier corrections). No functional changes.

## [1.0.0] - 2025-06-16

### Added
- Initial public release: Shewhart statistical process control charts
  (X̅-R, X̅-S, CUSUM, and P-attribute) with Western Electric rule checking,
  matplotlib rendering, CSV example data, and the `pyshewhart` command-line
  entry point.

[1.1.0]: https://github.com/huft-jonathan/pyshewhart/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/huft-jonathan/pyshewhart/releases/tag/1.0.1
