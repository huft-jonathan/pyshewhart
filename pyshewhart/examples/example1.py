#!/usr/bin/env python

"""
Demonstrate all the ways that time info can be supplied.
"""

import datetime
import time
import random
import pyshewhart


def main():

    kwargs = {"units": "Volts", "check_western_elec_rules": False}

    measurements = [random.normalvariate(mu=0, sigma=0.02) for _ in range(200)]

    # Plot #1 __________________________________________________________________
    pyshewhart.XbarSControlChart(
        measurements, suptitle="No Time Info Provided", **kwargs
    )

    # Plot #2 __________________________________________________________________
    period = 60 * 60 * 8  # Eight hours
    elapsed_times = [period * i for i in range(len(measurements))]
    pyshewhart.XbarSControlChart(
        elapsed_times, measurements, suptitle="Time Provided as Elapsed Times", **kwargs
    )

    # Plot #3 __________________________________________________________________
    timestamps = [time.time()]
    for i in range(1, len(measurements)):
        timestamps.append(
            timestamps[i - 1] + 60 * 60 * 8 * random.lognormvariate(mu=0, sigma=1.6)
        )
    pyshewhart.XbarSControlChart(
        timestamps,
        measurements,
        suptitle="Timestamps From Measurements Taken At Irregular Intervals",
        **kwargs
    )

    # Plot #4 __________________________________________________________________
    datetimes = [datetime.datetime.now()]
    for i in range(1, len(measurements)):
        datetimes.append(datetimes[i - 1] + datetime.timedelta(days=1))
    pyshewhart.XbarSControlChart(
        datetimes, measurements, suptitle="Time Provided as Datetimes", **kwargs
    )

    # Plot #5 __________________________________________________________________
    str_dts = [dt.isoformat() for dt in datetimes]
    pyshewhart.XbarSControlChart(
        str_dts, measurements, suptitle="Time Provided as Strings", **kwargs
    )

    input("Enter to close plots and exit.")


if __name__ == "__main__":
    main()
