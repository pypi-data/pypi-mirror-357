from enum import Enum

from hypothesis import example, given

from jubeatools import song
from jubeatools.formats import Format
from jubeatools.formats.konami.testutils import eve_compatible_song
from jubeatools.testutils.test_patterns import dump_and_load, dump_and_load_then_compare

from ..construct import jbsq
from . import example1


@given(eve_compatible_song())
def test_that_full_chart_roundtrips(song: song.Song) -> None:
    dump_and_load_then_compare(
        Format.JBSQ,
        song,
        bytes_decoder=lambda b: str(jbsq.parse(b)),
        load_options={"beat_snap": 12},
    )


@given(eve_compatible_song())
@example(example1.data)
def test_that_difficulty_name_is_loaded_properly(original_song: song.Song) -> None:
    recovered_song = dump_and_load(
        Format.JBSQ,
        original_song,
        bytes_decoder=lambda b: str(jbsq.parse(b)),
        load_options={"beat_snap": 12},
    )
    original_dif, _ = original_song.charts.popitem()
    recovered_dif, _ = recovered_song.charts.popitem()
    assert type(original_dif) is str
    assert not isinstance(original_dif, Enum)
    assert type(recovered_dif) is str
    assert not isinstance(recovered_dif, Enum)
