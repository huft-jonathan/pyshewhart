#!/usr/bin/env python

"""
Re-create an X̅ and R chart from a textbook example.

From "Managing Quality: Integrating the Supply Chain" by S. Thomas Foster, 5th
edition, re-create Figure 11-8 based on the sample measurements provided in the
table on page 287.

The resulting plot will show an out-of-control mean in the third sample and two
out-of-control ranges at samples 22 and 25.
"""

import matplotlib.pyplot as plt
import pyshewhart


plt.style.use("classic")  # Use a different Matplotlib style just for fun..

# fmt: off
measured_sizes = [
    24, 27, 28, 33, 29, 30, 29, 31, 38, 42, 36, 35, 24, 28, 27, 32,
    33, 36, 31, 28, 28, 28, 28, 28, 30, 28, 27, 26, 19, 26, 23, 22,
    24, 27, 33, 28, 26, 27, 38, 26, 25, 26, 27, 28, 28, 24, 29, 30,
    31, 26, 38, 24, 30, 31, 33, 32, 26, 25, 24, 36, 24, 36, 24, 36,
    25, 35, 25, 35, 26, 30, 28, 32, 27, 31, 29, 33, 28, 33, 30, 34,
    24, 24, 32, 32, 18, 42, 36, 30, 29, 30, 31, 28, 20, 36, 34, 32,
    14, 25, 36, 35]
# fmt: on


def main():

    cc = pyshewhart.XbarRControlChart(
        measured_sizes,
        sample_size=4,
        units="Unspecified Units",
        suptitle="Figure 11-8 from Foster Text",
        title="Grommet Size",
    )

    print("Is the process in control?")
    print("Yes" if cc.in_control else "No")
    input("Enter to close plots and exit.")


if __name__ == "__main__":
    main()
