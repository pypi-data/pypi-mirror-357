# cpbd-py312

[![PyPI version](https://badge.fury.io/py/cpbd-py312.svg)](https://badge.fury.io/py/cpbd-py312)
[![Python](https://img.shields.io/pypi/pyversions/cpbd-py312.svg)](https://pypi.org/project/cpbd-py312/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE.txt)

Python implementation of the Cumulative Probability of Blur Detection (CPBD) sharpness metric, updated for Python 3.12+ compatibility.

## About

CPBD is a perceptual-based no-reference objective image sharpness metric based on the cumulative probability of blur detection developed at the Image, Video and Usability Laboratory of Arizona State University.

> [The metric] is based on the study of human blur perception for varying contrast values. The metric utilizes a probabilistic model to estimate the probability of detecting blur at each edge in the image, and then the information is pooled by computing the cumulative probability of blur detection (CPBD).

This is a Python port of the [reference MATLAB implementation](http://lina.faculty.asu.edu/Software/CPBDM/CPBDM_Release_v1.0.zip). It supports Python 3.8 through 3.12.

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
- Added support for Python 3.8, 3.9, 3.10, 3.11, and 3.12
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
git clone https://github.com/0x64746b/python-cpbd.git
cd python-cpbd
pip install -e '.[dev]'
```

### Testing

```bash
# Run tests with current Python version
python setup.py test

# Test across Python versions  
tox
```

## Performance

The following graph shows the accuracy of this implementation compared to the reference MATLAB implementation when tested on the [LIVE Image Quality Assessment Database](http://live.ece.utexas.edu/research/quality/subjective.htm):

![Performance on LIVE database](https://raw.githubusercontent.com/0x64746b/python-cpbd/master/tests/data/performance_LIVE.png)

## References

If you use this code in your research, please cite:

- N. D. Narvekar and L. J. Karam, "A No-Reference Image Blur Metric Based on the Cumulative Probability of Blur Detection (CPBD)," IEEE Transactions on Image Processing, vol. 20, no. 9, pp. 2678-2683, Sept. 2011.
- N. D. Narvekar and L. J. Karam, "An Improved No-Reference Sharpness Metric Based on the Probability of Blur Detection," International Workshop on Video Processing and Quality Metrics for Consumer Electronics (VPQM), January 2010.

## License

See [LICENSE.txt](LICENSE.txt) for details. Please note the copyright statement of the original MATLAB implementation.