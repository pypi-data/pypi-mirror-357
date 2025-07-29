from decimal import Decimal
from functools import partial
from pathlib import Path

from hypothesis import example, given
from hypothesis import strategies as st

from jubeatools import song
from jubeatools.formats import Format
from jubeatools.formats.yubiosi.dump import dump_bgm_start
from jubeatools.formats.yubiosi.load import load_preview_start
from jubeatools.testutils import strategies as jbst
from jubeatools.testutils.test_patterns import dump_and_load_then_compare

from . import example1


@st.composite
def metadata_1_0(draw: st.DrawFn) -> song.Metadata:
    return song.Metadata(title=draw(jbst.shift_jis_safe_text()))


just_16ths = partial(jbst.beat_time, denominator_strat=st.just(4))


@st.composite
def yubiosi_1_0_song(draw: st.DrawFn) -> song.Song:
    """Yubiosi 1.0 files are very limited :
    - one chart
    - no dif info
    - only 16th notes
    - only tap notes
    - no bpm changes
    - only a title
    """
    return draw(
        jbst.song(
            diffs_strat=st.just(set([song.Difficulty.EXTREME.value])),
            common_timing_strat=st.none(),
            common_hakus_strat=st.none(),
            chart_strat=jbst.chart(
                level_strat=st.just(Decimal(0)),
                timing_strat=jbst.timing_info(with_bpm_changes=False),
                notes_strat=jbst.notes(
                    note_strat=jbst.tap_note(time_strat=just_16ths()),
                    beat_time_strat=just_16ths(),
                ),
            ),
            metadata_strat=metadata_1_0(),
        )
    )


@given(yubiosi_1_0_song())
def test_that_full_chart_roundtrips_1_0(s: song.Song) -> None:
    dump_and_load_then_compare(
        Format.YUBIOSI_1_0,
        s,
        bytes_decoder=lambda b: b.decode("shift-jis-2004"),
    )


@st.composite
def metadata_1_5(draw: st.DrawFn) -> song.Metadata:
    return song.Metadata(
        title=draw(jbst.shift_jis_safe_text()),
        audio=Path(draw(jbst.shift_jis_safe_text())),
    )


@st.composite
def safe_bpms(draw: st.DrawFn) -> Decimal:
    """Draw from a selection of bpms with a finite decimal expansion and whole
    number of ms per 1/4 note"""
    val = draw(
        st.sampled_from(
            [
                "75",
                "78.125",
                "93.75",
                "100",
                "117.1875",
                "120",
                "125",
                "150",
                "156.25",
                "187.5",
                "200",
                "234.375",
                "250",
            ]
        )
    )
    return Decimal(val)


@st.composite
def yubiosi_1_5_song(draw: st.DrawFn) -> song.Song:
    """Yubiosi 1.5 files are a bit less restricted :
    - integer level in the 1-10 range
    - bpm changes allowed
    - audio path
    """
    return draw(
        jbst.song(
            diffs_strat=st.just(set([song.Difficulty.EXTREME.value])),
            common_timing_strat=st.none(),
            common_hakus_strat=st.none(),
            chart_strat=jbst.chart(
                level_strat=st.integers(min_value=1, max_value=10),
                timing_strat=jbst.timing_info(
                    with_bpm_changes=True,
                    bpm_strat=safe_bpms(),
                    beat_zero_offset_strat=st.decimals(
                        min_value=0, max_value=20, places=2
                    ),
                    time_strat=just_16ths(min_section=1),
                ),
                notes_strat=jbst.notes(
                    note_strat=jbst.tap_note(time_strat=just_16ths()),
                    beat_time_strat=just_16ths(),
                ),
            ),
            metadata_strat=metadata_1_5(),
        )
    )


@given(yubiosi_1_5_song())
def test_that_full_chart_roundtrips_1_5(s: song.Song) -> None:
    dump_and_load_then_compare(
        Format.YUBIOSI_1_5, s, bytes_decoder=lambda b: b.decode("shift-jis-2004")
    )


@st.composite
def yubiosi_diffs(draw: st.DrawFn) -> set[str]:
    normal_diffs = draw(
        st.sets(
            st.sampled_from(list(d.value for d in song.Difficulty)),
            min_size=0,
            max_size=3,
        )
    )
    if not normal_diffs:
        min_edits = 1
    else:
        min_edits = 0

    edits = draw(st.integers(min_value=min_edits, max_value=7))
    return normal_diffs | {f"EDIT-{i + 1}" for i in range(edits)}


seconds_time = partial(
    st.decimals,
    min_value=0,
    max_value=10**25,
    allow_nan=False,
    allow_infinity=False,
    places=2,
)


@st.composite
def metadata_2_0(draw: st.DrawFn) -> song.Metadata:
    return song.Metadata(
        title=draw(jbst.metadata_text()),
        artist=draw(jbst.metadata_text()),
        audio=Path(draw(jbst.metadata_path())),
        cover=Path(draw(jbst.metadata_path())),
        preview=song.Preview(
            start=draw(seconds_time()),
            length=Decimal(15),
        ),
        preview_file=None,
    )


@st.composite
def yubiosi_2_0_song(draw: st.DrawFn) -> song.Song:
    """Yubiosi 2.0 files have more stuff :
    - utf-16 support
    - artist tag
    - jacket tag
    - audio tag
    - preview start tag
    - sets of charts, with the usual 3 difficulties + 7 optional edits
    - integer levels extented to the 1-99 range
    """
    return draw(
        jbst.song(
            diffs_strat=yubiosi_diffs(),
            common_timing_strat=jbst.timing_info(
                with_bpm_changes=True,
                bpm_strat=safe_bpms(),
                beat_zero_offset_strat=st.decimals(min_value=0, max_value=20, places=2),
                time_strat=just_16ths(min_section=1),
            ),
            common_hakus_strat=st.none(),
            chart_strat=jbst.chart(
                level_strat=st.integers(min_value=1, max_value=99),
                timing_strat=st.none(),
                notes_strat=jbst.notes(
                    note_strat=jbst.tap_note(time_strat=just_16ths()),
                    beat_time_strat=just_16ths(),
                ),
            ),
            metadata_strat=metadata_2_0(),
        )
    )


@given(seconds_time())
def test_that_bgm_start_roundtrips(expected: Decimal) -> None:
    text = dump_bgm_start(expected)
    actual = load_preview_start(text)
    assert actual == expected


@given(yubiosi_2_0_song())
@example(example1.data)
def test_that_full_chart_roundtrips_2_0(s: song.Song) -> None:
    dump_and_load_then_compare(
        Format.YUBIOSI_2_0, s, bytes_decoder=lambda b: b.decode("utf-16")
    )
