import string
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import AbstractSet, Any, Dict, Iterator, Optional, TypedDict

from jubeatools.formats.typing import ChartFileDumper, Dumper
from jubeatools.song import Chart, Difficulty, Song
from jubeatools.utils import none_or

DIFFICULTY_NUMBER: Dict[str, int] = {
    Difficulty.BASIC: 1,
    Difficulty.ADVANCED: 2,
    Difficulty.EXTREME: 3,
}

DIFFICULTY_INDEX: Dict[str, int] = {
    Difficulty.BASIC: 0,
    Difficulty.ADVANCED: 1,
    Difficulty.EXTREME: 2,
}


def make_dumper_from_chart_file_dumper(
    internal_dumper: ChartFileDumper,
    file_name_template: str,
) -> Dumper:
    """Adapt a ChartFileDumper to the Dumper protocol, The resulting function
    uses the file name template if it recieves an existing directory as an
    output path"""

    def dumper(song: Song, path: Path, **kwargs: Any) -> Dict[Path, bytes]:
        res: Dict[Path, bytes] = {}
        name_format = FileNameFormat.from_path(
            path, default_filename_format=file_name_template
        )
        files = internal_dumper(song, **kwargs)
        for chartfile in files:
            filepath = name_format.available_chart_filename(
                chartfile.song,
                chartfile.difficulty,
                chartfile.chart,
                already_chosen=res.keys(),
            )
            res[filepath] = chartfile.contents

        return res

    return dumper


class FormatParameters(TypedDict, total=False):
    title: str
    # uppercase BSC ADV EXT
    difficulty: str
    # 0-based
    difficulty_index: str
    # 1-based
    difficulty_number: str


@dataclass
class FileNameFormat:
    parent: Path
    name_format: str

    @classmethod
    def from_path(cls, path: Path, default_filename_format: str) -> "FileNameFormat":
        if path.is_dir():
            return FileNameFormat(parent=path, name_format=default_filename_format)
        else:
            return FileNameFormat(parent=path.parent, name_format=path.name)

    def available_chart_filename(
        self,
        song: Song,
        difficulty: str,
        chart: Chart,
        already_chosen: Optional[AbstractSet[Path]] = None,
    ) -> Path:
        fixed_params = extract_chart_format_params(song, difficulty, chart)
        return next(self.iter_possible_paths(fixed_params, already_chosen))

    def available_song_filename(
        self, song: Song, already_chosen: Optional[AbstractSet[Path]] = None
    ) -> Path:
        fixed_params = extract_song_format_params(song)
        return next(self.iter_possible_paths(fixed_params, already_chosen))

    def iter_possible_paths(
        self,
        fixed_params: FormatParameters,
        already_chosen: Optional[AbstractSet[Path]] = None,
    ) -> Iterator[Path]:
        all_paths = self.iter_deduped_paths(fixed_params)
        not_on_filesystem = (p for p in all_paths if not p.exists())
        if already_chosen is not None:
            yield from (p for p in not_on_filesystem if p not in already_chosen)
        else:
            yield from not_on_filesystem

    def iter_deduped_paths(self, params: FormatParameters) -> Iterator[Path]:
        parsed_name_format = Path(self.name_format)
        for dedup_index in count(start=0):
            dedup = "" if dedup_index == 0 else f" ({dedup_index})"
            formatter = BetterStringFormatter()
            stem = formatter.format(parsed_name_format.stem, **params)
            suffix = formatter.format(parsed_name_format.suffix, **params)
            yield self.parent / f"{stem}{dedup}{suffix}"


def extract_song_format_params(song: Song) -> FormatParameters:
    return FormatParameters(title=none_or(slugify, song.metadata.title) or "")


def extract_chart_format_params(
    song: Song, difficulty: str, chart: Chart
) -> FormatParameters:
    return FormatParameters(
        title=none_or(slugify, song.metadata.title) or "",
        difficulty=slugify(difficulty),
        difficulty_index=str(DIFFICULTY_INDEX.get(difficulty, 2)),
        difficulty_number=str(DIFFICULTY_NUMBER.get(difficulty, 3)),
    )


def slugify(s: str) -> str:
    s = remove_slashes(s)
    s = double_braces(s)
    return s


SLASHES = str.maketrans({"/": "", "\\": ""})


def remove_slashes(s: str) -> str:
    return s.translate(SLASHES)


BRACES = str.maketrans({"{": "{{", "}": "}}"})


def double_braces(s: str) -> str:
    return s.translate(BRACES)


class BetterStringFormatter(string.Formatter):
    """Enables the use of 'u' and 'l' suffixes in string format specifiers to
    convert the string to uppercase or lowercase
    Thanks stackoverflow ! https://stackoverflow.com/a/57570269/10768117"""

    def format_field(self, value: Any, format_spec: str) -> str:
        if isinstance(value, str):
            if format_spec.endswith("u"):
                value = value.upper()
                format_spec = format_spec[:-1]
            elif format_spec.endswith("l"):
                value = value.lower()
                format_spec = format_spec[:-1]
        return super().format(value, format_spec)
