from jubeatools.song import *

data = Song(
    metadata=Metadata(),
    charts={
        "ADV": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
        "EDIT-1": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
        "EDIT-3": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
        "BSC": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
        "EDIT-4": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
        "EDIT-2": Chart(
            level=Decimal("1"),
            timing=None,
            hakus=None,
            notes=[TapNote(time=Fraction(0, 1), position=NotePosition(x=0, y=0))],
        ),
        "EDIT-5": Chart(level=Decimal("1"), timing=None, hakus=None, notes=[]),
    },
    common_timing=Timing(
        events=(BPMEvent(time=Fraction(0, 1), BPM=Decimal("75")),),
        beat_zero_offset=Decimal("0.00"),
    ),
    common_hakus=None,
)
