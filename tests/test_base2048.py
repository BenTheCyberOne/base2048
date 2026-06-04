"""
Tests for the base2048 package.

Run with:  pytest
"""

import os
import pytest
from base2048 import encode, decode, decode_str, __version__


# ---------------------------------------------------------------------------
# Reference vectors from qntm/base2048 README
# ---------------------------------------------------------------------------

REFERENCE_VECTORS = [
    (bytes([1, 2, 4, 8, 16, 32, 64, 128]), "GƸOʜeҩ"),
    (b"Hello, World!", "ԋϠɲණరϢఋԵړƶ"),
]


@pytest.mark.parametrize("data, expected", REFERENCE_VECTORS)
def test_encode_reference_vectors(data, expected):
    assert encode(data) == expected


@pytest.mark.parametrize("data, expected", REFERENCE_VECTORS)
def test_decode_reference_vectors(data, expected):
    assert decode(expected) == data


# ---------------------------------------------------------------------------
# Round-trip correctness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("data", [
    b"",
    b"\x00",
    b"\xff",
    b"\x00\x00",
    b"\xff\xff",
    b"a",
    b"ab",
    b"abc",
    b"abcd",
    bytes(range(256)),
    b"\x00" * 100,
    b"\xff" * 100,
])
def test_round_trip(data):
    assert decode(encode(data)) == data


def test_round_trip_random():
    """1000 random payloads of varying length."""
    for _ in range(1000):
        n = int.from_bytes(os.urandom(1), "big") + 1  # 1–256 bytes
        data = os.urandom(n)
        assert decode(encode(data)) == data


# ---------------------------------------------------------------------------
# String input to encode()
# ---------------------------------------------------------------------------

def test_encode_str_input():
    text = "Hello, World!"
    assert encode(text) == encode(text.encode("utf-8"))


def test_decode_str_helper():
    text = "Hello, World!"
    assert decode_str(encode(text)) == text


def test_decode_str_unicode():
    text = "Python 🐍"
    assert decode_str(encode(text)) == text


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------

def test_encode_empty():
    assert encode(b"") == ""


def test_decode_empty():
    assert decode("") == b""


# ---------------------------------------------------------------------------
# Bit-length boundary cases (all 11-bit remainder sizes: 0–10 leftover bits)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_bytes", range(1, 23))
def test_all_bit_boundaries(n_bytes):
    """Cover every possible (n_bytes * 8) mod 11 remainder."""
    data = os.urandom(n_bytes)
    assert decode(encode(data)) == data


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_decode_unknown_character():
    with pytest.raises(ValueError, match="Unrecognised"):
        decode("💥")


def test_decode_secondary_not_at_end():
    """'3' is a secondary character; placing it before a primary char must fail."""
    primary = encode(b"\x00\x00")   # two primary chars
    with pytest.raises(ValueError, match="Secondary character"):
        decode("3" + primary)


def test_decode_bad_padding():
    """Flip a bit in a single-char encoding to corrupt the padding."""
    enc = encode(b"\x01")   # one byte → one secondary char
    # '0' has different padding bits than the correct char
    bad = "0" if enc != "0" else "1"
    with pytest.raises(ValueError, match="[Pp]adding"):
        decode(bad)


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def test_version_string():
    assert isinstance(__version__, str)
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)
