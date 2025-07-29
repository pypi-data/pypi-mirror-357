import hypothesis.strategies as st
from hypothesis import given

from jubeatools import song
from jubeatools.formats import Format
from jubeatools.testutils import strategies as jbst
from jubeatools.testutils.test_patterns import dump_and_load_then_compare


@st.composite
def iboogie_metadata(draw: st.DrawFn) -> song.Metadata:
    return song.Metadata(
        title=draw(
            st.text(
                alphabet=st.characters(
                    codec="ascii", blacklist_categories=("N", "C", "Po")
                ),
                min_size=1,
            )
        )
    )


@st.composite
def iboogie_song(draw: st.DrawFn) -> song.Song:
    return draw(
        jbst.song(
            common_timing_strat=st.none(),
            common_hakus_strat=st.none(),
            chart_strat=jbst.chart(
                level_strat=st.none(),
                timing_strat=jbst.timing_info(
                    with_bpm_changes=True,
                    beat_zero_offset_strat=st.decimals(
                        min_value=0, max_value=20, places=2
                    ),
                ),
                notes_strat=jbst.notes(note_strat=jbst.tap_note()),
            ),
            metadata_strat=iboogie_metadata(),
        )
    )


@given(iboogie_song())
def test_that_full_chart_roundtrips(chart: song.Song) -> None:
    dump_and_load_then_compare(
        Format.IBOOGIE,
        chart,
        bytes_decoder=lambda b: b.decode("utf-8"),
    )
