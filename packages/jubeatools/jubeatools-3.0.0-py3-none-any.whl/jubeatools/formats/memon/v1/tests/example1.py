from decimal import Decimal
from fractions import Fraction

from jubeatools.song import *

# The memon v1 dumper, when trying to remove shared timing keys, would
# mistakenly try to use chart.timing directly instead of relying on
# iter_charts_with_applicable_timing() to provide the common_timing fallback,
# which would end up creating wrong timing objects
#
# Here, for example, the dumper would notice charts A1 and A2 both use
# beat_zero_offset=Decimal(1) and try to use this value in the memon file-level
# timing object.
#
# Then, when computing the required timing keys for charts B1 and B2, the dumper
# would find that their Chart.timing field is None, then wrongly assume this
# means they can rely on the previously computed file-level timing object, and
# hence make them use the incorrect beat_zero_offset=Decimal(1) instead of the
# correct Decimal(2), as provided by Song.common_timing
data = Song(
    metadata=Metadata(),
    charts={
        "A1": Chart(
            timing=Timing(
                events=(BPMEvent(time=Fraction(1), BPM=Decimal(1)),),
                beat_zero_offset=Decimal(1),
            ),
        ),
        "A2": Chart(
            timing=Timing(
                events=(BPMEvent(time=Fraction(1), BPM=Decimal(10)),),
                beat_zero_offset=Decimal(1),
            ),
        ),
        "B1": Chart(),
        "B2": Chart(),
    },
    common_timing=Timing(
        events=(BPMEvent(time=Fraction(2), BPM=Decimal(2)),),
        beat_zero_offset=Decimal(2),
    ),
)
