import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from jubeatools.song import Chart, Difficulty, Metadata, SecondsTime, Song, Timing
from jubeatools.utils import group_by, none_or

from .load import Memo2Parser


def load_iboogie(path: Path, **kwargs: Any) -> Song:
    files = find_files(path)
    charts = {dif: load_iboogie_chart(path) for dif, path in files.charts.items()}
    title = none_or(lambda p: p.read_text("utf-8-sig"), files.song_title)
    return Song(metadata=Metadata(title=title), charts=charts)


@dataclass
class Files:
    song_title: Optional[Path] = None
    charts: Dict[str, Path] = field(default_factory=dict)

    def looks_valid(self) -> bool:
        return self.song_title is not None and len(self.charts) > 0


def find_files(path: Path) -> Files:
    if path.is_file():
        return find_files_from_file_path(path)
    elif path.is_dir():
        return find_files_in_dir(path)
    else:
        raise ValueError("The input path is neither a file nor a directory")


def find_files_from_file_path(path: Path) -> Files:
    name = path.stem
    if not name[-1].isdigit():
        return Files(charts={Difficulty.EXTREME.value: path})

    song_title_file = path.with_stem(name[:-1])
    if not song_title_file.is_file():
        return Files(charts={Difficulty.EXTREME.value: path})

    index = int(name[-1])
    dif = INDEX_TO_DIF[index]
    return Files(song_title=song_title_file, charts={dif: path})


def find_files_in_dir(path: Path) -> Files:
    files = list(path.glob("*.txt"))
    files_by_prefix = group_by(files, lambda f: re.sub(r"\d$", "", f.stem))
    file_set_by_prefix = {
        prefix: assign_file_kinds(files) for prefix, files in files_by_prefix.items()
    }
    valid_file_sets = [
        files for files in file_set_by_prefix.values() if files.looks_valid()
    ]
    if len(valid_file_sets) == 0:
        raise ValueError(
            "Could not find iboogie chart files in the folder. "
            "Make sure the folder contains BOTH a .txt file that contains "
            "the song title AND .txt chart files with the same name plus a "
            "digit suffix indicating difficulty. "
            "For instance :\n"
            "  - sigsig.txt (file containing the full song title)\n"
            "  - sigsig0.txt (BSC chart)\n"
            "  - sigsig1.txt (ADV chart)\n"
            "  - sigsig2.txt (EXT chart)"
        )
    elif len(valid_file_sets) > 1:
        raise ValueError("Multiple iboogie songs found in the folder")
    else:
        return valid_file_sets[0]


def assign_file_kinds(files: List[Path]) -> Files:
    result = Files()
    for file in files:
        dif = guess_file_difficulty(file.stem)
        if dif is None:
            result.song_title = file
        else:
            result.charts[dif] = file

    return result


def guess_file_difficulty(stem: str) -> Optional[str]:
    if not stem:
        return None

    try:
        index = int(stem[-1])
    except ValueError:
        return None

    return INDEX_TO_DIF.get(index)


INDEX_TO_DIF = {
    0: Difficulty.BASIC.value,
    1: Difficulty.ADVANCED.value,
    2: Difficulty.EXTREME.value,
    3: "EDIT-1",
    4: "EDIT-2",
    5: "EDIT-3",
    6: "EDIT-4",
    7: "EDIT-5",
    8: "EDIT-6",
    9: "EDIT-7",
}


def load_iboogie_chart(path: Path) -> Chart:
    parser = Memo2Parser(bytes_per_panel=1)
    lines = path.read_text(encoding="utf-8-sig").split("\n")
    for i, raw_line in enumerate(lines, start=1):
        try:
            parser.load_line(raw_line)
        except Exception as e:
            raise SyntaxError(f"On line {i}\n{e}")

    parser.finish_last_few_notes()
    timing = Timing(
        events=parser.timing_events,
        beat_zero_offset=SecondsTime(parser.offset or 0) / 1000,
    )
    return Chart(
        timing=timing,
        notes=sorted(parser.notes(), key=lambda n: (n.time, n.position)),
    )
