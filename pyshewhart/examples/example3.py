#!/usr/bin/env python

"""
Re-create an attribute chart from a textbook example.

From "Managing Quality: Integrating the Supply Chain" by S. Thomas Foster, 5th
edition, re-create Example 12-1 based on the data provided in the table on page
316.

The resulting chart should show that the process is not in control.

Note that using control charts to monitor the outcome of court cases, as Foster
does in this example, seems ethically questionable.
"""


import random
import matplotlib.pyplot as plt
from pyshewhart.data_types import Sample, Measurement, Record
import pyshewhart

plt.style.use("grayscale")


def get_example_data_foster_12_1():
    # fmt: off
    # Number of cases reviewed
    case_counts = [
        100, 95, 110, 142, 100, 98, 76, 125, 100, 125, 111, 116,
        92, 98, 162, 87, 105, 110, 98, 96, 100, 100, 97, 122,
        125, 110, 100]

    # Number of convictions
    conviction_counts = [
        60, 65, 68, 62, 56, 58, 30, 68, 54, 62, 70, 58,
        30, 68, 54, 62, 70, 58, 30, 68, 54, 62, 70, 58,
        30, 68, 54]
    # fmt: on

    r = Record()

    # Get samples of randomly arranged measurements containing the
    # corresponding numbers of cases and convictions
    for num_cases, num_convictions in zip(case_counts, conviction_counts):
        r.append(get_randomized_sample(num_cases, num_convictions))
    return r


def get_randomized_sample(num_cases, num_convictions):
    """
    The text only gives the numbers of cases and convictions per "sample",
    so this function generates semi-random underlying data that matches
    those numbers.
    """
    sequence = num_convictions * [1] + (num_cases - num_convictions) * [0]

    # Shuffle the list. (Not strictly necessary..)
    sequence = random.sample(sequence, len(sequence))

    s = Sample()
    for value in sequence:
        s.append(Measurement(value=value, is_attribute=True))
    return s


def main():

    cc = pyshewhart.PAttributeControlChart(
        record=get_example_data_foster_12_1(),
        suptitle="Example 12-1 from Foster Text",
        title="Conviction Rate",
    )

    print("Is the process in control?")
    print("Yes" if cc.in_control else "No")

    input("Enter to close plots and exit.")


if __name__ == "__main__":
    main()
