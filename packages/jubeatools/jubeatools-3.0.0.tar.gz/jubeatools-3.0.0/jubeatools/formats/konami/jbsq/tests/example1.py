from decimal import Decimal
from fractions import Fraction

from jubeatools.song import *

data = Song(
    metadata=Metadata(
        title=None, artist=None, audio=None, cover=None, preview=None, preview_file=None
    ),
    charts={
        "BSC": Chart(
            level=Decimal("0"),
            timing=Timing(
                events=(BPMEvent(time=Fraction(0, 1), BPM=Decimal("288.11")),),
                beat_zero_offset=Decimal("0.04"),
            ),
            hakus=set(),
            notes=[],
        )
    },
    common_timing=None,
    common_hakus=None,
)
