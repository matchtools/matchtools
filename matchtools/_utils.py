import re
import warnings
from functools import partial

from ._matchblock import MatchBlock

__all__ = ['return_element', 'match_rows', 'match_find', 'match_find_all',
           'move_element_to_front', 'move_element_to_back']


def return_element(word, element):
    """
    Split word and return the index of element.

    If element occurs more than once in the word, an index of the first
    instance is returned.

    :param word: str
    :param element: str
    :rtype: int

    :Example:

    >>> return_element('South America', 'America')
    1
    """

    try:
        if word.count(element) > 1:
            warnings.warn(
                "{} occurs more than once in {}".format(element, word))

        word_split = re.findall(r"[a-zA-Z0-9']+", word)
        position = word_split.index(element)

    except ValueError:
        raise ValueError('{} not in {}'.format(element, word.split()))
    else:
        return position


def move_element(word, element, where):
    """
    Low-level function for move_element_to_front and move_element_to_back.

    Move element of a word to the front/back depending on where parameter.

    If a string is used as element, return_element function is triggered to
    determine the position of element within the word.

    If an integer is used as element, it must reflect the position of element
    within the word split by non-alphanumeric character e.g.
    'Block-A 1' -> ['Block, 'A', '1']

    The function converts all sequences of non-alphanumeric characters
    into single whitespaces.

    :param word: str
    :param element: str (gets converted to int by return_element()) or int
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
        raise ValueError("wrong direction, use available: 'back', 'front'")

    return ' '.join(moved)


def match_rows(row1, row2):
    """
    Compare rows by transforming each pair of values into MatchBlock objects
    and perform equality check on them.

    The rows are considered to match if all checks result in True.

    :param row1: list, tuple
    :param row2: list, tuple
    :rtype: bool

    :Example:

    >>> row1 = ['Flight 1', 5, '1 May 2015']
    >>> row2 = ['Flight 01', 5, '2015-05-01']
    >>> match_rows(row1, row2)
    True

    >>> row1 = ['Flight 2', 5, '1 May 2015']
    >>> row2 = ['Flight 02', 6, '2015-05-01']
    >>> match_rows(row1, row2)
    False
    """

    if len(row1) != len(row2):
        return False

    return all(MatchBlock(x) == MatchBlock(y) for x, y in zip(row1, row2))


def match_find(row, rows):
    """
    Search list of rows and return first successful match with the input row.

    :param row: list, tuple
    :param rows: nested list, nested tuple
    :rtype: list

    :Example:

    >>> row = ['Flight 3', 100]
    >>> rows = [['Flight 1', 100], ['Flight 2', 100], ['Flight 3', 100]]
    >>> match_find(row, rows)
    ['Flight 3', 100]
    """

    for element in rows:
        if match_rows(row, element):
            return element


def match_find_all(row, rows):
    """
    Search list of rows and return all successful matches with the input row.

    :param row: list, tuple
    :param rows: nested list, nested tuple
    :rtype: list

    :Example:

    >>> row = ['Flight 2', 100]
    >>> rows = [['Flight 1', 100], ['Flight 2', 100], ['Flight 2', 100]]
    >>> match_find_all(row, rows)
    [['Flight 2', 100], ['Flight 2', 100]]
    """

    return [element for element in rows if match_rows(row, element)]


move_element_to_front = partial(move_element, where='front')
move_element_to_front.__name__ = 'move_element_to_front'
move_element_to_front.__doc__ = """
    Move element of a word to front.

    If a string is used as element, return_element function is triggered to
    determine the position of element within the word.

    If an integer is used as element, it must reflect the position of element
    within the word split by non-alphanumeric character e.g.
    'Block-A 1' -> ['Block, 'A', '1']

    The function converts all sequences of non-alphanumeric characters
    into single whitespaces.

    :param word: str
    :param element: str (gets converted to int by return_element()) or int
    :rtype: str

    :Example:

    >>> move_element_to_front('A B C', 2)
    'C A B'
    """

move_element_to_back = partial(move_element, where='back')
move_element_to_back.__name__ = 'move_element_to_back'
move_element_to_back.__doc__ = """
    Move element of a word to back.

    If a string is used as element, return_element function is triggered to
    determine the position of element within the word.

    If an integer is used as element, it must reflect the position of element
    within the word split by non-alphanumeric character e.g.
    'Block-A 1' -> ['Block, 'A', '1']

    The function converts all sequences of non-alphanumeric characters
    into single whitespaces.

    :param word: str
    :param element: str (gets converted to int by return_element()) or int
    :rtype: str

    :Example:

    >>> move_element_to_back('A B C', 0)
    'B C A'
    """
