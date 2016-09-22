import re
import warnings
from functools import partial

from matchtools.matchblock import MatchBlock


def return_element(word, element):
    """
    Split :word and return the index of :element.
    If :element occurs more than once in :word an index of the first
    instance is returned.

    :param word: str
    :param element: str
    :rtype: int

    :Example:

    >>> return_element('short text', 'short')
    0
    """

    try:
        if word.count(element) > 1:
            warnings.warn("{} occurs more than once in {}".format(element,
                                                                  word))
        word_split = re.findall(r"[0-9a-zA-Z]+", word)
        position = word_split.index(element)
    except ValueError:
        raise ValueError('{} not in {}'.format(element, word.split()))
    else:
        return position


def move_element(word, element, where):
    """
    This is a low-level function, use move_element_to_front
    and move_element_to_back to transform your input.

    :Example:

    >>> move_element_to_front('A B C', 2)
    'C A B'

    >>> move_element_to_back('A B C', 0)
    'B C A'

    This function moves :element of a :word to the front/back depending on
    :where parameter.
    If a string is used as :element return_element() is triggered to
    determine the position of :element within the word.
    If an integer is used as :element it must reflect the position of :element
    withing the :word split by non-alphanumeric character e.g.
    'Block-A 1' -> ['Block, 'A', '1']
    The function converts all sequences of non-alphanumeric characters
    into single whitespaces.

    :param word: str
    :param element: str(gets converted to int by return_element()) or int
    :param where: str, 'front' or 'back'
    :rtype: str

    :Example:

    >>> move_element('A B C', 'B', 'front')
    'B A C'

    >>> move_element('A B C', 1, 'back')
    'A C B'
    """

    if isinstance(element, str):
        element = return_element(word, element)

    word_split = re.findall(r"[0-9a-zA-Z]+", word)
    if len(word_split) <= element:
        raise IndexError

    if where == 'front':
        moved = [word_split[element]] + word_split[:element] \
                + word_split[element + 1:]
    elif where == 'back':
        moved = word_split[:element] + word_split[element + 1:] \
                + [word_split[element]]
    else:
        raise ValueError('wrong direction; use available: back, front')

    return ' '.join(moved)


def match_rows(row1, row2):
    """
    Compare rows by transforming each pair of values into MatchBlock objects
    and perform equality check on them.
    If all checks resulted in True, the rows are considered to match.

    :param row1: list, tuple
    :param row2: list, tuple
    :rtype: bool

    :Example:

    >>> match_rows(['Well 1', 5, '1 May 2015'], ['Well 01', 5, '2015-05-01'])
    True

    >>> match_rows(['Well 1', 5, '1 May 2015'], ['Well 01', 6, '2015-05-01'])
    False
    """

    if len(row1) != len(row2):
        return False

    return all(MatchBlock(value1) == MatchBlock(value2)
               for value1, value2 in zip(row1, row2))


def match_find(row, rows):
    """
    Run match_rows for row and each element within rows.
    Return the first matching element.

    :param row: list, tuple
    :param rows: nested list, nested tuple
    :rtype: list

    :Example:

    >>> row = ['Well 1', 100]
    >>> rows = [['Well 2', 100], ['Well 1', 100], ['Well 3', 100]]
    >>> match_find(row, rows)
    ['Well 1', 100]
    """

    for element in rows:
        if match_rows(row, element):
            return element


def match_find_all(row, rows):
    """
    Run match_rows for row and each element within rows.
    Return list containing all matching elements.

    :param row: list, tuple
    :param rows: nested list, nested tuple
    :rtype: list

    :Example:

    >>> row = ['Well 1', 100]
    >>> rows = [['Well 1', 100], ['Well 2', 100], ['Well 1', 100]]
    >>> match_find_all(row, rows)
    [['Well 1', 100], ['Well 1', 100]]
    """

    return [element for element in rows if match_rows(row, element)]


move_element_to_front = partial(move_element, where='front')
move_element_to_back = partial(move_element, where='back')
