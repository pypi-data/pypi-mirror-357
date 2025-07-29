from jubeatools.testutils.resources import load_test_file

from . import data


def test_1_0() -> None:
    """Demo chart from yubiosi's .apk"""
    load_test_file(data, "m1.txt")


def test_1_5() -> None:
    """Transcript of the official chart found on a Czech website :
    http://download.pocitac.com/index.php?dir=JuBeat/Android/"""
    load_test_file(data, "concon (EXT).txt")


def test_2_0() -> None:
    """Custom chart from http://pyagoraa.blog.fc2.com/"""
    song = load_test_file(data, "Oshama Scramble!.ybi")
    assert "EXT" in song.charts
