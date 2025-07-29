from io import StringIO
from itertools import chain
from pathlib import Path
from typing import Any, Dict

from more_itertools import windowed
from sortedcontainers import SortedKeyList

from jubeatools.formats.dump_tools import FileNameFormat
from jubeatools.formats.jubeat_analyser.dump_tools import SortedDefaultDict
from jubeatools.info import __repository_url__, __version__
from jubeatools.song import BeatsTime, Chart, LongNote, Song, Timing

from .dump import Frame, Memo2Section, StopEvent


def dump_iboogie_chart(chart: Chart, timing: Timing) -> bytes:
    def make_section(b: BeatsTime) -> Memo2Section:
        return Memo2Section(
            # Skip "x" here to avoid collision with the empty beat symbol
            note_symbols=list("123456789abcdefghijklmnopqrstuvwyz"),
            empty_beat_symbol="-",
            frame_factory=lambda: Frame(
                empty_position_symbol="x",
                spacing="",
            ),
        )

    sections = SortedDefaultDict(make_section)

    timing_events = sorted(timing.events, key=lambda e: e.time)
    notes = SortedKeyList(set(chart.notes), key=lambda n: n.time)
    all_events = SortedKeyList(timing_events + notes, key=lambda n: n.time)
    last_event = all_events[-1]
    last_measure = last_event.time // 4
    for i in range(last_measure + 1):
        beat = BeatsTime(4) * i
        sections.add_key(beat)

    # Timing events
    sections[BeatsTime(0)].events.append(
        StopEvent(BeatsTime(0), timing.beat_zero_offset)
    )
    for event in timing_events:
        section_beat = event.time - (event.time % 4)
        sections[section_beat].events.append(event)

    # Fill sections with notes
    for key, next_key in windowed(chain(sections.keys(), [None]), 2):
        assert key is not None
        sections[key].notes = list(
            notes.irange_key(min_key=key, max_key=next_key, inclusive=(True, False))
        )

    file = StringIO()
    file.write(f"// Converted using jubeatools {__version__}\n")
    file.write(f"// {__repository_url__}\n\n")
    file.write("\n\n".join(section.render() for _, section in sections.items()))

    return file.getvalue().encode("utf-8")


def _raise_if_chart_unfit_for_iboogie(chart: Chart, timing: Timing) -> None:
    if len(timing.events) < 1:
        raise ValueError("No BPM found in file") from None

    first_bpm = min(timing.events, key=lambda e: e.time)
    if first_bpm.time != 0:
        raise ValueError("First BPM event does not happen on beat zero")

    if any(isinstance(note, LongNote) for note in chart.notes):
        raise ValueError("iboogie does not support long notes")


def _raise_if_unfit_for_iboogie(song: Song) -> None:
    if next(song.edit_diffs(), None) is not None:
        raise ValueError("iboogie does not support edit diffs")

    for _, chart, timing in song.iter_charts_with_applicable_timing():
        _raise_if_chart_unfit_for_iboogie(chart, timing)


def choose_chart_filename_format(path: Path) -> FileNameFormat:
    if path.is_dir():
        return FileNameFormat(parent=path, name_format="{title}{difficulty_index}.txt")
    else:
        return FileNameFormat(
            parent=path.parent,
            name_format=f"{path.stem}{{difficulty_index}}{path.suffix}",
        )


def dump_iboogie(song: Song, path: Path, **kwargs: Any) -> Dict[Path, bytes]:
    _raise_if_unfit_for_iboogie(song)

    files: Dict[Path, bytes] = {}
    title_filename_format = FileNameFormat.from_path(
        path, default_filename_format="{title}.txt"
    )
    chart_filename_format = choose_chart_filename_format(path)
    title_filename = title_filename_format.available_song_filename(song)
    taken_filenames = {title_filename}
    files[title_filename] = (song.metadata.title or "").encode("utf-8")
    for dif, chart, timing in song.iter_charts_with_applicable_timing():
        chart_filename = chart_filename_format.available_chart_filename(
            song, dif, chart, already_chosen=taken_filenames
        )
        taken_filenames.add(chart_filename)
        files[chart_filename] = dump_iboogie_chart(chart, timing)

    return files
