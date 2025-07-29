from collections import defaultdict
from typing import DefaultDict, List, Sequence

from jubeatools import song
from jubeatools.formats.dump_tools import make_dumper_from_chart_file_dumper
from jubeatools.formats.filetypes import ChartFile
from jubeatools.utils import group_by

from .. import commons as konami
from ..commons import AnyNote
from ..dump_tools import make_events_from_chart
from . import construct


def _dump_jbsq(song: song.Song, **kwargs: dict) -> List[ChartFile]:
    res = []
    for dif, chart, timing, hakus in song.iter_charts():
        events = make_events_from_chart(chart.notes, timing, hakus)
        jbsq_chart = make_jbsq_chart(events, chart.notes)
        chart_bytes = construct.jbsq.build(jbsq_chart)
        res.append(ChartFile(chart_bytes, song, dif, chart))

    return res


dump_jbsq = make_dumper_from_chart_file_dumper(
    internal_dumper=_dump_jbsq, file_name_template="seq_{difficulty:l}.jbsq"
)


def make_jbsq_chart(
    events: Sequence[konami.Event], notes: Sequence[AnyNote]
) -> construct.JBSQ:
    jbsq_events = [convert_event_to_jbsq(e) for e in events]
    num_events = len(events)
    combo = compute_max_combo(notes)
    end_time = next(e for e in events if e.command == konami.Command.END).time
    first_note_time_in_beats = min((n.time for n in notes), default=0)
    starting_notes = [n for n in notes if n.time == first_note_time_in_beats]
    starting_buttons = sum(1 << n.position.index for n in starting_notes)
    first_note_time = min(
        (
            e.time
            for e in events
            if e.command in (konami.Command.PLAY, konami.Command.LONG)
        ),
        default=0,
    )
    densities = compute_density_graph(events, end_time)
    jbsq_chart = construct.JBSQ(
        num_events=num_events,
        combo=combo,
        end_time=end_time,
        starting_buttons=starting_buttons,
        start_time=first_note_time,
        density_graph=densities,
        events=jbsq_events,
    )
    jbsq_chart.magic = choose_magic_bytes(notes)
    return jbsq_chart


def convert_event_to_jbsq(event: konami.Event) -> construct.Event:
    return construct.Event(
        type_=construct.EventType[event.command.name],
        time_in_ticks=event.time,
        value=event.value,
    )


def compute_max_combo(notes: Sequence[AnyNote]) -> int:
    notes_by_type = group_by(notes, type)
    tap_notes = len(notes_by_type[song.TapNote])
    long_notes = len(notes_by_type[song.LongNote])
    return tap_notes + 2 * long_notes


def compute_density_graph(events: Sequence[konami.Event], end_time: int) -> List[int]:
    events_by_type = group_by(events, lambda e: e.command)
    buckets: DefaultDict[int, int] = defaultdict(int)
    for tap in events_by_type[konami.Command.PLAY]:
        bucket = int((tap.time / end_time) * 120)
        buckets[bucket] += 1

    for long in events_by_type[konami.Command.LONG]:
        press_bucket = int((long.time / end_time) * 120)
        buckets[press_bucket] += 1
        duration = konami.EveLong.from_value(long.value).duration
        release_time = long.time + duration
        release_bucket = int((release_time / end_time) * 120)
        buckets[release_bucket] += 1

    res = []
    for i in range(0, 120, 2):
        # The jbsq density graph in a array of nibbles, the twist is that for
        # some obscure reason each pair of nibbles is swapped in the byte ...
        # little-endianness is a hell of a drug, don't do drugs kids ...
        # Also jubeat plus only renders density graph bars that are of length
        # 0 → 8. Any value above 8 will display as empty.
        first_nibble = min(buckets[i], 8)
        second_nibble = min(buckets[i + 1], 8)
        density_byte = (second_nibble << 4) + first_nibble
        res.append(density_byte)

    return res


def choose_magic_bytes(notes: Sequence[AnyNote]) -> bytes:
    # The magic bytes are actually checked by the app to decide whether or not
    # to display the "hold note" icon next to the song jacket
    if any(isinstance(note, song.LongNote) for note in notes):
        return b"IJSQ"
    else:
        # Could have also used IJBQ here instead, I don't know if that makes a
        # difference
        return b"JBSQ"
