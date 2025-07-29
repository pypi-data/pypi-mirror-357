# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of the Cumulative Probability of Blur Detection (CPBD) metric - a no-reference image sharpness assessment algorithm. It measures image quality by quantifying blur levels without requiring a reference image.

## Key Commands

### Testing
- Run tests: `python setup.py test`
- Multi-version testing: `tox` (tests on Python 2.7, 3.5, 3.6)
- Run specific test: `python -m pytest tests/test_compute.py::TestCompute::test_specific_method`

### Development Setup
- Install with dev dependencies: `pip install -U '.[dev]'`
- Run algorithm on image: `python -m cpbd.compute <image_path>`

## Architecture Overview

### Core Algorithm Flow
1. **Edge Detection**: Canny edge detection identifies edge pixels
2. **Edge Width Calculation**: Marziliano method traces perpendicular to edges to measure blur width
3. **JNB Application**: Just Noticeable Blur thresholds adjust based on local contrast
4. **Probability Computation**: Blur detection probability calculated for each edge
5. **Final Metric**: Cumulative probability up to 64% confidence level

### Key Implementation Details
- **Block Processing**: Images processed in 64x64 pixel blocks
- **Custom Sobel**: `cpbd/octave.py` implements Octave-compatible Sobel edge detection
- **Contrast Ranges**: 5 contrast levels with different JNB widths (50-80% confidence)
- **Edge Threshold**: Minimum of 0.0001 edges/pixel for valid blocks

### Critical Files
- `cpbd/compute.py`: Main algorithm implementation with `compute()` function
- `cpbd/octave.py`: Sobel edge detection matching MATLAB/Octave behavior
- `tests/data/`: Reference outputs from MATLAB implementation for validation

### Testing Considerations
- Tests validate against MATLAB reference implementation outputs
- Floating-point precision differences may occur between Python/MATLAB
- Test data includes pre-computed CPBD values for LIVE database images