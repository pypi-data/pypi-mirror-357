import pytest

from jubeatools import song
from jubeatools.formats.konami.commons import ticks_to_seconds
from jubeatools.formats.timemap import TimeMap
from jubeatools.testutils.resources import load_test_file

from . import data


def test_that_loading_a_file_with_duplicate_tempo_events_emits_warning() -> None:
    """This file has duplicate TEMPO lines, it's weird how long it took us to
    notice that official data could have this issue.
    Make sure we send a warning and we only keep the BPM change of the
    last duplicate TEMPO line"""
    with pytest.warns(UserWarning, match="Duplicate TEMPO event"):
        example_song = load_test_file(data, "351450202_ext.eve")

    timing = example_song.charts[song.Difficulty.EXTREME].timing
    assert timing is not None  # This is to help mypy
    time_map = TimeMap.from_timing(timing)
    assert time_map.bpm_at_seconds(ticks_to_seconds(20394)) == 185
    assert time_map.bpm_at_seconds(ticks_to_seconds(42423)) == 190
