#!/usr/bin/env python

"""
Module containing classes to create various types of control charts.
"""


from abc import ABC, abstractmethod
import datetime
import functools
import math

import matplotlib
import matplotlib.pyplot as plt

from . import constants
from . import data_types

# pylint: disable=too-few-public-methods,too-many-arguments

mpl_date = matplotlib.dates.date2num


class _ABC(ABC):
    """"""

    # ABC has a docstring that appears in 'pdoc' documentation,
    # so simply override it to avoid confusion.


class _ControlChartBaseClass(_ABC):

    suptitle_fontsize = 20
    title_fontsize = 12
    axis_label_fontsize = 14
    figsize = (12, 8)

    def __init__(
        self,
        series1=None,
        series2=None,
        sample_size=5,
        record=None,
        suptitle="",
        title="",
    ):
        """
        Parameters
        ----------
        series1 : list
            Either:
             a list of measurements if `series2` is not provided, or
             a list of times.
        series2 : list
            A list of measurements (if provided `series1` must be times).
        sample_size : int, optional
            Number of measurements comprising a sample.
        record : data_types.Record, optional
            A fully-defined record containing the data (`series1` and
            `series2` must not be provided).
        suptitle : str, optional
            Overall title for the plot.
        title : str, optional
            Title for the first subplot.
        """

        if record is not None:
            if series1 is not None or series2 is not None:
                raise Exception(
                    "Cannot specify 'series1', 'series2' at the same time as 'record'."
                )
            assert isinstance(record, data_types.Record)
            self.record = record
        else:
            if series1 is not None:
                if series2 is not None:
                    times = series1
                    values = series2
                else:
                    times = [None for _ in series1]
                    values = series1
            else:
                raise Exception("Must specify some data!")

            self.record = data_types.import_times_values(
                times=times, values=values, sample_size=int(sample_size)
            )

        self.suptitle = suptitle
        self.title = title

        self._in_control = True
        self.fig = None
        self.ax1 = None

        self._init_plot()
        self._plot()
        self._finish_plot()

    # Plotting _________________________________________________________________
    def _init_plot(
        self,
    ):
        self.fig = plt.figure(figsize=self.figsize, constrained_layout=True)
        self.fig.suptitle(self.suptitle, size=self.suptitle_fontsize)

    @abstractmethod
    def _plot(self):
        pass

    def _finish_plot(self):
        if not self.in_control:
            plt.figtext(
                x=0.5,
                y=0.5,
                s="Not In Control",
                color="Red",
                alpha=0.4,
                size=48,
                verticalalignment="center",
                horizontalalignment="center",
                rotation=30,
            )

        plt.figtext(
            x=0.02, y=0.02, s="Created with pyshewhart", color="Gray", alpha=0.5, size=6
        )

        if "backend_inline" not in matplotlib.get_backend():
            self.fig.show()

    # Misc _____________________________________________________________________
    def _add_line_annotation(self, ax, axb, y, label, linecolor=None, linewidth=1):
        ax.axhline(y, color=linecolor, lw=linewidth)

        ticks = list(axb.get_yticks())
        ticks.append(y)

        labels = axb.get_yticklabels()
        labels.append(label)

        axb.set_yticks(ticks)
        axb.set_yticklabels(labels)

    def _format_subplot(self, ax, label):
        ax.set_ylabel(label, fontsize=self.axis_label_fontsize)

    def _plot_data_series(self, ax, y, label_top=False, label_bottom=False):

        def get_sample_ticks():
            return list(range(0, len(self.record), max(5, len(self.record) // 20)))

        if not self.record.has_time_info:
            # Simply use sample numbers on the bottom
            if label_bottom:
                ax.set_xlabel("Sample Number", size=self.axis_label_fontsize)
            self._plot_timescaled(ax, y, marker="o", linestyle=":")
            ax.grid(axis="x", linestyle=":")

        else:
            # If we have time info, we put time on the bottom and sample number
            # on the top.
            ax2 = ax.twiny()
            if label_top:
                ax2.set_xlabel("Sample Number", size=self.axis_label_fontsize)

            if isinstance(self.record.times[0], datetime.timedelta):
                if label_bottom:
                    ax.set_xlabel(
                        "Elapsed Time (Seconds)", size=self.axis_label_fontsize
                    )
                self._plot_timescaled(ax, y, marker="o", linestyle=":")
                # TODO: Don't double-plot.. just scale the second axis appropriately
                self._plot_timescaled(ax2, y, marker="o", linestyle=":")

                x_times = [
                    self.record.samples[i].time.total_seconds()
                    for i in get_sample_ticks()
                ]

            elif isinstance(self.record.times[0], datetime.datetime):
                if label_bottom:
                    ax.set_xlabel("Date / Time", size=self.axis_label_fontsize)

                self._plot_timescaled(ax, y, linestyle=":")
                # TODO: Don't double-plot.. just scale the second axis appropriately
                self._plot_timescaled(ax2, y, linestyle=":")

                x_times = [self.record.samples[i].time for i in get_sample_ticks()]

            else:
                raise data_types.TimeException(
                    f"Plotting times of type {type(self.record.times[0])} "
                    f"is not supported."
                )

            ax2.set_xticks(x_times, labels=get_sample_ticks())

            ax.grid(axis="x", alpha=0.5, linestyle=":")
            ax2.grid(axis="x", alpha=1.0, linestyle=":")

    def _plot_timescaled(self, ax, y, **kwargs):
        if not self.record.has_time_info:
            ax.plot(list(range(len(self.record))), y, **kwargs)
        elif isinstance(self.record.times[0], datetime.timedelta):
            ax.plot([t.total_seconds() for t in self.record.times], y, **kwargs)
        elif isinstance(self.record.times[0], datetime.datetime):
            ax.plot_date(mpl_date(self.record.times), y, **kwargs)
        else:
            raise data_types.TimeException("Don't know how to plot that...")

    @property
    def in_control(self):
        return self._in_control


class _Variable_ControlChartBaseClass(_ControlChartBaseClass):

    def __init__(self, *args, units="", check_western_elec_rules=True, **kwargs):
        str(super().__doc__) + (  # pylint: disable=no-member, expression-not-assigned
            """
        Parameters
        ----------
        units : str
            Units of the data.
        check_western_elec_rules : bool
            Check if samples are in violation of the "Western Electric"
            statistical rules.
        """
        )

        self.units = units
        self.check_western_elec_rules = check_western_elec_rules
        self._passing_western_elec_rules = True

        self.ax2 = None

        super().__init__(*args, **kwargs)

    @property
    def passing_western_elec_rules(self):
        return self._passing_western_elec_rules

    @property
    def in_control(self):
        return self._in_control and self.passing_western_elec_rules

    def _add_reference_lines(self, ax, mean, lcl, ucl):
        axb = ax.twinx()
        axb.set_yticks([])

        aa = functools.partial(self._add_line_annotation, ax=ax, axb=axb)

        aa(y=mean, label=f"Mean: {mean:5.3f}", linecolor="Black")

        aa(y=ucl, label=f"UCL: {ucl:5.3f}", linecolor="Red")
        aa(y=lcl, label=f"LCL: {lcl:5.3f}", linecolor="Red")

        aa(y=(ucl - mean) / 3 + mean, label="+1σ", linewidth=0.3)
        aa(y=(lcl - mean) / 3 + mean, label="-1σ", linewidth=0.3)

        aa(y=(ucl - mean) * 2 / 3 + mean, label="+2σ", linewidth=0.3)
        aa(y=(lcl - mean) * 2 / 3 + mean, label="-2σ", linewidth=0.3)

        axb.set_ylim(ax.get_ylim())

    @property
    def _unit_str(self):
        """For axis labels."""
        return f" ({self.units })" if self.units else ""

    @abstractmethod
    def _plot(self):
        pass

    def _plot_means(self):
        self.ax1.set_title(self.title, fontsize=self.title_fontsize)
        self._format_subplot(self.ax1, "Means" + self._unit_str)
        self._plot_data_series(self.ax1, self.record.means, label_top=True)

        if self.check_western_elec_rules:
            self._western_electric_rules()

        # Use mean of sample ranges
        ucl = self.record.mean_of_means + self._A2r
        lcl = self.record.mean_of_means - self._A2r

        self._add_reference_lines(
            ax=self.ax1, mean=self.record.mean_of_means, lcl=lcl, ucl=ucl
        )

        self._check_if_in_control(self.record.means, lcl, ucl)

    def _western_electric_rules(self):
        """
        Determine which samples of a record are in violation
        of the common "Western Electric" control chart rules.
        """

        def two_of_three_consecutive_outside_two_sigma_limits():
            ucl = self.record.mean_of_means + self._A2r * 2.0 / 3.0
            lcl = self.record.mean_of_means - self._A2r * 2.0 / 3.0
            return indices_of_m_out_of_tol_in_n(2, 3, lcl, ucl)

        def four_of_five_consecutive_outside_one_sigma_limits():
            ucl = self.record.mean_of_means + self._A2r / 3.0
            lcl = self.record.mean_of_means - self._A2r / 3.0
            return indices_of_m_out_of_tol_in_n(4, 5, lcl, ucl)

        def eight_consecutive_above_or_below_mean():
            ucl = self.record.mean_of_means
            lcl = self.record.mean_of_means
            return indices_of_m_out_of_tol_in_n(8, 8, lcl, ucl)

        def indices_of_m_out_of_tol_in_n(m, n, lcl, ucl):
            indices = []
            for i in range(n, len(self.record.means) + 1):
                series = self.record.means[i - n : i]
                for ineq, lim in [["lt", lcl], ["gt", ucl]]:
                    ooti = out_of_tol_indices(series, ineq=ineq, lim=lim)
                    if len(ooti) > m:
                        # Compute the total indices
                        ooti = [j + i - n for j in ooti]
                        indices += ooti

            return set(indices)

        def out_of_tol_indices(series, ineq="gt", lim=0.0):
            """
            Get the indices of list elements that are out of tolerance.
            """
            indices = []
            for i, val in enumerate(series):
                if ineq == "lt":
                    if val < lim:
                        indices.append(i)
                if ineq == "gt":
                    if val > lim:
                        indices.append(i)
            return indices

        need_legend = False
        for f in [
            two_of_three_consecutive_outside_two_sigma_limits,
            four_of_five_consecutive_outside_one_sigma_limits,
            eight_consecutive_above_or_below_mean,
        ]:

            rule_name = f.__name__.replace("_", " ").title()
            violator_indices = sorted(f())

            if len(violator_indices) > 0:
                self._passing_western_elec_rules = False

                print(f'Out of control points were detected using rule "{rule_name}":')
                for i in violator_indices:
                    print(f"{i}: ", end="")
                    print(self.record.samples[i])
                print()

                violator_means = [self.record.means[i] for i in violator_indices]

                if not self.record.has_time_info:
                    self.ax1.scatter(
                        list(violator_indices),
                        violator_means,
                        s=150,
                        alpha=0.5,
                        label=rule_name,
                    )
                else:
                    violator_times = [self.record.times[i] for i in violator_indices]
                    if isinstance(self.record.times[0], datetime.timedelta):
                        self.ax1.scatter(
                            [t.total_seconds() for t in violator_times],
                            violator_means,
                            s=150,
                            alpha=0.5,
                            label=rule_name,
                        )
                    elif isinstance(self.record.times[0], datetime.datetime):
                        self.ax1.scatter(
                            mpl_date(violator_times),
                            violator_means,
                            s=150,
                            alpha=0.5,
                            label=rule_name,
                        )

                need_legend = True

        if need_legend:
            self.ax1.legend()

    # Misc _____________________________________________________________________
    @property
    def _A2r(self):
        # Used in many places, so just define here to minimize repetition
        return constants.A2[self.record.sample_size] * self.record.mean_of_ranges

    def _check_if_in_control(self, arr, lcl, ucl):
        for v in arr:
            if not lcl <= v <= ucl:
                self._in_control = False


class XbarRControlChart(_Variable_ControlChartBaseClass):

    def _plot(self):
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        self._plot_means()

        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self._plot_ranges()

    def _plot_ranges(self):
        self._format_subplot(self.ax2, "Ranges" + self._unit_str)
        self._plot_data_series(
            self.ax2, self.record.ranges, label_bottom=not hasattr(self, "ax3")
        )

        ucl = self.record.mean_of_ranges * constants.D4[self.record.sample_size]
        lcl = self.record.mean_of_ranges * constants.D3[self.record.sample_size]

        self._add_reference_lines(self.ax2, self.record.mean_of_ranges, lcl, ucl)

        self._check_if_in_control(self.record.ranges, lcl, ucl)


class XbarSControlChart(_Variable_ControlChartBaseClass):

    def _plot(self):
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        self._plot_means()

        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self._plot_stdevs()

    def _plot_stdevs(self):
        self._format_subplot(self.ax2, "Std. Deviations" + self._unit_str)
        self._plot_data_series(
            self.ax2, self.record.stdevs, label_bottom=not hasattr(self, "ax3")
        )

        ucl = self.record.mean_of_stdevs * constants.B4[self.record.sample_size]
        lcl = self.record.mean_of_stdevs * constants.B3[self.record.sample_size]

        self._add_reference_lines(
            ax=self.ax2, mean=self.record.mean_of_stdevs, lcl=lcl, ucl=ucl
        )

        self._check_if_in_control(self.record.stdevs, lcl, ucl)


class CUSUMControlChart(XbarRControlChart):

    figsize = (12, 12)

    def __init__(self, *args, cusum_target, **kwargs):
        self.cusum_target = cusum_target
        self._cusum_k = 0.5
        self._cusum_h = 4.0
        self.ax3 = None
        super().__init__(*args, **kwargs)

    def _plot(self):

        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self._plot_means()

        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self._plot_ranges()

        self.ax3 = self.fig.add_subplot(3, 1, 3)
        self._plot_cusum()

    def _plot_cusum(self):
        self._format_subplot(self.ax3, "CUSUM")

        # Adjust sample stdev to estimated population stdev
        sigma = self.record.mean_of_stdevs * constants.A3[self.record.sample_size] / 3.0

        # Compute cumulative sums
        su, sl = [0], [0]
        for x in self.record.means:
            su.append(max(0, x - self.cusum_target - self._cusum_k * sigma + su[-1]))
            sl.append(min(0, x - self.cusum_target + self._cusum_k * sigma + sl[-1]))
        # Trim the first zeros off..
        su = su[1:]
        sl = sl[1:]

        self._plot_data_series(self.ax3, su, label_bottom=True)
        self._plot_data_series(self.ax3, sl, label_bottom=True)

        ucl = self._cusum_h * sigma
        lcl = -1.0 * ucl

        self._add_reference_lines(ax=self.ax3, mean=0, lcl=lcl, ucl=ucl)

        self._check_if_in_control(sl, lcl, ucl)
        self._check_if_in_control(su, lcl, ucl)


class PAttributeControlChart(_ControlChartBaseClass):

    def _plot(self):
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.ax1.set_title(self.title, fontsize=16)

        self._format_subplot(self.ax1, "Proportion")
        self._plot_data_series(
            self.ax1,
            self.record.proportions_defective,
            label_top=True,
            label_bottom=True,
        )

        mean_p = self.record.mean_proportion_defective

        axb = self.ax1.twinx()
        axb.set_ylim(self.ax1.get_ylim())
        axb.set_yticks([])
        self._add_line_annotation(self.ax1, axb, y=mean_p, label=f"Mean: {mean_p:5.3f}")

        # Compute upper and lower control lims
        ucl, lcl = [], []
        for s in self.record.samples:
            n = len(s.measurements)  # Sample size
            q = 3 * math.sqrt(mean_p * (1 - mean_p) / n)
            ucl.append(mean_p + q)
            lcl.append(max(0, mean_p - q))

        self._plot_timescaled(
            self.ax1, ucl, marker="_", markersize=16, lw=0, color="Red"
        )

        self._plot_timescaled(
            self.ax1, lcl, marker="_", markersize=16, lw=0, color="Red"
        )

        self._check_if_in_control(self.record.proportions_defective, lcl, ucl)

    def _check_if_in_control(self, arr, lcl, ucl):
        for a, l, u in zip(arr, lcl, ucl):
            if not l <= a <= u:
                self._in_control = False
        return self.in_control
