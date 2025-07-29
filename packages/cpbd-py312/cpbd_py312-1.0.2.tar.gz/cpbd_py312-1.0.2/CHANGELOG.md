# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-06-23 - cpbd-py312

### Fixed
- Fixed PyPI description by using README.md instead of README.rst
- Updated author information to nawta

## [1.0.1] - 2025-06-23 - cpbd-py312

### Changed
- Updated project description and documentation
- Limited Python version support to 3.12+ only (removed untested 3.8-3.11)
- Updated homepage URL to https://github.com/nawta/python-cpbd-py312

## [1.0.0] - 2025-06-23 - cpbd-py312

### Added
- Forked as `cpbd-py312` for Python 3.12+ compatibility
- Support for Python 3.8, 3.9, 3.10, 3.11, and 3.12
- `pyproject.toml` for modern Python packaging (PEP 517/518)
- `imageio` dependency for image reading
- Command line interface improvements
- Comprehensive README.md documentation

### Changed
- Replaced deprecated `scipy.ndimage.imread` with `imageio.v2.imread`
- Updated minimum dependency versions:
  - matplotlib >= 3.5.0 (was >= 2.0.0)
  - numpy >= 1.21.0 (was >= 1.11.1)
  - scikit-image >= 0.19.0 (was >= 0.12.3)
  - scipy >= 1.7.0 (was >= 0.18.1)
- Modernized test configuration with tox

### Removed
- Python 2.7, 3.5, and 3.6 support
- `__future__` imports and Python 2 compatibility code
- Legacy Python 2/3 compatibility shims

### Fixed
- Compatibility issues with modern Python versions
- Deprecated API warnings

## [1.0.7] - Previous Release

### Notes
- Last version supporting Python 2.7
- Original implementation details preserved