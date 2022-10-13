#!/usr/bin/env python

"""
Minimal example.
"""

import random
import pyshewhart


if __name__ == "__main__":

    measurements = [random.gauss(mu=1.0, sigma=0.02) for _ in range(200)]
    pyshewhart.XbarS(measurements)

    input("Enter to close plots and exit.")
