from fractions import Fraction
from math import ceil
from pathlib import Path
from typing import Any, Iterator, List, Sequence, Union
from uuid import uuid4

from jubeatools import song as jbt
from jubeatools.formats.dump_tools import (
    FileNameFormat,
    make_dumper_from_chart_file_dumper,
)
from jubeatools.formats.filetypes import ChartFile
from jubeatools.formats.timemap import TimeMap
from jubeatools.info import __repository_url__, __version__
from jubeatools.utils import clamp, fraction_to_decimal

from .tools import INDEX_TO_YUBIOSI_1_0


def _dump_yubiosi_1_0(song: jbt.Song, **kwargs: dict) -> List[ChartFile]:
    res = []
    for dif, chart, timing in song.iter_charts_with_applicable_timing():
        if any(isinstance(n, jbt.LongNote) for n in chart.notes):
            raise ValueError("yubiosi 1.0 does not support long notes")

        if len(timing.events) != 1:
            raise ValueError("yubiosi 1.0 does not support BPM changes")

        if any((n.time.denominator not in (1, 2, 4)) for n in chart.notes):
            raise ValueError("yubiosi 1.0 only supports 16th notes")

        timemap = TimeMap.from_timing(timing)
        sorted_notes = sorted(chart.notes, key=lambda n: n.time)
        if sorted_notes:
            last_note = sorted_notes[-1]
            chart_duration = ceil(timemap.seconds_at(last_note.time) * 1000)
        else:
            chart_duration = 0

        header = [
            song.metadata.title or "",
            "",  # save data name
            timing.events[0].BPM,
            chart_duration,  # chart duration in ms
            int(timing.beat_zero_offset * 1000),
            len(chart.notes),
        ]
        times = [int(note.time * 4) for note in sorted_notes]
        positions = [INDEX_TO_YUBIOSI_1_0[note.position.index] for note in sorted_notes]
        chart_lines = header + times + positions
        chart_text = "\n".join(map(str, chart_lines))
        chart_bytes = chart_text.encode("shift-jis-2004")
        res.append(ChartFile(chart_bytes, song, dif, chart))

    return res


dump_yubiosi_1_0 = make_dumper_from_chart_file_dumper(
    internal_dumper=_dump_yubiosi_1_0, file_name_template="{title}.txt"
)


def _dump_yubiosi_1_5(song: jbt.Song, **kwargs: dict) -> List[ChartFile]:
    res = []
    for dif, chart, timing in song.iter_charts_with_applicable_timing():
        if any(isinstance(n, jbt.LongNote) for n in chart.notes):
            raise ValueError("yubiosi 1.5 does not support long notes")

        if any((n.time.denominator not in (1, 2, 4)) for n in chart.notes):
            raise ValueError("yubiosi 1.5 only supports 16th notes")

        header = list(iter_header_lines_1_5(song.metadata, chart, timing))
        # redundant type check to placate mypy
        notes = [dump_note_1_5(n) for n in chart.notes if isinstance(n, jbt.TapNote)]
        chart_lines = header + ["", "[Notes]"] + notes
        chart_text = "\n".join(map(str, chart_lines))
        chart_bytes = chart_text.encode("shift-jis-2004")
        res.append(ChartFile(chart_bytes, song, dif, chart))

    return res


dump_yubiosi_1_5 = make_dumper_from_chart_file_dumper(
    internal_dumper=_dump_yubiosi_1_5, file_name_template="{title}.txt"
)

TAG_ORDER_1_5 = [
    "TITLE_NAME",
    "DATA_ID",
    "BPMS",
    "MUSIC_TIME",
    "OFFSET",
    "LEVEL",
    "PANEL_NUM",
    "AUDIO_FILE",
]


def iter_header_lines_1_5(
    metadata: jbt.Metadata, chart: jbt.Chart, timing: jbt.Timing
) -> Iterator[str]:
    tags = compute_header_tags_1_5(metadata, chart, timing)
    for key in TAG_ORDER_1_5:
        if key in tags:
            yield dump_tag(key, tags[key])


def dump_tag(key: str, value: str) -> str:
    return f"#{key}:{value}"


def compute_header_tags_1_5(
    metadata: jbt.Metadata, chart: jbt.Chart, timing: jbt.Timing
) -> dict[str, str]:
    timemap = TimeMap.from_timing(timing)
    sorted_notes = sorted(chart.notes, key=lambda n: n.time)
    if sorted_notes:
        last_note = sorted_notes[-1]
        chart_duration = ceil(timemap.seconds_at(last_note.time) * 1000)
    else:
        chart_duration = 0

    tags = {
        "DATA_ID": uuid4().hex,  # just use something unique
        "BPMS": dump_bpms(timemap, Fraction(timing.beat_zero_offset)),
        "MUSIC_TIME": chart_duration,
        "OFFSET": int(timing.beat_zero_offset * 1000),
        "PANEL_NUM": "4x4",
    }

    if metadata.title is not None:
        tags["TITLE_NAME"] = metadata.title

    if chart.level is not None:
        tags["LEVEL"] = clamp(int(chart.level), 1, 10)

    if metadata.audio is not None:
        tags["AUDIO_FILE"] = metadata.audio

    return {k: str(v) for k, v in tags.items()}


def dump_bpms(timemap: TimeMap, offset: Fraction) -> str:
    return ",".join(
        dump_bpm_event(e.BPM, e.seconds - offset) for e in timemap.events_by_seconds
    )


def dump_bpm_event(bpm: Fraction, seconds: Fraction) -> str:
    d_bpm = fraction_to_decimal(bpm)
    ms = int(seconds * 1000)
    return f"{d_bpm}/{ms}"


def dump_note_1_5(note: jbt.TapNote) -> str:
    time = int(note.time * 4)
    position = note.position.index + 1
    return f"{time},{position}"


def dump_yubiosi_2_0(song: jbt.Song, path: Path, **kwargs: dict) -> dict[Path, bytes]:
    info_file_name_format = FileNameFormat.from_path(
        path, default_filename_format="{title}.ybi"
    )
    ybi_path = info_file_name_format.available_song_filename(song)
    taken_filenames = {ybi_path}
    edits = list(song.edit_diffs())
    if len(edits) > 7:
        raise ValueError(
            f"This song has too many edit difficulties ({len(edits)}), yubiosi "
            "2.0 only supports 7 per song."
        )

    chart_paths = {}
    chart_path_suggestion = path.with_suffix(".ybh") if not path.is_dir() else path
    chart_file_name_format = FileNameFormat.from_path(
        chart_path_suggestion, default_filename_format="{title}[{difficulty}].ybh"
    )
    for dif, chart in song.charts.items():
        chart_filename = chart_file_name_format.available_chart_filename(
            song, dif, chart, already_chosen=taken_filenames
        )
        taken_filenames.add(chart_filename)
        chart_paths[dif] = chart_filename

    files = {ybi_path: dump_yubiosi_2_0_info_file(song, edits, chart_paths)}
    for dif, chart in song.charts.items():
        chart_path = chart_paths[dif]
        files[chart_path] = dump_yubiosi_2_0_chart_file(chart.notes)

    return files


def dump_yubiosi_2_0_info_file(
    song: jbt.Song, edits: list[str], chart_filenames: dict[str, Path]
) -> bytes:
    song.minimize_timings()
    if len(song.charts) > 1 and any(c.timing is not None for c in song.charts.values()):
        raise ValueError("Yubiosi 2.0 does not support per-chart timing")

    if len(song.charts) == 1:
        timing = next(iter(song.charts.values())).timing or song.common_timing
    else:
        timing = song.common_timing

    if timing is None:
        raise ValueError("No timing info")

    lines = [
        "//Yubiosi 2.0",
        f"// Converted using jubeatools {__version__}",
        f"// {__repository_url__}",
    ]
    lines.extend(iter_header_lines_2_0(song, timing))
    diffs_order = list(j.value for j in jbt.Difficulty) + sorted(edits)
    for i, dif in enumerate(diffs_order, start=1):
        if (chart := song.charts.get(dif)) is not None:
            filename = chart_filenames[dif]
            lines += dump_chart_section(chart, i, filename, timing.beat_zero_offset)

    return "\n".join(lines).encode("utf-16")


TAG_ORDER_2_0 = ["TITLE_NAME", "ARTIST", "BPMS", "AUDIO_FILE", "JACKET", "BGM_START"]


def iter_header_lines_2_0(song: jbt.Song, timing: jbt.Timing) -> Iterator[str]:
    tags = compute_header_tags_2_0(song, timing)
    for key in TAG_ORDER_2_0:
        if key in tags:
            yield dump_tag(key, tags[key])


def compute_header_tags_2_0(song: jbt.Song, timing: jbt.Timing) -> dict[str, str]:
    tags: dict[str, Any] = {}
    if song.metadata.title is not None:
        tags["TITLE_NAME"] = song.metadata.title

    if song.metadata.artist is not None:
        tags["ARTIST"] = song.metadata.artist

    timemap = TimeMap.from_timing(timing)
    tags["BPMS"] = dump_bpms(timemap, Fraction(timing.beat_zero_offset))

    if song.metadata.audio is not None:
        tags["AUDIO_FILE"] = song.metadata.audio

    if song.metadata.cover is not None:
        tags["JACKET"] = song.metadata.cover

    if song.metadata.preview is not None:
        tags["BGM_START"] = dump_bgm_start(song.metadata.preview.start)

    return {k: str(v) for k, v in tags.items()}


def dump_bgm_start(start: jbt.SecondsTime) -> str:
    return str(int(start * 1000))


def dump_chart_section(
    chart: jbt.Chart, index: int, path: Path, offset: jbt.SecondsTime
) -> list[str]:
    return [
        f"[Notes:{index}]",
        dump_tag("FILE", path.name),
        dump_tag("LEVEL", str(clamp(int(chart.level or 0), 1, 99))),
        dump_tag("OFFSET", str(int(offset * 1000))),
    ]


def dump_yubiosi_2_0_chart_file(
    notes: Sequence[Union[jbt.TapNote, jbt.LongNote]]
) -> bytes:
    if any(isinstance(n, jbt.LongNote) for n in notes):
        raise ValueError("yubiosi 2.0 does not support long notes")

    if any((n.time.denominator not in (1, 2, 4)) for n in notes):
        raise ValueError("yubiosi 2.0 only supports 16th notes")

    # redundant type check to placate mypy
    note_lines = [dump_note_1_5(n) for n in notes if isinstance(n, jbt.TapNote)]
    lines = ["//Yubiosi 2.0"] + note_lines
    return "\n".join(lines).encode("utf-16")
