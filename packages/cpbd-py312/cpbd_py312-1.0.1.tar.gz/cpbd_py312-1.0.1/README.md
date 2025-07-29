# cpbd-py312

[![PyPI version](https://badge.fury.io/py/cpbd-py312.svg)](https://badge.fury.io/py/cpbd-py312)
[![Python](https://img.shields.io/pypi/pyversions/cpbd-py312.svg)](https://pypi.org/project/cpbd-py312/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE.txt)

A Python 3.12+ compatible fork of the Cumulative Probability of Blur Detection (CPBD) image sharpness metric. This fork modernizes the original python-cpbd package with updated dependencies and removes deprecated functionality.

## About

`cpbd-py312` is a modernized fork of the original [python-cpbd](https://github.com/0x64746b/python-cpbd) package, specifically updated to work with Python 3.12 and newer versions. This package implements the Cumulative Probability of Blur Detection (CPBD) metric for no-reference image sharpness assessment.

CPBD is a perceptual-based metric that quantifies image sharpness without requiring a reference image. It estimates the probability of blur detection at each edge in an image and computes the cumulative probability to provide an overall sharpness score.

### Key Updates in This Fork
- **Python 3.12 Compatibility**: Full support for Python 3.12
- **Modern Dependencies**: Updated to use `imageio` instead of deprecated `scipy.ndimage.imread`
- **Streamlined Codebase**: Removed Python 2 compatibility code and legacy imports
- **Modern Packaging**: Uses `pyproject.toml` for PEP 517/518 compliant packaging

## Installation

```bash
pip install cpbd-py312
```

## Quick Start

```python
from cpbd import compute
from imageio.v2 import imread
from skimage.color import rgb2gray

# Load image
image = imread('path/to/image.png')

# Convert to grayscale if needed
if len(image.shape) == 3:
    image = rgb2gray(image)

# Calculate CPBD
cpbd_value = compute(image)
print(f'CPBD sharpness: {cpbd_value:.6f}')
```

Higher values indicate sharper images. The CPBD value ranges from 0 (very blurry) to 1 (very sharp).

## Command Line Usage

You can also run CPBD from the command line:

```bash
python -m cpbd.compute path/to/image.png
```

## Recent Updates (v1.0.0)

### Python 3.12 Support
- Confirmed support for Python 3.12
- Dropped support for Python 2.7, 3.5, and 3.6
- Replaced deprecated `scipy.ndimage.imread` with `imageio.v2.imread`
- Removed `__future__` imports and Python 2 compatibility code
- Added modern `pyproject.toml` for PEP 517/518 compliance

### Updated Dependencies
- matplotlib >= 3.5.0
- numpy >= 1.21.0  
- scikit-image >= 0.19.0
- scipy >= 1.7.0
- imageio >= 2.9.0

## Development

### Setup

```bash
git clone https://github.com/nawta/python-cpbd-py312.git
cd python-cpbd-py312
pip install -e '.[dev]'
```

### Testing

```bash
# Run tests with current Python version
python setup.py test

# Test with Python 3.12
pytest
```

## Performance

The following graph shows the accuracy of this implementation compared to the reference MATLAB implementation when tested on the [LIVE Image Quality Assessment Database](http://live.ece.utexas.edu/research/quality/subjective.htm):

The implementation maintains compatibility with the original MATLAB reference implementation, providing consistent results for image sharpness assessment.

## References

If you use this code in your research, please cite:

- N. D. Narvekar and L. J. Karam, "A No-Reference Image Blur Metric Based on the Cumulative Probability of Blur Detection (CPBD)," IEEE Transactions on Image Processing, vol. 20, no. 9, pp. 2678-2683, Sept. 2011.
- N. D. Narvekar and L. J. Karam, "An Improved No-Reference Sharpness Metric Based on the Probability of Blur Detection," International Workshop on Video Processing and Quality Metrics for Consumer Electronics (VPQM), January 2010.

## License

See [LICENSE.txt](LICENSE.txt) for details. Please note the copyright statement of the original MATLAB implementation.