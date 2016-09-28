# Matchtools

Streamline data matching and integration processes. Compare strings or even rows containing different kinds of data and use specific tolerance for each kind.

### Requirements
- Python 3.5 or higher
- [datefinder](https://github.com/akoumjian/datefinder)
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
- [geopy](https://github.com/geopy/geopy)
- [roman](https://pypi.python.org/pypi/roman)

### Installation
```python
>>> pip install matchtools
```

### Documentation

Please  refer to the [documentation](http://matchtools.readthedocs.io/en/latest/index.html) for the [API](http://matchtools.readthedocs.io/en/latest/api.html) description and more real life examples given in the [cookbook](http://matchtools.readthedocs.io/en/latest/cookbook.html).

### Usage

The matching process is handled by [MatchBlock](http://matchtools.readthedocs.io/en/latest/api.html#matchblock.MatchBlock) class.

When instantiated, MatchBlock object tries to automatically guess and extract following data types from a supplied *string*, *int* or *float* and saves it as an instance attribute:

* **number** – only if int or float were supplied (for number extracted from a string see below)
* **date** – as [datetime](https://docs.python.org/3.6/library/datetime.html#datetime-objects) object, extracted from a string
* **coordinates** – latitude and longitude, separated by comma, extracted from a string
* **string** – any amount of chars extracted from a string
* **str_number** – any number or char with number attached, extracted from a string
* **str_custom** – gets filled with value from a dictionary during string substitution operation

When MatchBlock objects compared, each data type from both objects gets compared to the corresponding type of another object. To determine if the pair of data types is a match, each type uses tolerance parameter, which should be set beforehand.

* **number_tolerance** – absolute difference between numbers compared to tolerance
* **date_tolerance** - difference between two dates compared to tolerance set in days
* **coordinates_tolerance** - distance between two points in km (by default) compared to tolerance
* **string_tolerance** - difference between two strings using fuzzywuzzy's UWRatio method (by default) compared to tolerance
* **str_number_tolerance** - same as **string_tolerance** but for numbers and chars with numbers
* **str_custom_tolerance** - same as **string_tolerance** but for strings obtained through substitution

If all of the data types are matched, two MatchBlock objects are considered as a match.

MatchBlock also has some useful class methods for string [transformations](http://matchtools.readthedocs.io/en/latest/cookbook.html#data-manipulation) which can be used alone.

### Examples

```python
>>> from matchtools import MatchBlock
```

##### Comparison

* Two strings containing *string* and *string number* data types:

```python
>>> MatchBlock('New York 35') == MatchBlock('35 new-york')
True
```

* Two strings containing *string* and *date* data types:

```python
MatchBlock('Madrid_2016-09-05') == MatchBlock('5_Sep_2016_madrid')
True
```

##### Data manipulation

Standardise names in pandas DataFrame using MatchBlock class methods:

```python
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
```

```python
          Name Standardized
0   nord IV N1   north N1 4
1  west 3 W001    west W1 3
2     e 02 E01    east E1 2
3     sud 1 S1   south S1 1
```

##### Data matching

Find record from a dataset that matches input record:

```python
from matchtools import MatchBlock, match_find

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

print(match_find(record_a, records_b))
````

```python
['Name 11', 15, '6 May 2015', '36.611111, 41.886111']
```
