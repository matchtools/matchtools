import datetime
import json
import os
import re
import warnings
from functools import wraps

import datefinder
import roman
from fuzzywuzzy import fuzz
from geopy.distance import great_circle
from geopy.distance import vincenty

__all__ = ['MatchBlock']


def tolerance_interval(lower=0, upper=None):
    """Decorator checking whether tolerance is within the boundaries."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'tolerance' in kwargs:
                if lower is not None and upper is None:
                    if kwargs['tolerance'] < lower:
                        msg = 'tolerance must be higher than {}'
                        raise ValueError(msg.format(lower))

                elif lower is None and upper is not None:
                    if kwargs['tolerance'] > upper:
                        msg = 'tolerance must be lower than {}'
                        raise ValueError(msg.format(upper))

                elif lower is not None and upper is not None:
                    if not (lower <= kwargs['tolerance'] <= upper):
                        msg = 'tolerance must be in between {}, and {}'
                        raise ValueError(msg.format(lower, upper))
            return f(*args, **kwargs)
        return wrapper

    if callable(lower):
        func, lower = lower, 0
        return decorator(func)
    return decorator


class Tolerance:
    """Tolerance attributes descriptor."""

    def __init__(self, attribute):
        self.attribute = '_' + attribute

    def __get__(self, instance, owner):
        if not hasattr(owner, self.attribute):
            setattr(owner, self.attribute, 0)
        return getattr(owner, self.attribute)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("tolerance can't be negative")
        setattr(type(instance), self.attribute, value)


class MatchBlock:
    """
    Core class that contains all methods for data extraction, processing,
    and comparison.

    """

    number_tolerance = Tolerance('number_tolerance')
    date_tolerance = Tolerance('date_tolerance')
    coordinates_tolerance = Tolerance('coordinates_tolerance')
    string_tolerance = Tolerance('string_tolerance')
    str_number_tolerance = Tolerance('str_number_tolerance')
    str_custom_tolerance = Tolerance('str_custom_tolerance')

    _null = (None, '', [], float('nan'))

    _re_non_alphanum_all = re.compile("([^a-zA-Z0-9']+)")
    _re_non_alphanum = re.compile("[^a-zA-Z0-9']+")
    _re_spaces = re.compile("[\s_]+")
    _re_digits_or_alpha = re.compile("\d+|[a-zA-Z]+")
    _re_digits = re.compile("\d+")
    _re_coordinates = re.compile("(-?(90|[0-8]?[0-9]\.[0-9]{0,8})\s*,\s*-?"
                                 "(180|(1[0-7][0-9]|[0-9]{0,2})\.[0-9]{0,8}))")

    _dictionary = {}
    _dictionary_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'dictionary.json')

    def __init__(self, entry, *, try_date=True, try_coordinates=True,
                 try_str_number=True, try_str_custom=True, convert_roman=True):
        """
        Initialize new object, try to extract known data types from supplied
        entry.

        :param entry: str, int, float
        """

        self._number = None
        self._date = []
        self._coordinates = None
        self._string = ''
        self._str_number = ''
        self._str_custom = ''

        if isinstance(entry, (int, float)):
            self._number = entry
        elif isinstance(entry, str):
            try:
                self._number = int(entry)
            except ValueError:
                try:
                    self._number = float(entry)
                except ValueError:
                    if entry and try_coordinates:
                        entry, self._coordinates = self.extract_coordinates(
                            entry)

                    if entry and try_date:
                        entry, self._date = self.extract_dates(entry)

                    if entry and convert_roman:
                        entry = self.roman_to_integers(entry)

                    if entry and try_str_number:
                        entry, self._str_number = self.extract_str_number(entry)

                        if self._str_number:
                            self._str_number = self.strip_zeros(
                                self._str_number)

                    if entry and try_str_custom:
                        entry, self._str_custom = self.extract_str_custom(entry)

                    self._string = entry
        else:
            raise TypeError('unsupported type(s)')

    @property
    def attributes(self):
        return (self._number, self._date, self._coordinates,
                self._string, self._str_number, self._str_custom)

    @property
    def number(self):
        return self._number

    @property
    def date(self):
        return self._date

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def string(self):
        return self._string

    @property
    def str_number(self):
        return self._str_number

    @property
    def str_custom(self):
        return self._str_custom

    def __repr__(self):
        names = ('number', 'date', 'coordinates', 'string',
                 'string (number part)', 'string (custom part)')

        values = []
        for i, (name, attr) in enumerate(zip(names, self.attributes)):
            if attr not in self._null:
                values.append(
                    name + ': ' + (str(attr) if i != 1
                                   else ' '.join(str(x.date()) for x in attr)))

        return '<{} object at {}: {}>'.format(
            type(self).__name__, hex(id(self)), ', '.join(values))

    def __str__(self):
        values = []
        for i, attr in enumerate(self.attributes):
            if attr not in self._null:
                values.append(str(attr) if i != 1
                              else ' '.join(str(x.date()) for x in attr))

        return ' '.join(values)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError('unsupported operand type(s)')

        if self.__len__() != len(other):
            return False

        funcs = (self.compare_numbers,
                 self.compare_dates,
                 self.compare_coordinates,
                 self.compare_strings,
                 self.compare_strings,
                 self.compare_strings)

        tols = ('number_tolerance',
                'date_tolerance',
                'coordinates_tolerance',
                'string_tolerance',
                'str_number_tolerance',
                'str_custom_tolerance')

        for func, self_attr, other_attr, tol in zip(
                funcs, self.attributes, other.attributes, tols):

            if self_attr in self._null and other_attr in self._null:
                continue
            elif self_attr in self._null or other_attr in self._null:
                return False

            if not func(
                    self_attr, other_attr, **{'tolerance': getattr(self, tol)}):
                return False
        else:
            return True

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return sum(1 for attr in self.attributes if attr not in self._null)

    @classmethod
    def _read_dictionary(cls, file):
        with open(file, 'r') as f:
            return {k: set(v) for k, v in json.loads(f.read()).items()}

    @classmethod
    def from_roman(cls, string):
        """
        Convert the whole input string from roman to arabic numeral.

        Use roman (https://pypi.python.org/pypi/roman).

        Return result if conversion was successful, otherwise return input.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.from_roman('VII')
        '7'

        >>> MatchBlock.from_roman('XIIIIX')
        'XIIIIX'

        >>> MatchBlock.from_roman('ABC')
        'ABC'
        """

        try:
            return str(roman.fromRoman(string))
        except roman.InvalidRomanNumeralError:
            return string

    @classmethod
    def integers_to_roman(cls, string):
        """
        Convert all integers within the string into roman numerals.

        Recognise integers separated by non-alphanumeric characters.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.integers_to_roman('LIV 4 DOR 3')
        'LIV IV DOR III'
        """

        return ''.join(roman.toRoman(int(x)) if x.isnumeric() else x
                       for x in cls.split_on_nonalpha(string))

    @classmethod
    def roman_to_integers(cls, string):
        """
        Convert all roman numerals within the string into integers.

        Recognise roman numerals separated by non-alphanumeric characters.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.roman_to_integers('IV ABC II')
        '4 ABC 2'
        """

        return ''.join(cls.from_roman(x) for x in cls.split_on_nonalpha(string))

    @classmethod
    def split_on_nonalpha(cls, string, return_all=True):
        """
        Split the input string into a list of alphanumeric and non-alphanumeric
        components.

        If return_all is False return list with alphanumeric components of the
        string only.

        :param string: str
        :param return_all: bool
        :rtype: list

        :Example:

        >>> MatchBlock.split_on_nonalpha('F.C. Liverpool', return_all=True)
        ['F', '.', 'C', '. ', 'Liverpool']

        >>> MatchBlock.split_on_nonalpha('F.C. Liverpool', return_all=False)
        ['F', 'C', 'Liverpool']
        """

        if return_all:
            return cls._re_non_alphanum_all.split(string)

        return cls._re_non_alphanum.split(string)

    @classmethod
    def strip_zeros(cls, string):
        """
        Strip leading zeros in any number longer than one digit found
        in a string.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.strip_zeros('Agent 007')
        'Agent 7'
        """

        numbers = cls._re_digits.findall(string)

        for number in numbers:
            if number.startswith('0') and len(number) > 1:
                string = string.replace(number, number.lstrip('0'))

        return string

    @classmethod
    def is_abbreviation(cls, string1, string2):
        """
        Check whether one string is an abbreviation of the other.

        :param string1: str
        :param string2: str
        :rtype: bool

        :Example:

        >>> MatchBlock.is_abbreviation('Federal Bureau of Investigation', 'FBI')
        True
        """

        skip = ('a', 'an', 'and', 'of', 'the')

        string1 = string1.strip().lower()
        string2 = string2.strip().lower()

        abbr, name = sorted((string1, string2), key=lambda x: len(x))

        if len(name.split()) < 2:
            return False

        abbr_try = ''.join(x[0] for x in name.split() if x not in skip)
        return abbr == abbr_try

    @classmethod
    def dict_sub(cls, string, dictionary_file=None):
        """
        Substitute string values with values from a dictionary.

        Replace part of the string, separated by non-alphanumeric
        characters, with a key found in a dictionary, if the string part is
        contained within values of the dictionary's key.

        The dictionary must be stored in the JSON format.
        Use the file provided with the package by default.

        :param string: str
        :param dictionary_file: str
        :rtype: str

        :Example:

        >>> MatchBlock.dict_sub('S Africa')
        'south Africa'
        """

        if dictionary_file is None:
            if not cls._dictionary:
                cls._dictionary = cls._read_dictionary(cls._dictionary_file)

            dictionary = cls._dictionary
        else:
            dictionary = cls._read_dictionary(dictionary_file)

        words = cls.split_on_nonalpha(string, return_all=True)

        for i, word in enumerate(words):
            for substitute, replacements in dictionary.items():
                if word.lower() in replacements:
                    words[i] = substitute
                    break

        return ''.join(words)

    @classmethod
    def extract_dates(cls, string):
        """
        Extract dates from text.

        Use datefinder (https://pypi.python.org/pypi/datefinder).

        :param string: str
        :rtype: tuple

        :Example:

        >>> MatchBlock.extract_dates('Istanbul 25 May 2005 ')
        ('Istanbul', [datetime.datetime(2005, 5, 25, 0, 0)])
        """

        dates_with_strings = list(
            datefinder.find_dates(string, source=True, strict=True))

        dates, strings = [], []

        for date_element, string_element in dates_with_strings:
            dates.append(date_element)
            strings.append(string_element)

        for string_element in strings:
            string = string.replace(string_element, '')

        return string.strip(), dates

    @classmethod
    def extract_coordinates(cls, string):
        """
        Extract pair of coordinates (latitude and longitude, separated by
        comma) from a string.

        If found, return remains of original string and tuple with coordinates,
        otherwise return original string and None.

        :param string: str
        :rtype: tuple

        :Example:

        >>> MatchBlock.extract_coordinates('Washington 38.8897, -77.0089')
        ('Washington', (38.8897, -77.0089))

        >>> MatchBlock.extract_coordinates('55.7522200,37.6155600')
        ('', (55.75222, 37.61556))

        >>> MatchBlock.extract_coordinates('Richmond 123.45')
        ('Richmond 123.45', None)
        """

        check = cls._re_coordinates.search(string)

        if check:
            lt, lg = check.group().split(',')
            lt, lg = float(lt), float(lg)
            return string.replace(check.group(), '').strip(), (lt, lg)
        else:
            return string, None

    @classmethod
    def extract_str_number(cls, string):
        """
        Extract all numeric elements found in a string. Consider an element
        to be a numeric if it contains at least one digit.

        Return string and its separated numeric parts.

        :param string: str
        :rtype: tuple

        :Example:

        >>> MatchBlock.extract_str_number('Jamaica 1')
        ('Jamaica', '1')

        >>> MatchBlock.extract_str_number('Jamaica 1X')
        ('Jamaica', '1X')

        >>> MatchBlock.extract_str_number('Jamaica')
        ('Jamaica', '')
        """

        new_string = []
        number = []

        words = cls._re_non_alphanum.split(string)

        for word in words:
            if any(char.isdigit() for char in word):
                number.append(word)
            else:
                new_string.append(word)

        return ' '.join(new_string), ' '.join(number)

    @classmethod
    def extract_str_custom(cls, string, dictionary_file=None):
        """
        Extract all custom values found in a string.

        Look up the values in the supplied dictionary's keys. First prepare
        the string by substituting values found in the dictionary's values with
        corresponding key using dict_sub function.

        Return string and its separated custom parts.

        :param string: str
        :param dictionary_file: str
        :rtype: tuple

        :Example:

        >>> MatchBlock.extract_str_custom('East Timor')
        ('Timor', 'east')

        >>> MatchBlock.extract_str_custom('Sud Ouest France')
        ('France', 'south west')
        """

        if dictionary_file is None:
            if not cls._dictionary:
                cls._dictionary = cls._read_dictionary(cls._dictionary_file)

            dictionary = cls._dictionary
        else:
            dictionary = cls._read_dictionary(dictionary_file)

        string_sub = cls.dict_sub(string, dictionary_file=dictionary_file)

        words = cls.split_on_nonalpha(string_sub, return_all=False)
        custom = []

        for i, word in enumerate(words):
            if word.lower() in dictionary:
                words[i] = ''
                custom.append(word.lower())

        return ' '.join(x for x in words if x != ''), ' '.join(sorted(custom))

    @classmethod
    @tolerance_interval
    def compare_numbers(cls, number1, number2, *, tolerance=None):
        """
        Check if the numbers provided are within the specified tolerance.

        Return True if yes, otherwise return False.

        :param number1: number
        :param number2: number
        :param tolerance: number
        :rtype: bool

        :Example:

        >>> MatchBlock.compare_numbers(1, 10, tolerance=10)
        True

        >>> MatchBlock.compare_numbers(1, 10, tolerance=5)
        False
        """

        if tolerance is None:
            tolerance = cls.number_tolerance

        return abs(number1 - number2) <= tolerance

    @classmethod
    @tolerance_interval
    def compare_dates(cls, date1, date2, *, tolerance=None, pattern='%d-%b-%Y'):
        """
        Check if the dates provided are within the specified tolerance.

        Return True if yes, otherwise return False.

        If lists of dates are provided check if they are of the same length.

        If yes, check whether the difference between each element of list1
        and the corresponding element of list2 is within the specified
        tolerance.

        :param date1: datetime.datetime object or a list of such objects
        :param date2: datetime.datetime object or a list of such objects
        :param tolerance: number
        :param pattern: str
        :rtype: bool

        :Example:

        >>> date1 = datetime.datetime(2005, 5, 25, 0, 0)
        >>> date2 = datetime.datetime(2005, 5, 26, 0, 0)
        >>> MatchBlock.compare_dates(date1, date2, tolerance=1)
        True

        >>> date1 = [datetime.datetime(2005, 5, 26, 0, 0)]
        >>> date2 = [datetime.datetime(2006, 5, 25, 0, 0)]
        >>> MatchBlock.compare_dates(date1, date2, tolerance=1)
        False
        """

        if tolerance is None:
            tolerance = cls.date_tolerance

        if isinstance(date1, list) and isinstance(date2, list):
            if len(date1) != len(date2):
                return False

            return all(abs((date1_obj - date2_obj).days) <= tolerance
                       for date1_obj, date2_obj in zip(date1, date2))
        else:
            if isinstance(date1, str):
                date1 = datetime.datetime.strptime(date1, pattern)
            if isinstance(date2, str):
                date2 = datetime.datetime.strptime(date2, pattern)

        return abs((date1 - date2).days) <= tolerance

    @classmethod
    @tolerance_interval
    def compare_coordinates(cls, coords1, coords2, *args, tolerance=None,
                            unit='km', **kwargs):
        """
        Check if a distance between the pairs of coordinates provided is
        within the specified tolerance.

        Return True if yes, otherwise return False.

        Use geopy (https://pypi.python.org/pypi/geopy).

        Try to use Vincenty formula, if error occurs use Great Circle formula.

        :param coords1: pair of coordinates - a tuple of two numbers
        :param coords2: pair of coordinates - a tuple of two numbers
        :param tolerance: number
        :param unit: str, one of: 'kilometers', 'km', 'meters',
                                  'm', 'miles', 'mi', 'feet',
                                  'ft', 'nautical', 'nm'
        :rtype: bool

        :Example:

        >>> a, b = (36.1332600, -5.4505100), (35.8893300, -5.3197900)
        >>> MatchBlock.compare_coordinates(a, b, tolerance=20, unit='mi')
        True

        >>> a, b = (36.1332600, -5.4505100), (35.8893300, -5.3197900)
        >>> MatchBlock.compare_coordinates(a, b, tolerance=1, unit='mi')
        False
        """

        if tolerance is None:
            tolerance = cls.coordinates_tolerance

        units = {'kilometers', 'km', 'meters', 'm', 'miles', 'mi',
                 'feet', 'ft', 'nautical', 'nm'}

        unit = unit.strip().lower()
        if unit not in units:
            raise ValueError('unsupported unit')

        try:
            length = getattr(vincenty(coords1, coords2, *args, **kwargs), unit)
        except ValueError as e:
            if 'Vincenty formula failed to converge!' in e.args:
                warnings.warn(
                    'vincenty formula failed, using great circle formula')
                length = getattr(great_circle(coords1, coords2, *args), unit)
            else:
                raise

        return length <= tolerance

    @classmethod
    @tolerance_interval(0, 100)
    def compare_strings(cls, string1, string2, *, tolerance=None,
                        method='uwratio'):
        """
        Check if the strings provided have a similarity ratio within the
        specified tolerance.

        Return True if yes, otherwise return False.

        Use fuzzywuzzy (https://pypi.python.org/pypi/fuzzywuzzy).

        :param string1: str
        :param string2: str
        :param tolerance: number
        :param method: str, one of: 'uwratio', 'partial_ratio',
                                    'token_sort_ratio', 'token_set_ratio',
                                    'ratio'
        :rtype: bool

        :Example:

        >>> MatchBlock.compare_strings('Beatles', 'The Beatles', tolerance=10)
        True

        >>> MatchBlock.compare_strings('AB', 'AC', tolerance=0, method='ratio')
        False
        """

        str_number = any(
            char.isdigit() for string in (string1, string2) for char in string)

        if tolerance is None:
            if str_number:
                tolerance = cls.str_number_tolerance
            else:
                tolerance = cls.string_tolerance

        if not str_number:
            if cls.is_abbreviation(string1, string2):
                return True

        methods = {'uwratio': fuzz.UWRatio,
                   'partial_ratio': fuzz.partial_ratio,
                   'token_sort_ratio': fuzz.token_sort_ratio,
                   'token_set_ratio': fuzz.token_set_ratio,
                   'ratio': fuzz.ratio}

        if method not in methods:
            msg = 'wrong method, use available: {}'
            raise ValueError(msg.format(', '.join(sorted(methods))))

        return methods[method](string1, string2) >= 100 - tolerance
