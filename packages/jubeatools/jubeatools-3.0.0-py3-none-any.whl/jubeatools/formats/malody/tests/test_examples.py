from jubeatools.testutils.resources import load_test_file

from . import data


def test_MilK() -> None:
    """An actual malody chart will have may keys unspecified in the marshmallow
    schema, these should be ignored"""
    load_test_file(data, "1533908574.mc")
