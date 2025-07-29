import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from hypothesis import strategies as st

from jubeatools import song
from jubeatools.testutils import strategies as jbst


@st.composite
def memo_compatible_metadata(draw: st.DrawFn) -> song.Metadata:
    metadata: song.Metadata = draw(
        jbst.metadata(
            text_strat=jbst.shift_jis_safe_text(), path_strat=jbst.shift_jis_safe_text()
        )
    )
    metadata.preview = None
    metadata.preview_file = None
    return metadata


@st.composite
def memo_compatible_song(draw: st.DrawFn) -> song.Song:
    """Memo only supports one difficulty per file"""
    diff = draw(st.sampled_from(list(d.value for d in song.Difficulty)))
    chart = draw(
        jbst.chart(
            timing_strat=jbst.timing_info(with_bpm_changes=True),
            notes_strat=jbst.notes(),
        )
    )
    metadata: song.Metadata = draw(memo_compatible_metadata())
    return song.Song(
        metadata=metadata,
        charts={diff: chart},
    )


@contextmanager
def temp_file_named_txt() -> Iterator[Path]:
    with tempfile.NamedTemporaryFile(suffix=".txt") as dst:
        yield Path(dst.name)
