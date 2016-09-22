import datetime
import unittest

from matchtools import MatchBlock


class TestMatchBlock(unittest.TestCase):
    # Decorators are tested as below:
    # 1. check_tolerance: test_compare_dates_warning
    def test_dict_sub_pass_1(self):
        string = 'Well 1 NE'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Well 1 north east', result)

    def test_dict_sub_pass_2(self):
        string = 'Sudan S'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Sudan south', result)

    def test_dict_sub_pass_3(self):
        string = 'Ait Hamouda South-West'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Ait Hamouda South-West', result)

    def test_dict_sub_pass_4(self):
        string = 'Ait Hamouda SouthWest'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Ait Hamouda south west', result)

    def test_dict_sub_pass_5(self):
        string = 'Nord Atlas'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('north Atlas', result)

    def test_dict_sub_pass_6(self):
        string = 'Ait Hamouda'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Ait Hamouda', result)

    def test_dict_sub_pass_7(self):
        string = 'Ait   Hamouda  N  '
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Ait   Hamouda  north  ', result)

    def test_dict_sub_pass_8(self):
        string = '0 Troll N/21'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('0 Troll north/21', result)

    def test_dict_sub_pass_9(self):
        string = '0 Troll N21'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('0 Troll N21', result)

    def test_dict_sub_pass_10(self):
        string = 'Hadi_bAraT_10'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('Hadi_west_10', result)

    def test_dict_sub_pass_11(self):
        string = 'J-W1-NX186'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('J-W1-NX186', result)

    def test_dict_sub_pass_12(self):
        string = "there's a feeling I get when I look to the W"
        result = MatchBlock.dict_sub(string)
        self.assertEqual(
            "there's a feeling I get when I look to the west", result)

    def test_strip_zeros_pass_1(self):
        string = 'Well 001'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('Well 1', result)

    def test_strip_zeros_pass_2(self):
        string = 'Well T001'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('Well T1', result)

    def test_strip_zeros_pass_3(self):
        string = 'A-001-102/004'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('A-1-102/4', result)

    def test_strip_zeros_pass_4(self):
        string = '005I-009-059'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('5I-9-59', result)

    def test_strip_zeros_pass_5(self):
        string = 'A-060H-017'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('A-60H-17', result)

    def test_strip_zeros_pass_6(self):
        string = '0-060H-0Z'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('0-60H-0Z', result)

    def test_strip_zeros_pass_7(self):
        string = ' 0 A/0- X-T0/1 -Z0'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual(' 0 A/0- X-T0/1 -Z0', result)

    def test_roman_to_integers_pass(self):
        word = 'Liverpool IV Dortmund III'
        tested = MatchBlock.roman_to_integers(word)
        self.assertEqual(tested, 'Liverpool 4 Dortmund 3')

    def test_integers_to_roman_pass(self):
        word = 'Liverpool 4 Dortmund 3'
        tested = MatchBlock.integers_to_roman(word)
        self.assertEqual(tested, 'Liverpool IV Dortmund III')

    def test_split_on_nonalpha_pass(self):
        word = 'ABC-D EF*G'
        tested = MatchBlock.split_on_nonalpha(word)
        self.assertEqual(tested, ['ABC', '-', 'D', ' ', 'EF', '*', 'G'])

    def test_is_abbreviation_pass_1(self):
        string1 = 'Garet Al Bafinat'
        string2 = 'GAB'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_2(self):
        string1 = 'GAB'
        string2 = 'Garet Al Bafinat'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_3(self):
        string1 = 'Name With an Article'
        string2 = 'NWA'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_4(self):
        string1 = 'Super Long String'
        string2 = '                        SLS   '
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_5(self):
        string1 = '                        SLS   '
        string2 = 'A Super Long String'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_extract_coordinates_pass_1(self):
        original_string = '36.611111,41.886111'
        string = ''
        coordinates = (36.611111, 41.886111)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_2(self):
        original_string = 'No coordinates'
        string = 'No coordinates'
        coordinates = None
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_3(self):
        original_string = '36.611111,41.886111 and some text'
        string = 'and some text'
        coordinates = (36.611111, 41.886111)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_4(self):
        original_string = '41.499498,-81.695391'
        string = ''
        coordinates = (41.499498, -81.695391)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_5(self):
        original_string = '  41.499498 , -81.695391  '
        string = ''
        coordinates = (41.499498, -81.695391)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_str_number_pass_1(self):
        original_string = 'Well 1 Nord'
        string = 'Well Nord'
        num = '1'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_2(self):
        original_string = 'Well Nord'
        string = 'Well Nord'
        num = ''
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_3(self):
        original_string = '3 Well 4 Nord 5a'
        string = 'Well Nord'
        num = '3 4 5a'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_4(self):
        original_string = 'New Well 4/1a'
        string = 'New Well'
        num = '4 1a'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_5(self):
        original_string = '34.2'
        string = ''
        num = '34 2'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_custom_pass_1(self):
        original_string = 'Well 1 Nord'
        string = 'Well 1'
        custom = 'north'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_2(self):
        original_string = 'Well Centre 1 Sud'
        string = 'Well 1'
        custom = 'center south'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_3(self):
        original_string = 'Well Sud 1 Centre'
        string = 'Well 1'
        custom = 'center south'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_4(self):
        original_string = 'Well 1'
        string = 'Well 1'
        custom = ''
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_5(self):
        original_string = 'Sud West'
        string = ''
        custom = 'south west'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_dates_pass_1(self):
        original_string = '11/1111'
        string = '11/1111'
        date = []
        result = MatchBlock.extract_dates(original_string)
        self.assertEqual((string, date), result)

    def test_extract_dates_pass_2(self):
        original_string = '11/11/1111'
        date = datetime.datetime(1111, 11, 11, 0, 0)
        string = ''
        result = MatchBlock.extract_dates(original_string)
        self.assertEqual((string, [date]), result)

    def test_extract_str_custom_pass_6(self):
        original_string = 'West Sud'
        string = ''
        custom = 'south west'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_compare_numbers_fail(self):
        num1, num2 = 12, 16
        tol = 2
        tested = MatchBlock.compare_numbers(num1, num2, tolerance=tol)
        self.assertIs(tested, False)

    def test_compare_numbers_pass(self):
        num1, num2 = 12, 16
        tol = 5
        tested = MatchBlock.compare_numbers(num1, num2, tolerance=tol)
        self.assertIs(tested, True)

    def test_compare_dates_warning(self):
        # testing decorator: check_tolerance
        d1, d2 = '12-Feb-2015', '15-Feb-2015'
        tol = -2
        self.assertRaises(ValueError, MatchBlock.compare_dates, d1, d2,
                          tolerance=tol)

    def test_compare_dates_pass_1(self):
        d1, d2 = '12-Feb-2015', '14-Feb-2015'
        tol = 2
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, True)

    def test_compare_dates_pass_2(self):
        d1, d2 = 'Feb 12 2010', 'Feb 13 2010'
        tol = 3
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol,
                                          pattern='%b %d %Y')
        self.assertEqual(tested, 1)

    def test_compare_dates_pass_3(self):
        d1, d2 = datetime.date.today(), datetime.date.today()
        tol = 3
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, True)

    def test_compare_dates_pass_4(self):
        d1 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        d2 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        tol = 0
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, True)

    def test_compare_dates_pass_5(self):
        d1 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        d2 = [datetime.date.today() + datetime.timedelta(1),
              datetime.date.today() - datetime.timedelta(2)]
        tol = 1
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, True)

    def test_compare_dates_fail_1(self):
        d1, d2 = '12-Feb-2015', '15-Feb-2015'
        tol = 2
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, False)

    def test_compare_dates_fail_2(self):
        d1 = [datetime.date.today(), datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        d2 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        tol = 0
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, False)

    def test_compare_dates_fail_3(self):
        d1 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(1)]
        d2 = [datetime.date.today(),
              datetime.date.today() - datetime.timedelta(3)]
        tol = 0
        tested = MatchBlock.compare_dates(d1, d2, tolerance=tol)
        self.assertIs(tested, False)

    def test_compare_strings_pass_1(self):
        string1 = 'Well'
        string2 = 'Well'
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_pass_2(self):
        string1 = 'Well'
        string2 = 'Wall'
        tolerance = 25
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_pass_3(self):
        string1 = 'Well'
        string2 = 'Wall'
        tolerance = 25.5
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_fail_1(self):
        string1 = 'Well'
        string2 = 'Wall'
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_strings_fail_2(self):
        string1 = 'Well'
        string2 = ''
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_strings_fail_3(self):
        string1 = 'Well'
        string2 = ''
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance, method='ratio')
        self.assertIs(result, False)

    def test_compare_strings_fail_4(self):
        string1 = 'Well'
        string2 = 'Well'
        tolerance = -1
        self.assertRaises(ValueError, MatchBlock.compare_strings,
                          string1, string2, tolerance=tolerance)

    def test_compare_strings_fail_5(self):
        string1 = 'Well'
        string2 = 'Well'
        tolerance = 101
        self.assertRaises(ValueError, MatchBlock.compare_strings,
                          string1, string2, tolerance=tolerance)

    def test_compare_strings_fail_6(self):
        string1 = 'Well'
        string2 = 'Wall'
        tolerance = 25.5
        self.assertRaises(ValueError, MatchBlock.compare_strings,
                          string1, string2, tolerance=tolerance, method='abc')

    def test_compare_coordinates_pass_1(self):
        lat1 = 41.49008
        lng1 = -71.312796
        lat2 = 41.499498
        lng2 = -81.695391
        tolerance = 900
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_coordinates_pass_2(self):
        lat1 = 36.611111
        lng1 = 41.886111
        lat2 = 32.383333
        lng2 = 47.390833
        tolerance = 600
        unit = 'mi'
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance, unit=unit)
        self.assertIs(result, True)

    def test_compare_coordinates_fail_1(self):
        lat1 = 41.49008
        lng1 = -71.312796
        lat2 = 41.499498
        lng2 = -81.695391
        tolerance = 100
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_coordinates_fail_2(self):
        lat1 = 36.611111
        lng1 = 41.886111
        lat2 = 32.383333
        lng2 = 47.390833
        tolerance = 600
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_coordinates_fail_3(self):
        lat1 = 36.611111
        lng1 = 41.886111
        lat2 = 32.383333
        lng2 = 47.390833
        tolerance = 600
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance,
                                                ellipsoid='Intl 1924')
        self.assertIs(result, False)

    def test_compare_coordinates_fail_4(self):
        lat1 = 36.0
        lng1 = 41.0
        lat2 = 32.0
        lng2 = 47.0
        tolerance = 100
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_coordinates_fail_5(self):
        lat1 = 41.49008
        lng1 = -71.312796
        lat2 = 41.499498
        lng2 = -81.695391
        tolerance = 100
        unit = ''
        self.assertRaises(ValueError, MatchBlock.compare_coordinates,
                          (lat1, lng1), (lat2, lng2),
                          tolerance=tolerance, unit=unit)

    def test_compare_coordinates_fail_6(self):
        lat1 = 41.49008
        lng1 = -71.312796
        lat2 = 41.499498
        lng2 = -81.695391
        tolerance = -1
        self.assertRaises(ValueError, MatchBlock.compare_coordinates,
                          (lat1, lng1), (lat2, lng2),
                          tolerance=tolerance)

    def test_extract_dates(self):
        text = '25 May 1977 Rome Istanbul 25 May 2005 '
        result = MatchBlock.extract_dates(text)
        self.assertEqual(result, ('Rome Istanbul',
                                  [datetime.datetime(1977, 5, 25, 0, 0),
                                   datetime.datetime(2005, 5, 25, 0, 0)]))

    def test_matchblock_pass_1(self):
        matchblock_1 = MatchBlock(1)
        matchblock_2 = MatchBlock(1)

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_2(self):
        matchblock_1 = MatchBlock('10-Dec-2015')
        matchblock_2 = MatchBlock('10-Dec-2015')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_3(self):
        matchblock_1 = MatchBlock('41.49008, -71.312796')
        matchblock_2 = MatchBlock('41.49008, -71.312796')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_4(self):
        matchblock_1 = MatchBlock('Well')
        matchblock_2 = MatchBlock('Well')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_5(self):
        matchblock_1 = MatchBlock('Well North')
        matchblock_2 = MatchBlock('Well N')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_6(self):
        matchblock_1 = MatchBlock('Well S')
        matchblock_2 = MatchBlock('Well N')

        self.assertIs(matchblock_1 != matchblock_2, True)

    def test_matchblock_pass_7(self):
        matchblock_1 = MatchBlock('Well 01')
        matchblock_2 = MatchBlock('Well 1')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_8(self):
        matchblock_1 = MatchBlock('Well With Ultra High Production 10')
        matchblock_2 = MatchBlock('WWUHP 10')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_9(self):
        matchblock_1 = MatchBlock('Well 10')
        matchblock_2 = MatchBlock('Well X')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_fail_1(self):
        matchblock_1 = MatchBlock('Well S')
        matchblock_2 = MatchBlock('Well N')

        self.assertIs(matchblock_1 == matchblock_2, False)

    def test_matchblock_fail_2(self):
        matchblock_1 = MatchBlock('Well 1')
        matchblock_2 = MatchBlock('Well')

        self.assertIs(len(matchblock_1) == len(matchblock_2), False)

    def test_matchblock_fail_3(self):
        matchblock_1 = MatchBlock('Well 1')
        matchblock_2 = 1

        self.assertRaises(TypeError, matchblock_1.__eq__, matchblock_2)

    def test_check_roman_pass_1(self):
        string = 'IX'
        tested = MatchBlock.check_roman(string)
        self.assertEqual(tested, '9')

    def test_check_roman_pass_2(self):
        string = 'IIVX'
        tested = MatchBlock.check_roman(string)
        self.assertEqual(tested, 'IIVX')
