"""This module defines a `process_csv` function for aggregating an input stream of weather data."""

import csv
from collections import namedtuple
from datetime import datetime
from typing import Optional

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)

# a single day's aggregated weather station data
_AggregateKey = namedtuple('_AggregateKey', ['station', 'date'])
_AggregateValue = namedtuple('_AggregateValue', ['start_time', 'end_time', 'start', 'end', 'high', 'low', 'n'])

# input CSV date-time format and output date format
_OUTPUT_DATE_FORMAT = '%m/%d/%Y'
_INPUT_DATETIME_FORMAT = _OUTPUT_DATE_FORMAT + ' %I:%M:%S %p'

# output header (to be written before all other output rows)
_OUTPUT_HEADER = 'Station Name,Date,Min Temp,Max Temp,First Temp,Last Temp'


def process_csv(reader, writer):
    """
    Aggregate the weather data rows received from the `reader` and output them to the `writer`.

    :param reader: Input reader file descriptor (e.g. sys.stdin).
    :param writer: Output writer file descriptor (e.g. sys.stdout).
    :return: None; writes to `writer`.
    """
    aggregates = _read(reader)
    _write(aggregates, writer)


def _update_aggregate_value(agg: Optional[_AggregateValue], temp: float, time) -> _AggregateKey:
    """
    Update a given _AggregateValue with a new observation.

    :param agg: Current _AggregateValue for a given _AggregateKey.
    :param temp: New temperature observation to incorporate into the `aggregate`.
    :param time: Time of the new temperature observation.
    :return: Returns an updated _AggregateValue.
    """
    if agg is None:
        return _AggregateValue(time, time, temp, temp, temp, temp, 1)

    return _AggregateValue(time if time < agg.start_time else agg.start_time,
                           time if time > agg.end_time   else agg.end_time,
                           temp if time < agg.start_time else agg.start,
                           temp if time > agg.end_time   else agg.end,
                           max(temp, agg.high),
                           min(temp, agg.low),
                           agg.n + 1)


def _read(reader) -> dict[_AggregateKey, _AggregateValue]:
    """
    Aggregate the weather data rows received from the `reader`.

    :param reader: Input reader file descriptor (e.g. sys.stdin).
    :return: Returns a dictionary of _AggregateKeys mapped to _AggregateValues
    """
    aggregates = {}

    csv_reader = csv.reader(reader)

    # skip header row which contains the following column headers:
    #   ['Station Name', 'Measurement Timestamp', 'Air Temperature', 'Wet Bulb Temperature', 'Humidity',
    #    'Rain Intensity', 'Interval Rain', 'Total Rain', 'Precipitation Type', 'Wind Direction', 'Wind Speed',
    #    'Maximum Wind Speed', 'Barometric Pressure', 'Solar Radiation', 'Heading', 'Battery Life',
    #    'Measurement Timestamp Label', 'Measurement ID']
    # this won't fail if the header is missing (unsure about desired behavior here though)
    if not next(csv_reader, None):
        raise IndexError('Empty input/reader stream')

    for i, row in enumerate(csv_reader):
        try:
            # parse input row
            station, dt, temp, *_ = row  # unpack the row (only first 3 columns matter for now)
            dt1 = datetime.strptime(dt, _INPUT_DATETIME_FORMAT)
            temp = float(temp)

            # update aggregate for this station-date
            key = _AggregateKey(station, dt1.date())
            aggregates[key] = _update_aggregate_value(aggregates.get(key), temp, dt1.time())

        except Exception as e:
            # adding 2: 1 for index start at 0, another 1 to account for header
            raise ValueError(f'Input error at line {i+2}: {row}') from e

    return aggregates


def _write(aggregates: dict[_AggregateKey, _AggregateValue], writer):
    """
    Write out aggregated weather station data to `writer` output stream.

    :param aggregates: Aggregated daily weather station data.
    :param writer: Output writer stream.
    :return: None; writes to `writer`.
    """
    csv_writer = csv.writer(writer)
    csv_writer.writerow(_OUTPUT_HEADER.split(','))
    for k, v in aggregates.items():
        csv_writer.writerow([k.station, k.date.strftime(_OUTPUT_DATE_FORMAT), v.low, v.high, v.start, v.end])
