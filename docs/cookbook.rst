Cookbook
========

Matchtools is a package written to streamline data matching and
integration processes.
This document contains an overview of the package's functionalities.
It is divided into three parts:

1. Data manipulation.

2. Compare single records.

3. Compare multiple records.

The first part presents how to use the package to perform some specific
data operations. Integrating data from different sources often requires
similar set of normalising steps - standardising numbers, removing
linguistic or conventional differences etc. Matchtools package provides
functionalities to automate that.

The second part introduces the matchtools methodology of finding
matching records in different sets. It includes two examples of how to
use the package to compare single records - e.g. checking whether two
strings or lists can be considered as equal. It also shows how to set up
different types of tolerance.

The third part shows how to use matchtools to find matching records
within nested lists.

The cookbook also includes a description of the way the package handles non-alphanumeric characters in versions 0.1.x

    >>> from matchtools import *

1. Data manipulation
--------------------

**Working with roman numerals**

Convert roman numerals to numbers:

    >>> caesar = 'Pro multitudine autem hominum et pro gloria belli atque fortitudinis angustos se fines habere arbitrabantur, qui in longitudinem milia passuum CCXL, in latitudinem CLXXX patebant.'
    >>> MatchBlock.roman_to_integers(caesar)
    'Pro multitudine autem hominum et pro gloria belli atque fortitudinis angustos se fines habere arbitrabantur, qui in longitudinem milia passuum 240, in latitudinem 180 patebant.'

Convert numbers to roman numerals:

    >>> caesar = 'They thought, that considering the extent of their population, and their renown for warfare and bravery, they had but narrow limits, although they extended in length 240, and in breadth 180 [Roman] miles.'
    >>> MatchBlock.integers_to_roman(caesar)
    'They thought, that considering the extent of their population, and their renown for warfare and bravery, they had but narrow limits, although they extended in length CCXL, and in breadth CLXXX [Roman] miles.'

**Working with zeros**

One of the most common data manipulation tasks when working on data
integration. It is often the case that 'Record 1' and 'Record 0001'
refer to the same object:

    >>> record_with_zeros = 'ABC 001 DEF 2 GHI 03'
    >>> MatchBlock.strip_zeros(record_with_zeros)
    'ABC 1 DEF 2 GHI 3'

**Checking if a word is an abbreviation of another word**

    >>> MatchBlock.is_abbreviation('Federal Bureau of Investigation', 'FBI')
    True

**Replacing words with their standardised forms**

When integrating data coming from different sources, some linguistic,
spelling or conventional inconsistencies are likely to occur. Such
situation often takes place when data contain cardinal directions. For
example, it probably makes sense to standardize *vest*, *w*, as well as
*zapad* (rus.) or *ouest* (fr.) as *west*. The package uses a predefined
set of standardised forms, see the documentation of MatchBlock.dict\_sub
to learn how to provide a user-defined one.

 >>> MatchBlock.dict_sub("there's a feeling I get when I look to the W")
 "there's a feeling I get when I look to the west"

**Moving elements of a string**

Matchtools package contains functions to move text elements to the
beginning or the end of a string. You can specify the element to move by
its name or position:

    >>> move_element_to_front('London E1 United Kingdom', 1)
    'E1 London United Kingdom'

    >>> move_element_to_back('London E1 United Kingdom', 'E1')
    'London United Kingdom E1'

**Example: standardising names in pandas DataFrame**

.. code:: python

    from matchtools import MatchBlock, move_element_to_back
    import pandas as pd
    
    input_data = [('nord IV N1'), ('west 3 W001'), ('e 02 E01'), ('sud 1 S1')]
    
    df = pd.DataFrame(input_data, columns = ['Name'])
    
    def standardize(element):
        element = move_element_to_back(element, 1)
        element = MatchBlock.dict_sub(element)
        element = MatchBlock.roman_to_integers(element)
        element = MatchBlock.strip_zeros(element)
        return element
    
    df['Standardized'] = df.apply(lambda row: standardize(row['Name']), axis=1)

    print(df)

.. parsed-literal::

              Name Standardized
    0   nord IV N1   north N1 4
    1  west 3 W001    west W1 3
    2     e 02 E01    east E1 2
    3     sud 1 S1   south S1 1

2. Compare single records
-------------------------

**Specifying tolerance**

Specifying tolerance for each data type is a crucial part of the
process. This is how we define what similarity criteria two MatchBlock
objects must fulfil in order to be considered as equal. MatchBlock class
allows the following tolerances:

+-------------------+-------------------------------------------------------+
| property name     | description                                           |
+===================+=======================================================+
| number\_tolerance | expressed in numbers. No maximum value. Default: 0.   |
+-------------------+-------------------------------------------------------+
| date\_tolerance   | expressed in numbers (days). No maximum value.        |
|                   | Default: 0.                                           |
+-------------------+-------------------------------------------------------+
| coordinates\_tol\ | expressed in numbers (kilometers, see the             |
| erance            | documentation MatchBlock.compare\_coordinates to      |
|                   | learn how to use different units. No maximum value.   |
|                   | Default: 0.                                           |
+-------------------+-------------------------------------------------------+
| string\_tolerance | expressed in numbers (Levenshtein distance when       |
|                   | calculating uwratio from fuzzywuzzy package, see the  |
|                   | documentation of MatchBlock.compare\_strings to learn |
|                   | how to use different algorithms). Maximum value: 100. |
|                   | Default: 0                                            |
+-------------------+-------------------------------------------------------+
| str\_number\_tol\ | Same as string\_tolerance. Used only for the numeric  |
| erance            | components of a string                                |
+-------------------+-------------------------------------------------------+

**Example 1: Comparing single MatchBlock objects**

This is a basic example of matchtool's main functionality. It shows how
to determine whether two string objects are the same, given the
tolerances specified.

.. note::
    Comparing two MatchBlock objects triggers the following data
    manipulation methods on both of them, there's no need to execute them
    before the comparison: roman\_to\_integers, strip\_zeros, is\_abbreviation,
    dict\_sub.
..

    >>> object1 = MatchBlock('WOJCIOW 11 DEV 07-NOV-86')
    >>> object2 = MatchBlock('WOJCIOW 12 DEV 01-NOV-86')
    >>> print(object1)
    MatchBlock object [Date: [datetime.datetime(1986, 11, 7, 0, 0)], String: WOJCIOW DEV, String (number part): 11]
    >>> print(object2)
    MatchBlock object [Date: [datetime.datetime(1986, 11, 1, 0, 0)], String: WOJCIOW DEV, String (number part): 12]

We created two MatchBlock objects. We can see how the input string has
been split into date, text and text-number components. Now, let's set
some tolerance values and perform a comparison:

    >>> MatchBlock.date_tolerance = 7
    >>> MatchBlock.number_tolerance = 0
    >>> MatchBlock.str_number_tolerance = 0
    >>> object1 == object2
    False

We can see that the objects are considered as different. While the
tolerance set for dates is probably high enough it looks that there is
still too much difference in the numeric components of the objects:

    >>> MatchBlock.number_tolerance = 1
    >>> object1 == object2
    False

Still false. This is because the numeric parts of the objects come from
a string, not an integer or float. Therefore we need to specify the
str\_number\_tolerance appropriately. A thing to remember,
str\_number\_tolerance is a Levenshtein distance tolerance. That's why
setting it to 1 wouldn't be enough in this case. We use
number\_tolerance when working with numbers that are not extracted from
strings and that tolerance is simply a distance between numbers in
integers. The next section includes such objects.

    >>> MatchBlock.str_number_tolerance = 50
    >>> object1 == object2
    True

**Example 2: Comparing two lists**

In a real work situation you will probably want to perform more complex
analysis. For example, you may want to determine whether a record from
Database A is equal to a record from Database B. This can be achieved with
match\_rows() function.

    >>> record_1 = ['Well 1', 5, '1 May 2015']
    >>> record_2 = ['Well 01', 10, '2015-05-01']
    >>> MatchBlock.number_tolerance = 10
    >>> match_rows(record_1, record_2)
    True

3. Compare multiple records
---------------------------

Matchtools include two functions to perform matching on a list of
records:

* match\_find() takes an input record, compares it to a set of records and
  returns the first matching object
* match\_find\_all() does the same but returns a list of all matching objects

.. code:: python

    from matchtools import MatchBlock, match_find, match_find_all

    MatchBlock.number_tolerance = 10
    MatchBlock.date_tolerance = 5
    MatchBlock.coordinates_tolerance = 0
    MatchBlock.string_tolerance = 0
    MatchBlock.str_number_tolerance = 0
        
    record_a = ['Name 11', 5, '1 May 2015', '36.611111, 41.886111']
    
    records_b = [['Name 1', 5, '1 May 2015', '36.611111, 41.886111'],
                 ['Name 11', 7, '1 May 2016', '36.611111, 41.886111'],
                 ['Name 11', 15, '6 May 2015','36.611111, 41.886111'],
                 ['Name 11', 15, '1 May 2015', '36.611111, 41.886111']]
..

    >>> match_find(record_a, records_b)
    ['Name 11', 15, '6 May 2015', '36.611111, 41.886111']

    >>> match_find_all(record_a, records_b)
    [['Name 11', 15, '6 May 2015', '36.611111, 41.886111'], ['Name 11', 15, '1 May 2015', '36.611111, 41.886111']]

Handling non-alphanumeric characters
------------------------------------

.. warning::
    In versions 0.1.x matchtools replaces non-alphanumeric characters with a
    single white space. In some situations this may result in some
    apparently matching records being unmatched.
..

    >>> print(MatchBlock('A-1'))
    MatchBlock object [String: A, String (number part): 1]

    >>> print(MatchBlock('A1'))
    MatchBlock object [String (number part): A1]

    >>> MatchBlock('A-1') == MatchBlock('A1')
    False

It is advised to examine, and when necessary, manipulate the datasets
compared, before using the package's matching methodology:

    >>> dataset1 = [['lfc1', '01-May-2001'], ['lfc2', '02-May-2002'], ['lfc3', '03-May-2003']]
    >>> dataset2 = [['lfc/2', '02-May-2002'], ['lfc/3', '03-May-2003'], ['lfc/1', '01-May-2001']]
    >>> dataset2 = [[name.replace('/',''), date] for name, date in dataset2]
    >>> dataset2
    [['lfc2', '02-May-2002'], ['lfc3', '03-May-2003'], ['lfc1', '01-May-2001']]

.. code:: python

    for record in dataset1:
        matching = match_find(record, dataset2)
        print("dataset1: {}, dataset2: {}".format(record, matching))

.. parsed-literal::

    dataset1: ['lfc1', '01-May-2001'], dataset2: ['lfc1', '01-May-2001']
    dataset1: ['lfc2', '02-May-2002'], dataset2: ['lfc2', '02-May-2002']
    dataset1: ['lfc3', '03-May-2003'], dataset2: ['lfc3', '03-May-2003']

.. note::
    The way the package handles non-alphanumeric characters might change
    in v.0.2.0.
