from jubeatools import song
from jubeatools.utils import reverse_dict

INDEX_TO_YUBIOSI_1_0 = {n: 2**n for n in range(16)}

YUBIOSI_1_0_TO_INDEX = reverse_dict(INDEX_TO_YUBIOSI_1_0)

INDEX_TO_DIF = {
    1: song.Difficulty.BASIC.value,
    2: song.Difficulty.ADVANCED.value,
    3: song.Difficulty.EXTREME.value,
    4: "EDIT-1",
    5: "EDIT-2",
    6: "EDIT-3",
    7: "EDIT-4",
    8: "EDIT-5",
    9: "EDIT-6",
    10: "EDIT-7",
}
