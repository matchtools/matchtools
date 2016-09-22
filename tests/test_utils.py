import unittest
import warnings

from matchtools import utils


class TestUtils(unittest.TestCase):
    def test_return_element_pass_1(self):
        word = 'A Block'
        element = 'Block'
        tested = utils.return_element(word, element)
        self.assertEqual(tested, 1)

    def test_return_element_fail_1(self):
        word = 'A Block'
        element = 'B'
        self.assertRaises(ValueError,
                          lambda: utils.return_element(word, element))

    def test_return_element_warning_1(self):
        word = 'A A A'
        element = 'A'
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            utils.return_element(word, element)
            assert "occurs more than once" in str(w[-1].message)

    def test_move_element_pass_1(self):
        word = 'A Block'
        element = 0
        where = 'back'
        tested = utils.move_element(word, element, where)
        self.assertEqual(tested, 'Block A')

    def test_move_element_pass_2(self):
        word = 'A Block'
        element = 'A'
        where = 'back'
        tested = utils.move_element(word, element, where)
        self.assertEqual(tested, 'Block A')

    def test_move_element_pass_3(self):
        word = 'A Block'
        element = 1
        where = 'front'
        tested = utils.move_element(word, element, where)
        self.assertEqual(tested, 'Block A')

    def test_move_element_pass_4(self):
        word = 'A Block'
        element = 'Block'
        where = 'front'
        tested = utils.move_element(word, element, where)
        self.assertEqual(tested, 'Block A')

    def test_move_element_fail_1(self):
        word = 'A Block'
        element = 3
        where = 'front'
        self.assertRaises(IndexError,
                          lambda: utils.move_element(word, element, where))

    def test_match_rows_pass_1(self):
        row1 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), True)

    def test_match_rows_pass_2(self):
        utils.MatchBlock.number_tolerance = 0
        utils.MatchBlock.date_tolerance = 0
        utils.MatchBlock.coordinates_tolerance = 0
        utils.MatchBlock.string_tolerance = 0
        utils.MatchBlock.str_number_tolerance = 10
        utils.MatchBlock.str_custom_tolerance = 0

        row1 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Well 1A', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), True)

    def test_match_rows_pass_3(self):
        utils.MatchBlock.number_tolerance = 10
        utils.MatchBlock.date_tolerance = 0
        utils.MatchBlock.coordinates_tolerance = 0
        utils.MatchBlock.string_tolerance = 0
        utils.MatchBlock.str_number_tolerance = 0
        utils.MatchBlock.str_custom_tolerance = 0

        row1 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Well 1', 90, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), True)

    def test_match_rows_pass_4(self):
        utils.MatchBlock.number_tolerance = 0
        utils.MatchBlock.date_tolerance = 0
        utils.MatchBlock.coordinates_tolerance = 650
        utils.MatchBlock.string_tolerance = 0
        utils.MatchBlock.str_number_tolerance = 0
        utils.MatchBlock.str_custom_tolerance = 0

        row1 = ['Well 1', 100, '55.75222, 37.61556', '10-Dec-2015']
        row2 = ['Well 1', 100, '59.93863, 30.31413', '10-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), True)

    def test_match_rows_pass_5(self):
        utils.MatchBlock.number_tolerance = 0
        utils.MatchBlock.date_tolerance = 10
        utils.MatchBlock.coordinates_tolerance = 0
        utils.MatchBlock.string_tolerance = 0
        utils.MatchBlock.str_number_tolerance = 0
        utils.MatchBlock.str_custom_tolerance = 0

        row1 = ['Well 1', 100, '55.75222, 37.61556', '10-Dec-2015']
        row2 = ['Well 1', 100, '55.75222, 37.61556', '20-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), True)

    def test_match_rows_fail_1(self):
        utils.MatchBlock.number_tolerance = 0
        utils.MatchBlock.date_tolerance = 0
        utils.MatchBlock.coordinates_tolerance = 0
        utils.MatchBlock.string_tolerance = 0
        utils.MatchBlock.str_number_tolerance = 0
        utils.MatchBlock.str_custom_tolerance = 0

        row1 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Well 1A', 100, '41.49008, -71.312796', '10-Dec-2015']

        self.assertIs(utils.match_rows(row1, row2), False)

    def test_match_rows_fail_2(self):
        row1 = ['Well 1', 100, '41.49008, -71.312796', '10-Dec-2015']
        row2 = ['Well 1', 100, '41.49008, -71.312796']

        self.assertIs(utils.match_rows(row1, row2), False)

    def test_match_find_pass_1(self):
        utils.MatchBlock.str_number_tolerance = 0
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(utils.match_find(row, rows),
                         ['Well 1', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_pass_2(self):
        utils.MatchBlock.str_number_tolerance = 20
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(utils.match_find(row, rows),
                         ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_fail_1(self):
        utils.MatchBlock.str_number_tolerance = 0
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 13', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertNotEqual(utils.match_find(row, rows),
                            ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'])

    def test_match_find_all_pass_1(self):
        utils.MatchBlock.str_number_tolerance = 0
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 1', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(utils.match_find_all(row, rows),
                         [['Well 1', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']])

    def test_match_find_all_pass_2(self):
        utils.MatchBlock.str_number_tolerance = 10
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 11', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 13', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(utils.match_find_all(row, rows),
                         [['Well 11', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                          ['Well 13', 100, '41.49, -71.312', '10-Dec-2015']])

    def test_match_find_all_pass_3(self):
        utils.MatchBlock.str_number_tolerance = 0
        row = ['Well 1', 100, '41.49, -71.312', '10-Dec-2015']
        rows = [['Well 11', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 12', 100, '41.49, -71.312', '10-Dec-2015'],
                ['Well 13', 100, '41.49, -71.312', '10-Dec-2015']]

        self.assertEqual(utils.match_find_all(row, rows), [])
