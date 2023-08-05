"""Tests for the interview/weather.py script."""

from interview import weather
import io
import os
import unittest

_TEST_DATA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'chicago_beach_weather.csv')


class TestWeather(unittest.TestCase):

    def _harness(self, input_rows_lambda):
        """Test harness; returns process_csv's written rows."""
        with open(_TEST_DATA_FILE) as fp:
            input_rows = input_rows_lambda(fp)
        reader = io.StringIO(''.join(input_rows))
        writer = io.StringIO()
        weather.process_csv(reader, writer)
        return writer.getvalue().splitlines()

    def test_one_data_row(self):
        """Test reading a single data row (and discarding the header)."""
        output_rows = self._harness(lambda fp: [next(fp) for _ in range(2)])
        self.assertEqual(output_rows[1], '63rd Street Weather Station,12/31/2016,-1.3,-1.3,-1.3,-1.3')

    def test_zero_data_rows(self):
        """Test reading no data rows (just discarding the header)."""
        output_rows = self._harness(lambda fp: [next(fp) for _ in range(1)])
        self.assertEqual(len(output_rows), 1)

    def test_no_rows_raises(self):
        """Test empty input (i.e. missing header)."""
        reader = io.StringIO(''.join([]))
        writer = io.StringIO()
        with self.assertRaises(IndexError):
            weather.process_csv(reader, writer)

    def test_ten_rows(self):
        """Test reading 10 rows."""
        output_rows = self._harness(lambda fp: [next(fp) for _ in range(10)])[1:]  # discard header
        output_rows.sort()
        self.assertEqual(output_rows[0], '63rd Street Weather Station,12/31/2016,-1.3,-0.2,-0.2,-1.3')
        self.assertEqual(output_rows[1], 'Foster Weather Station,12/31/2016,-1.56,-0.67,-0.67,-1.56')
        self.assertEqual(output_rows[2], 'Oak Street Weather Station,12/31/2016,-0.3,0.6,0.6,-0.3')

    def test_100_rows(self):
        """Test reading 100 rows."""
        output_rows = self._harness(lambda fp: [next(fp) for _ in range(100)])[1:]  # discard header
        output_rows.sort()
        self.assertEqual(len(output_rows), 6)
        self.assertEqual(output_rows[0], '63rd Street Weather Station,12/30/2016,0.5,3.6,0.8,3.6')

    def test_bogus_temp_raises(self):
        """Test a non-numeric temperature value."""
        with self.assertRaises(ValueError):
            self._harness(lambda fp: [next(fp).replace('-1.3', 'non-numeric') for _ in range(2)])