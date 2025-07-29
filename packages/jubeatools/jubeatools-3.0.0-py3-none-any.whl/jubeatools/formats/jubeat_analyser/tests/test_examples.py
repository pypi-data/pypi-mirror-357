import pytest

from jubeatools.testutils.resources import load_test_file

from . import data


def test_RorataJins_example() -> None:
    """This file has a #memo tag but actually uses mono-column formatting,
    Here I just check that a friendlier error message is sent because there
    is not much else I can to do here, the file is plain old wrong"""
    with pytest.raises(SyntaxError, match="separator line"):
        load_test_file(data, "RorataJin's example.txt")


def test_Booths_of_Fighters_memo() -> None:
    """This file has 2 quirks my code did not anticipate :
    - while it's in #memo2 format, it actually uses b= and t= commands
    - the position and timing parts are separated by some less common
      whitespace character"""
    load_test_file(data, "Booths_of_Fighters_memo.txt")


def test_MTC_Nageki_no_Ki_EXT() -> None:
    """This file is proper euc-kr text that's specially crafted to also be
    compatible with jubeat analyser, handcrafted mojibake and all"""
    load_test_file(data, "MTC_Nageki_no_Ki_EXT.txt")


def test_MTC_Mimi_EXT() -> None:
    """Also an euc-kr file but also has long notes"""
    load_test_file(data, "MTC_Mimi_EXT.txt")


def test_beat_1() -> None:
    """This file uses #bpp=2 with half-width hyphens in the timing part, this
    is bound to fail on the first line that has an odd length when encoded
    to shift-jis, for now I just want to display a friendlier error message"""
    with pytest.raises(SyntaxError, match="Series of notes of odd byte lengths"):
        load_test_file(data, "beat(1).txt")


def test_onnanoko_wa_tsuyoi() -> None:
    """This file uses some commands I had never seen anywhere else, I figured
    we might as well just ignore these and send a warning instead of failing
    with a hard error"""
    with pytest.warns(UserWarning, match="unknown command"):
        load_test_file(data, "女の子は強い_#4.txt")
