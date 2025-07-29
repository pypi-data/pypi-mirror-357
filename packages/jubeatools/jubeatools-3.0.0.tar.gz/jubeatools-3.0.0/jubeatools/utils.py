"""General utility functions"""

import unicodedata
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
from functools import reduce
from math import gcd
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Protocol,
    TypeVar,
)


def single_lcm(a: int, b: int) -> int:
    """Return lowest common multiple of two numbers"""
    return a * b // gcd(a, b)


def lcm(*args: int) -> int:
    """Return lcm of args."""
    return reduce(single_lcm, args, 1)


class SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...


SupportsLessThanT = TypeVar("SupportsLessThanT", bound=SupportsLessThan)  # noqa: Y001


def clamp(
    value: SupportsLessThanT, min_: SupportsLessThanT, max_: SupportsLessThanT
) -> Any:
    return max(min_, min(max_, value))


def charinfo(c: str) -> str:
    """Return some info on the character"""
    return f"{c!r}  # U+{ord(c):05X} : {unicodedata.name(c)}"


A = TypeVar("A")
B = TypeVar("B")

# Monadic stuff !
def none_or(c: Callable[[A], B], e: Optional[A]) -> Optional[B]:
    if e is None:
        return None
    else:
        return c(e)


def fraction_to_decimal(frac: Fraction) -> Decimal:
    "Thanks stackoverflow ! https://stackoverflow.com/a/40468867/10768117"
    return frac.numerator / Decimal(frac.denominator)


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def group_by(elements: Iterable[V], key: Callable[[V], K]) -> Dict[K, List[V]]:
    res = defaultdict(list)
    for e in elements:
        res[key(e)].append(e)

    return res


V2 = TypeVar("V2", bound=Hashable)


def reverse_dict(d: dict[K, V2]) -> dict[V2, K]:
    return {v: k for k, v in d.items()}


def mixed_number_format(f: Fraction) -> str:
    """Formats fractions the following way :

    >>> mixed_number_format(Fraction(4,2))
    '2'
    >>> mixed_number_format(Fraction(-12,3))
    '-4'
    >>> mixed_number_format(Fraction(1,3))
    '1/3'
    >>> mixed_number_format(Fraction(-1,3))
    '-1/3'
    >>> mixed_number_format(Fraction(5,3))
    '1 + 2/3'
    >>> mixed_number_format(Fraction(-7,3))
    '-(2 + 1/3)'
    """
    abs_value = abs(f)
    integer_part = int(abs_value)
    fractional_part = abs_value % 1
    addition_elements = []
    if integer_part != 0:
        addition_elements.append(str(integer_part))
    if fractional_part != 0:
        addition_elements.append(
            f"{fractional_part.numerator}/{fractional_part.denominator}"
        )
    if not addition_elements:
        return "0"

    addition = " + ".join(addition_elements)
    if f >= 0:
        return addition
    else:
        if len(addition_elements) > 1:
            return f"-({addition})"
        else:
            return f"-{addition}"
