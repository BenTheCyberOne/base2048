"""
CLI entry point — invoked via ``python -m base2048``.

Usage
-----
    python -m base2048                        # run demo with reference vectors
    python -m base2048 encode "some text"
    python -m base2048 -e "some text"
    python -m base2048 decode "<encoded>"
    python -m base2048 -d "<encoded>"
    echo "some text" | python -m base2048 encode -   # read from stdin
    echo "some text" | python -m base2048 -           # shorthand encode from stdin
"""

import sys
from . import encode, decode, decode_str


def _demo() -> None:
    vectors: list[tuple[bytes, str | None]] = [
        (bytes([1, 2, 4, 8, 16, 32, 64, 128]), "GƸOʜeҩ"),
        (b"Hello, World!", "ԋϠɲණరϢఋԵړƶ"),
        (b"The quick brown fox jumps over the lazy dog.", None),
    ]
    w = 62
    print("=" * w)
    print("  Base2048  (qntm/base2048 compatible)")
    print("=" * w)
    for data, expected in vectors:
        enc = encode(data)
        dec = decode(enc)
        ok = dec == data
        if expected:
            ref = "  ✓ matches reference" if enc == expected else f"  ✗ MISMATCH (expected {expected!r})"
        else:
            ref = ""
        ratio = len(enc) / len(data)
        snippet = repr(data[:50]) + ("..." if len(data) > 50 else "")
        print(f"\n  Input   : {snippet}")
        print(f"  Encoded : {enc}{ref}")
        print(f"  Decoded : {dec[:50]!r}{'...' if len(dec) > 50 else ''}  {'✓' if ok else '✗'}")
        print(f"  Ratio   : {len(data)} bytes → {len(enc)} chars ({ratio:.2f} chars/byte)")
    print("\n" + "=" * w)


def main(argv: list[str] | None = None) -> int:
    args = (argv if argv is not None else sys.argv[1:])

    if not args:
        _demo()
        return 0

    cmd = args[0].lstrip("-").lower()

    # Encode
    if cmd in ("e", "encode"):
        rest = args[1:]
        if not rest:
            print("Usage: base2048 encode <text>", file=sys.stderr)
            return 1
        if rest[0] == "-":
            data = sys.stdin.buffer.read()
        else:
            data = " ".join(rest).encode("utf-8")
        print(encode(data))
        return 0

    # Decode
    if cmd in ("d", "decode"):
        rest = args[1:]
        if not rest:
            print("Usage: base2048 decode <encoded>", file=sys.stderr)
            return 1
        encoded = rest[0] if rest[0] != "-" else sys.stdin.read().strip()
        try:
            print(decode_str(encoded))
        except (ValueError, UnicodeDecodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    # Bare text or stdin shorthand
    if args[0] == "-":
        data = sys.stdin.buffer.read()
        print(encode(data))
        return 0

    # Treat remaining args as text to encode
    text = " ".join(args)
    enc = encode(text)
    print(f"Encoded : {enc}")
    print(f"Decoded : {decode_str(enc)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
