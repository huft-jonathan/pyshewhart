#!/usr/bin/env python

"""
Demonstrate using a CUSUM chart to monitor a process with small amounts of
drift.
"""

import random
import matplotlib.pyplot as plt
import pyshewhart

plt.style.use("seaborn-v0_8-bright")


def get_measurements(mean=10, drift=False):
    n = 200
    measurements = [random.gauss(mu=mean, sigma=0.02) for _ in range(n)]
    if drift:
        for i in range(n // 2, n):  # Begin drifting halfway through
            max_drift = mean * 1.002
            measurements[i] += min((i - n // 2) * 0.0001, max_drift)
    return measurements


def main():
    for drift in [False, True]:
        mean = 10.0
        pyshewhart.CUSUMControlChart(
            get_measurements(mean=mean, drift=drift),
            sample_size=8,
            cusum_target=mean,
            units="Volts",
            suptitle="Calibration Control Chart",
            title="Simulated drifty data." if drift else "Simulated normal data.",
            check_western_elec_rules=True,
        )

    input("Enter to close plots and exit.")


if __name__ == "__main__":
    main()
