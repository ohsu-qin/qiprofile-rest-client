"""
Choice utility functions.
"""

def max_length(choices):
    """
    Returns the size of the longest choice.
    
    :param: the available choice strings or tuples
    :return: the maximum length
    """
    def length(item):
        if isinstance(item, str):
            value = item
        else:
            value = item[0]
        return len(value)
    
    return max((length(c) for c in choices))


def roman_range_choices(start, stop):
    """
    Returns the (arabic number, roman numeral) choice tuples
    for the given exclusive range bounds. This is useful, e.g.,
    for displaying the tumor stage. (Yes, this is the 21st
    century).
     
    Example:

    >>> from qirest_client import choices
    >>> choices.roman_range_choices(1, 5)
    [('I', 1), ('II', 2), ('III', 3), ('IV', 4)]
    
    :param start: the first value in the range
    :param stop: one greater than the last value in the range
    :param roman: flag indicating whether the display value
        is a roman numeral
    :return: the [(value, label)] choices list
    :raise ValueError: if the *roman* flag is set and start
        is less than one or stop is greater than five
    """
    return [(_roman(v), v) for v in range(start, stop)]


def _roman(n):
    """
    :param n: the input integer
    :return the roman numeral
    :raise ValueError: if the input integer is not a positive
        integer less than five
    """
    if n not in range(1, 5):
        raise ValueError("The roman numeral converter is not supported"
                         " for the value %d" % n)
    if n == 4:
        return 'IV'
    else:
        return 'I' * n
