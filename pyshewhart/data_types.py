#!/usr/bin/env python

"""
Defines the data structures that control charts are based on.

The hierarchy is as follows:

```
Record
    Sample 0
        Measurement 0
        Measurement 1
        Measurement 2
        Measurement 3
    Sample 1
        Measurement 0
        Measurement 1
        Measurement 2
        Measurement 3
    ...
    Sample N
        Measurement 0
        Measurement 1
        Measurement 2
        Measurement 3
```
"""

from functools import cached_property
import time as time_module
import datetime
import csv

import dateutil
import numpy

# Numbers less than this will be interpreted as timedeltas.
# Numbers greater will be interpreted as timestamps.
MINIMUM_TIMESTAMP = 650000000  # Approx 1990


def _sample_standard_deviation(x):
    """Not the population standard deviation!"""
    return numpy.std(x, ddof=1)


class ImportException(Exception):
    pass


class TimeException(Exception):
    pass


class Value:
    """
    Either a "variable" (continuous) value or an attribute (boolean) value.
    """

    def __init__(self, value, is_attribute=False):
        self._is_attribute = is_attribute
        if self.is_attribute:
            value = int(value)
            assert value in (0, 1)
        self.value = value

    @property
    def is_variable(self):
        return not self._is_attribute

    @property
    def is_attribute(self):
        return self._is_attribute


class Measurement(Value):
    """
    Measurements consist of a value and optionally the time when the
    value was observed.
    """

    def __init__(self, value, time=None, is_attribute=False):
        super().__init__(value=value, is_attribute=is_attribute)

        if isinstance(time, str):
            try:
                time = float(time)
            except ValueError:
                time = dateutil.parser.parse(time)

        if time is None:
            self.time = None
        elif isinstance(time, (datetime.timedelta, datetime.datetime)):
            self.time = time
        elif isinstance(time, (float, int)):
            if time > MINIMUM_TIMESTAMP:
                self.time = datetime.datetime.fromtimestamp(time)
            else:
                self.time = datetime.timedelta(seconds=time)
        else:
            raise TypeError(
                f"Unable to convert {time} of type {type(time)}to a valid time."
            )

    def __str__(self):
        s = self.__class__.__name__ + "\n"
        if self.time is not None:
            s += f"    {self.time}\n"
        if self.is_variable:
            s += f"    {self.value}"
        else:
            d = "Defective" if self.value else "Good"
            s += f"    {d}"
        return s


class Sample:
    """
    Samples are collections of measurements.
    """

    def __init__(self, measurements=None):
        self._measurements = []
        if measurements is not None:
            self.append(measurements)

    def append(self, meausurements):
        self._measurements += self._normalize(meausurements)

        # Make sure we have all variable data or all attribute data..
        assert all(
            m.is_variable == self._measurements[0].is_variable
            for m in self._measurements
        )

        for cached in ["mean", "range", "stdev"]:
            if cached in self.__dict__:
                del self.__dict__[cached]

    @staticmethod
    def _normalize(measurements):
        if isinstance(measurements, Measurement):
            ml = [measurements]
        else:
            ml = list(measurements)
        assert len(ml) > 0
        for m in ml:
            assert isinstance(m, Measurement)
        return ml

    @property
    def size(self):
        return len(self.measurements)

    @property
    def measurements(self):
        return self._measurements

    @property
    def values(self):
        return [m.value for m in self.measurements]

    @property
    def times(self):
        return [m.time for m in self.measurements]

    @property
    def is_variable(self):
        return self._measurements[0].is_variable

    @property
    def is_attribute(self):
        return self._measurements[0].is_attribute

    @property
    def time(self):
        if self.times[0] is None:
            return None
        return self.times[-1]

    # Variable _________________________________________________________________
    @cached_property
    def mean(self):
        assert self.is_variable
        return numpy.mean(self.values)

    @cached_property
    def range(self):
        assert self.is_variable
        return max(self.values) - min(self.values)

    @cached_property
    def stdev(self):
        assert self.is_variable
        return _sample_standard_deviation(self.values)

    # Attribute ________________________________________________________________
    @property
    def number_defective(self):
        assert self.is_attribute
        return sum(self.values)

    @property
    def proportion_defective(self):
        assert self.is_attribute
        return self.number_defective / self.size

    # Other ____________________________________________________________________
    def __str__(self):
        s = self.__class__.__name__ + "\n"
        if self.time is not None:
            s += f"    Time  : {self.time}\n"
        if self.is_variable:
            s += f"    Mean: {self.mean}\n"
            s += f"    Range: {self.range}\n"
            s += f"    Stdev: {self.stdev}"
        else:
            s += f"    Defect count: {self.number_defective}\n"
            s += f"    Proportion defective: {self.proportion_defective}"
        return s


class Record:
    """
    Records are collections of samples.
    """

    def __init__(self, samples=None):
        self._samples = []
        if samples is not None:
            self.append(samples)

    def append(self, samples):
        self._samples += self._normalize(samples)

        # Make sure we have all variable data or all attribute data..
        assert all(s.is_variable == self._samples[0].is_variable for s in self._samples)

        for cached in ["mean_of_means", "mean_of_ranges", "mean_of_stdevs"]:
            if cached in self.__dict__:
                del self.__dict__[cached]

    @staticmethod
    def _normalize(samples):
        if isinstance(samples, Sample):
            sl = [samples]
        else:
            sl = list(samples)
        assert len(sl) > 0
        for s in sl:
            assert isinstance(s, Sample)
        return sl

    # Derived properties for both variable and attribute data __________________
    def __len__(self):
        return len(self._samples)

    @property
    def times(self):
        return [s.time for s in self._samples]

    @property
    def has_time_info(self):
        # Just look at the first one, either they all should, or none should
        return self.samples[0].measurements[0].time is not None

    @property
    def sample_size(self):
        return self._samples[0].size

    @property
    def samples(self):
        return self._samples

    @property
    def is_variable(self):
        return self._samples[0].is_variable

    @property
    def is_attribute(self):
        return self._samples[0].is_attribute

    # Derived properties for variable data _____________________________________
    @property
    def means(self):
        assert self.is_variable
        return [s.mean for s in self._samples]

    @property
    def ranges(self):
        assert self.is_variable
        return [s.range for s in self._samples]

    @property
    def stdevs(self):
        assert self.is_variable
        return [s.stdev for s in self._samples]

    # Mean-of-.... ________________________
    @cached_property
    def mean_of_means(self):
        return numpy.mean(self.means)

    @cached_property
    def mean_of_ranges(self):
        return numpy.mean(self.ranges)

    @cached_property
    def mean_of_stdevs(self):
        return numpy.mean(self.stdevs)

    # Derived properties for attribute data ____________________________________
    @property
    def numbers_defective(self):
        assert self.is_attribute
        return [s.number_defective for s in self._samples]

    @property
    def proportions_defective(self):
        assert self.is_attribute
        return [s.proportion_defective for s in self._samples]

    @property
    def mean_proportion_defective(self):
        assert self.is_attribute
        return sum(self.numbers_defective) / sum([s.size for s in self.samples])

    # Other ____________________________________________________________________
    def __str__(self):
        s = self.__class__.__name__ + "\n"
        if self.is_variable:
            s += f"    Mean of means: {self.mean_of_means}\n"
            s += f"    Mean of ranges: { self.mean_of_ranges}\n"
            s += f"    Mean of stdevs: {self.mean_of_stdevs}"
        else:
            s += f"    Mean proportion defective: {self.mean_proportion_defective}"
        # for sample in self.samples:
        # print(sample)
        return s


def import_times_values(values, times=None, sample_size=5, is_attribute=False):
    """
    Imports sets of measurements values and times from arrays
    and organizes data sequentially into samples of given size
    Arrays must be same length.
    """

    if times is not None and len(times) != len(values):
        raise ImportException(
            f"Length mismatch: 'times' has length {len(times)}, "
            f"and  'values' has length {len(values)}."
        )
    r = Record()
    s = Sample()
    for i in range(len(values)):
        s.append(
            Measurement(
                value=values[i],
                time=times[i] if times is not None else None,
                is_attribute=is_attribute,
            )
        )
        if i % sample_size == sample_size - 1:
            r.append(s)
            s = Sample()
    return r


def import_csv_to_arrays(filename="./file.csv"):
    """Imports a file in the format:
    <time>, <value> \n
    """
    times, measurements = [], []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if len(row) == 1:
                times.append(None)
                measurements.append(float(row[0]))
            elif len(row) == 2:
                times.append(row[0])
                measurements.append(float(row[1]))
            else:
                raise ImportException(
                    "CSV file must contain either one or two columns."
                )

    return times, measurements


def demo_creating_measurements():
    print("Demoing measurements:")
    print(Measurement(value=1.1))
    print(Measurement(value=2.3, time=time_module.time()))

    print(Measurement(value=0, is_attribute=True))
    print(Measurement(value=1, time=time_module.time() + 1, is_attribute=True))
    print()


def demo_creating_a_record():
    print("Demoing record creation from scratch:")
    m11 = Measurement(11)
    m12 = Measurement(13)
    m13 = Measurement(15)
    s1 = Sample([m11, m12, m13])
    print(s1)
    assert s1.mean == 13
    assert s1.range == 4
    assert s1.stdev == 2

    m21 = Measurement(20)
    m22 = Measurement(23)
    m23 = Measurement(26)
    s2 = Sample([m21, m22, m23])
    print(s2)

    m31 = Measurement(31)
    m32 = Measurement(33)
    m33 = Measurement(35)
    s3 = Sample([m31, m32])
    s3.append([m33])
    print(s3)

    r = Record([s1, s2])
    r.append([s3])
    print(r)
    assert r.mean_of_means == 23

    print()


def demo_importing_series_data():
    t0 = time_module.time()
    times = [t0 + t for t in [1, 3, 5, 7, 9, 11, 13, 15]]
    values = [
        2,
        4,
        6,
        8,
        10,
        12,
        14,
        16,
    ]
    r = import_times_values(times, values, 2)
    print(r)


def main():
    demo_creating_measurements()
    demo_creating_a_record()
    demo_importing_series_data()


if __name__ == "__main__":
    main()
