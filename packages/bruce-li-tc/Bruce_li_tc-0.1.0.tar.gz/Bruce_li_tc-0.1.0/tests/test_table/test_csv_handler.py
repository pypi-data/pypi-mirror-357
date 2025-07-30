import unittest
import os
from bruce_li_tc.table.csv_handler import CSVHandler


class TestCSVHandler(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_data.csv"
        self.test_data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_write_and_read(self):
        handler = CSVHandler()
        handler.write(self.test_data, self.test_file)

        read_data = handler.read(self.test_file)
        self.assertEqual(len(read_data), 2)
        self.assertEqual(read_data[0]['name'], "Alice")
        self.assertEqual(read_data[1]['age'], "25")  # CSV读取为字符串