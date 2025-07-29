import hypothesis.strategies as st
from hypothesis import given

from .. import guess


@given(st.binary())
def test_that_guess_format_only_raises_the_specific_value_error(
    contents: bytes,
) -> None:
    try:
        guess.guess_file_format(contents)
    except ValueError as e:
        if e.args != ("Unrecognized file format",):
            raise


def test_that_yubiosi_2_0_detection_does_not_raise_exception_for_non_utf16_files() -> None:
    text = "blablabla"
    bytes_ = text.encode("ascii")
    guess.looks_like_yubiosi_2_0(bytes_)
