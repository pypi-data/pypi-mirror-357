from typing import Dict

from . import jubeat_analyser, konami, malody, memon, yubiosi
from .format_names import Format
from .typing import Dumper, Loader

#: Maps each Format enum member to its associated loader
LOADERS: Dict[Format, Loader] = {
    Format.EVE: konami.load_eve,
    Format.JBSQ: konami.load_jbsq,
    Format.MALODY: malody.load_malody,
    Format.MEMON_LEGACY: memon.load_memon_legacy,
    Format.MEMON_0_1_0: memon.load_memon_0_1_0,
    Format.MEMON_0_2_0: memon.load_memon_0_2_0,
    Format.MEMON_0_3_0: memon.load_memon_0_3_0,
    Format.MEMON_1_0_0: memon.load_memon_1_0_0,
    Format.MONO_COLUMN: jubeat_analyser.load_mono_column,
    Format.MEMO: jubeat_analyser.load_memo,
    Format.MEMO_1: jubeat_analyser.load_memo1,
    Format.MEMO_2: jubeat_analyser.load_memo2,
    Format.YUBIOSI_1_0: yubiosi.load_yubiosi_1_0,
    Format.YUBIOSI_1_5: yubiosi.load_yubiosi_1_5,
    Format.YUBIOSI_2_0: yubiosi.load_yubiosi_2_0,
    Format.IBOOGIE: jubeat_analyser.load_iboogie,
}

#: Maps each Format enum member to its associated dumper
DUMPERS: Dict[Format, Dumper] = {
    Format.EVE: konami.dump_eve,
    Format.JBSQ: konami.dump_jbsq,
    Format.MALODY: malody.dump_malody,
    Format.MEMON_LEGACY: memon.dump_memon_legacy,
    Format.MEMON_0_1_0: memon.dump_memon_0_1_0,
    Format.MEMON_0_2_0: memon.dump_memon_0_2_0,
    Format.MEMON_0_3_0: memon.dump_memon_0_3_0,
    Format.MEMON_1_0_0: memon.dump_memon_1_0_0,
    Format.MONO_COLUMN: jubeat_analyser.dump_mono_column,
    Format.MEMO: jubeat_analyser.dump_memo,
    Format.MEMO_1: jubeat_analyser.dump_memo1,
    Format.MEMO_2: jubeat_analyser.dump_memo2,
    Format.YUBIOSI_1_0: yubiosi.dump_yubiosi_1_0,
    Format.YUBIOSI_1_5: yubiosi.dump_yubiosi_1_5,
    Format.YUBIOSI_2_0: yubiosi.dump_yubiosi_2_0,
    Format.IBOOGIE: jubeat_analyser.dump_iboogie,
}
