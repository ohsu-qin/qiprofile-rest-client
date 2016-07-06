from qirest_client import choices
from nose.tools import assert_equal

class TestChoices(object):
    def test_roman_range_choices(self):
        expected = [('I', 1), ('II', 2), ('III', 3), ('IV', 4)]
        actual = choices.roman_range_choices(1, 5)
        assert_equal(actual, expected)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
