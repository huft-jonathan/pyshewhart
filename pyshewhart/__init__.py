#!/usr/bin/env python

import argparse
import sys

from .control_charts import *
from . import data_types

XbarR = XbarRControlChart
XbarS = XbarSControlChart
CUSUM = CUSUMControlChart
PAttribute = PAttributeControlChart


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_file",
        type=str,
        help="Specify the name of a CSV file consisting of timeseries and "
        "variable data.",
    )

    parser.add_argument("type", choices=["xbar-r", "xbar-s", "cusum", "attribute"])

    parser.add_argument(
        "sample_size",
        type=int,
        help='Specify the number of data points per statistical "sample".',
    )

    parser.add_argument("-c", "--cusum-target", type=float, default=False)

    parser.add_argument(
        "-w",
        "--we-rules",
        action="store_true",
        help="Evaluate the data against the Western Electric rule set.",
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="Unknown Data",
        help="Specify the plot title.",
    )

    parser.add_argument(
        "-u", "--units", type=str, default=None, help="Specify the units of the data."
    )

    args = parser.parse_args()

    t, v = data_types.import_csv_to_arrays(args.csv_file)
    r = data_types.import_times_values(times=t, values=v, sample_size=args.sample_size)

    print(r)

    if args.type == "xbar-r":
        in_control = XbarRControlChart(
            record=r,
            units=args.units,
            suptitle=args.title,
            check_western_elec_rules=args.we_rules,
        )

    elif args.type == "xbar-s":
        in_control = XbarSControlChart(
            record=r,
            units=args.units,
            suptitle=args.title,
            check_western_elec_rules=args.we_rules,
        )

    elif args.type == "cusum":
        in_control = CUSUMControlChart(
            record=r,
            units=args.units,
            cusum_target=args.cusum_target,
            suptitle=args.title,
            check_western_elec_rules=args.we_rules,
        )

    elif args.type == "attribute":
        in_control = PAttributeControlChart(record=r, suptitle=args.title)

    else:
        raise Exception

    input("Enter to close plots and exit.")

    return 0 if in_control else 100
