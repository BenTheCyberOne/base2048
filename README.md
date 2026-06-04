# base2048

A Python implementation of [Base2048](https://github.com/qntm/base2048) — a binary-to-text encoding that stores **11 bits per Unicode character**, producing roughly 25% fewer characters than Base64.

Output is **fully compatible** with [qntm/base2048](https://github.com/qntm/base2048) (the canonical JavaScript implementation). The same alphabet, the same padding scheme, the same reference test vectors.

```python
from base2048 import encode, decode, decode_str

encode(bytes([1, 2, 4, 8, 16, 32, 64, 128]))  # → 'GƸOʜeҩ'
encode("Hello, World!")                         # → 'ԋϠɲణరϢఋԵړƶ'
decode("ԋϠɲణరϢఋԵړƶ")                         # → b'Hello, World!'
decode_str("ԋϠɲణరϢఋԵړƶ")                      # → 'Hello, World!'
```

## Why Base2048?

Base64 encodes 6 bits per ASCII character. Base2048 encodes 11 bits per Unicode character — nearly 2× the information density. When your transport counts Unicode code points (not bytes), Base2048 wins:

| Encoding | Bits/char | Chars for 100 bytes |
|----------|-----------|---------------------|
| Base64   | 6         | ~136                |
| Base2048 | 11        | ~73                 |

The alphabet consists of 2048 carefully selected "safe" Unicode characters — no control characters, no whitespace, no combining diacritics — designed to survive copy-paste through any Unicode-clean system.

## Installation

```bash
pip install base2048
```

Or from source:

```bash
git clone https://github.com/benthecyberone/base2048
cd base2048
pip install .
```

## Usage

### Library

```python
from base2048 import encode, decode, decode_str

# Encode bytes
data = b"\x00\x01\x02\xff"
encoded = encode(data)         # str
decoded = decode(encoded)      # bytes — identical to data

# Encode a string (UTF-8 encoded automatically)
encoded = encode("Hello!")
text = decode_str(encoded)     # 'Hello!'
```

### Command line

```bash
# Encode
base2048 encode "Hello, World!"
echo -n "Hello, World!" | base2048 encode -

# Decode
base2048 decode "ԋϠɲణరϢఋԵړƶ"

# Demo with reference vectors
base2048
```

Or via `python -m`:

```bash
python -m base2048 encode "Hello!"
python -m base2048 decode "ϙƸ٣Ρ"
```

## API

### `encode(data: bytes | str) -> str`

Encode bytes (or a UTF-8 string) to a Base2048 string.

### `decode(encoded: str) -> bytes`

Decode a Base2048 string back to bytes. Raises `ValueError` for invalid input.

### `decode_str(encoded: str, encoding: str = "utf-8") -> str`

Convenience wrapper: decode and interpret the result as a string.

## Encoding spec

- **Primary alphabet**: 2048 Unicode characters, each encoding 11 bits.
- **Secondary alphabet**: `0`–`7`, used only as the *final* character when the input's bit count is not a multiple of 11. Encodes 3 bits.
- **Padding**: leftover bits are padded with `1`-bits (not `0`-bits). On decode, padding bits are verified and a `ValueError` is raised on mismatch.

This exactly matches the [qntm/base2048](https://github.com/qntm/base2048) specification.

## Requirements

- Python 3.10+
- No dependencies

## Running the tests

```bash
pip install pytest
pytest
```

## License

MIT
