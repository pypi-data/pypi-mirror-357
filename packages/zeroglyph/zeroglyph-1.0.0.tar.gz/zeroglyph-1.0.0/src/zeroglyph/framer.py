import struct
import binascii
from .utils import encode_varint, decode_varint

class Framer:
    """
    TLV header packer/unpacker with varint length and CRC32 integrity.
    """
    MAGIC = b'ZG'
    SCHEME_ID = 1
    VERSION = 1
    FLAGS = 0
    CRC_SIZE = 4

    @staticmethod
    def pack(payload: bytes) -> bytes:
        # Header fields
        length = len(payload)
        varint_len = encode_varint(length)
        crc = binascii.crc32(payload) & 0xFFFFFFFF

        header = bytearray()
        header += Framer.MAGIC
        header += struct.pack('B', Framer.SCHEME_ID)
        header += struct.pack('B', Framer.VERSION)
        header += struct.pack('B', Framer.FLAGS)
        header += varint_len
        header += struct.pack('>I', crc)
        return bytes(header) + payload

    @staticmethod
    def unpack(packet: bytes) -> bytes:
        # Validate magic
        if packet[:2] != Framer.MAGIC:
            raise ValueError("Invalid magic header")
        # Check scheme
        if packet[2] != Framer.SCHEME_ID:
            raise ValueError(f"Unsupported scheme ID: {packet[2]}")
        # Skip version and flags
        offset = 5
        # Decode varint length
        length, offset = decode_varint(packet, offset)
        # Read CRC
        crc_read = struct.unpack('>I', packet[offset:offset + Framer.CRC_SIZE])[0]
        offset += Framer.CRC_SIZE
        # Extract payload
        payload = packet[offset:offset + length]
        # Verify integrity
        crc_calc = binascii.crc32(payload) & 0xFFFFFFFF
        if crc_read != crc_calc:
            raise ValueError("CRC mismatch")
        return payload
