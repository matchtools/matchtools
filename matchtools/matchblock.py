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


def check_tolerance(*dec_args):
    """Wrapper checking whether tolerance is within the bounds."""
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'tolerance' in kwargs:
                if lower_bound is not None and upper_bound is None:
                    if kwargs['tolerance'] < lower_bound:
                        msg = 'tolerance must be higher than {}'
                        raise ValueError(msg.format(lower_bound))
                elif lower_bound is None and upper_bound is not None:
                    if kwargs['tolerance'] > upper_bound:
                        msg = 'tolerance must be lower than {}'
                        raise ValueError(msg.format(upper_bound))
                elif lower_bound is not None and upper_bound is not None:
                    if not (lower_bound <= kwargs['tolerance'] <= upper_bound):
                        msg = 'tolerance must be in between {}, and {}'
                        raise ValueError(msg.format(lower_bound, upper_bound))
            return f(*args, **kwargs)
        return wrapped

    if len(dec_args) == 1 and callable(dec_args[0]):
        # no bounds provided
        lower_bound, upper_bound = 0, None
        return wrapper(dec_args[0])

    if len(dec_args) == 2 and callable(dec_args[1]):
        # only lower bound provided
        lower_bound, upper_bound = dec_args[0], None
    elif len(dec_args) == 2:
        # both bounds provided
        lower_bound, upper_bound = dec_args[0], dec_args[1]
    else:
        raise ValueError('too many arguments: {}'.format(dec_args))

    return wrapper


class MatchBlock:
    """Detect and compare different types of data."""
    number_tolerance = 0
    date_tolerance = 0
    coordinates_tolerance = 0
    string_tolerance = 0
    str_number_tolerance = 0
    str_custom_tolerance = 0

    _empty = (None, '', [], float('nan'))

    dictionary = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'dictionary.json')

    def __init__(self, string):
        """Initialise each data type."""
        self.number = None
        self.date = None
        self.coordinates = None
        self.string = ''
        self.str_number = ''
        self.str_custom = ''

        self._extract_data(string)
        self._attributes = (self.number, self.date, self.coordinates,
                            self.string, self.str_number, self.str_custom)

    def __repr__(self):
        """Return object's unambiguous description."""
        return ' '.join(str(attr) for attr in self._attributes
                        if attr not in self._empty)

    def __str__(self):
        """Return object's readable description."""
        names = ('Number', 'Date', 'Coordinates', 'String',
                 'String (number part)', 'String (custom part)')

        values = ', '.join(name + ': ' + str(attr) for name, attr
                           in zip(names, self._attributes)
                           if attr not in self._empty)

        return 'MatchBlock object [{}]'.format(values)

    def __eq__(self, other):
        """Check whether two instances of the class are the same."""
        if not isinstance(other, MatchBlock):
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

        for tol in tols:
            if getattr(self, tol) != getattr(other, tol):
                msg = 'The objects compared have different {}, using {}'
                warnings.warn(msg.format(tol, getattr(self, tol)))

        def compare(func, self_attr, other_attr, tolerance):
            if all(x in self._empty for x in (self_attr, other_attr)):
                return self_attr == other_attr
            elif any(x in self._empty for x in (self_attr, other_attr)):
                return False

            return func(self_attr, other_attr,
                        **{'tolerance': getattr(self, tolerance)})

        return all(compare(*values) for values in
                   zip(funcs, self._attributes, other._attributes, tols))

    def __ne__(self, other):
        """Check whether two instances of the class are different."""
        return not self.__eq__(other)

    def __len__(self):
        """Return the length of the object."""
        return sum(1 for attr in self._attributes if attr not in self._empty)

    def _extract_data(self, string):
        """
        Detect data types in the string supplied, extract each occurrence
        and assign value to the corresponding instance attribute.

        :param string: str
        """

        if isinstance(string, (int, float)):
            self.number = string
        elif isinstance(string, str):
            try:
                self.number = int(string)
            except ValueError:
                try:
                    self.number = float(string)
                except ValueError:
                    self.string, self.coordinates \
                        = self.extract_coordinates(string)
                    self.string, self.date \
                        = self.extract_dates(self.string)

                    self.string = self.roman_to_integers(self.string)

                    self.string, self.str_number \
                        = self.extract_str_number(self.string)
                    self.string, self.str_custom \
                        = self.extract_str_custom(self.string)

                    if self.str_number:
                        self.str_number = self.strip_zeros(self.str_number)
        else:
            raise TypeError('unsupported type(s)')
        return self

    @classmethod
    def check_roman(cls, string):
        """
        Convert the whole input string into roman numeral.

        Use roman (https://pypi.python.org/pypi/roman).

        If it's a valid roman numeral, return it as integer, if not,
        return the input.

        :param string: str
        :rtype: int or str

        :Example:

        >>> MatchBlock.check_roman('VII')
        '7'

        >>> MatchBlock.check_roman('XIIIIX')
        'XIIIIX'

        >>> MatchBlock.check_roman('ABC')
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

        Recognise integers separated by white spaces and non-alphanumeric
        characters.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.integers_to_roman('LIV 4 DOR 3')
        'LIV IV DOR III'
        """

        converted = [roman.toRoman(int(element)) if element.isnumeric()
                     else element for element in cls.split_on_nonalpha(string)]
        return ''.join(converted)

    @classmethod
    def roman_to_integers(cls, string):
        """
        Convert all roman numerals within the string into integers.

        Recognise roman numerals separated by white spaces and non-alphanumeric
        characters.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.roman_to_integers('IV ABC II')
        '4 ABC 2'
        """

        converted = [cls.check_roman(element) for element
                     in cls.split_on_nonalpha(string)]
        return ''.join(converted)

    @classmethod
    def split_on_nonalpha(cls, string):
        """
        Split the input string into a list of alphanumeric
        and non-alphanumeric components.

        :param string: str

        Example:
        >>> MatchBlock.split_on_nonalpha('F.C. Liverpool 1892')
        ['F', '.', 'C', '. ', 'Liverpool', ' ', '1892']
        """

        return re.findall(r'[^0-9a-zA-Z]+|[0-9a-zA-Z]+', string)

    @classmethod
    def strip_zeros(cls, string):
        """
        Strip leading zeros in any number longer than one digit found
        in a string.

        :param string: str
        :rtype: str

        :Example:

        >>> MatchBlock.strip_zeros('Well Z-001')
        'Well Z-1'
        """

        numbers = ''.join(x if x.isdigit() else ' ' for x in string).split()

        for number in numbers:
            if number.startswith('0') and len(number) > 1:
                string = string.replace(number, number.lstrip('0'))

        return string

    @classmethod
    def is_abbreviation(cls, string1, string2):
        """
        Check whether one string is an abbreviation of another.

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
    def dict_sub(cls, string, dictionary=None):
        """
        Substitute string values with values from a dictionary.

        Replace part of the string, separated by non-alphanumeric
        characters, with a key found in a dictionary, if the string part is
        contained within values of the dictionary's key.

        The dictionary must be stored in the JSON format.
        Use the file provided with the package by default.

        :param string: str
        :param dictionary: str
        :rtype: str

        :Example:

        >>> MatchBlock.dict_sub('Troll N')
        'Troll north'
        """

        if dictionary is None:
            dictionary = cls.dictionary

        with open(dictionary, 'r') as file:
            dict_data = json.loads(file.read())

        tokens = []
        buffer = []
        for char in string:
            if char.isalnum():
                buffer.append(char)
            else:
                if buffer:
                    tokens.append(''.join(buffer))
                    buffer.clear()
                tokens.append(char)
        if buffer:
            tokens.append(''.join(buffer))

        for i, token in enumerate(tokens):
            token = token.strip().lower()
            if token == "s" and tokens[i - 1] == "'":
                pass
            else:
                for sub, versions in dict_data.items():
                    for version in versions:
                        if version == token:
                            tokens[i] = sub

        return ''.join(tokens)

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
        for element in dates_with_strings:
            dates.append(element[0])
            strings.append(element[1])
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

        >>> MatchBlock.extract_coordinates('Text part 38.8897,-77.0089')
        ('Text part', (38.8897, -77.0089))

        >>> MatchBlock.extract_coordinates('55.7522200,37.6155600')
        ('', (55.75222, 37.61556))

        >>> MatchBlock.extract_coordinates('Only text 123.45')
        ('Only text 123.45', None)
        """

        pattern = re.compile(r'(-?(90|[0-8]?[0-9]\.[0-9]{0,8})\s*,\s*'
                             r'-?(180|(1[0-7][0-9]|[0-9]{0,2})\.[0-9]{0,8}))')

        check = re.search(pattern, string)
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

        >>> MatchBlock.extract_str_number('Well 1')
        ('Well', '1')

        >>> MatchBlock.extract_str_number('Well 15b')
        ('Well', '15b')

        >>> MatchBlock.extract_str_number('Field')
        ('Field', '')
        """
        new_elements = []
        number = []

        elements = ''.join(x if x.isalnum() else ' ' for x in string).split()

        for element in elements:
            if any(char.isdigit() for char in element):
                number.append(element)
            else:
                new_elements.append(element)

        return ' '.join(new_elements), ' '.join(number)

    @classmethod
    def extract_str_custom(cls, string, dictionary=None):
        """
        Extract all custom values found in a string.

        Look up the values in the supplied dictionary's keys. First prepare
        the string by substituting values found in the dictionary's values with
        corresponding key using dict_sub function.

        Return string and its separated custom parts.

        :param string: str
        :param dictionary: str
        :rtype: tuple

        :Example:

        >>> MatchBlock.extract_str_custom('Well north')
        ('Well', 'north')

        >>> MatchBlock.extract_str_custom('Field West Sud')
        ('Field', 'south west')
        """

        if dictionary is None:
            dictionary = cls.dictionary

        string = cls.dict_sub(string, dictionary=dictionary)
        custom = []

        elements = ''.join(x if x.isalnum() else ' ' for x in string).split()

        with open(dictionary, 'r') as file:
            dict_data = json.loads(file.read())

        for i, element in enumerate(elements):
            for key in dict_data:
                if element.lower() == key:
                    elements[i] = ''
                    custom.append(key)

        return (' '.join(x for x in elements if x != ''),
                ' '.join(sorted(custom)))

    @classmethod
    @check_tolerance
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
    @check_tolerance
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
            else:
                return all(abs((date1_obj - date2_obj).days) <= tolerance
                           for date1_obj, date2_obj in zip(date1, date2))
        else:
            if isinstance(date1, str):
                date1 = datetime.datetime.strptime(date1, pattern)
            if isinstance(date2, str):
                date2 = datetime.datetime.strptime(date2, pattern)

        return abs((date1 - date2).days) <= tolerance

    @classmethod
    @check_tolerance
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

        >>> a, b = (36.611111, 41.886111), (32.383333, 47.390833)
        >>> MatchBlock.compare_coordinates(a, b, tolerance=600, unit='mi')
        True

        >>> a, b = (36.611111, 41.886111), (32.383333, 47.390833)
        >>> MatchBlock.compare_coordinates(a, b, tolerance=100, unit='mi')
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
        except ValueError as error:
            vincenty_err = 'Vincenty formula failed to converge!'
            warning_msg = 'Vincenty formula failed. Using great circle formula'

            if vincenty_err in error.args:
                warnings.warn(warning_msg)
                length = getattr(great_circle(coords1, coords2, *args), unit)
            else:
                raise

        return length <= tolerance

    @classmethod
    @check_tolerance(0, 100)
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

        if tolerance is None:
            if any(char.isdigit() for string in (string1, string2)
                   for char in string):
                tolerance = cls.str_number_tolerance
            else:
                tolerance = cls.string_tolerance

        if cls.is_abbreviation(string1, string2):
            return True

        methods = {'uwratio': fuzz.UWRatio,
                   'partial_ratio': fuzz.partial_ratio,
                   'token_sort_ratio': fuzz.token_sort_ratio,
                   'token_set_ratio': fuzz.token_set_ratio,
                   'ratio': fuzz.ratio}

        if method not in methods:
            msg = 'wrong method; use available: {}'
            raise ValueError(msg.format(', '.join(sorted(methods))))

        return methods[method](string1, string2) >= 100 - tolerance
