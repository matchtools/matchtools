import datetime
import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from matchtools import MatchBlock


class TestMatchBlock(unittest.TestCase):
    def test_dict_sub_pass_1(self):
        string = 'London 1 NE'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('London 1 north east', result)

    def test_dict_sub_pass_2(self):
        string = 'N London'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('north London', result)

    def test_dict_sub_pass_3(self):
        string = 'London South-West'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('London South-West', result)

    def test_dict_sub_pass_4(self):
        string = 'London SouthWest'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('London south west', result)

    def test_dict_sub_pass_5(self):
        string = 'Nord London'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('north London', result)

    def test_dict_sub_pass_6(self):
        string = 'London'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('London', result)

    def test_dict_sub_pass_7(self):
        string = '  London  N  '
        result = MatchBlock.dict_sub(string)
        self.assertEqual('  London  north  ', result)

    def test_dict_sub_pass_8(self):
        string = '0 London N/21'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('0 London north/21', result)

    def test_dict_sub_pass_9(self):
        string = '0 London N21'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('0 London N21', result)

    def test_dict_sub_pass_10(self):
        string = 'London_nOrD_10'
        result = MatchBlock.dict_sub(string)
        self.assertEqual('London_north_10', result)

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
        string = 'London 001'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('London 1', result)

    def test_strip_zeros_pass_2(self):
        string = 'London T001'
        result = MatchBlock.strip_zeros(string)
        self.assertEqual('London T1', result)

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
        string1 = 'National Health Service'
        string2 = 'NHS'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_2(self):
        string1 = 'NHS'
        string2 = 'National Health Service'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_3(self):
        string1 = 'The National Aeronautics and Space Administration'
        string2 = 'NASA'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_4(self):
        string1 = 'Jet Propulsion Laboratory'
        string2 = '                        JPL   '
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_is_abbreviation_pass_5(self):
        string1 = '                        JPL   '
        string2 = 'A Jet Propulsion Laboratory'
        result = MatchBlock.is_abbreviation(string1, string2)
        self.assertIs(result, True)

    def test_extract_coordinates_pass_1(self):
        original_string = '53.41058,-2.97794'
        string = ''
        coordinates = (53.41058, -2.97794)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_2(self):
        original_string = 'Liverpool'
        string = 'Liverpool'
        coordinates = None
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_3(self):
        original_string = '53.41058,-2.97794 Liverpool'
        string = 'Liverpool'
        coordinates = (53.41058, -2.97794)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_4(self):
        original_string = '59.911491,10.757933'
        string = ''
        coordinates = (59.911491, 10.757933)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_coordinates_pass_5(self):
        original_string = '  59.911491 ,  10.757933  '
        string = ''
        coordinates = (59.911491, 10.757933)
        result = MatchBlock.extract_coordinates(original_string)
        self.assertEqual((string, coordinates), result)

    def test_extract_str_number_pass_1(self):
        original_string = 'France 1 Nord'
        string = 'France Nord'
        num = '1'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_2(self):
        original_string = 'France Nord'
        string = 'France Nord'
        num = ''
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_3(self):
        original_string = '3 France 4 Nord 5a'
        string = 'France Nord'
        num = '3 4 5a'
        result = MatchBlock.extract_str_number(original_string)
        self.assertEqual((string, num), result)

    def test_extract_str_number_pass_4(self):
        original_string = 'France 4/1a'
        string = 'France'
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
        original_string = 'France 1 Nord'
        string = 'France 1'
        custom = 'north'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_2(self):
        original_string = 'France Centre 1 Sud'
        string = 'France 1'
        custom = 'center south'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_3(self):
        original_string = 'France Sud 1 Centre'
        string = 'France 1'
        custom = 'center south'
        result = MatchBlock.extract_str_custom(original_string)
        self.assertEqual((string, custom), result)

    def test_extract_str_custom_pass_4(self):
        original_string = 'France 1'
        string = 'France 1'
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

    def test_compare_dates_check_decorator_fail(self):
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
        self.assertEqual(tested, True)

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
        string1 = 'Wall'
        string2 = 'Wall'
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_pass_2(self):
        string1 = 'Wall'
        string2 = 'Fall'
        tolerance = 25
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_pass_3(self):
        string1 = 'Wall'
        string2 = 'Fall'
        tolerance = 25.5
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, True)

    def test_compare_strings_fail_1(self):
        string1 = 'Wall'
        string2 = 'Fall'
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_strings_fail_2(self):
        string1 = 'Wall'
        string2 = ''
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_strings_fail_3(self):
        string1 = 'Wall'
        string2 = ''
        tolerance = 0
        result = MatchBlock.compare_strings(string1, string2,
                                            tolerance=tolerance, method='ratio')
        self.assertIs(result, False)

    def test_compare_strings_fail_4(self):
        string1 = 'Wall'
        string2 = 'Wall'
        tolerance = -1
        self.assertRaises(ValueError, MatchBlock.compare_strings,
                          string1, string2, tolerance=tolerance)

    def test_compare_strings_fail_5(self):
        string1 = 'Wall'
        string2 = 'Wall'
        tolerance = 101
        self.assertRaises(ValueError, MatchBlock.compare_strings,
                          string1, string2, tolerance=tolerance)

    def test_compare_strings_fail_6(self):
        string1 = 'Wall'
        string2 = 'Fall'
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
        lat1 = 52.520008
        lng1 = 13.404954
        lat2 = 53.551086
        lng2 = 9.993682
        tolerance = 200
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
        lat1 = 52.520008
        lng1 = 13.404954
        lat2 = 42.520000
        lng2 = 23.400000
        tolerance = 600
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance)
        self.assertIs(result, False)

    def test_compare_coordinates_fail_3(self):
        lat1 = 52.520008
        lng1 = 13.404954
        lat2 = 42.520000
        lng2 = 23.400000
        tolerance = 600
        result = MatchBlock.compare_coordinates((lat1, lng1), (lat2, lng2),
                                                tolerance=tolerance,
                                                ellipsoid='Intl 1924')
        self.assertIs(result, False)

    def test_compare_coordinates_fail_4(self):
        lat1 = 52.0
        lng1 = 13.0
        lat2 = 42.0
        lng2 = 23.0
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

    def test_check_roman_pass_1(self):
        string = 'IX'
        tested = MatchBlock.from_roman(string)
        self.assertEqual(tested, '9')

    def test_check_roman_pass_2(self):
        string = 'IIVX'
        tested = MatchBlock.from_roman(string)
        self.assertEqual(tested, 'IIVX')

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
        matchblock_1 = MatchBlock('Madrid')
        matchblock_2 = MatchBlock('Madrid')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_5(self):
        matchblock_1 = MatchBlock('Madrid North')
        matchblock_2 = MatchBlock('Madrid N')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_6(self):
        matchblock_1 = MatchBlock('Madrid S')
        matchblock_2 = MatchBlock('Madrid N')

        self.assertIs(matchblock_1 != matchblock_2, True)

    def test_matchblock_pass_7(self):
        matchblock_1 = MatchBlock('Madrid 01')
        matchblock_2 = MatchBlock('Madrid 1')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_8(self):
        matchblock_1 = MatchBlock('IATA 10')
        matchblock_2 = MatchBlock('International Air Transport Association 10')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_pass_9(self):
        matchblock_1 = MatchBlock('Madrid 10')
        matchblock_2 = MatchBlock('Madrid X')

        self.assertIs(matchblock_1 == matchblock_2, True)

    def test_matchblock_fail_1(self):
        matchblock_1 = MatchBlock('Madrid S')
        matchblock_2 = MatchBlock('Madrid N')

        self.assertIs(matchblock_1 == matchblock_2, False)

    def test_matchblock_fail_2(self):
        matchblock_1 = MatchBlock('Madrid 1')
        matchblock_2 = MatchBlock('Madrid')

        self.assertIs(len(matchblock_1) == len(matchblock_2), False)

    def test_matchblock_fail_3(self):
        matchblock_1 = MatchBlock('Madrid 1')
        matchblock_2 = 1

        self.assertRaises(TypeError, matchblock_1.__eq__, matchblock_2)

    def test_matchblock_try_date_on_pass_1(self):
        matchblock = MatchBlock('31-Dec-2015 New Year', try_date=True)
        date = [datetime.datetime(2015, 12, 31, 0, 0)]
        string = 'New Year'
        str_number = ''

        self.assertEqual(matchblock.date, date)
        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_date_off_pass_1(self):
        matchblock = MatchBlock('31-Dec-2015 New Year', try_date=False)
        date = []
        string = 'Dec New Year'
        str_number = '31 2015'

        self.assertEqual(matchblock.date, date)
        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_coordinates_on_pass_1(self):
        matchblock = MatchBlock('41.49008, -71.312796', try_coordinates=True)
        coordinates = (41.49008, -71.312796)
        string = ''
        str_number = ''

        self.assertEqual(matchblock.coordinates, coordinates)
        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_coordinates_off_pass_1(self):
        matchblock = MatchBlock('41.49008, -71.312796', try_coordinates=False)
        coordinates = None
        string = ''
        str_number = '41 49008 71 312796'

        self.assertEqual(matchblock.coordinates, coordinates)
        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_str_number_on_pass_1(self):
        matchblock = MatchBlock('Year 2K', try_str_number=True)
        string = 'Year'
        str_number = '2K'

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_str_number_off_pass_1(self):
        matchblock = MatchBlock('Year 2K', try_str_number=False)
        string = 'Year 2K'
        str_number = ''

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_try_str_custom_on_pass_1(self):
        matchblock = MatchBlock('N America', try_str_custom=True)
        string = 'America'
        str_custom = 'north'

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_custom, str_custom)

    def test_matchblock_try_str_custom_off_pass_1(self):
        matchblock = MatchBlock('N America', try_str_custom=False)
        string = 'N America'
        str_custom = ''

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_custom, str_custom)

    def test_matchblock_convert_roman_on_pass_1(self):
        matchblock = MatchBlock('XXI Century', convert_roman=True)
        string = 'Century'
        str_number = '21'

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)

    def test_matchblock_convert_roman_off_pass_1(self):
        matchblock = MatchBlock('XXI Century', convert_roman=False)
        string = 'XXI Century'
        str_number = ''

        self.assertEqual(matchblock.string, string)
        self.assertEqual(matchblock.str_number, str_number)


if __name__ == '__main__':
    unittest.main()
