import os
import sys
import unittest
import warnings

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from matchtools import (MatchBlock, return_element, match_rows, match_find,
                        match_find_all, move_element_to_front,
                        move_element_to_back)


class TestUtils(unittest.TestCase):
    def test_return_element_pass_1(self):
        word = 'Foo Bar'
        element = 'Bar'
        tested = return_element(word, element)
        self.assertEqual(tested, 1)

    def test_return_element_fail_1(self):
        word = 'Foo Bar'
        element = 'Spam'
        self.assertRaises(ValueError, return_element, word, element)

    def test_return_element_warning_1(self):
        word = 'Spam Spam Spam'
        element = 'Spam'
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            return_element(word, element)
            assert "occurs more than once" in str(w[-1].message)

    def test_move_element_to_back_pass_1(self):
        word = 'Foo Bar'
        element = 0
        tested = move_element_to_back(word, element)
        self.assertEqual(tested, 'Bar Foo')

    def test_move_element_to_back_pass_2(self):
        word = 'Foo Bar'
        element = 'Foo'
        tested = move_element_to_back(word, element)
        self.assertEqual(tested, 'Bar Foo')

    def test_move_element_to_front_pass_1(self):
        word = 'Foo Bar'
        element = 1
        tested = move_element_to_front(word, element)
        self.assertEqual(tested, 'Bar Foo')

    def test_move_element_to_front_pass_2(self):
        word = 'Foo Bar'
        element = 'Bar'
        tested = move_element_to_front(word, element)
        self.assertEqual(tested, 'Bar Foo')

    def test_move_element_to_front_fail_1(self):
        word = 'Foo Bar'
        element = 2
        self.assertRaises(IndexError, move_element_to_front, word, element)

    def test_match_rows_pass_1(self):
        row1 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(match_rows(row1, row2), True)

    def test_match_rows_pass_2(self):
        MatchBlock.number_tolerance = 0
        MatchBlock.date_tolerance = 0
        MatchBlock.coordinates_tolerance = 0
        MatchBlock.string_tolerance = 0
        MatchBlock.str_number_tolerance = 10
        MatchBlock.str_custom_tolerance = 0

        row1 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Flight 1A', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(match_rows(row1, row2), True)

    def test_match_rows_pass_3(self):
        MatchBlock.number_tolerance = 10
        MatchBlock.date_tolerance = 0
        MatchBlock.coordinates_tolerance = 0
        MatchBlock.string_tolerance = 0
        MatchBlock.str_number_tolerance = 0
        MatchBlock.str_custom_tolerance = 0

        row1 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Flight 1', 90, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(match_rows(row1, row2), True)

    def test_match_rows_pass_4(self):
        MatchBlock.number_tolerance = 0
        MatchBlock.date_tolerance = 0
        MatchBlock.coordinates_tolerance = 650
        MatchBlock.string_tolerance = 0
        MatchBlock.str_number_tolerance = 0
        MatchBlock.str_custom_tolerance = 0

        row1 = ['Flight 1', 100, '55.75222, 37.61556', '10-Dec-2015']
        row2 = ['Flight 1', 100, '59.93863, 30.31413', '10-Dec-2015']

        self.assertIs(match_rows(row1, row2), True)

    def test_match_rows_pass_5(self):
        MatchBlock.number_tolerance = 0
        MatchBlock.date_tolerance = 10
        MatchBlock.coordinates_tolerance = 0
        MatchBlock.string_tolerance = 0
        MatchBlock.str_number_tolerance = 0
        MatchBlock.str_custom_tolerance = 0

        row1 = ['Flight 1', 100, '55.75222, 37.61556', '10-Dec-2015']
        row2 = ['Flight 1', 100, '55.75222, 37.61556', '20-Dec-2015']

        self.assertIs(match_rows(row1, row2), True)

    def test_match_rows_fail_1(self):
        MatchBlock.number_tolerance = 0
        MatchBlock.date_tolerance = 0
        MatchBlock.coordinates_tolerance = 0
        MatchBlock.string_tolerance = 0
        MatchBlock.str_number_tolerance = 0
        MatchBlock.str_custom_tolerance = 0

        row1 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Flight 1A', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(match_rows(row1, row2), False)

    def test_match_rows_fail_2(self):
        row1 = ['Flight 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Flight 1', 100, '41.49008, -71.312796']

        self.assertIs(match_rows(row1, row2), False)

    def test_match_find_pass_1(self):
        MatchBlock.str_number_tolerance = 0
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(match_find(row, rows),
                         ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_pass_2(self):
        MatchBlock.str_number_tolerance = 20
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(match_find(row, rows),
                         ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_fail_1(self):
        MatchBlock.str_number_tolerance = 0
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertNotEqual(match_find(row, rows),
                            ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_all_pass_1(self):
        MatchBlock.str_number_tolerance = 0
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 1', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(match_find_all(row, rows),
                         [['Flight 1', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']])

    def test_match_find_all_pass_2(self):
        MatchBlock.str_number_tolerance = 10
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 11', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(match_find_all(row, rows),
                         [['Flight 11', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015']])

    def test_match_find_all_pass_3(self):
        MatchBlock.str_number_tolerance = 0
        row = ['Flight 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Flight 11', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Flight 13', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(match_find_all(row, rows), [])


if __name__ == '__main__':
    unittest.main()
