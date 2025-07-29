import pytest
from zeroglyph.framer import Framer

@pytest.fixture
def sample_payload():
    return b"Hello, \xe2\x9c\x8c" * 5  # includes multi-byte emoji

def test_pack_unpack_roundtrip(sample_payload):
    packet = Framer.pack(sample_payload)
    recovered = Framer.unpack(packet)
    assert recovered == sample_payload

def test_magic_header_mismatch(sample_payload):
    packet = Framer.pack(sample_payload)
    bad = b'XX' + packet[2:]
    with pytest.raises(ValueError):
        Framer.unpack(bad)

def test_scheme_id_mismatch(sample_payload):
    packet = Framer.pack(sample_payload)
    bad = packet[:2] + b'\xFF' + packet[3:]
    with pytest.raises(ValueError):
        Framer.unpack(bad)

def test_crc_mismatch(sample_payload):
    packet = bytearray(Framer.pack(sample_payload))
    # flip a payload byte
    packet[-1] ^= 0xFF
    with pytest.raises(ValueError):
        Framer.unpack(bytes(packet))
