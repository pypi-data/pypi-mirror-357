"""
yubiosi (指押) is a now-defunct jubeat simulator for Android

It notably also supports 3x3 charts although jubeatools only supports
converting to and from 4x4 charts

The three versions of the format are documented on a dedicated wiki :

https://w.atwiki.jp/yubiosi2/
"""

from .dump import dump_yubiosi_1_0, dump_yubiosi_1_5, dump_yubiosi_2_0
from .load import load_yubiosi_1_0, load_yubiosi_1_5, load_yubiosi_2_0
