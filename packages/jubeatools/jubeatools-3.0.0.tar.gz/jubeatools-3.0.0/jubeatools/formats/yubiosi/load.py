import re
import warnings
from collections import defaultdict
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, NamedTuple, Optional

from jubeatools import song
from jubeatools.formats.load_tools import FolderLoader, make_folder_loader
from jubeatools.formats.timemap import BPMAtSecond, TimeMap
from jubeatools.utils import none_or

from .tools import INDEX_TO_DIF, YUBIOSI_1_0_TO_INDEX


def load_yubiosi_1_0(path: Path, **kwargs: Any) -> song.Song:
    files = load_folder_1_x(path)
    charts = [load_yubiosi_1_0_file(lines) for lines in files.values()]
    return song.Song.from_monochart_instances(*charts)


def load_file_1_x(path: Path) -> list[str]:
    with path.open(encoding="shift-jis-2004") as f:
        return f.read().split("\n")


load_folder_1_x: FolderLoader[list[str]] = make_folder_loader("*.txt", load_file_1_x)


def load_yubiosi_1_0_file(lines: list[str]) -> song.Song:
    (
        title,
        _,  # save data name
        raw_bpm,
        _,  # chart duration in ms
        raw_offset,
        raw_note_count,
        *raw_times_and_positions,
    ) = lines
    note_count = int(raw_note_count)
    if len(raw_times_and_positions) != 2 * note_count:
        raise ValueError(
            "Incorrect line count. The yubiosi file header claims this file "
            f"contains {note_count} notes, this imples the file body should "
            f"have twice as many lines ({note_count * 2}) but found {len(raw_times_and_positions)}"
        )

    bpm = Decimal(raw_bpm)
    offset = song.SecondsTime(raw_offset) / 1000
    timing = song.Timing(
        events=[song.BPMEvent(time=song.BeatsTime(0), BPM=bpm)], beat_zero_offset=offset
    )
    raw_times = raw_times_and_positions[:note_count]
    raw_positions = raw_times_and_positions[note_count:]
    times = [int(t) for t in raw_times]
    positions = [int(p) for p in raw_positions]
    notes = [load_1_0_note(t, p) for t, p in zip(times, positions)]
    chart = song.Chart(level=Decimal(0), timing=timing, notes=notes)
    return song.Song(
        metadata=song.Metadata(title=title),
        charts={song.Difficulty.EXTREME.value: chart},
    )


def load_1_0_note(time: int, position: int) -> song.TapNote:
    time_in_beats = song.BeatsTime(time, 4)
    index = YUBIOSI_1_0_TO_INDEX[position]
    return song.TapNote(
        time=time_in_beats, position=song.NotePosition.from_index(index)
    )


def load_yubiosi_1_5(path: Path, **kwargs: Any) -> song.Song:
    files = load_folder_1_x(path)
    charts = [load_yubiosi_1_5_file(lines) for lines in files.values()]
    return song.Song.from_monochart_instances(*charts)


def load_yubiosi_1_5_file(lines: list[str]) -> song.Song:
    try:
        notes_marker = lines.index("[Notes]")
    except ValueError:
        raise ValueError("No '[Notes]' line found in the file") from None

    tag_lines = lines[:notes_marker]
    note_lines = lines[notes_marker + 1 :]

    tags = dict(iter_tags(tag_lines))
    panel_num = tags.get("PANEL_NUM")
    if panel_num is not None and panel_num != "4x4":
        raise ValueError(f"Unsupported PANEL_NUM : {panel_num}")

    title = tags.get("TITLE_NAME")
    timing = load_timing_data_1_5(tags)
    notes = [load_1_5_note(line) for line in note_lines if line.strip()]
    level = Decimal(tags.get("LEVEL", 0))
    audio = tags.get("AUDIO_FILE")

    return song.Song(
        metadata=song.Metadata(title=title, audio=none_or(Path, audio)),
        charts={
            song.Difficulty.EXTREME.value: song.Chart(
                level=level, timing=timing, notes=notes
            )
        },
    )


TAG_REGEX = re.compile(r"#(?P<key>\w+?):(?P<value>.*)")


def iter_tags(tag_lines: list[str]) -> Iterator[tuple[str, str]]:
    for line in tag_lines:
        if match := TAG_REGEX.fullmatch(line):
            yield match["key"], match["value"]


def load_timing_data_1_5(tags: dict[str, str]) -> song.Timing:
    offset = load_offset(tags)
    events = [replace(e, seconds=e.seconds + offset) for e in iter_bpm_events(tags)]
    return TimeMap.from_seconds(events).convert_to_timing_info()


def load_offset(tags: dict[str, str]) -> Fraction:
    offset_ms = int(tags.get("OFFSET", 0))
    return Fraction(offset_ms, 1000)


def iter_bpm_events(tags: dict[str, str]) -> Iterator[BPMAtSecond]:
    if (raw_bpm_changes := tags.get("BPMS")) is not None:
        yield from iter_bpms_tag(raw_bpm_changes)
    elif (raw_bpm := tags.get("BPM")) is not None:
        yield BPMAtSecond(Fraction(0), Fraction(Decimal(raw_bpm)))
    else:
        raise ValueError("The file is missing either a #BPM or a #BPMS tag")


def iter_bpms_tag(tag_value: str) -> Iterator[BPMAtSecond]:
    for event in tag_value.split(","):
        bpm, ms = event.split("/")
        yield BPMAtSecond(seconds=Fraction(int(ms), 1000), BPM=Fraction(Decimal(bpm)))


def load_1_5_note(line: str) -> song.TapNote:
    raw_time, raw_position = line.split(",")
    return song.TapNote(
        time=song.BeatsTime(int(raw_time), 4),
        position=song.NotePosition.from_index(int(raw_position) - 1),
    )


def load_yubiosi_2_0(path: Path, **kwargs: Any) -> song.Song:
    ybi = find_ybi_file(path)
    header, charts_headers = load_yubiosi_2_0_ybi_file(ybi)
    metadata = load_yubiosi_2_0_metadata(header)
    bpms = list(iter_bpm_events(header))
    ignored_indicies = charts_headers.keys() - INDEX_TO_DIF.keys()
    if ignored_indicies:
        warnings.warn(
            "This file contains [Notes:_] sections with invalid difficulty "
            f"indicies : {ignored_indicies}. [Notes:_] sections with indicies "
            "outside the 1-10 range are ignored."
        )
    charts = {}
    for dif_index in charts_headers.keys() & INDEX_TO_DIF.keys():
        tags = charts_headers[dif_index]
        dif = INDEX_TO_DIF[dif_index]
        chart = load_yubiosi_2_0_chart(tags, bpms, ybi)
        charts[dif] = chart

    return song.Song(metadata=metadata, charts=charts)


def find_ybi_file(path: Path) -> Path:
    if path.is_file():
        if path.suffix != ".ybi":
            warnings.warn(
                "The input file does not have the .ybi extension. Make sure "
                "you gave the path to the metadata file and not the path to "
                "one of the .ybh charts by mistake."
            )
        return path
    elif path.is_dir():
        ybis = list(path.glob("*.ybi"))
        ybis_count = len(ybis)
        if ybis_count > 1:
            raise ValueError(
                "Found multiple .ybi files in the given folder. The given path "
                "should either be a file, or a folder containing only one file "
                "with .ybi extension"
            )
        elif ybis_count == 0:
            raise ValueError(
                "No .ybi files found in the given folder. The given path "
                "should either be a file, or a folder containing only one file "
                "with .ybi extension"
            )
        else:
            return ybis[0]
    else:
        raise ValueError("The source path is neither a file nor a folder")


def load_yubiosi_2_0_ybi_file(
    ybi: Path,
) -> tuple[dict[str, str], dict[int, dict[str, str]]]:
    lines = ybi.read_text(encoding="utf-16").split("\n")
    if not lines:
        raise ValueError("This file is empty")

    warn_for_missing_version_comment(lines)
    chart_headers: defaultdict[int, dict[str, str]] = defaultdict(dict)
    file_header: dict[str, str] = {}
    for dif_index, key, value in iter_section_and_tags(lines):
        if dif_index is None:
            file_header[key] = value
        else:
            chart_headers[dif_index][key] = value

    return file_header, dict(chart_headers)


def warn_for_missing_version_comment(lines: list[str]) -> None:
    if lines[0] != "//Yubiosi 2.0":
        warnings.warn(
            "Unexpected text on the first line of the .ybi file. "
            "The first line should be '//Yubiosi 2.0'"
        )


class TagWithSection(NamedTuple):
    section: Optional[int]
    key: str
    value: str


SECTION_REGEX = re.compile(r"\[Notes:(\d+)\]")


def iter_section_and_tags(lines: list[str]) -> Iterator[TagWithSection]:
    section = None
    for i, line in enumerate(lines, start=1):
        if line.startswith("//"):
            continue
        elif match := SECTION_REGEX.fullmatch(line):
            section = int(match[1])
        elif match := TAG_REGEX.fullmatch(line):
            yield TagWithSection(
                section=section, key=match["key"], value=match["value"]
            )
        elif line.strip():
            warnings.warn(f"Unexpected text on line {i}")


def load_preview_start(val: str) -> Decimal:
    return Decimal(val) / 1000


def load_yubiosi_2_0_metadata(header: dict[str, str]) -> song.Metadata:
    return song.Metadata(
        title=header.get("TITLE_NAME"),
        artist=header.get("ARTIST"),
        audio=none_or(Path, header.get("AUDIO_FILE")),
        cover=none_or(Path, header.get("JACKET")),
        preview=none_or(
            lambda t: song.Preview(start=load_preview_start(t), length=Decimal(15)),
            header.get("BGM_START"),
        ),
    )


def load_yubiosi_2_0_chart(
    tags: dict[str, str], bpms: list[BPMAtSecond], ybi: Path
) -> song.Chart:
    file = ybi.parent / Path(tags["FILE"])
    lines = file.read_text("utf-16").split("\n")
    warn_for_missing_version_comment(lines)
    offset = load_offset(tags)
    timing = TimeMap.from_seconds(
        [replace(e, seconds=e.seconds + offset) for e in bpms]
    ).convert_to_timing_info()
    level = Decimal(tags.get("LEVEL", 0))
    notes = list(iter_yubiosi_2_0_notes(lines))
    return song.Chart(level=level, timing=timing, notes=notes)


def iter_yubiosi_2_0_notes(lines: list[str]) -> Iterator[song.TapNote]:
    for i, line in enumerate(lines, start=1):
        if line.startswith("//"):
            continue
        elif not line.strip():
            continue
        else:
            try:
                yield load_1_5_note(line)
            except Exception:
                warnings.warn(f"Couldn't parse line {i} as a note ... ignoring it")
