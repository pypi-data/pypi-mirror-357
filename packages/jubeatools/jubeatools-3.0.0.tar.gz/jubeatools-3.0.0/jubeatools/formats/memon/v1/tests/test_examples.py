from jubeatools.testutils.resources import load_test_file

from . import data


def test_Beat_Juggling_Mix() -> None:
    """The loader used to move the common timing into the song timing because
    of a bug"""
    song = load_test_file(data, "Beat Juggling Mix.memon")
    assert song.common_timing is not None
