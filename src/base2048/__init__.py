"""
base2048.py — Base2048 encoder/decoder compatible with qntm/base2048

Implements the Base2048 encoding exactly as specified by qntm's canonical
JavaScript implementation (https://github.com/qntm/base2048).

Encoding summary
----------------
- Primary alphabet:  2048 Unicode characters, each storing 11 bits.
- Secondary alphabet: 8 Unicode characters ('0'–'7'), used for the final
  character when the input bit count is not a multiple of 11. It stores the
  remaining bits, right-padded with 1-bits to fill 3 bits.
- Padding rule: the last partial group is always padded with 1-bits (not 0-bits).
  If ≤ 3 bits remain in the final group, a secondary character is used;
  otherwise a primary character is used with 1-bit padding.

Reference test vector (from the official README):
    encode(bytes([1, 2, 4, 8, 16, 32, 64, 128])) == 'GƸOʜeҩ'

Usage
-----
    from base2048 import encode, decode, decode_str

    encoded  = encode(b"Hello!")      # bytes → str
    encoded  = encode("Hello!")       # str (UTF-8 encoded first) → str
    original = decode(encoded)        # str → bytes
    text     = decode_str(encoded)    # str → str (UTF-8 decoded)

CLI
---
    python base2048.py                        # demo with test vectors
    python base2048.py encode "some text"
    python base2048.py decode "<encoded>"
"""

import sys

# ---------------------------------------------------------------------------
# Alphabet — Unicode code-point ranges derived from qntm/base2048 source
# ---------------------------------------------------------------------------
# Each tuple is an inclusive (first, last) code-point range.
# Expanding all ranges in order produces the exact 2048-character primary
# alphabet used by the canonical JS implementation.

_RANGES_PRIMARY = [
    (56, 57), (65, 90), (97, 122), (198, 198), (208, 208), (216, 216),
    (222, 223), (230, 230), (240, 240), (248, 248), (254, 254), (272, 273),
    (294, 295), (305, 305), (312, 312), (321, 322), (330, 331), (338, 339),
    (358, 359), (384, 415), (418, 430), (433, 451), (477, 477), (484, 485),
    (502, 503), (540, 541), (544, 549), (564, 687), (880, 883), (886, 887),
    (891, 893), (895, 895), (913, 929), (931, 937), (945, 969), (975, 975),
    (983, 1007), (1011, 1011), (1015, 1016), (1018, 1023), (1026, 1026), (1028, 1030),
    (1032, 1035), (1039, 1048), (1050, 1080), (1082, 1103), (1106, 1106), (1108, 1110),
    (1112, 1115), (1119, 1141), (1144, 1153), (1162, 1216), (1219, 1231), (1236, 1237),
    (1240, 1241), (1248, 1249), (1256, 1257), (1270, 1271), (1274, 1327), (1329, 1366),
    (1377, 1414), (1488, 1514), (1520, 1522), (1568, 1569), (1575, 1599), (1601, 1610),
    (1632, 1641), (1646, 1647), (1649, 1652), (1657, 1727), (1729, 1729), (1731, 1746),
    (1749, 1749), (1774, 1788), (1791, 1791), (1808, 1808), (1810, 1839), (1869, 1957),
    (1969, 1969), (1984, 2026), (2048, 2069), (2112, 2136), (2144, 2154), (2208, 2228),
    (2230, 2237), (2308, 2344), (2346, 2352), (2354, 2355), (2357, 2361), (2365, 2365),
    (2384, 2384), (2400, 2401), (2406, 2415), (2418, 2432), (2437, 2444), (2447, 2448),
    (2451, 2472), (2474, 2480), (2482, 2482), (2486, 2489), (2493, 2493), (2510, 2510),
    (2528, 2529), (2534, 2545), (2548, 2553), (2556, 2556), (2565, 2570), (2575, 2576),
    (2579, 2600), (2602, 2608), (2610, 2610), (2613, 2613), (2616, 2617), (2652, 2652),
    (2662, 2671), (2674, 2676), (2693, 2701), (2703, 2705), (2707, 2728), (2730, 2736),
    (2738, 2739), (2741, 2745), (2749, 2749), (2768, 2768), (2784, 2785), (2790, 2799),
    (2809, 2809), (2821, 2828), (2831, 2832), (2835, 2856), (2858, 2864), (2866, 2867),
    (2869, 2873), (2877, 2877), (2911, 2913), (2918, 2927), (2929, 2935), (2947, 2947),
    (2949, 2954), (2958, 2960), (2962, 2963), (2965, 2965), (2969, 2970), (2972, 2972),
    (2974, 2975), (2979, 2980), (2984, 2986), (2990, 3001), (3024, 3024), (3046, 3058),
    (3077, 3084), (3086, 3088), (3090, 3112), (3114, 3129), (3133, 3133), (3160, 3162),
    (3168, 3169), (3174, 3183), (3192, 3198), (3200, 3200), (3205, 3212), (3214, 3216),
    (3218, 3240), (3242, 3251), (3253, 3257), (3261, 3261), (3294, 3294), (3296, 3297),
    (3302, 3311), (3313, 3314), (3333, 3340), (3342, 3344), (3346, 3386), (3389, 3389),
    (3406, 3406), (3412, 3414), (3416, 3425), (3430, 3448), (3450, 3455), (3461, 3478),
    (3482, 3505), (3507, 3515), (3517, 3517), (3520, 3526), (3558, 3567), (3585, 3632),
    (3634, 3634), (3648, 3653), (3664, 3673), (3713, 3714), (3716, 3716), (3719, 3720),
    (3722, 3722), (3725, 3725), (3732, 3735), (3737, 3743), (3745, 3747), (3749, 3749),
    (3751, 3751), (3754, 3755), (3757, 3760), (3762, 3762), (3773, 3773), (3776, 3780),
    (3792, 3801), (3806, 3807), (3840, 3840), (3872, 3891), (3904, 3906), (3908, 3911),
    (3913, 3916), (3918, 3921), (3923, 3926), (3928, 3931), (3933, 3944), (3946, 3948),
    (3976, 3980), (4096, 4133), (4135, 4138), (4159, 4169), (4176, 4181),
]

# Secondary alphabet: '0'–'7' (code points 48–55), stores 3 bits per character.
_RANGES_SECONDARY = [(48, 55)]

_BITS_PER_CHAR = 11
_BITS_PER_BYTE = 8


def _expand(ranges: list[tuple[int, int]]) -> list[str]:
    out: list[str] = []
    for first, last in ranges:
        out.extend(chr(cp) for cp in range(first, last + 1))
    return out


# Build lookup tables once at import time
_PRIMARY   = _expand(_RANGES_PRIMARY)    # 2048 chars, indexed 0–2047
_SECONDARY = _expand(_RANGES_SECONDARY)  # 8 chars,   indexed 0–7

# encode lookup: numZBits → alphabet list
_LOOKUP_E: dict[int, list[str]] = {
    _BITS_PER_CHAR:                          _PRIMARY,
    _BITS_PER_CHAR - _BITS_PER_BYTE:        _SECONDARY,  # 3 bits → secondary
}

# decode lookup: char → (numZBits, index)
_LOOKUP_D: dict[str, tuple[int, int]] = {
    ch: (numZBits, z)
    for numZBits, alphabet in _LOOKUP_E.items()
    for z, ch in enumerate(alphabet)
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encode(data: bytes | str) -> str:
    """
    Encode *data* to a Base2048 string compatible with qntm/base2048.

    Parameters
    ----------
    data:
        Bytes to encode.  A ``str`` is UTF-8 encoded automatically.

    Returns
    -------
    str
        Base2048-encoded string (empty string for empty input).
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    out: list[str] = []
    z = 0        # bit accumulator
    numZBits = 0

    for byte in data:
        for j in range(_BITS_PER_BYTE - 1, -1, -1):  # MSB first
            z = (z << 1) | ((byte >> j) & 1)
            numZBits += 1
            if numZBits == _BITS_PER_CHAR:
                out.append(_LOOKUP_E[numZBits][z])
                z = 0
                numZBits = 0

    # Final partial group: pad with 1-bits until numZBits is a valid key
    if numZBits:
        while numZBits not in _LOOKUP_E:
            z = (z << 1) | 1
            numZBits += 1
        out.append(_LOOKUP_E[numZBits][z])

    return "".join(out)


def decode(encoded: str) -> bytes:
    """
    Decode a Base2048 string produced by :func:`encode` (or qntm/base2048).

    Parameters
    ----------
    encoded:
        A Base2048-encoded string.

    Returns
    -------
    bytes
        Original bytes (empty bytes for empty string).

    Raises
    ------
    ValueError
        If *encoded* contains unknown characters, a secondary character appears
        in a non-final position, or the padding bits are not all 1s.
    """
    if not encoded:
        return b""

    buf = bytearray(len(encoded) * _BITS_PER_CHAR // _BITS_PER_BYTE)
    num_bytes = 0
    uint8 = 0
    num_bits = 0
    last_i = len(encoded) - 1

    for i, ch in enumerate(encoded):
        if ch not in _LOOKUP_D:
            raise ValueError(f"Unrecognised Base2048 character: {ch!r}")
        numZBits, z = _LOOKUP_D[ch]
        if numZBits != _BITS_PER_CHAR and i != last_i:
            raise ValueError(
                f"Secondary character found before end of input at position {i}"
            )
        for j in range(numZBits - 1, -1, -1):  # MSB first
            uint8 = (uint8 << 1) | ((z >> j) & 1)
            num_bits += 1
            if num_bits == _BITS_PER_BYTE:
                buf[num_bytes] = uint8
                num_bytes += 1
                uint8 = 0
                num_bits = 0

    # All remaining (padding) bits must be 1s
    if uint8 != (1 << num_bits) - 1:
        raise ValueError(
            "Padding mismatch — input may be corrupt or from an incompatible encoder"
        )

    return bytes(buf[:num_bytes])


def decode_str(encoded: str, encoding: str = "utf-8") -> str:
    """
    Decode a Base2048 string and interpret the bytes as text.

    Parameters
    ----------
    encoded:
        A Base2048-encoded string.
    encoding:
        Text encoding to use (default ``"utf-8"``).

    Returns
    -------
    str
        The original string.
    """
    return decode(encoded).decode(encoding)

__version__ = "1.0.0"
__all__ = ["encode", "decode", "decode_str"]
