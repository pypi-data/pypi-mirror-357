import json
import re
from functools import wraps
from io import StringIO
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Type

from .format_names import Format


def guess_format(path: Path) -> Format:
    """Try to guess the format of the given file, raise an exception if the
    format is unknown"""
    if path.is_dir():
        raise ValueError("Can't guess chart format for a folder")

    contents = path.read_bytes()

    return guess_file_format(contents)


def guess_file_format(contents: bytes) -> Format:
    try:
        return recognize_json_formats(contents)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        pass

    try:
        return recognize_jubeat_analyser_format(contents)
    except (UnicodeError, ValueError):
        pass

    if looks_like_eve(contents):
        return Format.EVE

    if looks_like_jbsq(contents):
        return Format.JBSQ

    if looks_like_yubiosi_1_0(contents):
        return Format.YUBIOSI_1_0

    if looks_like_yubiosi_1_5(contents):
        return Format.YUBIOSI_1_5

    if looks_like_yubiosi_2_0(contents):
        return Format.YUBIOSI_2_0

    if looks_like_iboogie(contents):
        return Format.IBOOGIE

    raise ValueError("Unrecognized file format")


def recognize_json_formats(contents: bytes) -> Format:
    obj = json.loads(contents)

    if not isinstance(obj, dict):
        raise ValueError("Top level value is not an object")

    if obj.keys() & {"metadata", "data", "version"}:
        return recognize_memon_version(obj)
    elif obj.keys() >= {"meta", "time", "note"}:
        return Format.MALODY
    else:
        raise ValueError("Unrecognized file format")


def recognize_memon_version(obj: dict) -> Format:
    try:
        version = obj["version"]
    except KeyError:
        return Format.MEMON_LEGACY

    if version == "0.1.0":
        return Format.MEMON_0_1_0
    elif version == "0.2.0":
        return Format.MEMON_0_2_0
    elif version == "0.3.0":
        return Format.MEMON_0_3_0
    elif version == "1.0.0":
        return Format.MEMON_1_0_0
    else:
        raise ValueError(f"Unsupported memon version : {version}")


JUBEAT_ANALYSER_COMMANDS = {
    "b",
    "m",
    "o",
    "r",
    "t",
    "#lev",
    "#dif",
    "#title",
    "#artist",
}

COMMENT = re.compile(r"//.*")


def _dirty_jba_line_strip(line: str) -> str:
    """This does not deal with '//' in quotes properly,
    thankfully we don't care when looking for an argument-less command"""
    return COMMENT.sub("", line).strip()


def recognize_jubeat_analyser_format(contents: bytes) -> Format:
    text = contents.decode(encoding="shift-jis-2004", errors="surrogateescape")
    lines = text.splitlines()

    saw_jubeat_analyser_commands = False
    for raw_line in lines:
        line = _dirty_jba_line_strip(raw_line)
        if line in ("#memo2", "#boogie"):
            return Format.MEMO_2
        elif line == "#memo1":
            return Format.MEMO_1
        elif line == "#memo":
            return Format.MEMO
        elif "=" in line:
            index = line.index("=")
            if line[:index] in JUBEAT_ANALYSER_COMMANDS:
                saw_jubeat_analyser_commands = True

    if saw_jubeat_analyser_commands:
        return Format.MONO_COLUMN
    else:
        raise ValueError("Unrecognized file format")


def false_if_raises(
    *exceptions: Type[Exception],
) -> Callable[[Callable[..., bool]], Callable[..., bool]]:
    def decorator(f: Callable[..., bool]) -> Callable[..., bool]:
        @wraps(f)
        def wrapper(*a: Any, **kw: Any) -> bool:
            try:
                return f(*a, **kw)
            except Exception as e:
                if exceptions and not isinstance(e, exceptions):
                    raise
                else:
                    return False

        return wrapper

    return decorator


@false_if_raises(UnicodeError, StopIteration)
def looks_like_eve(contents: bytes) -> bool:
    f = StringIO(contents.decode("ascii"))
    return looks_like_eve_line(f.readline())


EVE_COMMANDS = {
    "END",
    "MEASURE",
    "HAKU",
    "PLAY",
    "LONG",
    "TEMPO",
}


def looks_like_eve_line(line: str) -> bool:
    columns = line.split(",")
    if len(columns) != 3:
        return False

    raw_tick, raw_command, raw_value = map(str.strip, columns)
    try:
        int(raw_tick)
    except Exception:
        return False

    if raw_command not in EVE_COMMANDS:
        return False

    try:
        int(raw_value)
    except Exception:
        return False

    return True


def looks_like_jbsq(contents: bytes) -> bool:
    magic = contents[:4]
    return magic in (b"IJBQ", b"IJSQ", b"JBSQ")


@false_if_raises(UnicodeError, ValueError)
def looks_like_yubiosi_1_0(contents: bytes) -> bool:
    lines = contents.decode(encoding="shift-jis-2004").splitlines()
    (
        _,  # title
        _,  # save_data_name
        raw_bpm,
        chart_duration_ms,
        raw_offset,
        raw_note_count,
        *raw_times_and_positions,
    ) = lines
    float(raw_bpm)
    int(chart_duration_ms)
    int(raw_offset)
    note_count = int(raw_note_count)
    return len(raw_times_and_positions) == 2 * note_count


YUBIOSI_1_5_TAGS = {
    "TITLE_NAME",
    "DATA_ID",
    "BPM",
    "BPMS",
    "MUSIC_TIME",
    "OFFSET",
    "LEVEL",
    "PANEL_NUM",
    "AUDIO_FILE",
}


@false_if_raises(UnicodeError, ValueError)
def looks_like_yubiosi_1_5(contents: bytes) -> bool:
    lines = contents.decode(encoding="shift-jis-2004").splitlines()
    note_index = lines.index("[Notes]")
    return any(line_has_yubiosi_tag(line) for line in lines[:note_index])


def line_has_yubiosi_tag(line: str) -> bool:
    if line.startswith("#") and ":" in line:
        potential_tag = line[1 : line.index(":")]
        return potential_tag in YUBIOSI_1_5_TAGS
    else:
        return False


@false_if_raises(UnicodeError)
def looks_like_yubiosi_2_0(contents: bytes) -> bool:
    text = contents.decode("utf-16")
    lines = text.splitlines()
    return len(lines) >= 1 and lines[0] == "//Yubiosi 2.0"


@false_if_raises(IndexError)
def looks_like_iboogie(contents: bytes) -> bool:
    text = contents.decode("utf-8-sig", errors="surrogateescape")
    lines = text.splitlines()
    non_empty_lines = (l for l in lines if l.strip())  # noqa: E741
    first_five_lines = islice(non_empty_lines, 5)
    return any(looks_like_iboogie_chart_line(l) for l in first_five_lines)  # noqa: E741


def looks_like_iboogie_chart_line(line: str) -> bool:
    match = re.match(r".{4}[ 　]*\|(.*)\|", line)
    if not match:
        return False
    potential_timing_part = match.group(1)
    # Look for a BPM definition
    if not re.search(r"\(\d+(\.\d+)*\)", potential_timing_part):
        return False

    return True
