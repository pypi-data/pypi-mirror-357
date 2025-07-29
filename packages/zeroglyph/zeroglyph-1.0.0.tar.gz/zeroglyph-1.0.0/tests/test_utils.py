# tests/test_utils.py
from zeroglyph.utils import encode_varint, decode_varint

def test_varint_roundtrip():
    for n in [0, 1, 128, 1024, 2**20]:
        encoded = encode_varint(n)
        decoded, _ = decode_varint(encoded)
        assert decoded == n
