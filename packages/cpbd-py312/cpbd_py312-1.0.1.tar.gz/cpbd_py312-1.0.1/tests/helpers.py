# coding: utf-8

# Python 3.12+ doesn't need __future__ imports

import numpy as np


def parse_matlab_data(file_path, dtype=np.float64):
    """Parse an array written with `dlmwrite`."""
    data = []
    with open(file_path) as f:
        for line in f.readlines():
            data.append(line.strip('\n').split(','))

    return np.array(data, dtype=dtype)

